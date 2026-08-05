# Agent Guidelines

## Communication

- Before starting work, briefly confirm your understanding and intended scope with the user.
- Ask concise questions when requirements or decisions are unclear.
- Keep responses concise, direct, and easy to scan.
- Do not invent requirements, assumptions, or architectural decisions.

## Software Development Lifecycle

- Follow the sequence: requirements, design, implementation, verification, documentation, and handoff.
- Confirm requirements before proposing a design.
- Confirm significant design decisions before implementation.
- Make only the changes explicitly requested.
- Verify completed work and report what was actually checked.
- Clearly state anything incomplete or unverified.

## Working Practices

- Read relevant documentation and inspect existing work before making changes.
- Confirm before adding dependencies or expanding scope.
- Preserve unrelated files and existing user changes.
- Never expose secrets, credentials, or private data.
- Do not perform destructive or external actions without explicit approval.
- Do not commit or push unless explicitly requested.
- Treat this file as living guidance and update it when repository commands, conventions, or boundaries are established.

## Python Environment Management
- *YOU MUST ALWAYS* ask the user for the explicit path to their local Python virtual environment before running any Python commands, scripts, or package installations.
- *YOU MUST NEVER* assume the location of the virtual environment or execute system-wide Python commands.
- *YOU MUST* remember and reuse the identified virtual environment path across the entire session once provided.

## Authentication & Google Cloud Configuration
- *YOU MUST NEVER* use, generate, or prompt for an API KEY for model authentication.
- *YOU MUST ALWAYS* use Google Cloud Vertex AI / Application Default Credentials (ADC) for authentication.
- *YOU MUST* ask the user for their Google Cloud Project ID (`GOOGLE_CLOUD_PROJECT`), Location/Region (`GOOGLE_CLOUD_LOCATION`), and related cloud configuration details, i.e. GOOGLE_GENAI_USE_ENTERPRISE as True before running or configuring agent models.

## Google Agents CLI Skills & Robust Code
- IFF you are building agents using ADK 2.0, *YOU MUST ALWAYS* consult and adhere to the relevant Google Agents CLI skills before generating or modifying agent code to ensure robust, standard ADK patterns.
- Owing to environment restrictions, agents-cli MAY NOT always be installed.
- *Therefore, YOU MUST NOT* invoke `uvx agents-cli`; always operate within the user-specified Python environment.

## Strict Requirement Adherence (Do Not Overdo)
- *YOU MUST STRICTLY* implement only what is explicitly requested by the user.
- *YOU MUST NOT* over-engineer, add speculative features, introduce unrequested abstractions, or expand the scope of any task ("DON'T OVERDO").

## Testing & Verification Policy
- *YOU MUST NOT* generate or execute automated unit/integration tests by default, as the user validates agent behavior interactively using the `adk web` command.
- *YOU MUST ONLY* write or run tests when explicitly instructed by the user.
