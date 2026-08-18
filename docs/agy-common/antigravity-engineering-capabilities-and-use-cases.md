# Antigravity Engineering Capabilities and Use Cases

> **Status:** Draft v0.1
>
> **Reviewed:** August 18, 2026
>
> **Purpose:** Bridge the Antigravity product pitch to concrete software-engineering, agent-engineering, and platform-engineering tasks and demonstrations.

## Why this guide exists

A product overview explains what Google Antigravity is. A demonstration shows one outcome. Engineering teams still need a bridge between the two:

- Which engineering jobs are suitable for Antigravity?
- How should Antigravity be used for each kind of work?
- When should a developer pair with an agent, delegate work, orchestrate specialists, or automate a workflow?
- What context, tools, permissions, approvals, and verification are required?
- Which codelabs and workshop demonstrations provide relevant examples?

This guide organizes Antigravity around engineering work rather than around product features or a flat list of codelabs.

## Executive summary

Antigravity is an agentic engineering environment for planning, executing, and verifying bounded tasks across code, terminal commands, browsers, web research, and connected tools. Its value is not limited to generating new applications. It can support work across the engineering lifecycle:

1. Discover and understand a problem or codebase.
2. Clarify requirements and produce specifications.
3. Design applications, agents, data flows, and cloud architectures.
4. Build new applications and services.
5. Add features and correct defects in existing systems.
6. Test, review, secure, and modernize code.
7. Deploy and operate applications and agents.
8. Build repeatable engineering workflows with skills, subagents, the CLI, and the SDK.

The recommended operating model is governed delegation:

```text
Intent
  → Context and constraints
  → Specification
  → Plan and human approval
  → Execution
  → Automated verification
  → Evidence and review
```

Antigravity accelerates engineering work, but it does not remove accountability. Teams remain responsible for requirements, architecture, security, data handling, approval of consequential actions, verification, and production readiness.

## Antigravity surfaces

Antigravity provides several surfaces over a shared agent harness. Select the surface based on the nature of the work rather than personal preference alone.

| Surface | Best suited to | Typical examples |
|---|---|---|
| **Antigravity 2.0** | Managing multiple tasks or projects and orchestrating asynchronous work | Parallel investigations, scheduled maintenance, multi-project delivery |
| **Antigravity IDE** | Hands-on development with direct code and diff review | Feature development, debugging, refactoring, browser verification |
| **Antigravity CLI** | Terminal-oriented, remote, or headless work | Repository analysis, scripted delivery, server-side workflows |
| **Antigravity SDK** | Custom and repeatable automated engineering workflows | CI review agents, internal engineering automation, scheduled pipelines |

