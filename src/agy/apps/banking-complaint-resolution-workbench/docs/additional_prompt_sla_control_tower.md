# SLA Control Tower Track Prompt

Add a supervisor-facing SLA Control Tower to the existing Banking Complaint Resolution Workbench. Begin by reading the workspace `AGENTS.md`, the existing Conductor project context and completed MVP track, and `docs/additional_requirement_sla_control_tower.md`. Treat the additional requirements as authoritative for this track and preserve existing complaint-dashboard, workflow, and audit behavior unless an approved change is required for the new feature.

Use the installed specification-driven development workflow to create a new, separately identifiable Conductor track. Clarify unresolved product or design decisions, produce the track specification and implementation plan, and obtain the confirmations required by the workspace guidance before changing application code.

The completed feature should enable the existing `SLA Reports` navigation item and provide a highly visible Control Tower with overdue, due-within-24-hours, due-within-3-days, and on-track metrics; red, amber, and green risk groups with accessible text labels; complaint cards; handler workload visualization; filters; preserved complaint-detail context; and supervisor-only assignment, reassignment, and escalation actions. All material actions must be enforced by the backend and recorded in the complaint audit history.

Reuse the current React, TypeScript, FastAPI, SQLAlchemy, SQLite, and vanilla CSS architecture. Do not add a charting library solely for this feature. Do not add outbound notifications, scheduled jobs, regulatory deadline calculations, production authentication, automatic assignment, external integrations, agentic decision-making, or real customer data.

After the specification and implementation plan are approved, implement only the agreed scope. Verify SLA boundary calculations, filtering, authorization, assignment and escalation rules, audit consistency, frontend behavior, and the production frontend build. Clearly report all completed checks and anything incomplete or unverified.
