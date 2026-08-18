# Banking Complaint Resolution Workbench

The Banking Complaint Resolution Workbench is a workshop application for demonstrating greenfield and brownfield development with Google Antigravity. It gives bank case handlers and supervisors a controlled workflow for recording, assigning, investigating, approving, and resolving customer complaints with an audit history.

All workshop data must remain synthetic, and consequential complaint decisions remain with human users.

## Project structure

```text
banking-complaint-resolution-workbench/
├── README.md
├── docs/
│   ├── prompt.md
│   └── requirements.md
├── banking-complaint-resolution-workbench-demo/
│   ├── .agents/
│   │   ├── agents/
│   │   ├── plugins/
│   │   │   └── conductor/
│   │   ├── rules/
│   │   └── skills/
│   └── AGENTS.md
└── banking-complaint-resolution-workbench-1/  # Existing development workspace
```

### `docs/`

- [`prompt.md`](docs/prompt.md) is the self-contained initial prompt for participants.
- [`requirements.md`](docs/requirements.md) records the detailed workshop requirements and acceptance criteria for facilitators and reviewers.

### `banking-complaint-resolution-workbench-demo/`

The prepared Antigravity workspace for the workshop. It contains:

- The baseline `AGENTS.md` and workspace rules.
- Eight reusable software-development subagents under `.agents/agents/`.
- Baseline workspace skills and Google Agents CLI skills under `.agents/skills/`.
- A workspace-local installation of the Conductor plugin under `.agents/plugins/conductor/`.

The directory contains the development setup, not a completed application. Copy it before starting so that the prepared workspace remains unchanged and can be reused by other participants.

### `banking-complaint-resolution-workbench-1/`

An existing development workspace containing application and Conductor artifacts. It is separate from the reusable prepared demo and is not the starting point for a new participant exercise.

## Use the prepared workspace

Run these commands from the `src/agy/apps/banking-complaint-resolution-workbench/` directory.

1. Copy the prepared workspace using a distinct name:

   ```bash
   cp -R banking-complaint-resolution-workbench-demo banking-complaint-resolution-workbench-work
   ```

2. Open `banking-complaint-resolution-workbench-work/` as the workspace and read its `AGENTS.md`.
3. Submit the contents of [`docs/prompt.md`](docs/prompt.md) as the initial request.

No additional workspace seeding, Agents CLI skill import, or Conductor import is required when using the prepared workspace.

## Develop the application with Conductor

The workbench can be developed using Conductor's specification-driven workflow. In the copied workspace:

1. Run `/conductor:conductor-setup` to establish the product, technology, and workflow context.
2. Run `/conductor:conductor-new-track` to clarify and review the application specification and implementation plan.
3. After approving the specification and plan, run `/conductor:conductor-implement`.
4. Verify the completed behavior against the approved requirements and acceptance criteria. Use `/conductor:conductor-review` when a structured review is useful.

Conductor is already stored locally in the prepared workspace and is carried into each participant copy.

## Initialize a workspace from scratch

As an alternative to copying the prepared demo, create a workspace from the repository's reusable resources:

1. Seed the baseline `AGENTS.md`, rules, skills, and reusable SDLC subagents:

   ```bash
   ../../../scripts/seed-workspace.sh banking-complaint-resolution-workbench-work
   ```

2. Follow the official installation methods first when optional tooling is required:

   ```bash
   uvx google-agents-cli setup
   agy plugins install https://github.com/gemini-cli-extensions/conductor
   ```

3. If the standard installations are unavailable, or workspace-local copies are required, use the repository import scripts:

   ```bash
   python3 ../../../scripts/import_google_agents_cli_skills.py banking-complaint-resolution-workbench-work
   python3 ../../../scripts/import_conductor_plugin.py banking-complaint-resolution-workbench-work
   ```

   The import scripts require network access. Use `--dry-run` to download and validate content without changing the workspace. Existing installations are replaced only when `--force` is supplied.

4. Open the new workspace, read `AGENTS.md`, and submit the initial prompt.

## Workshop scope

The initial application covers complaint intake, assignment, investigation, review, approval, resolution, and audit history. A brownfield exercise can extend a prepared working version with independent maker-checker approval for high-priority complaints.

External integrations, production authentication, real banking or customer data, and agentic decision-making are outside the initial scope.

## Status

The requirements, initial prompt, and prepared Antigravity workspace are available. The reusable workspace includes baseline guidance, SDLC subagents, Google Agents CLI skills, and Conductor. Application development is performed in a participant copy.
