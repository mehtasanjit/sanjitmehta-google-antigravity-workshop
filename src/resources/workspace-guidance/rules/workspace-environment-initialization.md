# Workspace Environment Initialization Rule

## Rule Metadata

- **Summary:** Establish the workspace execution environment, runtime, and dependency tooling before toolchain-dependent execution or environment changes.
- **Activation Mode:** Model Decision

## Applicability

You must complete the relevant parts of this workflow before executing project code; running builds, tests, linters, formatters, or other commands that depend on the project toolchain; creating or changing a project environment; installing or synchronizing dependencies; or invoking a runtime, environment manager, or package manager.

This rule does not apply to file or documentation inspection, non-mutating version-control inspection, or other non-mutating workspace operations that do not depend on the project runtime or toolchain.

You must repeat the relevant steps when the workspace, project, runtime, or execution environment changes.

## Workflow

### Step 1: Inspect the workspace

1. Determine the project or workspace in scope.
2. Read all applicable `AGENTS.md` files.
3. Inspect relevant project configuration, runtime, dependency, and lock files.
4. Do not run package managers, installation commands, or project executables during this step.

### Step 2: Discover the execution environment

Use environment details already provided by the user or platform-provided environment context. If a required detail remains unknown, ask whether the user wants to provide it or authorize automated, read-only discovery.

Determine only:

1. Operating system.
2. Active shell.
3. Workspace root.
4. Current working directory.

If the user provides the details, record them without running discovery commands. If the user authorizes automated discovery, use non-mutating checks appropriate for the host. Reuse that authorization for the same discovery scope; ask again only when the scope expands.

If additional environment details required for the current task remain unknown, ask the user or, with their authorization, determine them using appropriate non-mutating checks.

### Step 3: Identify the established runtime and dependency tooling

1. Treat existing project instructions, configuration, and lock files as authoritative.
2. When applicable, identify the runtime, environment manager, and package manager established by the project and required by the current task.
3. You must not introduce a different package manager into an established project unless the change was explicitly requested or approved.
4. You must not create competing dependency or lock files.
5. If authoritative runtime or dependency-tooling indicators conflict and applicable instructions do not resolve the conflict, you must stop and ask the user which configuration is authoritative.

### Step 4: Apply the relevant environment and toolchain skills

1. Identify every language runtime, environment manager, package manager, service platform, and toolchain required by the task.
2. Use the available skills identified by the base workspace workflow, including workspace-local skills and installed or bundled skills exposed by the agent host.
3. Match each skill's name, description, and exposed applicability guidance to the user request, project configuration, and required toolchains.
4. Apply every matching skill for the part of the task it governs. You must not select only one skill when multiple skills apply.
5. If the task requires Python, you must apply the `python-environment-initialization` skill before executing Python, creating or changing a virtual environment, or installing Python packages or tools.
6. Each applicable skill governs the toolchain-specific work described by its instructions. You must not repeat equivalent generic steps in this rule. Reuse its findings and approvals for the same action and scope, and include its required report in the consolidated report in Step 8 instead of reporting it separately.
7. If applicable skills overlap, limit each skill to the work it governs. If their instructions conflict and the applicable instruction hierarchy does not resolve the conflict, stop and ask the user.
8. If the task or applicable instructions require a specific environment or toolchain skill and that skill is unavailable, explain the limitation and ask the user how to proceed.

A host-provided tool or integration is not a skill unless the host exposes skill instructions for it. Identify such capabilities as task-required tools in Step 5 and apply any separate matching skill when available.

### Step 5: Check task-required tools

1. Identify only the tools and host-provided integrations required for the current task that are not already governed by applicable environment or toolchain skills.
2. Use availability information already provided by the user or established by applicable skills. For any required check that remains, reuse existing read-only discovery authorization when it covers the check; otherwise ask the user for authorization.
3. Check tool versions only when compatibility matters.
4. Report required tools that are missing or incompatible before proceeding.

### Step 6: Obtain approval for environment changes

Before making an environment change that is not already governed by applicable environment or toolchain skills:

1. Explain what environment, packages, tools, or files would be created or modified.
2. Identify any installation or download that is required.
3. Explain any intended dependency or lock-file changes.
4. Obtain explicit approval before creating an environment or installing packages or tools unless the same action and scope were explicitly requested or already approved.
5. You must not perform global or system-level installation without explicit approval.

You must reuse an explicit request or approval for the same action and scope. You must not ask for duplicate approval. Obtain new approval when the action or expected changes expand.

### Step 7: Configure and use the environment

After resolving the environment and obtaining any required approval, configure only the parts not already governed by applicable environment or toolchain skills:

1. Use only the resolved or approved environment and package manager.
2. Install only dependencies required by the requested or approved task.
3. Preserve existing dependency versions unless a change is necessary and approved.
4. Keep the established lock file synchronized with approved, intentional dependency changes.
5. You must not mix environment or package managers.

### Step 8: Verify and report

Verify the applicable results that are not already governed by environment or toolchain skills:

1. The selected runtime, environment, and package manager match the established project configuration.
2. The tools required by the task are available and compatible when compatibility matters.
3. Environment, dependency, configuration, and lock-file changes remain within the requested or approved scope.

Before proceeding with toolchain-dependent work, provide one consolidated report containing only the applicable items:

- Operating system and active shell.
- Workspace root and current working directory.
- Runtime and version when applicable.
- Resolved environment path when applicable.
- Selected environment and package managers when applicable.
- Required tools that are available, missing, incompatible, or unverified.
- Environment changes performed.
- Remaining environment limitations.

You must not expose credentials, secret values, or the complete process environment in this report.

## Stop Conditions

You must stop and ask the user before proceeding when:

- The task or applicable instructions require a specific environment or toolchain skill that is unavailable.
- Authoritative project instructions, runtime files, or dependency files conflict and the applicable instructions do not resolve the conflict.
- The available runtime is incompatible with the project.
- A required tool is missing or incompatible and no requested or approved alternative is available.
- Required environment creation, installation, or download was not explicitly requested or approved.
- A required action needs unavailable permissions.
- Continuing would require an unapproved global or system-level change.
