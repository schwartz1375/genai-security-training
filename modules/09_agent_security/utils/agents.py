"""LLM-driven multi-agent runtime with graph orchestration support."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, TypedDict

from .llm_adapter import LocalLLMAdapter, LLMConfig
from .policy import DEFAULT_POLICY, check_policy, detect_threat_indicators, sanitize_input, validate_output
from .tools import TOOL_REGISTRY


class AgentState(TypedDict, total=False):
    goal: str
    sanitized_goal: str
    conversation_id: str
    memory_path: str
    base_dir: str
    knowledge_base: Dict[str, str]
    memory_context: str
    threat_indicators: list[str]
    risk_score: int
    policy_events: list[Dict[str, Any]]
    tool_results: list[Dict[str, Any]]
    tool_call_counts: Dict[str, int]
    plan: str
    next_action: str
    proposed_tool: str
    proposed_args: Dict[str, Any]
    latest_output: str
    reviewer_verdict: str
    final_output: str
    alerts: list[str]
    halt_reason: str
    steps: int
    used_langgraph: bool


def _load_memory(memory_path: str, conversation_id: str) -> tuple[str, list[str]]:
    path = Path(memory_path).resolve()
    if not path.exists():
        return "", []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "", []
    entries = data.get(conversation_id, [])
    context_lines: list[str] = []
    indicators: set[str] = set()
    for item in entries[-5:]:
        if isinstance(item, dict):
            note = str(item.get("note", ""))
            source = str(item.get("source_agent", "unknown"))
            tags = [str(t) for t in item.get("provenance_tags", [])]
            context_lines.append(f"- [{source}] {note}")
            indicators.update(tags)
            indicators.update(detect_threat_indicators(note))
        else:
            note = str(item)
            context_lines.append(f"- {note}")
            indicators.update(detect_threat_indicators(note))
    return "\n".join(context_lines), sorted(indicators)


def _planner_node(state: AgentState, llm: LocalLLMAdapter) -> AgentState:
    goal = state["goal"]
    sanitized = sanitize_input(goal)
    memory_context, memory_indicators = _load_memory(state["memory_path"], state["conversation_id"])

    prompt = f"""
You are a security-aware planning agent.
Given the user goal, decide the safest next step.
Return JSON only with keys:
- action: one of ["tool_call", "finalize"]
- tool_name: one of ["retrieve_knowledge", "read_file", "query_db", "append_memory_note", ""]
- tool_args: JSON object
- plan: short text

