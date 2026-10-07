# Kanban Board — Conductor and Subagents

Kanban Board is a greenfield application-development exercise with Google Antigravity. This variant runs it with the Conductor plugin and the eight SDLC subagents: the agent gets the base `AGENTS.md` guidelines, the workspace memory rule, Conductor, and the subagents. There are no other skills or plugins. Without the subagents, see [Kanban Board — Conductor](../kanban-board-conductor/); without Conductor, see [Kanban Board](../kanban-board/).

The application gives an individual or small team a visual board for organizing work, limiting work in progress, and moving cards through a simple delivery flow.

## Project contents

```text
kanban-board-conductor-subagents/
├── README.md
├── setup-workspace.sh
├── docs/
│   └── requirements.md
└── kanban-board-conductor-subagents-N/   # Generated workshop runs
```

- [`docs/requirements.md`](docs/requirements.md) defines the product need, users, initial scope, and success criteria.
- [`setup-workspace.sh`](setup-workspace.sh) creates the next available numbered workspace.
- Generated `kanban-board-conductor-subagents-N/` directories are independent runs and are not reusable templates.

## Create a workshop workspace

From this directory, run:

```bash
./setup-workspace.sh
```

The script checks `kanban-board-conductor-subagents-1/`, `kanban-board-conductor-subagents-2/`, and subsequent numbers and atomically reserves the first name that does not exist. It never overwrites an existing workspace.

Use `--dry-run` to see the next directory without creating it:

```bash
./setup-workspace.sh --dry-run
```

The setup needs Bash, Python 3, and network access to download a validated copy of the [Conductor plugin](https://github.com/gemini-cli-extensions/conductor) from its `main` branch. To pin a specific version, set `CONDUCTOR_REF` to a commit on `main`. Conductor's release tags use an older layout without `plugin.json` and do not work here.

```bash
CONDUCTOR_REF=6e8f9a860bcd ./setup-workspace.sh
```

If any setup step fails, the script removes only the newly reserved incomplete directory. It does not modify existing numbered workspaces.

## What the script creates

```text
kanban-board-conductor-subagents-N/
├── AGENTS.md                        # Copy of src/resources/workspace-guidance/agents/base.md
└── .agents/
    ├── agents/                      # Copy of src/resources/subagents/sdlc-subagents/.agents/agents/ (8 SDLC subagents)
    ├── plugins/
    │   └── conductor/               # Conductor plugin, downloaded at setup
    └── rules/
        └── workspace-memory.md      # Copy of src/resources/workspace-guidance/rules/workspace-memory.md
```

The workspace contains no Kanban Board application code, specification, plan, dependency environment, or `.memory/`. Those are created only while working inside that numbered workspace.

## Run the exercise

1. Create a numbered workspace with `./setup-workspace.sh`.
2. Open the newly created directory as the Antigravity workspace.
3. Give the agent the requirements in [`docs/requirements.md`](docs/requirements.md), either by pasting them or by pointing it to the file.
4. Use `/conductor:conductor-setup` to establish product, technology, and workflow context.
5. Use `/conductor:conductor-new-track` to clarify the requirements and review the specification and implementation plan.
6. Approve significant product and technical decisions before implementation.
7. Use `/conductor:conductor-implement` for the approved scope, delegating bounded work to the subagents in `.agents/agents/` where they fit.
8. Verify the result against the requirements, and use `/conductor:conductor-review` when an independent structured review is useful.
9. Keep the specification, plan, test results, screenshots, and review findings as SDLC evidence.

## Initial product scope

The first version is a single-board, single-device Kanban application. It supports configurable columns, task cards, card movement and ordering, search and filtering, work-in-progress limits, archiving, and local persistence.

Accounts, real-time collaboration, remote synchronization, external integrations, notifications, analytics, and AI-generated project decisions are outside the initial version.
