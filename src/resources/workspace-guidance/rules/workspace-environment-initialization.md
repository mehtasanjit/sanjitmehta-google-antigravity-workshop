# Workspace Environment Initialization Rule

## Rule Metadata

- **Summary:** Establish the workspace execution environment, runtime, and dependency tooling before running project commands or changing the environment.
- **Activation Mode:** Model Decision

## Applicability

You must complete this workflow before running project commands, creating or changing a project environment, installing dependencies, or invoking development tools.

You must repeat the relevant steps when the workspace, project, runtime, or execution environment changes.

## Workflow

### Step 1: Inspect the workspace

1. Determine the project or workspace in scope.
2. Read all applicable `AGENTS.md` files.
3. Inspect relevant project configuration, runtime, dependency, and lock files.
4. Do not run package managers, installation commands, or project executables during this step.

### Step 2: Discover the execution environment

Ask the user whether they want to provide the environment details or authorize automated, read-only discovery.

Determine only:

1. Operating system.
2. Active shell.
3. Workspace root.
4. Current working directory.

If the user provides the details, record them without running discovery commands. If the user authorizes automated discovery, use non-mutating checks appropriate for the host.

If additional environment details required for the current task remain unknown, ask the user or, with their authorization, determine them using appropriate non-mutating checks.

### Step 3: Identify the established runtime and dependency tooling

1. Treat existing project instructions, configuration, and lock files as authoritative.
2. Identify the runtime, environment manager, and package manager already used by the project.
3. You must not introduce a different package manager into an established project without explicit approval.
4. You must not create competing dependency or lock files.
5. If the project contains conflicting runtime or dependency-tooling indicators, you must stop and ask the user which configuration is authoritative.

### Step 4: Apply the relevant environment skill

1. Determine whether the task requires a language-specific runtime or package manager.
2. Inspect `.agents/skills/` for an applicable environment-initialization skill.
3. If the task requires Python, you must apply the `python-environment-initialization` skill before executing Python, creating or changing a virtual environment, or installing Python packages or tools.
4. If a required environment skill is unavailable, explain the limitation and ask the user how to proceed.

### Step 5: Check task-required tools

1. Identify only the tools required for the current task.
2. With the user's authorization, use non-mutating checks to determine whether those tools are available.
3. Check tool versions only when compatibility matters.
4. Report required tools that are missing or incompatible before proceeding.

### Step 6: Obtain approval for environment changes

Before changing the environment:

1. Explain what environment, packages, tools, or files would be created or modified.
2. Identify any installation or download that is required.
3. Explain any intended dependency or lock-file changes.
4. Obtain explicit approval before creating an environment or installing packages or tools.
5. You must not perform global or system-level installation without explicit approval.

### Step 7: Configure and use the environment

After approval:

1. Use only the approved environment and package manager.
2. Install only dependencies required by the approved task.
3. Preserve existing dependency versions unless a change is necessary for the task.
4. Keep the established lock file synchronized with intentional dependency changes.
5. You must not mix environment or package managers.

### Step 8: Verify and report

Before beginning implementation, report:

- Operating system and active shell.
- Workspace root and current working directory.
- Runtime and version when applicable.
- Approved environment path when applicable.
- Selected package manager.
- Required tools that are available, missing, incompatible, or unverified.
- Environment changes performed.
- Remaining environment limitations.

You must not expose credentials, secret values, or the complete process environment in this report.

## Stop Conditions

You must stop and ask the user before proceeding when:

- A required language-specific environment skill is unavailable.
- Existing project instructions, runtime files, or dependency files conflict.
- The available runtime is incompatible with the project.
- Environment creation, installation, or download has not been approved.
- A required action needs unavailable permissions.
- Continuing would require an unapproved global or system-level change.
