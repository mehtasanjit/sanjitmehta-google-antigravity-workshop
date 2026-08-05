• # Agent Guidelines

  ## Communication

  - Before starting work, briefly confirm your understanding and intended scope.
  - Ask concise questions when requirements or decisions are unclear.
  - Keep communication concise, direct, and easy to scan.
  - Do not invent requirements, assumptions, or architectural decisions.

  ## Software Development Lifecycle

  - Follow this sequence: requirements, design, implementation, verification, documentation, and handoff.
  - Confirm the requirements before proposing a design.
  - Confirm significant design decisions before implementation.
  - Implement only the changes explicitly requested.
  - Verify completed work and report exactly what was checked.
  - Clearly identify anything incomplete, blocked, or unverified.

  ## Agent Development

  - For any agent-development work—including design, implementation, modification, evaluation, deployment, or troubleshooting—*YOU MUST ALWAYS* identify, consult,
  and actively apply the relevant Google Agents CLI skills.
  - This requirement applies whether the work is initiated directly in AGY or through a specification-driven framework such as Conductor, Spec Kit, or a similar
  workflow.
  - Specification-driven frameworks may manage the overall development lifecycle, but they do not replace the agent-specific guidance provided by the Google Agents
  CLI skills.
  - Approved requirements and specifications remain authoritative. Apply the Agents CLI skills within that scope without introducing additional requirements.
  - Owing to environment restrictions, `agents-cli` may not always be installed.
  - You should not invoke `uvx agents-cli`. Perform the required implementation within the scope of the user-specified Python environment, while using the relevant
  Google Agents CLI skills as guidance.

  ## Python Environment Management

  - *YOU MUST ALWAYS* ask the user for the explicit path to their local Python virtual environment before running Python commands, scripts, or package installations.
  - *YOU MUST NEVER* assume the virtual environment location or run Python commands against the system environment.
  - Once provided, reuse the identified virtual environment path for the remainder of the session.

  ## Authentication and Google Cloud Configuration

  - *YOU MUST NEVER* use, generate, request, or recommend an API key for model authentication.
  - *YOU MUST ALWAYS* use Google Cloud Vertex AI with Application Default Credentials (ADC).
  - Before configuring or running agent models, ask the user for the required Google Cloud configuration, including:
    - `GOOGLE_CLOUD_PROJECT`
    - `GOOGLE_CLOUD_LOCATION`
    - `GOOGLE_GENAI_USE_ENTERPRISE=True`

  ## Scope Discipline

  - *YOU MUST STRICTLY* implement only what the user explicitly requests.
  - *YOU MUST NOT* over-engineer, add speculative features, introduce unnecessary abstractions, or otherwise expand the task scope.
  - Confirm with the user before adding dependencies or making a significant architectural decision.

  ## Testing and Verification

  - *YOU MUST ONLY* write or run tests when explicitly instructed by the user.
  - When testing is requested, report exactly which checks were performed and their results.
  - Do not claim that unexecuted tests or unverified behavior passed.

  ## Working Practices

  - Read relevant documentation and inspect existing work before making changes.
  - Preserve unrelated files and existing user changes.
  - Never expose secrets, credentials, or private data.
  - Do not perform destructive or externally visible actions without explicit approval.
  - Do not commit or push changes unless explicitly requested.
  - Treat this file as living guidance and update it when repository commands, conventions, or boundaries are established.

