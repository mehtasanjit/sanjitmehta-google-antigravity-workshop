# Lecture Pulse

Lecture Pulse is a workshop application project for exploring how Google Antigravity can be used to take a product from initial requirements through design and implementation.

The application is intended to give students a low-pressure way to submit questions during a live lecture and help lecturers identify the questions and unclear concepts shared by the class.

## Project structure

```text
lecture-pulse/
├── README.md
├── docs/
│   └── requirements.md
├── lecture-pulse-work/
│   ├── .agents/
│   │   ├── plugins/
│   │   ├── rules/
│   │   └── skills/
│   └── AGENTS.md
└── lecture-pulse-demo/       # Completed reference implementation, when available
```

### `docs/`

Contains the product requirements that define the problem, intended users, required experience, initial scope, and success criteria. These requirements are the authoritative starting point for the workshop exercise.

### `lecture-pulse-work/`

The prepared participant workspace. It contains:

- Instructions for agents working on the project.
- Google Agents CLI skills for agent development workflows.
- The Conductor plugin for specification-driven planning and implementation.
- Project-specific rules requiring applicable skills and current official documentation to be consulted before implementation.

Participants use this directory to create the project specification, make design decisions, develop the application, and record verification results.

### `lecture-pulse-demo/`

The intended location for a completed, runnable reference implementation. The demo should remain separate from the participant workspace so that workshop users can attempt the exercise before reviewing a finished solution.

The reference implementation has not yet been added to this repository.

## Workshop flow

1. Read [`docs/requirements.md`](docs/requirements.md).
2. Open the [`lecture-pulse-work`](lecture-pulse-work/) workspace.
3. Read [`lecture-pulse-work/AGENTS.md`](lecture-pulse-work/AGENTS.md) before starting work.
4. Use the installed skills and Conductor workflow to clarify requirements, agree on the design, plan the work, and implement the application.
5. Verify the completed behavior against the requirements and record anything incomplete or unverified.
6. Compare the result with `lecture-pulse-demo/` when the reference implementation becomes available.

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

The requirements and Antigravity participant workspace are prepared. Application implementation and the completed reference demo are not currently included.
