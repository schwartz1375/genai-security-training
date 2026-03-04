# Agent Testing & Incident Response

## Security Testing Strategy

Agent systems require scenario-driven tests that validate both behavior and controls.

## Regression Test Categories

1. Prompt-level attack tests
- Goal hijack attempts
- Instruction override attempts

2. Tool misuse tests
- Unauthorized tool invocation
- Malformed/unsafe arguments

3. Memory integrity tests
- Poisoned memory injection
- Persistence verification across runs

4. Reviewer robustness tests
- Safe-looking unsafe content
- False-negative reduction checks

## Core Metrics

- `attack_success_rate`
- `policy_block_rate`
- `unsafe_tool_exec_count`
- `reviewer_false_negative_rate`

Track metrics over time to identify regressions after code/model changes.

## Incident Response Workflow

1. Detect
- Alert on threshold breaches or suspicious policy patterns

2. Contain
- Disable risky tools
- Freeze memory writes
- Route to manual review

3. Analyze
- Reconstruct trace from logs
- Identify root cause (prompt, policy gap, tool bug, memory poisoning)

4. Recover
- Patch policy/tooling
- Replay regression suite
- Restore normal operations after pass

5. Learn
- Add new test scenario for discovered failure mode

## Key Takeaways

1. Regression harnesses convert one-time bugs into permanent defenses.
2. Incident response depends on high-quality traces.
3. Every incident should produce at least one new security test.

## Next Steps

1. Run [Lab 4](labs/lab4_security_regression.ipynb)
2. Review [ANSWERS.ipynb](labs/ANSWERS.ipynb)
