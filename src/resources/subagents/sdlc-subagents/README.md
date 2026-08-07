# SDLC subagents for Google Antigravity

This resource pack defines eight reusable, workspace-scoped subagents for a
software delivery lifecycle. The main agent remains the SDLC orchestrator: it
owns the goal, sequencing, synthesis, human interaction, and approval gates.

## Install

Copy the `.agents` directory from this folder into the root of an Antigravity
workspace. Antigravity discovers each definition at
`.agents/agents/<name>/agent.md`.

## Included agents

| Agent | Purpose | Suggested invocation workspace |
| --- | --- | --- |
| `requirements-analyst` | Turn intent into testable requirements | `inherit` |
| `solution-architect` | Resolve architecture, interfaces, and trade-offs | `inherit` |
| `delivery-planner` | Produce bounded, dependency-ordered task packets | `inherit` |
| `implementation-engineer` | Implement one approved task packet | `branch` |
| `test-engineer` | Add and run unit, integration, and regression tests | `branch` or `inherit` |
| `code-reviewer` | Independently review correctness and maintainability | `inherit` |
| `security-reviewer` | Independently review threats and vulnerabilities | `inherit` |
| `release-readiness-reviewer` | Make an evidence-based release recommendation | `inherit` |

Workspace selection is intentionally not encoded in agent frontmatter. Select
`branch` at invocation time for meaningful code-producing work and `inherit`
for analysis or read-only review.

## Delegation contract

Subagents are separate sessions and do not inherit the parent conversation.
Every invocation must therefore include a self-contained task packet containing
the objective, repository context, approved decisions, scope, acceptance
criteria, validation, and expected output. Start from
[`task-packet-template.md`](task-packet-template.md).

Review agents are deliberately read-only. Send remediation back to an
implementation agent as a new bounded task. Keep human approval gates for
architecture decisions, accepted security risk, destructive migrations, and
production releases.

## References

- [Antigravity custom subagents specification](https://antigravity.google/docs/subagents)
- [Antigravity CLI background tasks and subagents](https://antigravity.google/docs/cli/subagents)
- [Antigravity `/agents` command](https://antigravity.google/docs/cli/commands/agents)
