# Module 9: Agent Security & Sub-Agent Operations

## Overview

This module extends the curriculum into agentic AI security. You will model threats in multi-agent workflows, simulate attacks against sub-agent orchestration, implement policy controls, and build security regression tests for agent systems.

The runtime uses:
- Local `transformers` models for planner/reviewer decisions
- LangGraph orchestration (with local fallback if unavailable)
- Notebook-first exercises with reusable code in `utils/`

## Learning Objectives

By the end of this module, you will be able to:
- Threat model planner/executor/reviewer systems
- Identify and test sub-agent escalation paths
- Enforce tool-level least privilege controls
- Build repeatable security regression tests for agent workflows
- Produce actionable incident response artifacts for agent failures

## Prerequisites

- Completion of Modules 1-8
- Python + Jupyter familiarity
- Basic understanding of prompt injection, jailbreaks, and security testing

## Module Structure

### Theory Documents

1. [Agent Threat Modeling](01_agent_threat_modeling.md)
2. [Sub-Agent Attack Patterns](02_subagent_attack_patterns.md)
3. [Tool & Policy Security](03_tool_policy_security.md)
4. [Agent Testing & Incident Response](04_agent_testing_and_ir.md)

### Hands-On Labs

1. [Lab 1: Agent Orchestration Basics](labs/lab1_agent_orchestration_basics.ipynb)
2. [Lab 2: Sub-Agent Attack Simulation](labs/lab2_subagent_attacks.ipynb)  
   Attack focus: indirect prompt injection + cross-agent trust issues
3. [Lab 3: Tool Policy Enforcement](labs/lab3_policy_enforcement.ipynb)  
   Attack focus: tool argument injection (path traversal, SQLi-style payloads)
4. [Lab 4: Security Regression for Agents](labs/lab4_security_regression.ipynb)  
   Attack focus: memory poisoning persistence + regression thresholds
5. [Lab 5 (Advanced Optional): Delegation Attacks](labs/lab5_delegation_attacks.ipynb)  
   Attack focus: supervisor/worker handoff trust and delegation abuse

### Answer Key

- [ANSWERS.ipynb](labs/ANSWERS.ipynb)

## Local Model Pattern (Consistent With Prior Modules)

Labs follow the same local execution model used elsewhere in this repo:
- `transformers` + `torch`
- Local model loading via `from_pretrained(...)`
- Device selection priority: CUDA -> MPS -> CPU
- Notebook-first workflow with reusable helper code in `utils/`

### Recommended Local Model Profiles

- **Fast baseline**: `distilgpt2` (quick iteration, lower reasoning quality)
- **Balanced local chat model**: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- **Higher quality (heavier hardware)**: local Mistral-class instruct models

Use `run_workflow(..., model_name=\"<model>\")` in labs to compare behavior and security outcomes.

## Runtime Components (`utils/`)

Module 9 labs are notebook-first, but the core runtime lives in `utils/` so students can inspect and reuse the same logic across labs:

- `utils/agents.py`
  - Main orchestration entrypoints:
    - `run_workflow(...)` for planner/policy/executor/reviewer flow
    - `run_delegation_workflow(...)` for advanced supervisor/worker delegation attacks
- `utils/policy.py`
  - Policy gates, threat-indicator detection, input sanitization, and output validation
- `utils/tools.py`
  - Local demo tools (retrieval, file reads with traversal checks, SQL query demo, memory writes with provenance)
- `utils/eval.py`
  - Metrics used in labs (`attack_success_rate`, false negatives, block rates, delegation metrics)
- `utils/llm_adapter.py`
  - Local `transformers` model adapter used for planner/reviewer generation
- `utils/model_setup.py`
  - Environment helpers (device selection and runtime compatibility checks)

Students should treat these as reference runtime code, not opaque internals.

## Lab-to-Utils Mapping

- **Lab 1**: `agents.py`, `eval.py`, `model_setup.py`
  - Understand baseline orchestration and how state is produced.
- **Lab 2**: `agents.py`, `policy.py`, `tools.py`, `eval.py`
  - Observe indirect prompt injection signals and trust-boundary effects.
- **Lab 3**: `policy.py`, `tools.py`, `eval.py`
  - Focus on tool argument injection and policy hardening outcomes.
- **Lab 4**: `tools.py`, `agents.py`, `eval.py`
  - Validate memory poisoning persistence and regression thresholds.
