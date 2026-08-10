# Workspace Memory Rule

## Rule Metadata

- **Summary:** Discover, read, create, and maintain durable workspace memory in `.memory/`.
- **Activation Mode:** Always On

## Applicability

You must apply this rule to every task performed in a workspace.

This rule does not require memory to be created when the user declines it. Do not store temporary notes, conversation transcripts, secrets, credentials, or information unrelated to the workspace.

## Workflow

### Step 1: Inspect workspace memory

1. Resolve the workspace or Git root.
2. Inspect `<workspace-root>/.memory/`.
3. If `.memory/` exists, read `.memory/MEMORY.md` first.
4. Read `.memory/active-context.md` to determine the current focus, completed work, blockers, and next steps.
5. Inspect the remaining memory files and read only those relevant to the current task.
6. Do not load every memory file by default.

If an existing memory store uses an equivalent file under a different name, preserve it and record the mapping in `MEMORY.md`. Do not create duplicate files only to enforce the recommended names.

If `.memory/` exists without `MEMORY.md`, inspect its contents and create or repair the index when making memory updates. If it has no active-context file or equivalent, create `active-context.md` when the task produces useful continuation state.

### Step 2: Ask before creating memory

If `.memory/` does not exist, ask:

> Should workspace memory remain private, or be committed to the repository for the team?

Apply the answer as follows:

- **Private:** Create `<workspace-root>/.memory/` and ensure `/.memory/` is listed in the root `.gitignore`.
- **Committed:** Create `<workspace-root>/.memory/` and do not add it to `.gitignore`.

If the user declines workspace memory, proceed without creating it. Do not repeat the question during the same task.

If `.memory/` is already tracked and the user chooses private memory, explain that `.gitignore` does not untrack existing files and obtain approval before changing Git tracking. If the user chooses committed memory but `.memory/` is ignored, ask before removing the applicable ignore entry.

### Step 3: Initialize memory

You must initialize these core files:

- `.memory/MEMORY.md`: A concise entry point containing critical reminders and links to memory files and authoritative workspace documents.
- `.memory/active-context.md`: The current focus, recent completed work, blockers, and next steps required to continue effectively.

Keep both core files concise. `MEMORY.md` is an index, not a copy of the other memory files.

Create the following files only when they have useful content:

- `decisions.md`: Settled decisions and links to the requirements, specifications, discussions, or records that established them.
- `discoveries.md`: Non-obvious findings, debugging lessons, project-specific traps, and useful verified commands.
- `topics/<topic>.md`: Detailed memory for a specific component, integration, agent, or workflow.

Create these situational files only when the information does not already have an authoritative home:

- `environment.md`: Established workspace- or machine-specific environment facts.
- `preferences.md`: Personal working preferences. Keep this file private.
- `progress.md`: Longer-term milestones when they no longer fit clearly in `active-context.md`.
- `architecture.md`: Architectural recall when no authoritative architecture document exists.

Use lowercase kebab-case names for additional memory files. Link every memory file from `MEMORY.md` and do not duplicate its detailed content in the index.

### Step 4: Keep authoritative information outside memory

Memory is a recall and continuity layer. It must not replace authoritative workspace information.

You must store:

- Mandatory agent behavior in `AGENTS.md` or `.agents/rules/`.
- Repeatable procedures in `.agents/skills/`.
- Requirements, specifications, product context, and authoritative architecture in project documentation.
- Information that can be derived reliably from source files or configuration in those source files or configuration.

Memory files must link to authoritative sources instead of copying them. If the authoritative location does not yet exist, ask the user before treating memory as its permanent replacement.

### Step 5: Use memory

1. Use relevant memory to avoid repeating workspace discovery and settled decisions.
2. Treat current user instructions, `AGENTS.md`, applicable rules, approved requirements, specifications, source files, and configuration as more authoritative than memory.
3. When memory conflicts with the current workspace, follow the authoritative source and correct the memory.
4. Ask the user when a conflict cannot be resolved from authoritative workspace sources.

### Step 6: Maintain memory

Update memory when the task establishes durable information that will be useful in future sessions.

You must:

1. Keep entries concise, factual, and scoped to the workspace.
2. Update an existing entry instead of adding a duplicate.
3. Remove or correct information shown to be obsolete by the completed work.
4. Record decisions only after they are approved or established by authoritative project sources.
5. Keep `MEMORY.md` short and move details into relevant topic files.
6. Keep `active-context.md` current; remove completed or obsolete continuation items.
7. Never store secrets, credentials, personal data, or complete command output.

Do not record transient implementation details that can be recovered easily from the repository.

## Handoff

When memory was created or materially changed, report:

- The memory files created or updated.
- Whether `.memory/` is private or committed.
- Any unresolved conflict, stale entry, or Git-tracking limitation.
