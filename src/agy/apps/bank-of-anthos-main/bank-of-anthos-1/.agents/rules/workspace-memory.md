# Workspace Memory Rule

## Rule Metadata

- **Summary:** Discover, read, create, and continuously maintain indexed workspace memory in `.memory/`.
- **Activation Mode:** Always On

## Applicability

You must apply this rule to every task performed in a workspace.

This rule does not require memory to be created when the user declines it. Do not store temporary notes, conversation transcripts, secrets, credentials, personal data, or information unrelated to the workspace.

## Workflow

### Step 1: Inspect workspace memory

1. Resolve `<workspace-root>` as defined by the base workspace guidance.
2. Inspect `<workspace-root>/.memory/`.
3. If `.memory/` exists, read `.memory/MEMORY.md` first.
4. Use the index descriptions to identify memories relevant to the current task.
5. Read only the relevant memory files.
6. Do not load every memory file by default.

If `.memory/` exists without `MEMORY.md`, inspect the available memory-file names and frontmatter, then create or repair the index before making further memory updates.

If an existing memory file lacks the required frontmatter, add it when that file is next updated. Do not create a duplicate file merely to apply the current format.

### Step 2: Resolve memory creation and Git visibility

If `.memory/` does not exist, ask:

> No workspace memory exists. Should I create `.memory/`?

If the user declines, proceed without workspace memory and do not repeat the question during the same task.

If the user approves creation:

1. Determine whether the workspace is a Git repository.
2. If it is not a Git repository, create `<workspace-root>/.memory/` without asking about Git visibility.
3. If it is a Git repository, ask:

   > Should workspace memory remain private, or be available to commit to the repository for the team?

4. Apply the answer as follows:
   - **Private:** Create `<workspace-root>/.memory/` and ensure `/.memory/` is listed in the root `.gitignore`.
   - **Repository-shared:** Create `<workspace-root>/.memory/` and do not add it to `.gitignore`.

Creating repository-shared memory does not authorize a Git commit.

If `.memory/` already exists in a Git repository, determine its current Git visibility using non-mutating checks:

- If it is tracked, treat it as repository-shared.
- If it is ignored and untracked, treat it as private.
- If it is neither tracked nor ignored, ask whether it should be private or repository-shared. Add `/.memory/` to the root `.gitignore` only when the user chooses private.
- If it is tracked and also matches an ignore rule, explain that `.gitignore` does not untrack existing files and ask whether to keep it repository-shared or make it private. Obtain explicit approval before changing Git tracking.

Preserve an existing, unambiguous Git-visibility choice unless the user requests a change.

Private memory may contain user- or machine-specific workspace facts, but never secrets or personal data. Repository-shared memory must contain only information suitable for the entire team and repository history; it must not contain personal preferences, machine-specific values, or session identifiers.

### Step 3: Initialize the memory index

Create only `.memory/MEMORY.md` during initialization.

`MEMORY.md` is the only reserved memory filename and does not require frontmatter.

Use this structure:

```md
# Memory Index

- [Memory title](memory-name.md) — concise description of when this memory is relevant
```

You must:

1. Keep `MEMORY.md` concise.
2. Include one entry for every subject-specific memory file.
3. Use each memory file's description in its index entry.
4. Link to memory files using relative paths.
5. Never duplicate detailed memory content in the index.

Do not create empty category files during initialization.

### Step 4: Create subject-specific memory files

Create a new memory file only when durable information represents a distinct subject and no existing memory file covers it.

Use a stable lowercase kebab-case filename and require this frontmatter:

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

You must:

1. Make `name` match the filename without `.md`.
2. Keep `description` concise and specific enough to support relevance decisions.
3. Set `metadata.node_type` to `memory`.
4. Set `metadata.type` to `project`.
5. Set `metadata.modified` to the current RFC 3339 timestamp whenever the file changes consequentially.
6. Keep one coherent memory subject per file.
7. Add the file to `MEMORY.md` immediately after creating it.

The body format may follow the needs of the subject. Keep it concise, factual, and easy to update.

Optional metadata may include `status`, `related`, `sources`, and `originSessionId`. Use `originSessionId` only in private memory. Do not require optional metadata when it provides no value.

### Step 5: Use memory

Memory is a recall and continuity layer. It must not replace authoritative workspace information.

1. Use relevant memory to avoid repeating workspace discovery and settled decisions.
2. Link to authoritative workspace sources instead of copying their contents into memory.
3. When memory conflicts with an authoritative source, follow that source and correct the memory.
4. Ask the user when a conflict cannot be resolved from the workspace.

### Step 6: Maintain memory continuously

When workspace memory exists or the user approves its creation, you must update it immediately after every consequential step and before continuing to the next consequential action.

A consequential step includes:

- An explicit user request to remember, record, or update workspace information.
- A user correction, clarification, confirmed preference, or rejection that affects future work.
- An approved requirement, decision, or change in direction.
- A durable discovery, constraint, convention, known issue, failed approach, or verified command.
- A material change to workspace files, behavior, architecture, dependencies, environment, or external shared state.
- A verification result that confirms behavior, exposes a limitation, or invalidates an assumption.
- A blocker, unresolved issue, completed milestone, or change to the next required action.
- Any other durable fact or state change that a later session would need to continue safely or avoid repeating work.

After each consequential step, you must:

1. Identify the existing memory file for that subject.
2. Update that file and its `metadata.modified` timestamp.
3. Create a new memory file only when no existing file covers the subject.
4. Update `MEMORY.md` only when its file index or an indexed description changes.
5. Complete the memory update before beginning the next consequential action.

You must not create a new file for every step, append duplicate entries, or defer all memory updates until final handoff.

You must correct or supersede obsolete information, record decisions only after they are approved or established, and avoid transient details that can be recovered easily from the repository.

## Handoff

When memory was created or materially changed, report:

- The memory files created or updated.
- Whether `.memory/` is private or repository-shared.
- Any unresolved conflict, stale entry, or Git-tracking limitation.
