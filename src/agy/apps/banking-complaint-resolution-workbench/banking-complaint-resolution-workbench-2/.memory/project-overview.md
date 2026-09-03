---
name: project-overview
description: Foundational goals, technical architecture, role workflows, and environment configuration for the Banking Complaint Resolution Workbench.
metadata:
  node_type: memory
  type: project
  modified: 2026-09-02T13:10:00Z
  status: in_progress_remediations
---

# Banking Complaint Resolution Workbench - Project Overview

## Core Objective
An internal, highly reactive and intuitive Banking Complaint Resolution Workbench for bank case handlers, investigators, supervisors, and intake specialists with an interactive Kanban board and a complete immutable audit log history.

## Technical Stack & Runtime
- **Backend Framework:** FastAPI + Uvicorn ASGI Server + SQLite DB (SQLAlchemy/SQLite3)
- **Python Runtime:** `/home/sanjitmehta/work/python/venv_3_13_14_1/bin/python` (Python 3.13)
- **Frontend Architecture:** React + Vite + Tailwind CSS + Lucide Icons for a responsive, reactive Kanban SPA
- **Testing:** Pytest with FastAPI TestClient for backend API; Vite build verification for frontend
- **Track:** `conductor/tracks/complaint_workbench_mvp_20260902/`

## Key Lifecycle Stages (Kanban Columns)
1. `New / Intake`: Complaints recorded by intake specialists.
2. `In Investigation`: Cases being analyzed by assigned case handlers.
3. `Under Supervisor Review`: Proposed redress & resolution submitted for supervisor sign-off.
4. `Approved`: Supervisor signed off; ready for final customer payout/communication.
5. `Resolved`: Case closed and settled.
6. `Escalated`: Flagged for compliance or legal review.

## Role Permissions
- **Intake Specialist:** Record new complaints with synthetic customer details.
- **Case Handler / Investigator:** Assign to self, investigate, calculate redress, submit for review, close approved cases.
- **Supervisor:** Approve/reject proposed resolutions, reassign, override priority/escalation.
- **Auditor:** View complete chronological audit timeline and export report.