User goal: {sanitized}
Memory context:
{memory_context}
"""
    goal_l = sanitized.lower()
    if "read file" in goal_l:
        path = "../../../../etc/passwd"
        if "read file" in sanitized:
            path = sanitized.split("read file", 1)[1].strip().split(" ", 1)[0] or path
        fallback = {
            "action": "tool_call",
            "tool_name": "read_file",
            "tool_args": {"path": path},
            "plan": "Fallback selected file-read request path from user goal.",
        }
    elif "query database" in goal_l or "select " in goal_l:
        sql = "SELECT id, username, role FROM users"
        if ":" in sanitized:
            sql = sanitized.split(":", 1)[1].strip() or sql
        fallback = {
            "action": "tool_call",
            "tool_name": "query_db",
            "tool_args": {"sql": sql},
            "plan": "Fallback selected DB query based on user goal.",
        }
    elif "store memory note" in goal_l:
        note = sanitized
        if ":" in sanitized:
            note = sanitized.split(":", 1)[1].strip() or note
        fallback = {
            "action": "tool_call",
            "tool_name": "append_memory_note",
            "tool_args": {"note": note},
            "plan": "Fallback selected memory update based on user goal.",
        }
    else:
        fallback = {
            "action": "tool_call",
            "tool_name": "retrieve_knowledge",
            "tool_args": {"query": "agent"},
            "plan": "Fallback selected retrieval flow.",
        }
    decision = llm.generate_json(prompt, fallback=fallback)

    state["sanitized_goal"] = sanitized
    state["memory_context"] = memory_context
    state["plan"] = str(decision.get("plan", ""))
    state["next_action"] = str(decision.get("action", "finalize"))
    state["proposed_tool"] = str(decision.get("tool_name", ""))
    state["proposed_args"] = decision.get("tool_args", {}) if isinstance(decision.get("tool_args", {}), dict) else {}

    indicators = detect_threat_indicators(goal + "\n" + memory_context + "\n" + json.dumps(state["proposed_args"]))
    indicators = sorted(set(indicators) | set(memory_indicators))
    state["threat_indicators"] = indicators
    state["risk_score"] = len(indicators)
    if indicators:
        state.setdefault("alerts", []).append(f"Threat indicators: {', '.join(indicators)}")
    return state


def _policy_gate_node(state: AgentState, policy: Dict[str, Any]) -> AgentState:
    action = state.get("next_action", "finalize")
    if action != "tool_call":
        state["latest_output"] = "Planner chose to finalize without tool usage."
        return state

    event = check_policy(
        # Gate the planner proposal using executor permissions, since executor would run it.
        agent="executor",
        tool_name=state.get("proposed_tool", ""),
        args=state.get("proposed_args", {}),
        state=state,
        policy=policy,
    )
    state.setdefault("policy_events", []).append(
        {
            "agent": "planner",
            "tool": state.get("proposed_tool", ""),
            "args": state.get("proposed_args", {}),
            "allowed": event["allowed"],
            "reason": event["reason"],
        }
    )
    if not event["allowed"]:
        state["latest_output"] = event["reason"]
    return state


def _executor_node(state: AgentState, policy: Dict[str, Any]) -> AgentState:
    tool_name = state.get("proposed_tool", "")
    args = dict(state.get("proposed_args", {}))

    # Executor gets its own policy check with stricter role limits.
    event = check_policy(agent="executor", tool_name=tool_name, args=args, state=state, policy=policy)
    state.setdefault("policy_events", []).append(
        {"agent": "executor", "tool": tool_name, "args": args, "allowed": event["allowed"], "reason": event["reason"]}
    )
    if not event["allowed"]:
        state["latest_output"] = event["reason"]
        return state

    tool = TOOL_REGISTRY.get(tool_name)
    if not tool:
        state["latest_output"] = f"Unknown tool '{tool_name}'."
        return state

    # Add runtime context for tools that need local state.
    if tool_name == "read_file":
        args.setdefault("base_dir", state["base_dir"])
    elif tool_name == "query_db":
        args.setdefault("base_dir", state["base_dir"])
    elif tool_name == "append_memory_note":
        args.setdefault("memory_path", state["memory_path"])
        args.setdefault("conversation_id", state["conversation_id"])
        args.setdefault("source_agent", "executor")
        args.setdefault("provenance_tags", state.get("threat_indicators", []))
    elif tool_name == "retrieve_knowledge":
        args.setdefault("kb", state.get("knowledge_base", {}))

    result = tool(**args)
    state.setdefault("tool_results", []).append({"tool": tool_name, "args": args, "result": result})
    data_text = json.dumps(result)
    output_indicators = detect_threat_indicators(data_text)
    if output_indicators:
        state["risk_score"] = state.get("risk_score", 0) + len(output_indicators)
        state.setdefault("alerts", []).append(f"Tool output indicators: {', '.join(output_indicators)}")
        merged = set(state.get("threat_indicators", [])) | set(output_indicators)
        state["threat_indicators"] = sorted(merged)
    state["latest_output"] = json.dumps(result)
    return state


def _reviewer_node(state: AgentState, llm: LocalLLMAdapter) -> AgentState:
    latest_output = state.get("latest_output", "")
    policy_events = state.get("policy_events", [])

    output_validation = validate_output(latest_output)
    if not output_validation["ok"]:
        state.setdefault("alerts", []).append(f"Output validation flags: {output_validation['risk_flags']}")

    prompt = f"""
You are a security reviewer.
Given planner/executor outcomes, decide final verdict.
Return JSON only with keys:
- verdict: one of ["allow", "block", "review"]
- reason: short explanation
- final_output: short response

