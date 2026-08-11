# Workspace Memory Rule

## Rule Metadata

- **Summary:** Discover, read, create, and continuously maintain indexed workspace memory in `.memory/`.
- **Activation Mode:** Always On

## Applicability

You must apply this rule to every task performed in a workspace.

This rule does not require memory to be created when the user declines it. Do not store temporary notes, conversation transcripts, secrets, credentials, personal data, or information unrelated to the workspace.

## Workflow

### Step 1: Inspect workspace memory

1. Resolve the workspace or Git root.
2. Inspect `<workspace-root>/.memory/`.
3. If `.memory/` exists, read `.memory/MEMORY.md` first.
4. Use the index descriptions to identify memories relevant to the current task.
5. Read only the relevant memory files.
6. Do not load every memory file by default.

If `.memory/` exists without `MEMORY.md`, inspect the available memory-file names and frontmatter, then create or repair the index before making further memory updates.

If an existing memory file lacks the required frontmatter, add it when that file is next updated. Do not create a duplicate file merely to apply the current format.

### Step 2: Ask before creating memory

If `.memory/` does not exist, ask:

> Should workspace memory remain private, or be committed to the repository for the team?

Apply the answer as follows:

- **Private:** Create `<workspace-root>/.memory/` and ensure `/.memory/` is listed in the root `.gitignore`.
- **Committed:** Create `<workspace-root>/.memory/` and do not add it to `.gitignore`.

Private memory may contain user- or machine-specific workspace facts, but never secrets or personal data. Committed memory must contain only information suitable for the entire team and repository history; it must not contain personal preferences, machine-specific values, or session identifiers.

If the user declines workspace memory, proceed without creating it. Do not repeat the question during the same task.

If `.memory/` is already tracked and the user chooses private memory, explain that `.gitignore` does not untrack existing files and obtain approval before changing Git tracking. If the user chooses committed memory but `.memory/` is ignored, ask before removing the applicable ignore entry.

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

### Step 5: Keep authoritative information outside memory

Memory is a recall and continuity layer. It must not replace authoritative workspace information.

You must store:

- Mandatory agent behavior in `AGENTS.md` or `.agents/rules/`.
- Repeatable procedures in `.agents/skills/`.
- Requirements, specifications, product context, and authoritative architecture in project documentation.
- Information that can be derived reliably from source files or configuration in those source files or configuration.

Memory files must link to authoritative sources instead of copying them. If the authoritative location does not yet exist, ask the user before treating memory as its permanent replacement.

### Step 6: Use memory

1. Use relevant memory to avoid repeating workspace discovery and settled decisions.
2. Treat current user instructions, `AGENTS.md`, applicable rules, approved requirements, specifications, source files, and configuration as more authoritative than memory.
3. When memory conflicts with an authoritative source, follow that source and correct the memory.
4. Ask the user when a conflict cannot be resolved from authoritative workspace sources.

### Step 7: Maintain memory continuously

When workspace memory exists or the user approves its creation, you must update it immediately after every consequential step and before continuing to the next consequential action.

A consequential step includes:

- An explicit user request to remember, record, or update workspace information.
- An approved requirement, decision, or change in direction.
- A durable discovery, constraint, convention, or verified command.
- A material change to workspace files, behavior, architecture, dependencies, or environment.
- A verification result that confirms behavior or exposes a limitation.
- A blocker, unresolved issue, completed milestone, or change to the next required action.

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
- Whether `.memory/` is private or committed.
- Any unresolved conflict, stale entry, or Git-tracking limitation.
