# Lecture Pulse

Lecture Pulse is a workshop application project for exploring how Google Antigravity can be used to take a product from initial requirements through design and implementation.

The application is intended to give students a low-pressure way to submit questions during a live lecture and help lecturers identify the questions and unclear concepts shared by the class.

## Project structure

```text
lecture-pulse/
├── README.md
├── docs/
│   └── requirements.md
└── lecture-pulse-demo/
    ├── .agents/
    │   ├── agents/
    │   ├── plugins/
    │   │   └── conductor/
    │   ├── rules/
    │   └── skills/
    └── AGENTS.md
```

### `docs/`

Contains the product requirements that define the problem, intended users, required experience, initial scope, and success criteria. These requirements are the authoritative starting point for the workshop exercise.

### `lecture-pulse-demo/`

The prepared Antigravity workspace for the workshop. It contains:

- The baseline `AGENTS.md` and workspace rules.
- Reusable software-development subagents under `.agents/agents/`.
- Baseline workspace skills and Google Agents CLI skills under `.agents/skills/`.
- A workspace-local installation of the Conductor plugin under `.agents/plugins/conductor/`.

The directory contains the development setup, not a completed Lecture Pulse application. Copy it before starting so that the prepared workspace remains unchanged and can be reused by other participants.

## Use the prepared workspace

Run these commands from the `src/agy/apps/lecture-pulse/` directory.

1. Copy the prepared workspace using a distinct name:

   ```bash
   cp -R lecture-pulse-demo lecture-pulse-work-1
   ```

2. Open `lecture-pulse-work-1/` as the workspace and read its `AGENTS.md` before starting the exercise. No additional workspace seeding or Conductor import is required.

## Develop Lecture Pulse with Conductor

Lecture Pulse can be developed using Conductor's specification-driven workflow. In the copied workspace:

1. Read [`docs/requirements.md`](docs/requirements.md) in this project directory.
2. Run `/conductor:conductor-setup` to establish the product, technology, and workflow context.
3. Run `/conductor:conductor-new-track` and use the requirements to define and review the application specification and implementation plan.
4. After approving the specification and plan, run `/conductor:conductor-implement`.
5. Verify the completed behavior against the requirements. Use `/conductor:conductor-review` when a structured review is useful.

Conductor is already stored locally in `lecture-pulse-demo/.agents/plugins/conductor/`, so it is carried into the copied workspace.

## Initialize a workspace from scratch

As an alternative to copying `lecture-pulse-demo/`, create a workspace from the repository's reusable resources:

1. Seed the workspace with the baseline `AGENTS.md`, rules, skills, and reusable SDLC subagents:

   ```bash
   ../../../scripts/seed-workspace.sh lecture-pulse-work-1
   ```

   The seed script installs subagent definitions under `.agents/agents/`, does not overwrite existing files, and does not create workspace memory.

2. Follow the official installation methods first when optional tooling is required:

   ```bash
   uvx google-agents-cli setup
   agy plugins install https://github.com/gemini-cli-extensions/conductor
   ```

3. If the standard installations are unavailable, or workspace-local copies are required, use the repository import scripts:

   ```bash
   python3 ../../../scripts/import_google_agents_cli_skills.py lecture-pulse-work-1
   python3 ../../../scripts/import_conductor_plugin.py lecture-pulse-work-1
   ```

   The import commands download content from the official upstream repositories and require network access. Use `--dry-run` to download and validate the content without changing the workspace. Existing installations are not replaced unless `--force` is supplied.

4. Open `lecture-pulse-work-1/` as the workspace and read its `AGENTS.md` before starting the exercise.

## Workshop flow

1. Read [`docs/requirements.md`](docs/requirements.md).
2. Copy [`lecture-pulse-demo/`](lecture-pulse-demo/) to a new participant workspace and open the copy.
3. Read the copied workspace's `AGENTS.md` before starting work.
4. Use Conductor to clarify requirements, agree on the design, plan the work, and implement the application.
5. Verify the completed behavior against the requirements and record anything incomplete or unverified.

## Initial scope

The first version focuses on live lecture questions and feedback:

- A lecturer starts and closes a question session.
- Students join with a short code without creating a permanent account.
- Students submit questions or indicate that an existing question also affects them.
- Lecturers see questions and their level of student interest as the session progresses.
- Lecturers mark questions as answered.
- Student participation can remain anonymous to the class.

Attendance, grading, assessments, student-performance tracking, and learning-management-system integrations are outside the initial scope.

## Status

The requirements and prepared Antigravity workspace are available. The workspace includes the baseline guidance, reusable SDLC subagents, Google Agents CLI skills, and Conductor. The application implementation is intentionally left to workshop participants.