Latest output: {latest_output}
Policy events: {json.dumps(policy_events[-4:])}
Risk score: {state.get("risk_score", 0)}
Output validation flags: {output_validation.get("risk_flags", [])}
"""
    denied = sum(1 for e in policy_events if not e.get("allowed"))
    low_risk = denied == 0 and output_validation["ok"] and state.get("risk_score", 0) == 0
    if low_risk:
        fallback = {"verdict": "allow", "reason": "Fallback low-risk path.", "final_output": latest_output}
    else:
        fallback = {"verdict": "review", "reason": "Fallback elevated-risk path.", "final_output": "Manual review required."}
    decision = llm.generate_json(prompt, fallback=fallback)

    verdict = str(decision.get("verdict", "block")).lower()
    reason = str(decision.get("reason", "No reason provided."))
    final_output = str(decision.get("final_output", latest_output))

    if denied > 0 or not output_validation["ok"] or state.get("risk_score", 0) > 0:
        if verdict == "allow":
            # Reduce false negatives: high risk cannot be auto-allowed.
            verdict = "review"
            reason = "Auto-escalated due to risk/policy conditions."
            final_output = "Manual review required."

    state["reviewer_verdict"] = verdict
    state["halt_reason"] = reason
    state["final_output"] = final_output
    return state


def _next_from_policy(state: AgentState) -> str:
    if state.get("next_action") != "tool_call":
        return "reviewer"
    latest = state.get("latest_output", "")
    if latest.startswith("Tool ") or "not allowed" in latest or "limit exceeded" in latest or "manual review" in latest.lower():
        return "reviewer"
    return "executor"


def _run_with_langgraph(initial_state: AgentState, llm: LocalLLMAdapter, policy: Dict[str, Any], max_steps: int) -> AgentState:
    from langgraph.graph import END, StateGraph

    workflow = StateGraph(AgentState)
    workflow.add_node("planner", lambda s: _planner_node(s, llm))
    workflow.add_node("policy_gate", lambda s: _policy_gate_node(s, policy))
    workflow.add_node("executor", lambda s: _executor_node(s, policy))
    workflow.add_node("reviewer", lambda s: _reviewer_node(s, llm))

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "policy_gate")
    workflow.add_conditional_edges("policy_gate", _next_from_policy, {"executor": "executor", "reviewer": "reviewer"})
    workflow.add_edge("executor", "reviewer")
    workflow.add_edge("reviewer", END)

    app = workflow.compile()
    result = app.invoke(initial_state, config={"recursion_limit": max_steps})
    result["steps"] = 2 + len(result.get("policy_events", []))
    result["used_langgraph"] = True
    return result


def _run_fallback(initial_state: AgentState, llm: LocalLLMAdapter, policy: Dict[str, Any], max_steps: int) -> AgentState:
    state = dict(initial_state)
    steps = 0
    steps += 1
    state = _planner_node(state, llm)
    if steps >= max_steps:
        state["halt_reason"] = "max_steps"
        state["used_langgraph"] = False
        return state

    steps += 1
    state = _policy_gate_node(state, policy)
    if _next_from_policy(state) == "executor" and steps < max_steps:
        steps += 1
        state = _executor_node(state, policy)
    if steps < max_steps:
        steps += 1
        state = _reviewer_node(state, llm)
    state["steps"] = steps
    state["used_langgraph"] = False
    return state


def run_workflow(
    goal: str,
    *,
    policy: Optional[Dict[str, Any]] = None,
    max_steps: int = 8,
    model_name: str = "distilgpt2",
    memory_path: str = "modules/09_agent_security/labs/memory_store.json",
    conversation_id: str = "default",
    base_dir: str = "modules/09_agent_security/labs/sandbox_data",
    knowledge_base: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    state: AgentState = {
        "goal": goal,
        "conversation_id": conversation_id,
        "memory_path": memory_path,
        "base_dir": base_dir,
        "knowledge_base": knowledge_base or {},
        "policy_events": [],
        "tool_results": [],
        "tool_call_counts": {},
        "alerts": [],
        "final_output": "",
        "reviewer_verdict": "review",
        "steps": 0,
        "used_langgraph": False,
    }

    runtime_policy = policy or DEFAULT_POLICY
    llm = LocalLLMAdapter(LLMConfig(model_name=model_name))

    if sys.version_info >= (3, 14):
        result = _run_fallback(state, llm, runtime_policy, max_steps=max_steps)
        result.setdefault("alerts", []).append("LangGraph path skipped on Python 3.14+ runtime.")
    else:
        try:
            result = _run_with_langgraph(state, llm, runtime_policy, max_steps=max_steps)
        except Exception:
            result = _run_fallback(state, llm, runtime_policy, max_steps=max_steps)

    result.setdefault("final_output", result.get("latest_output", ""))
    result.setdefault("steps", 0)
    return result


def run_delegation_workflow(
    goal: str,
    *,
    policy: Optional[Dict[str, Any]] = None,
    model_name: str = "distilgpt2",
    worker_response_override: str = "",
    enforce_handoff_validation: bool = False,
    max_steps: int = 10,
) -> Dict[str, Any]:
    """Supervisor/worker workflow used by advanced delegation lab.

    This intentionally models a common risk: supervisor trusting worker output
    without provenance-aware validation.
    """
    runtime_policy = policy or DEFAULT_POLICY
    llm = LocalLLMAdapter(LLMConfig(model_name=model_name))
    state: Dict[str, Any] = {
        "goal": goal,
        "policy_events": [],
        "tool_results": [],
        "tool_call_counts": {},
        "delegation_events": [],
        "alerts": [],
        "risk_score": 0,
        "threat_indicators": [],
        "steps": 0,
        "used_langgraph": False,
    }

    # Supervisor planning
    state["steps"] += 1
    sup_prompt = f"""
