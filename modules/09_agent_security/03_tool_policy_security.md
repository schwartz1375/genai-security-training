# Tool & Policy Security

## Principle: Least Privilege by Default

Each agent should only access the minimum tool set required for its role.

Example:
- `planner`: no external tools, text-only planning
- `executor`: limited operational tools
- `reviewer`: read-only checks and scoring tools

## Policy Gates

A policy gate should run before every tool call:

1. Tool authorization
- Is this tool allowlisted for this agent?

2. Argument validation
- Are arguments schema-valid?
- Are values in safe bounds?

3. Runtime constraints
- Max tool calls per run
- Blocklists for risky tokens/paths

4. Logging and explainability
- Record allow/deny decision and reason

## Minimal Policy Model

Policy object should contain:
- `allowed_tools_by_agent`
- `max_calls_per_agent`
- `blocked_patterns`
- `critical_action_requires_review`

## Common Mistakes

- Global allowlists shared by all agents
- Silent fallback on policy errors
- Reviewer does not inspect policy events
- Missing telemetry for denied calls

## Validation Checklist

- Unknown tool is denied
- Invalid arguments are denied
- Over-limit tool attempts are denied
- All denials are persisted to audit logs

## Key Takeaways

1. Policy must be code, not documentation only.
2. Decision logs are mandatory for incident analysis.
3. Reviewer should treat repeated denies as escalation signals.

## Next Steps

1. Continue to [Agent Testing & Incident Response](04_agent_testing_and_ir.md)
2. Run [Lab 3](labs/lab3_policy_enforcement.ipynb)
