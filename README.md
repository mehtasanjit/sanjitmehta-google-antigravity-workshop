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
| [`src/resources/`](src/resources/) | The shared workspace guidance (`AGENTS.md`, rules, skills) and the eight software-development subagents that setup scripts copy into workspaces. |
| [`src/scripts/`](src/scripts/) | The Conductor importer used by the setup scripts, plus scripts for seeding a workspace and importing Google Agents CLI skills by hand. |

These areas support three related workshop activities:

1. Define and build applications and AI agents in structured Antigravity workspaces.
2. Practice reusable agentic software-development workflows using rules, skills, plugins, and subagents.
3. Integrate agents with external systems through MCP and secure, identity-aware access patterns.

## Start a Workshop Workspace

The following paths are common starting points, not fixed prescriptions. A workshop can use material from either or both areas:

- Use [`src/agy/apps/`](src/agy/apps/) for greenfield and brownfield application development.
- Use [`src/agy/agents/`](src/agy/agents/) for agent development.

### How the application workshops are organised

Every application exercise comes in up to three variants. The variants share the same requirements and differ only in the tooling placed in the workspace, so a workshop can compare how much each layer helps:

| Variant | Folder suffix | What each workspace gets |
|---|---|---|
| Vanilla | *(none)* | `AGENTS.md` and the workspace memory rule |
| Conductor | `-conductor` | The above, plus the [Conductor plugin](https://github.com/gemini-cli-extensions/conductor) for specification-driven development |
| Conductor and Subagents | `-conductor-subagents` | The above, plus the eight SDLC subagents |

All variants copy the same files from [`src/resources/`](src/resources/):

| Workspace file | Source |
|---|---|
| `AGENTS.md` | [`workspace-guidance/agents/base.md`](src/resources/workspace-guidance/agents/base.md) |
| `.agents/rules/workspace-memory.md` | [`workspace-guidance/rules/workspace-memory.md`](src/resources/workspace-guidance/rules/workspace-memory.md) |
| `.agents/agents/` | [`subagents/sdlc-subagents/.agents/agents/`](src/resources/subagents/sdlc-subagents/.agents/agents/) |
| `.agents/plugins/conductor/` | Downloaded from Conductor's `main` branch at setup by [`src/scripts/import_conductor_plugin.py`](src/scripts/import_conductor_plugin.py) |

Editing a file in `src/resources/` changes every workspace created afterwards; existing workspaces keep the copy they were created with. Prompts that rely on Conductor are shipped only in the Conductor variants; vanilla variants give the agent the requirements directly.

### Setup scripts

Each application folder has a `setup-workspace.sh`:

- It creates the next numbered workspace (`<folder>-1`, `<folder>-2`, …) next to the script and never overwrites an existing one. `--dry-run` shows the next name without creating anything. The empty workspaces also accept a name: `./setup-workspace.sh my-project`.
- If setup fails, it removes only the workspace it was creating.
- Generated workspaces are local workshop output. Brownfield folders include a `.gitignore` so their nested Git repositories stay out of this repository.
- Variants with Conductor need Python 3 and network access. To pin Conductor, set `CONDUCTOR_REF` to a commit on its `main` branch; its release tags use an older layout without `plugin.json` and do not work.
- Brownfield workspaces are Git repositories with a clean baseline, so `git diff` shows exactly what the agent changed. Workspace files (`AGENTS.md`, `.agents/`, `.memory/`, `.scratch/`) are excluded through `.git/info/exclude` and never appear in the application diff.

After setup, open the generated directory, not the repository root, as the Antigravity workspace.

**Application workshops — [`src/agy/apps/`](src/agy/apps/)**

| Exercise | Type | Vanilla | Conductor | Conductor and Subagents |
|---|---|---|---|---|
| Lecture Pulse | Greenfield | [lecture-pulse](src/agy/apps/lecture-pulse/) | [lecture-pulse-conductor](src/agy/apps/lecture-pulse-conductor/) | [lecture-pulse-conductor-subagents](src/agy/apps/lecture-pulse-conductor-subagents/) |
| Kanban Board | Greenfield | [kanban-board](src/agy/apps/kanban-board/) | [kanban-board-conductor](src/agy/apps/kanban-board-conductor/) | [kanban-board-conductor-subagents](src/agy/apps/kanban-board-conductor-subagents/) |
| Bank Complaints Workbench | Greenfield, with a brownfield SLA Control Tower follow-up | [bank-complaints-workbench](src/agy/apps/bank-complaints-workbench/) | [bank-complaints-workbench-conductor](src/agy/apps/bank-complaints-workbench-conductor/) | [bank-complaints-workbench-conductor-subagents](src/agy/apps/bank-complaints-workbench-conductor-subagents/) |
| Empty Workspace | Any project; bring your own brief | [empty-workspace](src/agy/apps/empty-workspace/) | [empty-workspace-conductor](src/agy/apps/empty-workspace-conductor/) | [empty-workspace-conductor-subagents](src/agy/apps/empty-workspace-conductor-subagents/) |
| Kanban Board brownfield demo | Brownfield: copy of a working FastAPI + SQLite + React app; add story points in 12–15 minutes | [kanban-board-brownfield](src/agy/apps/kanban-board-brownfield/) | [kanban-board-brownfield-conductor](src/agy/apps/kanban-board-brownfield-conductor/) | [kanban-board-brownfield-conductor-subagents](src/agy/apps/kanban-board-brownfield-conductor-subagents/) |
| Bank of Anthos | Brownfield: pinned clone of the [Bank of Anthos fork](https://github.com/mehtasanjit/bank-of-anthos); add transaction search and CSV export | [bank-of-anthos](src/agy/apps/bank-of-anthos/) | [bank-of-anthos-conductor](src/agy/apps/bank-of-anthos-conductor/) | [bank-of-anthos-conductor-subagents](src/agy/apps/bank-of-anthos-conductor-subagents/) |

[Kanban Board — Straitjacket](src/agy/apps/kanban-board-straitjacket/) is a separate greenfield exercise for Claude Code and Codex under the Straitjacket (`ctx`) context-containment harness. It has no setup script; start from its requirements.

Follow the selected folder's README for prerequisites and the step-by-step exercise.

**Agent workshops — [`src/agy/agents/`](src/agy/agents/)**

| Workshop | Starting point |
|---|---|
| [ChemLab Research and Preparation Assistant](src/agy/agents/chem-lab-research-and-prep/) | Agent requirements and prompts, with a prepared Antigravity workspace for ADK agent development |
| [External Campus Academic Assistant](src/agy/agents/external-campus-academic-assistant/) | Agent requirements and prompts, with a prepared Antigravity workspace for ADK agent development |

Agent workshops have no project README: start from the requirements and prompts in their `docs/` directory, then open the prepared `*-work/` directory as the workspace and read its `AGENTS.md`.

To initialize a workspace by hand instead, the seed script copies the full guidance set: `AGENTS.md`, both rules (memory and environment initialization), both guidance skills, and the eight subagents. The application setup scripts do not use it; they copy only the files listed above. It does not overwrite existing destination files.

```bash
./src/scripts/seed-workspace.sh <your-workspace>
```

### Install optional development tooling

For agent-development exercises, first follow the official [Google Agents CLI getting-started guide](https://google.github.io/agents-cli/guide/getting-started/). Its recommended setup command installs the CLI and its context-aware skills:

```bash
uvx google-agents-cli setup
```

For specification-driven development, first install the official [Conductor plugin](https://github.com/gemini-cli-extensions/conductor) through Antigravity:

```bash
agy plugins install https://github.com/gemini-cli-extensions/conductor
```

If either standard installation is unavailable, use the repository's import scripts as workspace-local fallbacks. The Conductor importer is also useful when Conductor must be stored locally in the workspace, while the Google Agents CLI importer is useful when only its skills—not the CLI itself—are needed.

Set `PYTHON` to the explicit Python 3 interpreter you want to use, such as the binary in your project's virtual environment, then run:

```bash
PYTHON=/path/to/your/.venv/bin/python
"$PYTHON" src/scripts/import_conductor_plugin.py <your-workspace>
"$PYTHON" src/scripts/import_google_agents_cli_skills.py <your-workspace>
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
