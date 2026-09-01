# Kanban Board Lab — Straitjacket

Kanban Board Lab is a greenfield application-development exercise for building and verifying a focused Kanban workflow with Claude Code and Codex under the Straitjacket (`ctx`) context-containment harness.

The application gives an individual or small team a visual board for organizing work, limiting work in progress, and moving cards through a simple delivery flow. Straitjacket is the development and evidence substrate; it is not an application feature or a user-facing dependency.

## Project contents

```text
kanban-board-lab-straitjacket/
├── README.md
└── docs/
    └── requirements.md
```

- [`docs/requirements.md`](docs/requirements.md) defines the product need, required behavior, scope boundaries, and success criteria.
- Application architecture, framework, storage implementation, and test tooling remain intentionally undecided until repository setup and planning.

## Development approach

1. Review and clarify [`docs/requirements.md`](docs/requirements.md).
2. Select the smallest suitable application architecture and record significant decisions.
3. Initialize Straitjacket only within this workspace, then verify its Claude Code and Codex integrations with `ctx doctor`.
4. Implement the approved scope in small, testable increments.
5. Route noisy commands and large evidence through `ctx`, retaining exact evidence handles rather than copying raw output into conversations.
6. Verify the completed application against the requirements, including keyboard interaction, persistence, filtering, and work-in-progress rules.
7. Retain test results, screenshots, review findings, and known limitations as delivery evidence.

## Initial product scope

The initial version is a single-board, single-device Kanban application. It supports configurable columns, task cards, card movement and ordering, search and filtering, work-in-progress limits, and local persistence.

Accounts, real-time collaboration, remote synchronization, external integrations, notifications, analytics, and AI-generated project decisions are outside the first version.