See the [Antigravity overview](https://antigravity.google/docs/overview) and [guide to choosing an Antigravity surface](https://cloud.google.com/blog/topics/developers-practitioners/choosing-your-surface-antigravity-20-antigravity-cli-antigravity-ide-or-antigravity-sdk).

## Four engagement modes

### 1. Pair

The developer works interactively with the agent and remains closely involved in each step.

Use this mode for:

- codebase questions;
- debugging and incident investigation;
- small feature changes;
- focused refactoring;
- test creation;
- reviewing a diff; and
- learning an unfamiliar technology.

Expected human involvement is high. The developer guides the work, reviews edits, and validates the result.

### 2. Delegate

The developer gives the agent a bounded outcome, relevant constraints, and an approval path. The agent plans and executes the task, then returns evidence.

Use this mode for:

- implementing an approved feature;
- building a service or user interface;
- creating an integration;
- generating infrastructure as code;
- adding automated tests; and
- preparing documentation or migration plans.

The task should have clear acceptance criteria and executable verification.

### 3. Orchestrate

A coordinating agent divides work among specialized agents or subagents.

Use this mode for:

- auditing multiple services or languages;
- parallel frontend, backend, test, and security work;
- repository-wide modernization;
- coordinated research and implementation; and
- delivery pipelines with specialist review stages.

Work packages need explicit ownership, input and output contracts, merge boundaries, and approval gates.

### 4. Automate

A repeatable workflow runs through the CLI, SDK, CI, or a schedule.

Use this mode for:

- pull-request review;
- dependency and policy checks;
- scheduled code-health analysis;
- release-readiness reporting;
- documentation maintenance; and
- repeatable scaffolding or delivery workflows.

Automation should start with low-risk, read-only tasks. Write access and external side effects should be introduced only with explicit controls and recovery procedures.

## Control and extension mechanisms

| Mechanism | Purpose | Example |
|---|---|---|
| **Project/workspace context** | Defines the files and environment available to the agent | Frontend and backend folders in one project |
| **`AGENTS.md`** | Establishes standing engineering instructions and boundaries | Required lifecycle, testing policy, deployment restrictions |
| **Rules** | Applies persistent or task-specific constraints | Environment initialization, security checks, memory handling |
| **Skills** | Packages specialized knowledge and reusable procedures | ADK development, code review, Cloud Run deployment |
| **Workflows and plugins** | Provides repeatable multi-stage processes | Conductor specification, implementation, and review tracks |
| **MCP servers** | Connects approved external tools and systems | Documentation, cloud services, databases, design systems |
| **Subagents** | Delegates bounded specialist work | Requirements analyst, test engineer, security reviewer |
| **Artifacts** | Makes plans and results reviewable | Implementation plan, task list, diff, screenshot, walkthrough |
| **Permissions and approvals** | Limits files, commands, tools, and side effects | Read-only analysis, command approval, deployment approval |

These mechanisms should be composed deliberately. More tools and more autonomy do not automatically produce a better outcome.

## Software-engineering use cases

### Discover and understand

Examples:

- map a repository and identify services, languages, dependencies, and entry points;
- explain an unfamiliar component or request path;
- identify where a proposed change would have impact;
- compare implementation behavior with documentation;
- research an API or framework using authoritative documentation; and
- produce an architecture or dependency summary.

Recommended mode: **Pair** for interactive exploration or **Delegate** for a bounded assessment.

Human gate: confirm the discovered system boundaries before using the analysis for design or implementation.

Evidence: repository map, referenced file list, architecture diagram, risk and unknowns list.

### Requirements and specification

Examples:

- turn a product idea into testable requirements;
- identify missing business rules and edge cases;
- define personas and workflows;
- produce acceptance criteria;
- distinguish initial scope from future scope; and
- convert an approved requirement into an implementation-ready specification.

Recommended mode: **Pair**, because product decisions require human input.

Human gate: approve requirements, scope, and unresolved decisions before design or implementation.

Evidence: requirements document, specification, acceptance criteria, decision log.

### Architecture and design

Examples:

- propose application or service architecture;
- define APIs, schemas, state transitions, and error behavior;
- compare implementation alternatives;
- plan a cloud or event-driven architecture;
- design identity and authorization boundaries; and
- turn visual designs into implementation plans.

Recommended mode: **Pair** followed by **Delegate** after significant decisions are approved.

Human gate: approve public interfaces, security boundaries, dependencies, and material trade-offs.

Evidence: architecture diagram, interface definitions, data model, decision record, implementation plan.

### Greenfield application development

Examples:

- scaffold a web application or API;
- build frontend and backend components;
- create database schemas and seed data;
- generate UI assets;
- implement tests and local run instructions; and
- verify behavior in a browser.

Recommended mode: **Delegate** for a small bounded application or **Orchestrate** for separable frontend, backend, and verification tasks.

Human gate: approve the specification and design before broad implementation.

Evidence: working application, tests, screenshots, walkthrough, requirements traceability.

### Brownfield feature development

Examples:

- add a business workflow to an existing application;
- modify validation or authorization rules;
- add an API endpoint without breaking existing clients;
- extend an existing database model;
- introduce a new user role; and
- correct a defect with a regression test.

Recommended mode: **Pair** during discovery, then **Delegate** for the approved change.

Human gate: approve the impact assessment, compatibility rules, and migration approach.

Evidence: baseline verification, impact plan, focused diff, new tests, full regression results.

### UI and design-to-code

Examples:

- turn a design system or prototype into code;
- extract design tokens through MCP;
- create accessible components;
- compare implementation with a visual source of truth; and
- iterate using browser screenshots.

Recommended mode: **Delegate** with browser-based review.

Human gate: approve design fidelity, accessibility, and responsive behavior.

Evidence: screenshots, browser recording, component inventory, accessibility results.

### Testing and debugging

Examples:

- reproduce a defect;
- generate unit, integration, and regression tests;
- create mocks and fixtures;
- analyze runtime or compiler errors;
- run browser-based end-to-end checks; and
- verify that a remediation did not introduce regressions.

Recommended mode: **Pair** for ambiguous failures or **Delegate** for a reproducible defect.

Human gate: confirm that tests represent intended behavior rather than merely current behavior.

Evidence: reproduction steps, failing test, root-cause analysis, passing regression suite.

### Code review and security

Examples:

- review a feature-branch diff;
- find correctness, maintainability, and security issues;
- perform threat modeling;
- apply secure-coding standards;
- run static analysis and remediate findings; and
- automate structured pull-request review.

Recommended mode: **Pair** for interactive review, **Delegate** for independent review, or **Automate** for read-only CI checks.

Human gate: a human accepts findings, risk decisions, and remediation.

Evidence: structured findings with severity and file references, threat model, scan results, corrected diff.

### Legacy modernization

Examples:

- reverse-engineer a legacy application;
- capture existing behavior with tests;
- migrate frameworks or languages;
- separate a monolith into components;
- replace deprecated dependencies; and
- perform side-by-side parity verification.

Recommended mode: **Orchestrate**, with separate discovery, specification, implementation, and parity-verification stages.

Human gate: approve target architecture, compatibility requirements, data migration, cutover, and rollback.

Evidence: legacy behavior inventory, migration plan, parity tests, side-by-side results, unresolved differences.

### Deployment and operations

Examples:

- generate deployment configuration or infrastructure as code;
- deploy an application to Cloud Run;
- configure required service accounts and permissions;
- run smoke tests;
- inspect logs and runtime behavior;
- prepare rollback instructions; and
- schedule recurring maintenance checks.

Recommended mode: **Delegate** for non-production environments and **Automate** only after the workflow is proven and governed.

Human gate: approve cloud mutations, identity changes, production deployments, destructive operations, and cost-bearing resources.

Evidence: deployment plan, command log, service URL, smoke-test results, monitoring and rollback instructions.

### Data engineering and analytics

Examples:

- discover data across approved services;
- investigate anomalies with visible queries;
- construct SQL or dbt models;
- add data-quality tests;
- diagnose modeling defects; and
- turn an investigation into a repeatable pipeline.

Recommended mode: **Pair** for exploration followed by **Delegate** for an approved pipeline.

Human gate: approve data access, query cost, sensitive-data handling, model semantics, and production scheduling.

Evidence: visible queries, lineage, dbt models and tests, investigation summary, reproducible pipeline.

## Agent-engineering use cases

### Agent requirements and design

Examples:

- define the agent's purpose, users, tools, and boundaries;
- decide where deterministic code should replace model reasoning;
- define human-in-the-loop decisions;
- design tool contracts and error behavior;
- identify sensitive inputs and prohibited actions; and
- define evaluation scenarios before implementation.

Recommended mode: **Pair**.

Evidence: agent specification, tool inventory, policy boundaries, workflow diagram, evaluation plan.

### Agent scaffolding and implementation

Examples:

- scaffold an ADK agent;
- create LLM, sequential, parallel, or graph workflows;
- add custom tools;
- manage session state and memory;
- add callbacks or guardrails; and
- create a local playground or development UI.

Recommended mode: **Delegate**, guided by relevant ADK or Agents CLI skills.

Evidence: runnable agent, tool schemas, local interaction results, tests, implementation walkthrough.

### Tools, MCP, and enterprise integration

Examples:

- expose an external system through an MCP server;
- connect an agent to a database or business API;
- forward user identity through an on-behalf-of flow;
- enforce authorization at the system of record;
- map downstream errors into safe agent responses; and
- connect design, documentation, cloud, or data tools to Antigravity.

Recommended mode: **Pair** for security design, then **Delegate** for bounded implementation.

Human gate: approve identity flow, scopes, authorization, data exposure, and external writes.

Evidence: trust-boundary diagram, tool contracts, authorization tests, failure-mode tests, end-to-end trace.

### Agent evaluation and security

Examples:

- create representative evaluation datasets;
- test tool selection and argument correctness;
- simulate users and edge cases;
- test prompt-injection and data-leakage resistance;
- evaluate response quality; and
- add regression gates for agent changes.

Recommended mode: **Delegate** or **Automate**, with independent review.

Human gate: approve evaluation criteria, thresholds, residual risk, and release readiness.

Evidence: versioned dataset, metric results, failure analysis, security test results, comparison with baseline.

### Agent deployment and integration

Examples:

- deploy an agent to Agent Runtime or Cloud Run;
- connect a web application to an agent API;
- implement streaming responses;
- preserve sessions across browser interactions;
- add a manager approval dashboard; and
- connect event sources such as Pub/Sub.

Recommended mode: **Delegate**, with explicit cloud and identity approval.

Human gate: approve deployment, IAM, network exposure, runtime identity, and operating cost.

Evidence: deployment metadata, authenticated smoke tests, UI walkthrough, session trace, rollback instructions.

### Agent observability and operations

Examples:

- inspect sessions and tool traces;
- analyze failed tool calls;
- monitor latency, cost, and quality;
- compare production behavior with evaluations;
- improve instructions or tools based on evidence; and
- prepare incident and rollback procedures.

Recommended mode: **Pair** for investigation and **Automate** for approved recurring analysis.

Human gate: approve behavior changes and any automated remediation.

Evidence: trace analysis, quality trend, incident report, proposed change, post-change evaluation.

## Selecting an appropriate use case

Antigravity is a strong fit when most of the following are true:

- the task has a clear objective or can be clarified interactively;
- the relevant context can be placed inside a bounded project;
- success can be verified through tests, inspection, or measurable outcomes;
- tools and permissions can be scoped to the task;
- changes can be reviewed and recovered;
- the agent can produce evidence rather than an unsupported completion claim; and
- humans remain available for product, architecture, security, and release decisions.

Use additional caution when:

- requirements or business rules are still disputed;
- the task touches real customer, financial, health, or identity data;
- a wrong action would be irreversible or difficult to recover;
- production access is broader than the task requires;
- validation depends primarily on subjective model output;
- external systems lack suitable test environments; or
- the organization cannot independently review or verify the result.

Avoid autonomous execution when a task requires unapproved production changes, destructive data operations, acceptance of legal or security risk, or consequential decisions about individuals.

## Standard use-case card

Use the following structure to describe every workshop or enterprise use case.

```md
### Use-case name

- Business situation:
- Engineering task:
- Expected outcome:
- Engagement mode: Pair | Delegate | Orchestrate | Automate
- Recommended Antigravity surface:
- Required context:
- Applicable rules and skills:
- Required tools or MCP servers:
- Human approval gates:
- Verification:
- Evidence artifacts:
- Risk boundary:
- Representative codelab:
- Workshop demonstration:
```

## Example use-case cards

### Add maker-checker approval to complaint resolution

- **Business situation:** High-priority customer complaints require independent review before closure.
- **Engineering task:** Add a supervisor approval workflow to an existing complaint application.
- **Expected outcome:** High-priority complaints cannot be resolved by the person who submitted the resolution.
- **Engagement mode:** Pair for discovery, then Delegate for implementation.
- **Recommended surface:** Antigravity IDE.
- **Required context:** Existing repository, workflow requirements, status model, roles, current tests.
- **Human gates:** Approve workflow states, authorization model, audit rules, and implementation plan.
- **Verification:** Self-approval rejection, approval and rejection paths, audit history, full regression suite.
- **Evidence:** Impact assessment, plan, diff, test results, browser walkthrough.
- **Risk boundary:** Synthetic data; no production identity integration or deployment.
- **Representative codelab:** [Plan and Build Apps with Conductor](https://codelabs.developers.google.com/conductor-plugin?hl=en).
- **Workshop demonstration:** Banking Complaint Resolution Workbench.

### Audit a multi-language banking platform

- **Business situation:** An engineering leader needs a consistent code-quality assessment across independently maintained services.
- **Engineering task:** Discover services, classify languages, run specialist reviews in parallel, and produce a consolidated report.
- **Expected outcome:** Prioritized, evidence-backed findings without changing code before approval.
- **Engagement mode:** Orchestrate.
- **Recommended surface:** Antigravity 2.0 or Antigravity IDE.
- **Required context:** Repository boundaries, language standards, test commands, review criteria.
- **Human gates:** Approve audit plan and approve any remediation phase separately.
- **Verification:** Re-run service tests and compare findings after remediation.
- **Evidence:** Repository map, audit plan, per-service reports, consolidated report, test results.
- **Risk boundary:** Begin read-only; remediation is a separately approved task.
- **Representative codelab:** [Build a Multi-Language Code Auditor](https://codelabs.developers.google.com/multi-language-code-auditor-antigravity?hl=en).

### Add an agent-assisted complaint summary

- **Business situation:** Case handlers spend time reading long complaint histories before deciding the next action.
- **Engineering task:** Add an agent that summarizes the case and cites the underlying notes without deciding the outcome.
- **Expected outcome:** A reviewable draft summary that links each important statement to source evidence.
- **Engagement mode:** Pair for agent design, then Delegate for implementation and evaluation.
- **Recommended surface:** Antigravity IDE with Agents CLI skills.
- **Required context:** Agent requirements, complaint schema, privacy rules, tool contracts, evaluation cases.
- **Human gates:** Approve data access, prompt and tool design, evaluation thresholds, and deployment.
- **Verification:** Factuality, source attribution, missing-information behavior, prompt-injection tests, access-control tests.
- **Evidence:** Agent specification, evaluation dataset, metric results, trace examples, security review.
- **Risk boundary:** The agent drafts a summary only; bank staff retain all complaint and customer decisions.
- **Representative codelab:** [Spec-Driven ADK Agent Development](https://codelabs.developers.google.com/sdd-adk-antigravity?hl=en).
- **Workshop demonstration:** A later agent-engineering extension to the Banking Complaint Resolution Workbench.

## Codelab-to-task map

The codelabs below are grouped by their primary engineering lesson. Individual codelabs may cover more than one category.

### Foundation and product operation

| Codelab | Primary engineering lesson |
|---|---|
| [Getting Started with Google Antigravity](https://codelabs.developers.google.com/getting-started-google-antigravity?hl=en) | Projects, permissions, artifacts, browser interaction, MCP, and skills |
| [Building with Google Antigravity](https://codelabs.developers.google.com/building-with-google-antigravity?hl=en) | Research, full-stack development, iteration, UI refinement, and unit testing |
| [Mastering Slash Commands of Antigravity 2.0](https://codelabs.developers.google.com/codelabs/devsite/codelabs/mastering-slash-commands-antigravity?hl=en) | Reusable commands and task-oriented interaction |

### Context, skills, MCP, and orchestration

| Codelab | Primary engineering lesson |
|---|---|
| [Authoring Google Antigravity Skills](https://codelabs.developers.google.com/getting-started-with-antigravity-skills?hl=en) | Packaging reusable domain and engineering procedures |
| [Google Developer Knowledge MCP Server](https://codelabs.developers.google.com/developer-knowledge-mcp-antigravity?hl=en) | Grounding technical work in current official documentation |
| [Google Workspace MCP Servers](https://codelabs.developers.google.com/google-workspace-mcp-antigravity?hl=en) | Connecting agents to approved productivity tools |
| [Command and Control with Gemini and MCP](https://codelabs.developers.google.com/gemini-mcp-agy?hl=en) | Orchestrating application development through MCP |
| [Autonomous Developer Pipelines](https://codelabs.developers.google.com/autonomous-ai-developer-pipelines-antigravity?hl=en) | `agents.md`, skills, workflows, and multi-stage delivery pipelines |

### Specification, design, and application development

| Codelab | Primary engineering lesson |
|---|---|
| [Getting Started with Spec-Driven Development](https://codelabs.developers.google.com/codelabs/getting-started-with-spec-driven-development-in-antigravity?hl=en) | Application delivery from specification to deployment |
| [Spec-Driven Development with Antigravity CLI](https://codelabs.developers.google.com/sdd-agy-cli?hl=en) | Structured CLI workflows with skills and MCP |
| [Plan and Build Apps with Conductor](https://codelabs.developers.google.com/conductor-plugin?hl=en) | Greenfield planning and brownfield feature development |
| [Design-to-Code with Stitch MCP](https://codelabs.developers.google.com/design-to-code-with-antigravity-stitch?hl=en) | Translating design metadata into verified UI code |
| [Build a Match 3 Arcade Game](https://codelabs.developers.google.com/gemini-match3-golang?hl=en) | End-to-end application construction and iteration |
| [Google Pay Checkout with MCP](https://codelabs.developers.google.com/codelabs/gpay-api-vibe-code-mcp-servers?hl=en) | Building an integration-backed customer experience |

### Cloud architecture and deployment

| Codelab | Primary engineering lesson |
|---|---|
| [Deploy Applications to Cloud Run Using MCP](https://codelabs.developers.google.com/deploy-to-cloud-run-using-oss-mcp-server?hl=en) | Tool-assisted Cloud Run deployment |
| [Build and Deploy to Google Cloud with Antigravity](https://codelabs.developers.google.com/build-and-deploy-gcp-with-antigravity?hl=en) | Architecture planning, infrastructure, service development, and end-to-end verification |
| [How to Deploy a Secure MCP Server on Cloud Run](https://codelabs.developers.google.com/codelabs/cloud-run/how-to-deploy-a-secure-mcp-server-on-cloud-run?hl=en) | Authenticated remote MCP deployment |
| [Mastering KCC Operations with Antigravity](https://codelabs.developers.google.com/next26/kcc-ops-skill-antigravity?hl=en) | Infrastructure and platform operations through specialized skills |

### Agent engineering

| Codelab | Primary engineering lesson |
|---|---|
| [Vibecode and Deploy a Frontend for an ADK Agent](https://codelabs.developers.google.com/vibecode-frontend-with-antigravity?hl=en) | Human-in-the-loop dashboard, event integration, and agent UI deployment |
| [Vibecode an ADK 2.0 Ambient Agent](https://codelabs.developers.google.com/vibecode-ambient-expense-agent?hl=en) | Stateful agent workflows, deterministic branching, security screening, and event triggers |
| [Agent-to-Agent Engineering](https://codelabs.developers.google.com/build-deploy-embed-agy-agents-cli?hl=en) | Scaffold, test, deploy, and embed an ADK agent in an existing application |
| [Spec-Driven ADK Agent Development](https://codelabs.developers.google.com/sdd-adk-antigravity?hl=en) | Adding a database-backed capability to an existing agent through SDD |
| [Secure an AI Agent Lifecycle with TDD](https://codelabs.developers.google.com/secure-agentic-coding?hl=en) | Threat modeling, secure standards, testing, hooks, and remediation loops |

### Review, data, and modernization

| Codelab | Primary engineering lesson |
|---|---|
| [Build a Multi-Language Code Auditor](https://codelabs.developers.google.com/multi-language-code-auditor-antigravity?hl=en) | Parallel discovery, review, remediation, and regression testing |
| [AI-Assisted Code Review with CLI and SDK](https://codelabs.developers.google.com/agy-cli-sdk-code-review?hl=en) | Interactive review and automated pull-request review |
| [Analytics with the Data Agent Kit](https://codelabs.developers.google.com/dak-analytics-eng-antigravity-ide?hl=en) | Cross-service data discovery, investigation, dbt development, and debugging |
| [Migrate from Firebase Studio to Antigravity](https://codelabs.developers.google.com/antigravity/how-to-migrate-from-firebase-studio-to-antigravity?hl=en) | Project migration and environment transition |
| [Automating Legacy Modernization at Scale](https://codelabs.developers.google.com/automating-modernization-with-antigravity?hl=en) | Reverse engineering, multi-agent modernization, and parity verification |

## Recommended presentation bridge

Use this sequence between the product pitch and demonstrations:

1. **What Antigravity is:** Introduce the surfaces and shared harness.
2. **How teams engage it:** Explain Pair, Delegate, Orchestrate, and Automate.
3. **Where it fits:** Show the software- and agent-engineering lifecycle map.
4. **How work remains governed:** Explain context, plan, approval, execution, verification, and evidence.
5. **Choose one use-case card:** Show the inputs, controls, outcome, and proof for the upcoming demo.
6. **Run the demonstration:** Refer back to the use-case card at each approval or verification step.
7. **Show the scale-out path:** Explain how the same pattern extends to review, modernization, data, deployment, or agent engineering.

A suggested workshop narrative is:

```text
Product capability
  → Engineering engagement mode
  → Suitable task and controls
  → Demonstrated workflow
  → Evidence of completion
  → Path to organizational adoption
```

## Adoption path

### Stage 1: Bounded assistance

- Use synthetic or non-sensitive projects.
- Start with code explanation, test generation, and documentation.
- Require review of every change.
- Establish basic workspace instructions.

### Stage 2: Structured delivery

- Introduce requirements, acceptance criteria, plans, and walkthroughs.
- Add project rules and approved skills.
- Delegate small features with executable verification.
- Record recurring failure modes and conventions.

### Stage 3: Specialist workflows

- Add security, review, cloud, data, or ADK skills.
- Connect narrowly scoped MCP tools.
- Use specialist subagents for independent analysis and review.
- Measure cycle time, defect escape, rework, and review quality.

### Stage 4: Governed orchestration

- Parallelize independent work packages.
- Establish explicit input/output contracts and merge ownership.
- Add security and release-readiness gates.
- Retain human approval for architecture, risk, external changes, and release.

### Stage 5: Repeatable automation

- Move proven read-only workflows into the CLI, SDK, CI, or schedules.
- Use least-privilege service identities and isolated environments.
- Monitor quality, cost, latency, tool behavior, and false positives.
- Expand write authority only after controls and recovery have been demonstrated.

## Measures of value

Evaluate Antigravity using engineering outcomes rather than lines of generated code:

- time from requirement to reviewed implementation;
- time required to understand an unfamiliar codebase;
- percentage of acceptance criteria verified automatically;
- review findings caught before merge;
- regression and escaped-defect rates;
- rework caused by unclear requirements;
- deployment lead time and recovery evidence;
- reuse of approved skills and workflows;
- human review time per bounded task; and
- agent-evaluation quality and failure recurrence.

## Draft follow-up work

This first version should be refined by:

1. Reviewing terminology against the target Antigravity release used in the workshop.
2. Selecting a smaller set of codelabs for each target audience.
3. Adding presentation-ready diagrams for the engagement modes and governed loop.
4. Creating detailed use-case cards for the selected banking demonstrations.
5. Adding prerequisites, estimated setup time, and demo duration to the codelab map.
6. Defining separate paths for engineering leaders, application developers, agent engineers, platform engineers, and security teams.
7. Validating all demonstrations in the intended workshop environment before presenting them.
