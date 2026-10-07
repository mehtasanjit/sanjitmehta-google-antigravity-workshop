# Empty Workspace — Conductor

An empty Google Antigravity workspace for any project, with the Conductor plugin for a specification-driven workflow: the agent gets the base `AGENTS.md` guidelines, the workspace memory rule, and Conductor. There are no other skills, subagents, or plugins, and no project requirements. Bring your own brief. Without Conductor, see [Empty Workspace](../empty-workspace/).

## Project contents

```text
empty-workspace-conductor/
├── README.md
├── setup-workspace.sh
└── empty-workspace-conductor-N/   # Generated workspaces (or the name you chose)
```

- [`setup-workspace.sh`](setup-workspace.sh) creates the next available numbered workspace.
- Generated `empty-workspace-conductor-N/` directories are independent runs and are not reusable templates.

## Create a workspace

From this directory, run:

```bash
./setup-workspace.sh
```

The script checks `empty-workspace-conductor-1/`, `empty-workspace-conductor-2/`, and subsequent numbers and atomically reserves the first name that does not exist. It never overwrites an existing workspace.

To choose the name yourself, pass it as an argument. The workspace is created next to the script, and the name may contain letters, digits, dots, hyphens, and underscores:

```bash
./setup-workspace.sh my-project
```

If a folder with that name already exists, the script stops without changing it.

Use `--dry-run` to see the directory that would be created, without creating it:

```bash
./setup-workspace.sh --dry-run
./setup-workspace.sh --dry-run my-project
```

The setup needs Bash, Python 3, and network access to download a validated copy of the [Conductor plugin](https://github.com/gemini-cli-extensions/conductor) from its `main` branch. To pin a specific version, set `CONDUCTOR_REF` to a commit on `main`. Conductor's release tags use an older layout without `plugin.json` and do not work here.

```bash
CONDUCTOR_REF=6e8f9a860bcd ./setup-workspace.sh
```

If any setup step fails, the script removes only the newly reserved incomplete directory. It does not modify existing workspaces.

## What the script creates

```text
empty-workspace-conductor-N/
├── AGENTS.md                        # Copy of src/resources/workspace-guidance/agents/base.md
└── .agents/
    ├── plugins/
    │   └── conductor/               # Conductor plugin, downloaded at setup
    └── rules/
        └── workspace-memory.md      # Copy of src/resources/workspace-guidance/rules/workspace-memory.md
```

The workspace contains no application code, specification, plan, dependency environment, or `.memory/`. Those are created only while working inside that numbered workspace.

## Run the exercise

1. Create a workspace with `./setup-workspace.sh`, or `./setup-workspace.sh my-project` to name it.
2. Open the newly created directory as the Antigravity workspace.
3. Give the agent your own requirements or brief.
4. Use `/conductor:conductor-setup` to establish product, technology, and workflow context.
5. Use `/conductor:conductor-new-track` to clarify the requirements and review the specification and implementation plan.
6. Approve significant product and technical decisions before implementation.
7. Use `/conductor:conductor-implement` for the approved scope.
8. Verify the result against the requirements, and use `/conductor:conductor-review` when an independent structured review is useful.
9. Keep the specification, plan, test results, screenshots, and review findings as SDLC evidence.
