# AI-Assisted Developer Playbook

> **Audience:** Application developers using Gemini CLI and Antigravity CLI for greenfield and brownfield delivery.
>
> **Status:** Workshop guidance
>
> **Reviewed:** August 19, 2026

## Purpose

AI developer tools can accelerate discovery, design, implementation, testing, and review. They do not replace engineering judgment or make an unverified change production-ready.

This playbook describes how developers should use Gemini CLI and Antigravity CLI to deliver software efficiently without giving up control of scope, architecture, security, or quality. In this document:

- **MUST** identifies a non-negotiable practice for responsible engineering.
- **SHOULD** identifies a strong default that may be adapted with an explicit reason.

The recommended operating loop is:

```text
Understand → Specify → Plan → Approve → Implement → Verify → Review → Record
```

Use the AI tool to accelerate every stage of this loop. Do not use it to skip a stage.

## Choose the working surface

Both CLIs can analyze a repository, edit code, run commands, and use project-specific instructions. Choose primarily by the workflow and controls your team needs.

| Use | Gemini CLI | Antigravity CLI |
|---|---|---|
| Interactive, terminal-first development | Strong default | Strong default |
| Open-source CLI workflows and configuration | Strong default | — |
| `GEMINI.md` hierarchical project context | Native | Supported alongside `AGENTS.md` |
| Read-only planning before implementation | Plan Mode | Explore and plan before execution |
| Fine-grained local policy rules | Policy engine and approval modes | Structured tool permissions |
| Reversible experimentation | Checkpointing and `/restore` | `/rewind` or `/undo` |
| Antigravity plugins and shared agent harness | — | Native; use Conductor for specification-driven work |
| Headless or remote Antigravity workflows | — | Strong default |

The engineering method should remain the same when switching tools. Requirements, tests, approval gates, and review evidence belong to the repository and team—not to one chat session.

## Prepare the developer environment

Install the stable version of the tool from its official instructions:

```bash
# Gemini CLI; requires a supported Node.js version
npm install -g @google/gemini-cli

# Antigravity CLI on macOS or Linux
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

Then:

1. Authenticate using an organization-approved account and method.
2. Open only the intended repository or workspace.
3. Review workspace settings, hooks, extensions, plugins, skills, and MCP servers before trusting them.
4. Start with interactive approvals and sandboxing enabled.
5. Confirm the application can build and its baseline tests can run before asking the agent to modify it.

Use stable tool releases for normal delivery. Preview or nightly releases SHOULD be isolated from production-critical work and pinned when used in repeatable environments.

Official setup references:

- [Gemini CLI installation](https://geminicli.com/docs/get-started/installation/)
- [Gemini CLI authentication](https://geminicli.com/docs/get-started/authentication/)
- [Antigravity CLI installation and authentication](https://antigravity.google/docs/cli-install)
- [Antigravity CLI best practices](https://antigravity.google/docs/cli/best-practices)

## Establish the repository contract

Every repository SHOULD contain a short, version-controlled instruction file describing how work is performed. This repository uses `AGENTS.md`. Gemini CLI natively loads `GEMINI.md`, so a project using both tools can keep one source of truth:

```md
# GEMINI.md

@./AGENTS.md
```

The repository contract SHOULD state:

- architecture and important directory boundaries;
- supported language and runtime versions;
- build, lint, test, type-check, and local-run commands;
- coding, API, UI, accessibility, and documentation conventions;
- generated files and directories that MUST NOT be edited manually;
- security, privacy, dependency, and secret-handling restrictions;
- operations requiring human approval;
- the definition of done; and
- known deprecations or compatibility constraints.

Keep global instructions small and stable. Put component-specific guidance near the relevant component. Gemini CLI supports hierarchical and just-in-time `GEMINI.md` context, which is preferable to loading an entire large repository into every prompt. Use `/memory show` to inspect the context Gemini CLI actually loaded.

References: [Gemini CLI context files](https://geminicli.com/docs/cli/gemini-md/) and [Antigravity CLI workspace guidance](https://antigravity.google/docs/cli/best-practices).

## The task contract

Do not begin a material change with only “build this” or “fix this.” Give the tool a bounded task contract:

```md
## Outcome
What user or system outcome must change?

