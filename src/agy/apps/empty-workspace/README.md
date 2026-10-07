# Empty Workspace

An empty Google Antigravity workspace for any project: the agent gets only the base `AGENTS.md` guidelines and the workspace memory rule. There are no skills, subagents, plugins, or workflow tools, and no project requirements. Bring your own brief.

## Project contents

```text
empty-workspace/
├── README.md
├── setup-workspace.sh
└── empty-workspace-N/   # Generated workspaces (or the name you chose)
```

- [`setup-workspace.sh`](setup-workspace.sh) creates the next available numbered workspace.
- Generated `empty-workspace-N/` directories are independent runs and are not reusable templates.

## Create a workspace

From this directory, run:

```bash
./setup-workspace.sh
```

The script checks `empty-workspace-1/`, `empty-workspace-2/`, and subsequent numbers and atomically reserves the first name that does not exist. It never overwrites an existing workspace.

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

The setup needs only Bash. It downloads nothing. If any setup step fails, the script removes only the newly reserved incomplete directory. It does not modify existing workspaces.

## What the script creates

```text
empty-workspace-N/
├── AGENTS.md                        # Copy of src/resources/workspace-guidance/agents/base.md
└── .agents/
    └── rules/
        └── workspace-memory.md      # Copy of src/resources/workspace-guidance/rules/workspace-memory.md
```

The workspace contains no application code, specification, plan, dependency environment, or `.memory/`. Those are created only while working inside that numbered workspace.

## Run the exercise

1. Create a workspace with `./setup-workspace.sh`, or `./setup-workspace.sh my-project` to name it.
2. Open the newly created directory as the Antigravity workspace.
3. Give the agent your own requirements or brief.
4. Let the agent plan, confirm significant product and technical decisions with it, then build in small steps.
5. Verify the result against the requirements.
6. Keep the plan, test results, screenshots, and review notes as SDLC evidence.
