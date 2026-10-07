# Lecture Pulse — Conductor

Lecture Pulse is a greenfield application-development exercise with Google Antigravity. This variant runs it with the Conductor plugin for a specification-driven workflow: the agent gets the base `AGENTS.md` guidelines, the workspace memory rule, and Conductor. There are no other skills, subagents, or plugins. For the same exercise without Conductor, see [Lecture Pulse](../lecture-pulse/).

Students use Lecture Pulse to submit questions during a live lecture without interrupting the class. Lecturers use it to identify popular questions and concepts that need clarification.

## Project contents

```text
lecture-pulse-conductor/
├── README.md
├── setup-workspace.sh
├── docs/
│   └── requirements.md
└── lecture-pulse-conductor-N/   # Generated workshop runs
```

- [`docs/requirements.md`](docs/requirements.md) defines the product need, users, initial scope, and success criteria.
- [`setup-workspace.sh`](setup-workspace.sh) creates the next available numbered workshop workspace.
- Generated `lecture-pulse-conductor-N/` directories are independent development runs and are not reusable templates.

## Create a workshop workspace

From this directory, run:

```bash
./setup-workspace.sh
```

The script checks `lecture-pulse-conductor-1/`, `lecture-pulse-conductor-2/`, and subsequent numbers and atomically reserves the first name that does not exist. It never overwrites an existing workspace.

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
lecture-pulse-conductor-N/
├── AGENTS.md                        # Copy of src/resources/workspace-guidance/agents/base.md
└── .agents/
    ├── plugins/
    │   └── conductor/               # Conductor plugin, downloaded at setup
    └── rules/
        └── workspace-memory.md      # Copy of src/resources/workspace-guidance/rules/workspace-memory.md
```

The workspace contains no Lecture Pulse application code, specification, plan, dependency environment, or `.memory/`. Those are created only while performing the exercise inside that numbered workspace.

## Run the exercise

1. Create a numbered workspace with `./setup-workspace.sh`.
2. Open the newly created directory as the Antigravity workspace.
3. Give the agent the requirements in [`docs/requirements.md`](docs/requirements.md), either by pasting them or by pointing it to the file.
4. Use `/conductor:conductor-setup` to establish product, technology, and workflow context.
5. Use `/conductor:conductor-new-track` to clarify the requirements and review the specification and implementation plan.
6. Approve significant product and technical decisions before implementation.
7. Use `/conductor:conductor-implement` for the approved scope.
8. Verify the result against the requirements, and use `/conductor:conductor-review` when an independent structured review is useful.
9. Keep the specification, plan, test results, screenshots, and review findings as SDLC evidence.

## Initial product scope

The first version focuses on live lecture questions and feedback:

- A lecturer starts and closes a question session.
- Students join with a short code without creating a permanent account.
- Students submit questions or unclear concepts, or indicate that an existing question also affects them.
- Lecturers see questions and their level of student interest as the session progresses.
- Lecturers mark questions as answered, and students can see whether a question has been acknowledged or answered.
- Student participation can remain anonymous to the class.

Attendance, grading, assessments, student-performance tracking, and learning-management-system integrations are outside the initial scope.
