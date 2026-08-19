# Google Antigravity Workshop

## Purpose

This repository supports hands-on workshops for using Google Antigravity to carry out structured software and AI-agent development—from requirements discovery and workspace initialization through design, implementation, verification, evaluation, and deployment.

It includes projects built with Google Agent Development Kit (ADK) and examples that integrate Gemini Enterprise with external systems through the Model Context Protocol (MCP).

The repository brings together:

- Requirements and prepared or seedable Antigravity workspaces for application and AI-agent projects.
- Reusable `AGENTS.md` guidance, rules, skills, plugins, and software-development subagents.
- Workshop projects for practicing specification-driven development, implementation, review, testing, and deployment.
- Runnable examples demonstrating MCP integrations and secure, on-behalf-of access to external systems.
- Curated documentation and learning paths for progressing from foundational Antigravity usage to advanced agentic software-engineering workflows.

The repository is intended for learning and experimentation. Its examples demonstrate development patterns and integration concepts and must be reviewed, secured, and hardened before production use.

Developers should read the [AI-Assisted Developer Playbook](docs/agy-common/developer-playbook-greenfield-and-brownfield.md) before beginning a greenfield or brownfield exercise. It provides the recommended Gemini CLI and Antigravity CLI workflow, task-contract templates, approval gates, verification practices, and definitions of done.

## Repository Overview

The repository is organized into five main areas:

| Area | Purpose |
|---|---|
| [`src/agy/agents/`](src/agy/agents/) | Agent-development workshops, requirements, prompts, and prepared Antigravity workspaces. |
| [`src/agy/apps/`](src/agy/apps/) | Greenfield and brownfield application-development workshops. |
| [`src/geap/`](src/geap/) | Runnable Gemini Enterprise, ADK, MCP, authentication, and external-system integration examples. |
| [`src/resources/`](src/resources/) | Reusable `AGENTS.md` guidance, rules, skills, plugins, and software-development subagents for initializing workspaces. |
| [`src/scripts/`](src/scripts/) | Scripts for seeding workspaces and importing supported skills and plugins. |

These areas support three related workshop activities:

1. Define and build applications and AI agents in structured Antigravity workspaces.
2. Practice reusable agentic software-development workflows using rules, skills, plugins, and subagents.
3. Integrate agents with external systems through MCP and secure, identity-aware access patterns.

## Start a Workshop Workspace

The following paths are common starting points, not fixed prescriptions. A workshop can use material from either or both areas:

- Use [`src/agy/apps/`](src/agy/apps/) for greenfield and brownfield application development.
- Use [`src/agy/agents/`](src/agy/agents/) for agent development.

Each project contains its requirements and supporting workshop material. Directories whose names end in `-demo` contain pre-created Antigravity workspaces. Copy the relevant `-demo` directory to a new working directory, open the copy as your workspace, and read its `AGENTS.md` before starting. Keeping the original unchanged makes it easy to repeat the workshop or create a workspace for another participant.

For example, from the repository root:

```bash
cp -R src/agy/apps/<project>/<project>-demo <your-workspace>
```

Alternatively, initialize a new workspace from the repository's reusable resources:

```bash
./src/scripts/seed-workspace.sh <your-workspace>
```

The seed script adds the baseline `AGENTS.md`, rules, skills, and reusable software-development subagents. It does not overwrite existing destination files.

### Install optional development tooling

