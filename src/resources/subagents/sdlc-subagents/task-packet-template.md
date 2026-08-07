# Subagent task packet

Replace every placeholder before delegating. Remove sections that genuinely do
not apply, but do not rely on the parent conversation for missing context.

```text
ROLE
Invoke: <subagent-name>

OBJECTIVE
<One concrete, independently verifiable outcome>

REPOSITORY CONTEXT
<Architecture and conventions needed to work safely>
Relevant files:
- <path>

INPUTS AND APPROVED DECISIONS
- <Requirements, design, issue, or prior findings>

ALLOWED CHANGES
- <Files, modules, tests, or documents that may change>

DO NOT CHANGE
- <Explicitly excluded behavior and files>

DEPENDENCIES
- <Prerequisite task IDs or external dependencies>

ACCEPTANCE CRITERIA
1. <Observable, testable criterion>

VALIDATION
- <Exact command and expected result>

EXPECTED ARTIFACTS
- <Code, tests, report, ADR, migration, or other output>

RISK AND ESCALATION
Risk: <low | medium | high>
Stop and escalate when:
- <Condition requiring a parent or human decision>

OUTPUT
Return files changed, evidence, commands and results, assumptions, deviations,
remaining risks, and unresolved decisions.
```