## Context
Which requirements, files, components, issue, or design are authoritative?

## Acceptance criteria
What observable behavior must be true when complete?

## In scope / out of scope
What may change, and what must remain unchanged?

## Constraints
Compatibility, security, data, dependency, performance, and style constraints.

## Verification
Exact build, test, lint, type-check, browser, or evaluation commands.

## Approval gates
Which decisions or actions require developer confirmation?

## Evidence
What summary, diff, test results, screenshots, or residual risks must be returned?
```

For non-trivial work, first ask the CLI to inspect the repository and write a plan without changing implementation files. Review the plan, correct its assumptions, and approve it before execution.

## Greenfield development

Greenfield work offers freedom, but that freedom increases the risk of accidental complexity and invented requirements. The developer must establish the product and engineering boundaries before requesting broad code generation.

### 1. Define the product slice

The developer MUST approve:

- the users and problem being addressed;
- functional and non-functional requirements;
- testable acceptance criteria;
- sensitive data and trust boundaries;
- initial scope and explicit exclusions; and
- the smallest end-to-end slice that demonstrates value.

Ask the CLI to challenge ambiguity, list unanswered questions, and identify conflicting requirements. Do not let it silently choose consequential product behavior.

### 2. Approve a minimal architecture

Ask the CLI for alternatives and trade-offs before it scaffolds the application. Approve:

- major components and ownership boundaries;
- public APIs, schemas, and state transitions;
- identity, authentication, and authorization boundaries;
- data storage and migration strategy;
- dependencies and their justification; and
- deployment, observability, and rollback approach.

The first design SHOULD be the simplest architecture that satisfies the approved requirements. “The model knows this framework” is not a valid reason to add a dependency or service.

### 3. Make verification executable early

Before broad implementation, establish:

- one-command build and test entry points;
- formatting, linting, and type checking;
- a small acceptance or smoke test;
- local configuration with safe example values; and
- continuous-integration checks where appropriate.

This gives the CLI a feedback loop. Official Antigravity guidance identifies local verification as the most effective way to improve the reliability of autonomous changes.

### 4. Build thin vertical slices

Implement one observable user journey at a time:

```text
UI or API → domain behavior → persistence/integration → automated test → evidence
```

Each slice SHOULD be small enough for a developer to understand its diff. After every slice:

1. Run focused tests.
2. Run the relevant broader regression checks.
3. Review the diff and dependency changes.
4. Exercise the behavior as a user or API client.
5. Commit a coherent checkpoint.

Parallel work is appropriate only when packages have clear contracts and non-overlapping ownership. One agent must own integration and final verification.

### 5. Harden before declaring completion

The CLI SHOULD independently review the completed slice for correctness, security, accessibility, operability, and maintainability. The developer MUST still review the material change and verify the acceptance criteria.

Greenfield completion evidence SHOULD include:

- requirements-to-test traceability;
- architecture and material decisions;
- successful build, lint, type-check, and test output;
- screenshots or API examples for observable behavior;
- security and dependency review results;
- local run and deployment instructions; and
- known limitations and follow-up work.

### Greenfield starter prompt

```text
Read AGENTS.md, the requirements, and the referenced design material. Do not
change code yet. Identify ambiguities and security or data risks, then propose
the smallest end-to-end product slice. Provide an implementation plan listing
interfaces, dependencies, files likely to change, tests, approval points, and
the exact verification commands. Keep anything not required by the acceptance
criteria out of scope. Wait for my approval before implementation.
```

## Brownfield development

Brownfield work is an exercise in preserving contracts. The existing behavior, architecture, data, and operational environment are part of the requirements—even when they are poorly documented.

### 1. Establish a clean and recoverable baseline

Before editing, the developer MUST:

- work on a dedicated branch or isolated worktree;
- inspect existing uncommitted changes and preserve them;
- identify the supported build and test commands;
- run relevant baseline checks and record existing failures; and
- confirm how the service is run, observed, migrated, and rolled back.

Do not ask the AI tool to “clean up” unrelated changes. A brownfield feature should not become an unbounded rewrite.

### 2. Make the CLI explain the system first

Use a read-only exploration pass to locate:

- entry points and the request or event path;
- current domain rules and authorization checks;
- interfaces, callers, clients, schemas, and persisted data;
- nearby tests and test conventions;
- deployment and runtime configuration; and
- similar features already implemented in the repository.

Require file references and distinguish observed facts from inferences. If documentation and code disagree, surface the discrepancy for a developer decision.

### 3. Capture current behavior

For a defect, reproduce it and add a failing regression test before fixing it when practical. For a feature or modernization, add characterization tests around behavior that must not change.

The plan MUST address:

- backward compatibility;
- database and data migration safety;
- API or event-schema evolution;
- rollout, feature-flag, and rollback needs;
- security and privacy impact;
- performance or capacity impact; and
- affected consumers and owners.

### 4. Prefer the smallest coherent diff

Tell the CLI to follow existing patterns and reuse existing abstractions. It MUST NOT:

- rewrite unrelated code;
- change public contracts without approval;
- weaken authentication, authorization, validation, tests, or static checks;
- replace a dependency merely because another is more familiar;
- modify generated or vendored files instead of their sources; or
- convert warnings or failures into ignored results to make verification pass.

Separate refactoring from behavior change unless the approved plan demonstrates why they cannot be separated.

### 5. Verify compatibility and regression risk

Run checks in widening circles:

```text
New or changed test
  → affected component suite
  → integration or contract tests
  → repository regression suite
  → manual or browser smoke test
