# Kanban Board Lab

Kanban Board Lab is a traditional greenfield application-development exercise for building a focused Kanban board using a normal, direct development workflow.

The application gives an individual or small team a visual board for organizing work, limiting work in progress, and moving cards through a simple delivery flow. The lab does not prescribe a coding harness, agent framework, specification plugin, application architecture, frontend framework, or evidence format.

## Project contents

```text
kanban-board-lab/
├── README.md
├── setup-workspace.sh
└── docs/
    └── requirements.md
```

[`docs/requirements.md`](docs/requirements.md) defines the product behavior, scope, and success criteria. Technology selection and implementation decisions remain open.

## Create an empty workspace

Run the lightweight setup script from this directory:

```bash
./setup-workspace.sh
```

The script creates the lowest available numbered directory: `kanban-board-lab-1/`, then `kanban-board-lab-2/`, and so on. It never overwrites an existing run.

The generated directory is completely empty. The script does not install `AGENTS.md`, rules, skills, subagents, plugins, frameworks, dependencies, or application files.

Use `--dry-run` to display the next directory without creating it:

```bash
./setup-workspace.sh --dry-run
```

## Traditional development flow

1. Create an empty numbered directory with `./setup-workspace.sh` and open it using the development tool of your choice.
2. Read and clarify [`docs/requirements.md`](docs/requirements.md).
3. Choose a sensible application architecture and technology stack.
4. Implement the application in small, working increments.
5. Run appropriate automated tests and inspect the application in a browser.
6. Review the result against the requirements and record any remaining limitations.

No particular planning format, orchestration system, plugin, subagent, or command wrapper is required. Participants may use ordinary editor, terminal, source-control, testing, and browser workflows.

## Initial product scope

The first version is a single-board, single-device Kanban application. It supports configurable columns, task cards, card movement and ordering, search and filtering, work-in-progress limits, archiving, and local persistence.

Accounts, real-time collaboration, remote synchronization, external integrations, notifications, analytics, and AI-generated project decisions are outside the initial version.
