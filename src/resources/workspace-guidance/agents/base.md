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

Rules are stored in `.agents/rules/`. Skills are stored in `.agents/skills/`.

The IDE may not enforce rule activation. You must enforce it from the rule files.

Every rule must contain:

- `Rule Metadata` with a summary and an activation mode.
- `Applicability` stating when the rule does and does not apply.
- A manual invocation name when the mode is `Manual`.
- File patterns when the mode is `Glob`.

Before starting task work, you must:

1. List the available rules and skills.
2. Inspect each rule file. Read its `Rule Metadata` and `Applicability` sections when present.
3. Apply rule modes as follows:
   - `Always On`: Read and apply the complete rule.
   - `Manual`: Apply only when the user invokes the rule.
   - `Model Decision`: Apply when its summary and applicability match the task.
   - `Glob`: Apply when the task reads, creates, or changes a matching file.
4. Inspect each skill's `SKILL.md`. Read its `name` and `description` frontmatter when present.
5. Read every applicable rule and skill completely before acting.
6. Load supporting references only when needed.

If metadata is missing, read the complete file. If applicability is still unclear, ask the user. Do not apply unrelated guidance.

## Workspace Memory

You must apply the `workspace-memory` rule in `.agents/rules/workspace-memory.md` to every workspace task.

You must inspect `<workspace-root>/.memory/` before starting task work. If it exists, read `MEMORY.md` first when present and load only the indexed memory files relevant to the task; if the index is missing, follow the rule's repair workflow. If `.memory/` does not exist, follow the rule's memory-creation and Git-visibility workflow.

When workspace memory exists or the user approves its creation, you must update the relevant subject-specific memory immediately after every consequential step defined by the rule. You must complete the memory update before continuing to the next consequential action.

You must update an existing memory file when it covers the subject. You must create a new memory file only for a distinct subject, maintain its required frontmatter, and update `MEMORY.md` when the index changes.

You must also update workspace memory immediately when the user explicitly asks you to remember, record, or update workspace information. You must not append duplicate entries or defer all memory updates until final handoff. All memory operations remain subject to the rule's privacy and prohibited-content restrictions.

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