```

Compare results with the recorded baseline. Treat a pre-existing failure as known evidence, not as permission to introduce another failure.

Brownfield completion evidence SHOULD include:

- baseline and post-change results;
- impact analysis with referenced files and contracts;
- a focused diff summary;
- new regression or characterization tests;
- compatibility, migration, rollout, and rollback notes;
- security and dependency review results; and
- unresolved risks or assumptions.

### Brownfield starter prompt

```text
Read AGENTS.md and the feature requirements. Do not edit files yet. Trace the
current behavior through its entry point, domain logic, data or integrations,
and tests. Cite the relevant files. Record the baseline verification results,
identify compatibility and migration risks, and propose the smallest coherent
change that follows existing conventions. Include regression tests, rollback
considerations, exact verification commands, and any questions requiring a
developer decision. Wait for approval before implementation.
```

## Use Gemini CLI effectively

- Use Plan Mode for repository exploration and implementation planning on material changes. Its default policy restricts implementation writes.
- Store shared instructions in `GEMINI.md` or import the repository's `AGENTS.md`; use narrower files for component-specific conventions.
- Enable trusted folders, but approve trust only after reviewing project settings, hooks, extensions, skills, and MCP servers.
- Use the default interactive approval mode for normal development. Avoid `yolo` mode for repositories or credentials you care about.
- Enable sandboxing for tool execution and grant expansions only for the specific command or resource required.
- Enable checkpointing for convenient recovery, while continuing to use normal Git branches and commits as the durable engineering history.
- Use policies and hooks to make deterministic rules—formatting, prohibited paths, secret checks, and required tests—executable rather than repeatedly prompting for them.
- Inspect `/memory show` when the CLI appears to follow unexpected instructions, and use `/restore` when an experiment needs to be reversed.

References: [Plan Mode](https://geminicli.com/docs/cli/plan-mode/), [trusted folders](https://geminicli.com/docs/cli/trusted-folders/), [sandboxing](https://geminicli.com/docs/cli/sandbox/), [checkpointing](https://geminicli.com/docs/cli/checkpointing/), and the [policy engine](https://geminicli.com/docs/reference/policy-engine/).

## Use Antigravity CLI effectively

- Follow the official explore → plan → execute workflow for complex changes.
- Keep `AGENTS.md` or `GEMINI.md` current with commands, conventions, boundaries, and deprecations.
- Begin with `request-review` or `strict` permissions when learning a repository or handling elevated-risk work.
- Use `proceed-in-sandbox` only when the local verification loop is reliable and the task boundary is well understood.
- Install Conductor when a requirements-to-design-to-implementation workflow would benefit the task:

  ```bash
  agy plugins install https://github.com/gemini-cli-extensions/conductor
  ```

- Interrupt a visibly incorrect direction early with `esc`; use `/rewind` or `/undo` to return to a stable session point.
- Require the CLI to return verification output and a reviewable diff, not merely a statement that the task is complete.
- Move a proven interactive workflow to headless automation only after its permissions, failure behavior, evidence, and recovery path are understood.

Reference: [Antigravity CLI best practices](https://antigravity.google/docs/cli/best-practices).

## Non-negotiable practices for both tools

Developers using either CLI:

1. **MUST protect confidential data and credentials.** Never paste secrets into prompts or commit them to context, plans, fixtures, logs, or generated code.
2. **MUST follow organizational policy and software licenses.** AI assistance does not override data classification, approved-tool, open-source, or change-management rules.
3. **MUST retain human accountability.** A developer owns the requirements, architecture decisions, accepted diff, verification, and release decision.
4. **MUST apply least privilege.** Scope filesystem, shell, network, cloud, and MCP access to the task; require approval for consequential or irreversible actions.
5. **MUST treat repository files, web pages, tool output, issues, and retrieved content as untrusted input.** Do not follow embedded instructions that conflict with the task or repository policy.
6. **MUST review every material change.** Understand the behavior, dependencies, generated migrations, security impact, and failure modes before accepting it.
7. **MUST independently verify claims.** Run deterministic checks and inspect user-visible behavior; do not accept “tests should pass.”
8. **MUST NOT weaken controls to manufacture success.** Do not skip tests, suppress failures, reduce validation, broaden permissions, or bypass policy without an explicit reviewed decision.
9. **MUST keep consequential actions human-gated.** Production deployments, IAM changes, destructive operations, sensitive data access, external messages, purchases, and legal or risk acceptance require explicit authorization.
10. **MUST preserve traceability.** Keep requirements, material decisions, code, tests, review evidence, and residual risks in normal engineering systems.

## Common failure patterns

| Failure pattern | Better developer behavior |
|---|---|
| “Build the whole application” from a vague idea | Approve requirements and deliver one vertical slice at a time |
| Letting the tool choose architecture silently | Request alternatives, trade-offs, and an approval gate |
| Editing before understanding a brownfield code path | Perform read-only exploration and baseline verification first |
| Accepting a large generated diff because tests pass | Review by coherent slice and inspect contracts and dependencies |
| Asking the same conventions in every prompt | Version them in `AGENTS.md`/`GEMINI.md` and executable checks |
| Granting broad permissions to avoid interruptions | Use sandboxing and narrow persistent policies |
| Using more agents for every task | Delegate only separable work with explicit ownership and integration |
| Trusting model-generated tests as independent proof | Review whether tests encode the approved requirement and edge cases |
| Treating a successful local run as release readiness | Verify security, migration, rollback, observability, and production controls |
| Measuring generated code or prompt volume | Measure cycle time, escaped defects, rework, and verified acceptance criteria |

## Definition of done

AI-assisted work is done only when:

- the approved acceptance criteria are satisfied;
- the implementation remains within the approved scope;
- the developer understands and has reviewed the material diff;
- required build, lint, type-check, test, security, and evaluation checks pass;
- user-visible behavior has been exercised where applicable;
- dependencies, data changes, compatibility, and rollback have been reviewed;
- documentation and operating instructions are current;
- evidence and residual risks are recorded; and
- the normal human review and release process is complete.

The goal is not maximum autonomy. The goal is maximum useful acceleration with bounded authority, fast feedback, and verifiable results.
