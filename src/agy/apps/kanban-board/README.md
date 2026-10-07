# Kanban Board

Kanban Board is a greenfield application-development exercise with Google Antigravity, run in a vanilla workspace: the agent gets only the base `AGENTS.md` guidelines and the workspace memory rule. There are no extra skills, subagents, plugins, or workflow tools.

The application gives an individual or small team a visual board for organizing work, limiting work in progress, and moving cards through a simple delivery flow.

## Project contents

```text
kanban-board/
├── README.md
├── setup-workspace.sh
├── docs/
│   └── requirements.md
└── kanban-board-N/       # Generated workshop runs
```

- [`docs/requirements.md`](docs/requirements.md) defines the product need, users, initial scope, and success criteria.
- [`setup-workspace.sh`](setup-workspace.sh) creates the next available numbered workshop workspace.
- Generated `kanban-board-N/` directories are independent development runs and are not reusable templates.

## Create a workshop workspace

From this directory, run:

```bash
./setup-workspace.sh
```

The script checks `kanban-board-1/`, `kanban-board-2/`, and subsequent numbers and atomically reserves the first name that does not exist. It never overwrites an existing workspace. For example, if `kanban-board-1/` exists, the next run creates `kanban-board-2/`.

Use `--dry-run` to see the next directory without creating it:

```bash
./setup-workspace.sh --dry-run
```

The setup needs only Bash. It downloads nothing. If any setup step fails, the script removes only the newly reserved incomplete directory. It does not modify existing numbered workspaces.

## What the script creates

```text
kanban-board-N/
├── AGENTS.md                        # Copy of src/resources/workspace-guidance/agents/base.md
└── .agents/
    └── rules/
        └── workspace-memory.md      # Copy of src/resources/workspace-guidance/rules/workspace-memory.md
```

The workspace contains no Kanban Board application code, specification, plan, dependency environment, or `.memory/`. Those are created only while performing the exercise inside that numbered workspace.

## Run the exercise

1. Create a numbered workspace with `./setup-workspace.sh`.
2. Open the newly created directory as the Antigravity workspace.
3. Give the agent the requirements in [`docs/requirements.md`](docs/requirements.md), either by pasting them or by pointing it to the file.
4. Let the agent plan, confirm significant product and technical decisions with it, then build in small steps.
5. Verify the result against the requirements.
6. Keep the plan, test results, screenshots, and review notes as SDLC evidence.

## Initial product scope

The first version is a single-board, single-device Kanban application. It supports configurable columns, task cards, card movement and ordering, search and filtering, work-in-progress limits, archiving, and local persistence.

Accounts, real-time collaboration, remote synchronization, external integrations, notifications, analytics, and AI-generated project decisions are outside the initial version.
