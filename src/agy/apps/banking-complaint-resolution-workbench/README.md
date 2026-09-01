# Banking Complaint Resolution Workbench

The Banking Complaint Resolution Workbench is a workshop application for practicing governed software delivery with Google Antigravity. It gives fictional bank case handlers and supervisors a controlled workflow for recording, assigning, investigating, reviewing, approving, and resolving customer complaints with an audit history.

All workshop identities, customers, complaints, and banking data must remain synthetic. Consequential complaint decisions remain with human users.

## Project contents

```text
banking-complaint-resolution-workbench/
├── README.md
├── setup-workspace.sh
├── docs/
│   ├── prompt.md
│   ├── requirements.md
│   ├── additional_prompt_sla_control_tower.md
│   └── additional_requirement_sla_control_tower.md
└── banking-complaint-resolution-workbench-N/  # Numbered runs
```

- [`requirements.md`](docs/requirements.md) defines the initial product behavior and acceptance criteria.
- [`prompt.md`](docs/prompt.md) is the self-contained initial request for a greenfield run.
- [`additional_requirement_sla_control_tower.md`](docs/additional_requirement_sla_control_tower.md) and [`additional_prompt_sla_control_tower.md`](docs/additional_prompt_sla_control_tower.md) define a later visible feature track for a suitable existing implementation.
- [`setup-workspace.sh`](setup-workspace.sh) creates the next available numbered application-empty workspace.
- Existing `banking-complaint-resolution-workbench-N/` directories are independent development runs and must not be overwritten by setup.

## Create a workshop workspace

From this directory, run:

```bash
./setup-workspace.sh
```

The script checks `banking-complaint-resolution-workbench-1/`, `-2/`, and subsequent numbers and atomically reserves the first name that does not exist. For example, when `-1/` exists, the next run creates `-2/`.

Use `--dry-run` to display the next directory without creating it:

```bash
./setup-workspace.sh --dry-run
```

The setup requires Bash, Python 3, and network access to download validated workspace-local copies of the official Google Agents CLI skills and Conductor plugin. Pin upstream branches, tags, or commits when a workshop requires reproducible tool versions:

```bash
AGENTS_CLI_REF=<ref> CONDUCTOR_REF=<ref> ./setup-workspace.sh
```

The script never overwrites an existing numbered workspace. If setup fails, it removes only the newly reserved incomplete directory.

## What the script creates

Each generated workspace is intentionally application-empty:

```text
banking-complaint-resolution-workbench-N/
├── AGENTS.md
└── .agents/
    ├── agents/              # Reusable SDLC subagents
    ├── plugins/
    │   └── conductor/   # Specification-driven workflow
    ├── rules/               # Workspace and memory rules
    └── skills/              # Environment and Agents CLI skills
```

It contains no application code, generated specification, implementation plan, dependency environment, or `.memory/`. Those are created only during the exercise.

## Greenfield SDLC exercise

1. Run `./setup-workspace.sh` and open the new numbered directory as the Antigravity workspace.
2. Read its `AGENTS.md` and follow the applicable rules and skills.
3. Submit the contents of [`docs/prompt.md`](docs/prompt.md).
4. Use `/conductor:conductor-setup` to establish product, technology, and workflow context.
5. Use `/conductor:conductor-new-track` to clarify and approve the specification and implementation plan.
6. Approve significant product, architecture, security, and data decisions before implementation.
7. Use `/conductor:conductor-implement` for the approved scope.
8. Verify the result against [`docs/requirements.md`](docs/requirements.md), then use `/conductor:conductor-review` when an independent structured review is useful.
9. Retain the specification, plan, tests, screenshots, review findings, and remaining limitations as SDLC evidence.

## Brownfield feature exercise

The numbered generator creates an empty starting point, so it is a greenfield setup. A brownfield exercise must instead begin from a deliberately selected, working numbered implementation with a known test baseline.

Before using the SLA Control Tower track:

1. Select and preserve a working implementation as the brownfield baseline.
2. Confirm its run instructions, tests, and current behavior.
3. Work in a separate copy or branch without changing the preserved baseline.
4. Submit [`docs/additional_prompt_sla_control_tower.md`](docs/additional_prompt_sla_control_tower.md).
5. Perform repository discovery and impact assessment before approving the feature specification and plan.
6. Verify the completed change against [`docs/additional_requirement_sla_control_tower.md`](docs/additional_requirement_sla_control_tower.md) and the full regression baseline.

## Initial product scope

The initial application covers complaint intake, assignment, investigation, review, approval, resolution, and audit history. External integrations, production authentication, real banking or customer data, and agentic decision-making are outside the initial scope.
