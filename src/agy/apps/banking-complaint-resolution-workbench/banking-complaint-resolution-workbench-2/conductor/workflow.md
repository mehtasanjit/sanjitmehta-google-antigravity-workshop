# Project Workflow

## Guiding Principles

1. **The Plan is the Source of Truth:** All work must be tracked in `plan.md`.
2. **The Tech Stack is Deliberate:** Changes to the tech stack must be documented in `tech-stack.md` before implementation.
3. **Test-Driven Development:** Write unit tests before implementing functionality.
4. **High Code Coverage:** Aim for >80% code coverage for all backend logic and API routes.
5. **Simplicity & Usability:** Prioritize an extremely clear, role-aware Kanban board interface.
6. **Non-Interactive & CI-Aware:** Prefer non-interactive commands.

## Development Commands

### Environment & Execution
- Python Interpreter: `/home/sanjitmehta/work/python/venv_3_13_14_1/bin/python`
- Run Server: `/home/sanjitmehta/work/python/venv_3_13_14_1/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- Run Tests: `/home/sanjitmehta/work/python/venv_3_13_14_1/bin/python -m pytest -v`
- Seed Synthetic Data: `/home/sanjitmehta/work/python/venv_3_13_14_1/bin/python -m app.seed`

## Task Workflow

All tasks follow a strict lifecycle:

1. **Select Task:** Choose the next available task from `plan.md` in sequential order.
2. **Mark In Progress:** Edit `plan.md` and change the task from `[ ]` to `[~]`.
3. **Write Failing Tests (Red Phase):** Write tests verifying acceptance criteria.
4. **Implement to Pass Tests (Green Phase):** Implement application code to pass tests.
5. **Refactor & Verify:** Ensure code is clean, robust, and verified.
6. **Update Status:** Update `plan.md` from `[~]` to `[x]`.

## Quality Gates

Before marking any task complete, verify:
- [ ] All tests pass (`pytest`)
- [ ] Code follows project style guidelines
- [ ] Types and schemas are strictly validated
- [ ] Audit log entry is generated for all complaint state transitions
- [ ] Synthetic data adheres to privacy constraints (zero PII)
