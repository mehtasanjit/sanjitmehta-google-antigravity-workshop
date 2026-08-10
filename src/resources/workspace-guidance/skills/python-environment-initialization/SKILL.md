---
name: python-environment-initialization
description: >
  Establishes or reuses a safe project-specific Python environment and selects
  the appropriate Python package-management workflow. Use before executing
  Python commands, creating or changing a virtual environment, installing
  Python dependencies, or choosing between uv, Poetry, Pipenv, pip, uvx, and
  pipx.
---

# Python Environment Initialization

## Workflow

### 1. Inspect the Python project configuration

1. Read the `AGENTS.md` file governing the current project.
2. If `.agents/rules/workspace-environment-initialization.md` exists, confirm that its workspace-discovery and toolchain-identification steps have been completed.
3. Inspect relevant files such as `pyproject.toml`, `uv.lock`, `poetry.lock`, `Pipfile`, `Pipfile.lock`, `requirements*.txt`, and `.python-version`.
4. Determine the required Python version and the project's established environment and package-management method when declared.
5. Do not execute Python, create an environment, or run a package manager during this step.

### 2. Resolve the virtual environment

1. Ask the user for the explicit path to the Python virtual environment.
2. Do not execute Python until the user confirms the environment path.
3. With the user's authorization, inspect the confirmed environment using its exact interpreter path.
4. Reuse the environment only when it belongs to the current project, uses a compatible Python version, and is suitable for the established dependency workflow.
5. Do not reuse a global environment or an environment shared by unrelated projects.
6. If no suitable environment exists, propose creating a project-local environment and obtain explicit approval before creating it.
7. Do not assume that a directory named `.venv` is the correct environment without user confirmation.
8. Never use the system Python or install project packages globally.

### 3. Select the package-management method

Follow explicit project instructions first. Otherwise, use the existing project files as the authority:

1. Use `uv` when the project contains `uv.lock` or is configured for uv.
2. Use Poetry when the project contains `poetry.lock`.
3. Use Pipenv when the project contains `Pipfile.lock`.
4. Use `pip` through the approved virtual environment for a requirements-based project.
5. For a new Python project with no established toolchain, recommend `uv` and obtain approval before establishing it.

Do not introduce a second package manager, create a competing lock file, or replace the established dependency workflow without explicit approval.

### 4. Handle standalone Python tools

- Use `uv tool` for an approved persistent uv-managed CLI installation.
- Use `uvx` only for approved temporary CLI execution.
- Use `pipx` when it is the established or approved standalone-tool manager.
- Do not use `uv tool`, `uvx`, or `pipx` for project runtime dependencies.
- Do not install standalone tools until the user approves the installation or temporary execution.

### 5. Obtain approval for changes

Before changing the Python environment:

1. Explain whether the environment will be reused or created.
2. Identify packages, tools, configuration files, and lock files that would be created or modified.
3. Explain any required installation or download.
4. Obtain explicit approval before creating the environment or installing packages or tools.

### 6. Configure the environment

After approval:

1. Use only the approved environment and package manager.
2. Use the exact interpreter from the approved environment for direct Python execution.
3. Install only dependencies required by the approved task.
4. Preserve existing dependency versions unless a change is necessary for the task.
5. Keep the established lock file synchronized with intentional dependency changes.
6. Do not mix environments or package managers.

### 7. Verify and report

Report:

- Python version.
- Approved interpreter and environment path.
- Whether the environment was reused or created.
- Selected package manager.
- Dependency or tool changes performed.
- Missing, incompatible, or unverified components.

Do not expose credentials, secret values, or the complete process environment.

## Stop Conditions

Stop and ask the user before proceeding when:

- The user has not confirmed the virtual-environment path.
- Python version or toolchain requirements conflict.
- The confirmed environment is incompatible or belongs to another project.
- Environment creation, installation, download, or lock-file changes have not been approved.
- Continuing would require a global or system-level installation.
