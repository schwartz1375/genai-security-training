"""Defense-in-depth policy controls for Module 9."""

from __future__ import annotations

from typing import Any, Dict, List


DEFAULT_POLICY: Dict[str, Any] = {
    "allowed_tools_by_agent": {
        "planner": ["retrieve_knowledge"],
        "executor": ["retrieve_knowledge", "read_file", "query_db", "append_memory_note"],
        "reviewer": [],
    },
    "max_calls_per_agent": {
        "planner": 1,
        "executor": 3,
        "reviewer": 0,
    },
    "blocked_patterns": [
        "ignore policy",
        "bypass",
        "exfiltrate",
        "/etc/passwd",
        "../",
        "drop table",
        "union select",
    ],
    "critical_tools": ["read_file", "query_db"],
    "require_human_review_for_critical": True,
    "max_denied_events_before_halt": 2,
}


def sanitize_input(text: str) -> str:
    lowered = text.lower()
    for token in ["system prompt", "ignore previous", "bypass safety"]:
        lowered = lowered.replace(token, "[redacted]")
    return lowered


def validate_output(text: str) -> Dict[str, Any]:
    lowered = text.lower()
    risky = []
    for token in ["secret", "api key", "password", "drop table", "/etc/passwd"]:
        if token in lowered:
            risky.append(token)
    return {"ok": len(risky) == 0, "risk_flags": risky}


def detect_threat_indicators(text: str) -> List[str]:
    lowered = text.lower()
    hits = []
    for token in [
        "ignore policy",
        "bypass",
        "exfiltrate",
        "drop table",
        "union select",
        "../",
        "override guardrails",
    ]:
        if token in lowered:
            hits.append(token)
    return hits


def check_policy(
    *,
    agent: str,
    tool_name: str,
    args: Dict[str, Any],
    state: Dict[str, Any],
    policy: Dict[str, Any],
) -> Dict[str, Any]:
    allowed_tools: List[str] = policy["allowed_tools_by_agent"].get(agent, [])
    if tool_name not in allowed_tools:
        return {"allowed": False, "reason": f"Tool '{tool_name}' not allowed for agent '{agent}'."}

    counts = state.setdefault("tool_call_counts", {})
    current = counts.get(agent, 0)
    max_calls = policy["max_calls_per_agent"].get(agent, 0)
    if current >= max_calls:
        return {"allowed": False, "reason": f"Tool call limit exceeded for '{agent}'."}

    arg_text = " ".join(str(v).lower() for v in args.values())
    for pattern in policy.get("blocked_patterns", []):
        if pattern in arg_text:
            return {"allowed": False, "reason": f"Blocked pattern detected in arguments: '{pattern}'."}

    denied_events = sum(1 for e in state.get("policy_events", []) if not e.get("allowed"))
    if denied_events >= policy.get("max_denied_events_before_halt", 2):
        return {"allowed": False, "reason": "Too many denied events in this run."}

    human_review_required = (
        policy.get("require_human_review_for_critical", True)
        and tool_name in policy.get("critical_tools", [])
        and state.get("risk_score", 0) > 0
    )
    if human_review_required:
        return {"allowed": False, "reason": f"Tool '{tool_name}' requires human review under current risk score."}

    counts[agent] = current + 1
    return {"allowed": True, "reason": "Allowed."}

