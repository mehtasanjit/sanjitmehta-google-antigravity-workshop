---
name: python-environment-initialization
description: >
  Establish or reuse a safe project-specific Python environment while preserving
  the project's established runtime, environment manager, and dependency
  workflow. Use before executing project Python commands, creating or changing
  a Python environment, installing or synchronizing Python dependencies, or
  installing or temporarily running standalone Python tools.
---

# Python Environment Initialization

## Workflow

### 1. Inspect the Python project

1. Inspect the relevant Python configuration, dependency, lock, and version files. These may include `pyproject.toml`, manager-specific lock files, `Pipfile`, `requirements*.txt`, `.python-version`, and other project-declared runtime files.
2. Determine the required Python version and the established environment and dependency workflow when declared.
3. Treat applicable instructions and unambiguous project configuration as authoritative.
4. Do not execute Python, run a package manager, create an environment, install dependencies, or modify files during this step.

If runtime, environment, or dependency indicators conflict, stop and ask the user which configuration is authoritative.

### 2. Discover the Python environment

1. Ask whether the user wants to provide the environment path or authorize automated, read-only discovery.
2. If the user provides a path, record it without running discovery commands.
3. If the user authorizes discovery, inspect project configuration, known environment locations, and non-mutating environment-manager information.
4. Do not use commands that can create, synchronize, update, or remove an environment or lock file during discovery.
5. Identify the exact interpreter path and determine whether the environment is associated with the current project.
6. Reuse an environment only when it is project-specific, compatible with the required Python version, and suitable for the established dependency workflow.
7. Do not reuse system Python, a global environment, or an environment shared by unrelated projects as the project environment.
8. Do not assume `.venv` is correct solely because the directory exists.

If compatibility or project association cannot be established from files alone, obtain authorization before running a non-mutating check with the exact interpreter or established manager.

If no suitable environment exists, propose an environment using the established manager and its configured location. For a new unmanaged project, prefer `<workspace-root>/.venv`. Obtain approval before creating it.

You may inspect a base Python interpreter or use it to create an approved isolated environment. You must never install project dependencies into the system or global Python environment.

### 3. Select the dependency workflow

Follow this precedence:

1. Follow explicit project instructions.
2. Preserve an established dependency or environment manager, including one not listed in this skill.
3. Use `uv` when `uv.lock`, uv configuration, or project instructions establish uv.
4. Use Poetry when `poetry.lock`, Poetry dependency configuration, or project instructions establish Poetry.
5. Use Pipenv when `Pipfile`, `Pipfile.lock`, or project instructions establish Pipenv.
6. Use the resolved environment's interpreter with `-m pip` for a requirements-based project only when no higher-level manager is established.
7. For a new project with no established dependency workflow, recommend `uv` and obtain approval before establishing it.

Do not infer pip usage from a requirements file when another manager is established. Do not introduce a second manager, create a competing lock file, or replace the established workflow without explicit approval.

If multiple managers appear authoritative or the established manager is unclear, stop and ask the user.

### 4. Handle standalone Python tools

- Use `uv tool` for an approved persistent uv-managed CLI installation.
- Use `uvx` only for approved temporary CLI execution.
- Use `pipx` when it is the established or approved standalone-tool manager.
- Preserve another established standalone-tool manager when present.
- Do not use standalone-tool managers for project runtime dependencies.
- Treat temporary execution as running downloaded code and obtain approval first.

### 5. Obtain approval for changes

Before changing the Python environment:

1. State the selected environment, interpreter, environment manager, and dependency manager.
2. Explain whether the environment will be reused, created, or synchronized.
3. Identify the commands to be run and the packages, tools, configuration files, and lock files that may change.
4. Identify any required installation, download, or network access.
5. Obtain explicit approval for environment creation, synchronization, installation, temporary tool execution, and dependency or lock-file changes.

Reuse an explicit approval already obtained for the same action and scope. Do not ask for duplicate approval. Obtain new approval when the action or expected changes expand.

### 6. Configure and use the environment

After resolving the environment and obtaining any required approvals:

1. Use only the resolved environment and established manager.
2. Prefer the established manager's native execution command. Use the exact resolved interpreter for direct Python execution.
3. For a requirements-based pip workflow, invoke pip as `<resolved-python> -m pip`.
4. Do not depend on shell activation when a manager command or exact executable path is available.
5. Treat commands that automatically create or synchronize an environment as environment changes, even when their primary purpose is command execution.
6. Use locked or frozen behavior when supported and no dependency change is intended.
7. Install only dependencies required by the approved task.
8. Preserve existing versions unless a change is required and approved.
9. Update dependency declarations and lock files only for intentional, approved dependency changes.
10. Do not bypass the established manager or mix environments and managers.

### 7. Verify and report

Verify, using the resolved environment:

1. The exact interpreter path and Python version.
2. Compatibility with the project's declared Python requirement.
3. Association between the environment, manager, and current project.
4. Availability of the dependencies or tools required by the task.
5. That no unapproved configuration, dependency, or lock-file changes occurred.

Report:

- Python version and exact interpreter path.
- Environment path and whether it was reused, created, or synchronized.
- Selected environment and dependency managers.
- Dependency, tool, configuration, and lock-file changes performed.
- Missing, incompatible, or unverified components.

Do not expose credentials, secret values, private index URLs, or the complete process environment.

## Stop Conditions

Stop and ask the user before proceeding when:

- The user has neither provided an environment path nor authorized discovery.
- Runtime, environment, dependency, or lock-file indicators conflict.
- No compatible Python interpreter is available.
- The environment is ambiguous, incompatible, global, or associated with another project.
- The established manager is unavailable and using another manager would change the workflow.
- A required environment change, installation, download, temporary execution, or lock-file update is not approved.
- Continuing would require installing project dependencies globally or modifying the system Python environment.
