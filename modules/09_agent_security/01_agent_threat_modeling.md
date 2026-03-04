# Agent Threat Modeling

## Why Agent Threat Modeling Is Different

Agent systems introduce additional security risk compared with single-turn chat applications because they:
- Decompose goals into intermediate actions
- Call tools with side effects
- Store and reuse memory across steps
- Hand off work between specialized sub-agents

Security analysis must therefore include both prompt/content risks and workflow/control risks.

## Reference Architecture

Typical training architecture:
- `planner`: proposes next action
- `policy`: validates action and tool access
- `executor`: performs allowed tool call
- `reviewer`: inspects output quality and risk

Each boundary between these components is a trust boundary.

## Threat Modeling Procedure

1. Define assets
- System prompts
- Tool credentials
- Retrieved documents
- Memory state
- Final outputs and reports

2. Define actors
- Legitimate user
- Adversarial user
- Compromised data source
- Malicious tool response

3. Enumerate attack surfaces
- User prompt channel
- Retrieval content
- Tool arguments
- Memory writes
- Agent-to-agent messages

4. Map abuse paths
- Prompt injection -> planner goal hijack
- Tool call escalation -> unauthorized action
- Memory poisoning -> persistent behavior drift
- Reviewer bypass -> unsafe output accepted

## Key Risks

- **Goal hijacking**: attacker alters the planner objective
- **Tool overreach**: executor calls tools beyond allowed scope
- **Cross-agent trust abuse**: downstream agent assumes upstream output is safe
- **Persistent poisoning**: malicious memory entry impacts future runs

## Case Study Snapshots

### Case Study: Plugin/Tool Overreach in Early Agent Integrations
- **Pattern**: Over-privileged tool integrations accepted unsafe action requests.
- **Failure mode**: Natural-language instructions crossed trust boundaries and triggered risky operations.
- **Training relevance**: Highlights why per-agent tool allowlists and argument validation must be enforced before execution.

### Case Study: Retrieval Content Used as Instructions
- **Pattern**: Untrusted retrieved content was treated as authoritative workflow guidance.
- **Failure mode**: Indirect prompt injection altered planner intent and downstream execution.
- **Training relevance**: Reinforces retrieval provenance, sanitization, and reviewer escalation controls.

## Mitigations

- Strict per-agent tool allowlists
- Argument-level validation before execution
- Memory scoping and provenance tags
- Mandatory reviewer gate for high-risk outputs
- Full audit trail for every decision and tool call

## Key Takeaways

1. Agent security is workflow security, not only prompt security.
2. Trust boundaries must be explicit and enforced in code.
3. Memory and tool access are primary control points.

## Next Steps

1. Continue to [Sub-Agent Attack Patterns](02_subagent_attack_patterns.md)
2. Run [Lab 1](labs/lab1_agent_orchestration_basics.ipynb)
