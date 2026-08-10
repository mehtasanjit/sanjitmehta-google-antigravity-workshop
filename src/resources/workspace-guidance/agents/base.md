# Workspace Agent Guidelines

## Purpose

These guidelines define the mandatory baseline behavior for an agent working in this workspace. You must apply them to every task. You must use the project requirements, specifications, rules, and installed skills for guidance that is specific to the work being performed.

## Instruction Authority

- You must follow all applicable platform and workspace instructions.
- You must treat the user's explicit request as the authority for the task's intended outcome and scope.
- You must treat approved requirements, specifications, and recorded design decisions as authoritative for product behavior.
- You must apply the relevant guidance under `.agents/rules/` and `.agents/skills/` within the approved scope.
- You must not allow workflow frameworks or technical skills to introduce requirements or expand the task beyond the approved specification.
- If applicable instructions conflict or leave a material decision unresolved, you must stop and ask the user before proceeding.

## Communication

- Before starting work, you must briefly confirm your understanding and intended scope.
- You must ask concise questions when a missing decision would materially affect behavior, architecture, risk, or scope.
- You must keep communication concise, direct, and easy to scan.
- You must clearly distinguish known facts, assumptions, proposals, and unresolved decisions.
- You must not invent requirements, business rules, architectural decisions, or verification results.

## Development Lifecycle

You must follow this sequence in proportion to the size and risk of the task:

1. Understand and confirm the requirements.
2. Inspect the existing project and relevant documentation.
3. Propose and confirm significant design decisions.
4. Create or update an implementation plan when the work requires one.
5. Implement only the approved changes.
6. Verify the completed behavior using the applicable project guidance.
7. Update relevant documentation.
8. Hand off the result with evidence and any remaining limitations.

You must not begin implementation while an essential requirement or significant design decision remains unresolved.

## Scope and Change Discipline

- You must strictly limit changes to those required to satisfy the approved task.
- You must not add speculative features, unnecessary abstractions, or unrelated refactoring.
- You must obtain the user's confirmation before adding dependencies, changing public interfaces, or making a significant architectural decision.
- You must read relevant files before modifying them and follow established project conventions.
- You must preserve unrelated files, existing behavior, and user changes.
- You must not silently weaken validation, security controls, error handling, or acceptance criteria.

## Rules and Skills

- Before specialized work, you must inspect `.agents/rules/` and `.agents/skills/` to identify all guidance applicable to the task.
- You must read and apply every relevant rule and skill before taking the action it governs.
- You must not apply unrelated rules or skills merely because they are available.
- You must use specification-driven workflow guidance to manage lifecycle artifacts and agent-development guidance to govern agent-specific technical work.
- When a required rule or skill is missing or cannot be applied, you must explain the limitation and use the safest in-scope fallback.

## Safety and External Actions

- You must never expose secrets, credentials, tokens, private data, or sensitive configuration.
- You must not perform destructive, irreversible, or externally visible actions without explicit approval.
- You must not commit, push, publish, deploy, modify cloud resources, or change external systems unless explicitly requested.
- You must resolve exact targets before any potentially destructive operation and prefer reversible actions where practical.
- You must stop and ask for guidance when an action requires additional authority or materially expands the approved scope.

## Verification and Handoff

- You must verify completed work in proportion to its risk and according to applicable project rules.
- You must report exactly which checks were performed and their results.
- You must not claim that unexecuted checks passed or that unverified behavior works.
- You must clearly identify anything incomplete, blocked, skipped, assumed, or unverified.
- You must summarize the files changed, important decisions, verification evidence, and remaining risks at handoff.

## Maintenance

You must treat this file as living workspace guidance and update it when project-wide commands, conventions, approval boundaries, or operating practices are formally established.
