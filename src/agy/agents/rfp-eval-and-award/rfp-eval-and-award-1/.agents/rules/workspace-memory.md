# Workspace Memory Rule

## Rule Metadata

- **Summary:** Read and maintain indexed workspace memory in `.memory/`.
- **Activation Mode:** Always On

## Applicability

Apply this rule to every task. `<workspace-root>` is the folder that contains the `.agents/` folder holding this rule; if that cannot be determined, use the folder the host opened as the workspace, and if that is still ambiguous, ask.

Never store temporary notes, conversation transcripts, secrets, credentials, personal data, or information unrelated to the workspace.

## Read memory

- If `<workspace-root>/.memory/` exists, read `MEMORY.md`, then only the memory files relevant to the task.
- If `MEMORY.md` is missing, rebuild it from the memory files' names and frontmatter before updating memory.
- Add missing frontmatter to an existing memory file when you next update it; don't create a duplicate for it.

## Create memory

If `.memory/` does not exist, ask:

> No workspace memory exists. Should I create `.memory/`?

If the user declines, proceed without memory and don't ask again this session. If they approve and the workspace is inside a Git repository, ask:

> Should workspace memory remain private, or be available to commit to the repository for the team?

- **Private:** create `<workspace-root>/.memory/`. If Git does not already ignore it, list `/.memory/` in `<workspace-root>/.gitignore`.
- **Repository-shared, or not inside a Git repository:** create `<workspace-root>/.memory/` without changing `.gitignore`.

At creation, write only `MEMORY.md`. Creating repository-shared memory does not authorise a commit.

If a `.memory/` folder already exists and the project uses Git, find out whether the memory is private or shared. Don't change anything while you check.

- If the folder has been committed to Git, the memory is shared with the team.
- If the folder has not been committed and `.gitignore` lists it, the memory is private.
- If the folder has not been committed and `.gitignore` does not list it, ask the user whether they want it private or shared.
- Ask the user before you change `.gitignore` or remove the folder from Git.

Keep an existing, clear visibility choice unless the user asks to change it. Private memory may hold user- or machine-specific workspace facts. Repository-shared memory holds only what suits the whole team and repository history: no personal preferences, machine-specific values, or session identifiers. Neither holds secrets or personal data.

## Format

`MEMORY.md` is the index and has no frontmatter. One entry per memory file, using that file's description, with a relative link and no further detail:

```md
# Memory Index

- [Memory title](memory-name.md) — concise description of when this memory is relevant
```

Each memory file covers one subject, has a stable lowercase kebab-case filename, and starts with:

```yaml
---
name: memory-name
description: One concise sentence explaining when this memory is relevant
metadata:
  node_type: memory
  type: project
  modified: 2026-08-10T00:00:00Z
---
```

`name` matches the filename without `.md`; `modified` is an RFC 3339 timestamp, updated on every meaningful change. Optional metadata: `status`, `related`, `sources`, and `originSessionId` (private memory only). Keep the body concise and factual.

## Use memory

Memory is recall, not authority. Use it to avoid repeating discovery and settled decisions, and link to authoritative sources instead of copying them. When memory conflicts with an authoritative source, follow the source and correct the memory; ask if the workspace cannot resolve the conflict.

## Update memory

Update memory immediately after each consequential step, before the next one. A step is consequential when it produces something a later session needs, such as:

- a request to remember something, or a correction, preference, or rejection that affects future work;
- an approved requirement, decision, or change of direction;
- a durable discovery, constraint, convention, known issue, failed approach, or verified command;
- a material change to files, behaviour, architecture, dependencies, environment, or external shared state;
- a verification result that confirms behaviour, exposes a limitation, or invalidates an assumption;
- a blocker, unresolved issue, or completed milestone.

Update the existing file for that subject and its `modified` timestamp; create a new file only when no file covers the subject; update `MEMORY.md` only when the index changes. Correct or replace obsolete entries. Don't append duplicates, record decisions before they are approved, or store details easily recovered from the repository.

## Handoff

When memory was created or changed, report the files created or updated, whether memory is private or repository-shared, and any unresolved conflict, stale entry, or Git-tracking limitation.