You are a supervisor agent. Delegate the user goal to worker_retrieval or worker_data.
Return JSON with keys: worker, task.
Goal: {sanitize_input(goal)}
"""
    sup_fallback = {"worker": "worker_retrieval", "task": "Summarize policy guidance safely."}
    sup_decision = llm.generate_json(sup_prompt, fallback=sup_fallback)
    worker = str(sup_decision.get("worker", "worker_retrieval"))
    task = str(sup_decision.get("task", goal))
    state["delegation_events"].append({"stage": "supervisor_plan", "worker": worker, "task": task})

    # Worker execution (can be overridden to simulate compromised sub-agent output)
    state["steps"] += 1
    if worker_response_override:
        worker_output = worker_response_override
    else:
        worker_prompt = f"""
You are {worker}. Complete task safely and return one short response.
Task: {task}
"""
        text = llm.generate(worker_prompt)
        worker_output = text if text else f"{worker}: completed task with safe guidance."
    state["delegation_events"].append({"stage": "worker_output", "worker": worker, "output": worker_output})

    # Supervisor receives worker handoff and optionally validates.
    state["steps"] += 1
    handoff_indicators = detect_threat_indicators(worker_output)
    if handoff_indicators:
        state["risk_score"] = len(handoff_indicators)
        state["threat_indicators"] = sorted(set(handoff_indicators))
        state["alerts"].append(f"Handoff indicators: {', '.join(handoff_indicators)}")

    if enforce_handoff_validation and handoff_indicators:
        state["reviewer_verdict"] = "review"
        state["final_output"] = "Manual review required due to untrusted worker handoff."
        state["halt_reason"] = "delegation_handoff_blocked"
        return state

    # Vulnerable path: supervisor trusts worker output.
    out_check = validate_output(worker_output)
    if not out_check["ok"]:
        state["alerts"].append(f"Output validation flags: {out_check['risk_flags']}")
    state["reviewer_verdict"] = "allow" if out_check["ok"] else "review"
    state["final_output"] = worker_output if out_check["ok"] else "Manual review required."
    state["halt_reason"] = "delegation_complete"
    return state
