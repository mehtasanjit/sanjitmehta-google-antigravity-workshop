# Lecture Pulse

Lecture Pulse is a greenfield application-development exercise for taking a product requirement through a governed software-development lifecycle with Google Antigravity.

Students use Lecture Pulse to submit questions during a live lecture without interrupting the class. Lecturers use it to identify popular questions and concepts that need clarification.

## Project contents

```text
lecture-pulse/
├── README.md
├── setup-workspace.sh
├── docs/
│   └── requirements.md
└── lecture-pulse-N/       # Generated workshop runs
```

- [`docs/requirements.md`](docs/requirements.md) defines the product need, users, initial scope, and success criteria.
- [`setup-workspace.sh`](setup-workspace.sh) creates the next available numbered workshop workspace.
- Generated `lecture-pulse-N/` directories are independent development runs and are not reusable templates.

## Create a workshop workspace

From this directory, run:

```bash
./setup-workspace.sh
```

The script checks `lecture-pulse-1/`, `lecture-pulse-2/`, and subsequent numbers and atomically reserves the first name that does not exist. It never overwrites an existing workspace. For example, if `lecture-pulse-1/` exists, the next run creates `lecture-pulse-2/`.

Use `--dry-run` to see the next directory without creating it:

```bash
./setup-workspace.sh --dry-run
```

The setup requires Bash, Python 3, and network access to download validated workspace-local copies of the official Google Agents CLI skills and Conductor plugin. Specific upstream branches, tags, or commits can be selected when reproducibility requires pinned versions:

```bash
AGENTS_CLI_REF=<ref> CONDUCTOR_REF=<ref> ./setup-workspace.sh
```

If any setup step fails, the script removes only the newly reserved incomplete directory. It does not modify existing numbered workspaces.

## What the script creates

A newly generated workspace is intentionally application-empty:

```text
lecture-pulse-N/
├── AGENTS.md
└── .agents/
    ├── agents/              # Reusable SDLC subagents
    ├── plugins/
    │   └── conductor/   # Specification-driven workflow
    ├── rules/               # Workspace and memory rules
    └── skills/              # Environment and Agents CLI skills
```

It contains no Lecture Pulse application code, generated specification, implementation plan, dependency environment, or `.memory/`. Those are created only while performing the exercise inside that numbered workspace.

## Run the exercise

1. Create a numbered workspace with `./setup-workspace.sh`.
2. Open the newly created directory as the Antigravity workspace.
3. Read its `AGENTS.md` and follow the applicable rules and skills.
4. Read [`docs/requirements.md`](docs/requirements.md) from this project folder.
5. Use `/conductor:conductor-setup` to establish product, technology, and workflow context.
6. Use `/conductor:conductor-new-track` to clarify the requirements and review the specification and implementation plan.
7. Approve significant product and technical decisions before implementation.
8. Use `/conductor:conductor-implement` for the approved scope.
9. Verify the result against the requirements and use `/conductor:conductor-review` when an independent structured review is useful.
10. Retain the specification, plan, test results, screenshots, and review findings as SDLC evidence.

## Initial product scope

The first version focuses on live lecture questions and feedback:

- A lecturer starts and closes a question session.
- Students join with a short code without creating a permanent account.
- Students submit questions or indicate that an existing question also affects them.
- Lecturers see questions and their level of student interest as the session progresses.
- Lecturers mark questions as answered.
- Student participation can remain anonymous to the class.

Attendance, grading, assessments, student-performance tracking, and learning-management-system integrations are outside the initial scope.
