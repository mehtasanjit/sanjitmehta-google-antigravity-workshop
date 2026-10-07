# Bank Complaints Workbench

The Bank Complaints Workbench is a greenfield application-development exercise with Google Antigravity, run in a vanilla workspace: the agent gets only the base `AGENTS.md` guidelines and the workspace memory rule. There are no extra skills, subagents, plugins, or workflow tools. The prompts for the Conductor variants are in [Bank Complaints Workbench — Conductor](../bank-complaints-workbench-conductor/).

It gives fictional bank case handlers and supervisors a controlled workflow for recording, assigning, investigating, reviewing, approving, and resolving customer complaints with an audit history.

All workshop identities, customers, complaints, and banking data must remain synthetic. Consequential complaint decisions remain with human users.

## Project contents

```text
bank-complaints-workbench/
├── README.md
├── setup-workspace.sh
├── docs/
│   ├── requirements.md
│   └── additional_requirement_sla_control_tower.md
└── bank-complaints-workbench-N/   # Generated workshop runs
```

- [`docs/requirements.md`](docs/requirements.md) defines the initial product behaviour and acceptance criteria.
- [`docs/additional_requirement_sla_control_tower.md`](docs/additional_requirement_sla_control_tower.md) defines a later SLA Control Tower feature for an existing implementation (the brownfield exercise below).
- [`setup-workspace.sh`](setup-workspace.sh) creates the next available numbered workshop workspace.
- Generated `bank-complaints-workbench-N/` directories are independent development runs and are not reusable templates.

## Create a workshop workspace

From this directory, run:

```bash
./setup-workspace.sh
```

The script checks `bank-complaints-workbench-1/`, `bank-complaints-workbench-2/`, and subsequent numbers and atomically reserves the first name that does not exist. It never overwrites an existing workspace. For example, if `bank-complaints-workbench-1/` exists, the next run creates `bank-complaints-workbench-2/`.

Use `--dry-run` to see the next directory without creating it:

```bash
./setup-workspace.sh --dry-run
```

The setup needs only Bash. It downloads nothing. If any setup step fails, the script removes only the newly reserved incomplete directory. It does not modify existing numbered workspaces.

## What the script creates

```text
bank-complaints-workbench-N/
├── AGENTS.md                        # Copy of src/resources/workspace-guidance/agents/base.md
└── .agents/
    └── rules/
        └── workspace-memory.md      # Copy of src/resources/workspace-guidance/rules/workspace-memory.md
```

The workspace contains no application code, specification, plan, dependency environment, or `.memory/`. Those are created only while performing the exercise inside that numbered workspace.

## Greenfield exercise

1. Create a numbered workspace with `./setup-workspace.sh`.
2. Open the newly created directory as the Antigravity workspace.
3. Give the agent the requirements in [`docs/requirements.md`](docs/requirements.md), either by pasting them or by pointing it to the file.
4. Let the agent plan, confirm significant product, architecture, security, and data decisions with it, then build in small steps.
5. Verify the result against the requirements.
6. Keep the plan, tests, screenshots, review notes, and remaining limitations as SDLC evidence.

## Brownfield exercise

The setup script creates an empty starting point, so it is a greenfield setup. The brownfield exercise starts from a working implementation from an earlier run, with a known test baseline.

1. Select and preserve a working implementation as the brownfield baseline.
2. Confirm its run instructions, tests, and current behaviour.
3. Work in a separate copy or branch without changing the preserved baseline.
4. Give the agent [`docs/additional_requirement_sla_control_tower.md`](docs/additional_requirement_sla_control_tower.md) as the feature request.
5. Have the agent explore the existing code and assess the impact before you approve the feature plan.
6. Verify the completed change against [`docs/additional_requirement_sla_control_tower.md`](docs/additional_requirement_sla_control_tower.md) and the full regression baseline.

## Initial product scope

The initial application covers complaint intake, assignment, investigation, review, approval, resolution, and audit history. External integrations, production authentication, real banking or customer data, and agentic decision-making are outside the initial scope.