For agent-development exercises, first follow the official [Google Agents CLI getting-started guide](https://google.github.io/agents-cli/guide/getting-started/). Its recommended setup command installs the CLI and its context-aware skills:

```bash
uvx google-agents-cli setup
```

For specification-driven development, first install the official [Conductor plugin](https://github.com/gemini-cli-extensions/conductor) through Antigravity:

```bash
agy plugins install https://github.com/gemini-cli-extensions/conductor
```

If either standard installation is unavailable, use the repository's import scripts as workspace-local fallbacks. The Conductor importer is also useful when Conductor must be stored locally in the workspace, while the Google Agents CLI importer is useful when only its skills—not the CLI itself—are needed:

```bash
python3 src/scripts/import_conductor_plugin.py <your-workspace>
python3 src/scripts/import_google_agents_cli_skills.py <your-workspace>
```

The import scripts download content from the official upstream repositories and therefore require network access. Use `--dry-run` to download and validate an import without changing the workspace; existing installations are replaced only when `--force` is supplied.

## Recommended Google Antigravity Codelab Learning Path

The following learning path orders the codelabs in the [Google Antigravity catalog](https://codelabs.developers.google.com/?product=antigravity) from foundational topics to more mature application, agent, platform, and enterprise workflows. This is a recommended progression, not a formal prerequisite chain.

> [!NOTE]
> This list was reviewed on August 11, 2026. Google Antigravity and its codelabs evolve independently, so not every codelab may be updated for the latest product behavior, interface, terminology, or tooling. Check each codelab's update date and prerequisites, and validate its instructions against the current [Google Antigravity documentation](https://antigravity.google/docs/home) before using it in the workshop.

### Stage 1: Understand Antigravity

1. [Getting Started with Google Antigravity](https://codelabs.developers.google.com/getting-started-google-antigravity?hl=en)
2. [Building with Google Antigravity](https://codelabs.developers.google.com/building-with-google-antigravity?hl=en)

### Stage 2: Learn its control surfaces

3. [Mastering Slash Commands of Antigravity 2.0: AI-Native Game Solver & Balance Tester](https://codelabs.developers.google.com/codelabs/devsite/codelabs/mastering-slash-commands-antigravity?hl=en)
4. [Authoring Google Antigravity Skills](https://codelabs.developers.google.com/getting-started-with-antigravity-skills?hl=en)
5. [Google Developer Knowledge MCP server in Google Antigravity 2.0, IDE, and/or CLI](https://codelabs.developers.google.com/developer-knowledge-mcp-antigravity?hl=en)
6. [Google Workspace MCP servers in Google Antigravity 2.0, IDE, and/or CLI](https://codelabs.developers.google.com/google-workspace-mcp-antigravity?hl=en)
7. [Command and control: Orchestrate app development with Gemini and MCP](https://codelabs.developers.google.com/gemini-mcp-agy?hl=en)

### Stage 3: Adopt structured development workflows

8. [Getting started with Spec Driven Development in Antigravity](https://codelabs.developers.google.com/codelabs/getting-started-with-spec-driven-development-in-antigravity?hl=en)
9. [Spec-Driven Development with Antigravity CLI: Structured Agent Workflows with Skills and MCP](https://codelabs.developers.google.com/sdd-agy-cli?hl=en)
10. [Plan and Build Apps with Conductor Plugin](https://codelabs.developers.google.com/conductor-plugin?hl=en)
11. [Build Autonomous Developer Pipelines using agents.md and skills.md in Antigravity](https://codelabs.developers.google.com/autonomous-ai-developer-pipelines-antigravity?hl=en)
12. [Design-to-Code with Antigravity and Stitch MCP](https://codelabs.developers.google.com/design-to-code-with-antigravity-stitch?hl=en)

### Stage 4: Build and deploy complete applications

13. [Build a Match 3 Arcade Game With Gemini and Antigravity](https://codelabs.developers.google.com/gemini-match3-golang?hl=en)
14. [Google Pay API: Vibe-code checkout page with MCP servers and Antigravity](https://codelabs.developers.google.com/codelabs/gpay-api-vibe-code-mcp-servers?hl=en)
15. [Deploy Applications from Gemini CLI and Antigravity to Cloud Run using MCP Server](https://codelabs.developers.google.com/deploy-to-cloud-run-using-oss-mcp-server?hl=en)
16. [Build and Deploy to Google Cloud with Antigravity](https://codelabs.developers.google.com/build-and-deploy-gcp-with-antigravity?hl=en)

### Stage 5: Develop production-grade AI agents

17. [Vibecode and Deploy a Frontend for an ADK agent](https://codelabs.developers.google.com/vibecode-frontend-with-antigravity?hl=en)
18. [Vibecode an ADK 2.0 Ambient Agent with Antigravity and Agents CLI](https://codelabs.developers.google.com/vibecode-ambient-expense-agent?hl=en)
19. [Agent-to-Agent Engineering: Build, Deploy, and Embed ADK Agents with Antigravity CLI and agents-cli](https://codelabs.developers.google.com/build-deploy-embed-agy-agents-cli?hl=en)
20. [Spec-Driven ADK Agent Development with Antigravity and Spec-kit](https://codelabs.developers.google.com/sdd-adk-antigravity?hl=en)
21. [Vibecode and Secure an AI Agent Lifecycle with Antigravity and TDD](https://codelabs.developers.google.com/secure-agentic-coding?hl=en)

### Stage 6: Apply advanced engineering and enterprise operations

22. [Build a Multi-Language Code Auditor with Parallel Antigravity Agents](https://codelabs.developers.google.com/multi-language-code-auditor-antigravity?hl=en)
23. [Supercharge Code Quality: AI-Assisted Code Review with Antigravity CLI and SDK](https://codelabs.developers.google.com/agy-cli-sdk-code-review?hl=en)
24. [How to deploy a secure MCP server on Cloud Run](https://codelabs.developers.google.com/codelabs/cloud-run/how-to-deploy-a-secure-mcp-server-on-cloud-run?hl=en)
25. [Analytics with the Data Agent Kit and Antigravity IDE](https://codelabs.developers.google.com/dak-analytics-eng-antigravity-ide?hl=en)
26. [Mastering KCC Operations with Google Antigravity](https://codelabs.developers.google.com/next26/kcc-ops-skill-antigravity?hl=en)
27. [How to Migrate from Firebase Studio to Antigravity](https://codelabs.developers.google.com/antigravity/how-to-migrate-from-firebase-studio-to-antigravity?hl=en)
28. [Automating legacy modernization at scale using agentic pipelines and Antigravity](https://codelabs.developers.google.com/automating-modernization-with-antigravity?hl=en)

Stages 1 through 3 form the recommended core path. After completing them, learners can focus on general application development in Stage 4, ADK and agent engineering in Stage 5, or advanced platform and enterprise scenarios in Stage 6.