- **Lab 5 (optional)**: `agents.py`, `eval.py`
  - Analyze delegation handoff risk and provenance-aware supervisor controls.

## Orchestration Framework Options

This module compares common orchestration options for agent security training.

### 1. LangGraph (Recommended for this module)
- Explicit state graph (best for showing control-flow vulnerabilities)
- Easy to model cycles, conditional routing, and checkpoint attacks
- Works with local `transformers` models used in this repo
- Strong fit for planner/executor/reviewer workflows

### 2. LangChain Agents
- Faster to start for ReAct-style tool-using agents
- Good tool ecosystem and local model integration
- Less explicit state control than LangGraph

### 3. AWS Strands SDK
- Strong managed orchestration option
- Often paired with AWS-native model/runtime integrations
- Can support local-model patterns with extra adapter work
- Better as an advanced deployment track than the default training path here

At time of writing, commonly referenced Strands model-provider paths include:
- Direct support: Ollama, llama.cpp, SageMaker-hosted models, LiteLLM-backed endpoints
- Custom provider support: `transformers` via a custom Strands model provider implementation

Use the official Strands docs to verify current provider support before implementation.

### Advanced Optional Track: AWS Strands With Local Models

This module remains local-first, but advanced students can evaluate a deployment-style orchestration pattern:
- Keep local `transformers` inference for planner/reviewer logic
- Use Strands for orchestration state, routing, retries, and observability
- Re-run Labs 2-4 attack suites and compare:
  - policy block rates
  - false-negative rates
  - incident trace quality

This optional comparison helps distinguish training-oriented runtime design from production orchestration concerns.

Example custom provider shape for `transformers`:

```python
from strands.models import Model
from transformers import pipeline


class TransformersModel(Model):
    def __init__(self, model_name="distilgpt2"):
        self.generator = pipeline("text-generation", model=model_name)

    async def stream(self, messages, tool_specs=None, system_prompt=None):
        # Convert messages to prompt
        prompt = self._format_messages(messages, system_prompt)
        
        # Generate with transformers
        output = self.generator(prompt, max_new_tokens=100)
        
        # Yield Strands StreamEvents
        yield {"messageStart": {"role": "assistant"}}
        yield {"contentBlockDelta": {"delta": {"text": output[0]["generated_text"]}}}
        yield {"messageStop": {"stopReason": "end_turn"}}
```

Why Module 9 still defaults to LangGraph + `transformers`:
- Simpler for students and easier to debug in notebooks
- Direct control over security logic and policy gates
- Transparent execution flow for teaching attack/defense mechanics
- Keeps the core lab dependency surface smaller

### 4. Raw `transformers` + custom orchestration
- Maximum transparency for teaching internals
- Good for foundational labs
- Higher maintenance burden as scenarios grow

## Selected Approach for Module 9

For consistency with Modules 1-8, Module 9 uses:
- Local model inference with `transformers` + `torch`
- Notebook-first exercises
- LangGraph for orchestration and state transitions (fallback runtime included for environments without LangGraph)

This keeps training aligned with local model workflows while still teaching realistic agent orchestration security.

## Integration With Prior Modules

- Module 2: Prompt injection and jailbreak patterns are reused in agent chains.
- Module 3: Evasion concepts inform reviewer bypass and detection gaps.
- Module 7: Metrics and regression testing methodology are extended to agent workflows.
- Module 8: Incident analysis and reporting patterns are reused in final exercises.

## Future Expansion

Module 9 focuses on the core planner/executor/reviewer pattern, plus an optional advanced delegation lab. A future advanced track can further expand to worker swarms, broker agents, and recursive sub-agent spawning.

## Time Estimate

- Theory: 3-4 hours
- Labs: 7-10 hours
- Total: 10-14 hours

## Success Criteria

By completing this module, you should be able to:
- Demonstrate at least 3 sub-agent attack attempts
- Quantify policy effectiveness before/after hardening
- Generate a reproducible regression report with security metrics

## Next Steps

1. Begin with [Agent Threat Modeling](01_agent_threat_modeling.md)
2. Run [Lab 1](labs/lab1_agent_orchestration_basics.ipynb)
3. Progress through Labs 2-4 in sequence
4. Optional: run [Lab 5](labs/lab5_delegation_attacks.ipynb) for delegation-specific attacks
