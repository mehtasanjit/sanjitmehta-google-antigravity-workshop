# Bank Complaints Workbench — Conductor and Subagents

The Bank Complaints Workbench is a greenfield application-development exercise with Google Antigravity. This variant runs it with the Conductor plugin and the eight SDLC subagents: the agent gets the base `AGENTS.md` guidelines, the workspace memory rule, Conductor, and the subagents. There are no other skills or plugins. Without the subagents, see [Bank Complaints Workbench — Conductor](../bank-complaints-workbench-conductor/); without Conductor, see [Bank Complaints Workbench](../bank-complaints-workbench/).

It gives fictional bank case handlers and supervisors a controlled workflow for recording, assigning, investigating, reviewing, approving, and resolving customer complaints with an audit history.

All workshop identities, customers, complaints, and banking data must remain synthetic. Consequential complaint decisions remain with human users.

## Project contents

```text
bank-complaints-workbench-conductor-subagents/
├── README.md
├── setup-workspace.sh
├── docs/
│   ├── prompt.md
│   ├── requirements.md
│   ├── additional_prompt_sla_control_tower.md
│   └── additional_requirement_sla_control_tower.md
└── bank-complaints-workbench-conductor-subagents-N/   # Generated workshop runs
```

- [`docs/prompt.md`](docs/prompt.md) is the self-contained initial request for a greenfield run.
- [`docs/requirements.md`](docs/requirements.md) defines the initial product behaviour and acceptance criteria.
- [`docs/additional_requirement_sla_control_tower.md`](docs/additional_requirement_sla_control_tower.md) defines a later SLA Control Tower feature for an existing implementation (the brownfield exercise below).
- [`docs/additional_prompt_sla_control_tower.md`](docs/additional_prompt_sla_control_tower.md) is the request for the SLA Control Tower track.
- [`setup-workspace.sh`](setup-workspace.sh) creates the next available numbered workshop workspace.
- Generated `bank-complaints-workbench-conductor-subagents-N/` directories are independent development runs and are not reusable templates.

## Create a workshop workspace

From this directory, run:

```bash
./setup-workspace.sh
```

The script checks `bank-complaints-workbench-conductor-subagents-conductor-subagents-1/`, `bank-complaints-workbench-conductor-subagents-conductor-subagents-2/`, and subsequent numbers and atomically reserves the first name that does not exist. It never overwrites an existing workspace.

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
bank-complaints-workbench-conductor-subagents-conductor-subagents-N/
├── AGENTS.md                        # Copy of src/resources/workspace-guidance/agents/base.md
└── .agents/
    ├── agents/                      # Copy of src/resources/subagents/sdlc-subagents/.agents/agents/ (8 SDLC subagents)
    ├── plugins/
    │   └── conductor/               # Conductor plugin, downloaded at setup
    └── rules/
        └── workspace-memory.md      # Copy of src/resources/workspace-guidance/rules/workspace-memory.md
```

The workspace contains no application code, specification, plan, dependency environment, or `.memory/`. Those are created only while working inside that numbered workspace.

## Greenfield exercise

1. Create a numbered workspace with `./setup-workspace.sh`.
2. Open the newly created directory as the Antigravity workspace.
3. Submit the contents of [`docs/prompt.md`](docs/prompt.md).
4. Use `/conductor:conductor-setup` to establish product, technology, and workflow context.
5. Use `/conductor:conductor-new-track` to clarify and approve the specification and implementation plan.
6. Approve significant product, architecture, security, and data decisions before implementation.
7. Use `/conductor:conductor-implement` for the approved scope, delegating bounded work to the subagents in `.agents/agents/` where they fit.
8. Verify the result against [`docs/requirements.md`](docs/requirements.md), then use `/conductor:conductor-review` when an independent structured review is useful.
9. Keep the specification, plan, tests, screenshots, review findings, and remaining limitations as SDLC evidence.

## Brownfield exercise

The setup script creates an empty starting point, so it is a greenfield setup. The brownfield exercise starts from a working implementation from an earlier run, with a known test baseline.

1. Select and preserve a working implementation as the brownfield baseline.
2. Confirm its run instructions, tests, and current behaviour.
3. Work in a separate copy or branch without changing the preserved baseline.
4. Submit [`docs/additional_prompt_sla_control_tower.md`](docs/additional_prompt_sla_control_tower.md).
5. Have the agent explore the existing code and assess the impact before you approve the feature plan.
6. Verify the completed change against [`docs/additional_requirement_sla_control_tower.md`](docs/additional_requirement_sla_control_tower.md) and the full regression baseline.

## Initial product scope

The initial application covers complaint intake, assignment, investigation, review, approval, resolution, and audit history. External integrations, production authentication, real banking or customer data, and agentic decision-making are outside the initial scope.
