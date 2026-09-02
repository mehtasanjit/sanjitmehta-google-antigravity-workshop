# Implementation Plan: Banking Complaint Resolution Workbench MVP

## Phase 1: Database Models, Schemas & Synthetic Data Seeder
- [x] Task: Define SQLite Database Schema & Models (`backend/app/models.py`)
  - [x] Create `Complaint` model with customer details, product type, status enum, priority enum, disputed amount, redress amounts, root cause, assigned handler, timestamps.
  - [x] Create `AuditLog` model with `complaint_id`, `timestamp`, `actor_role`, `actor_name`, `action_type`, `from_status`, `to_status`, `details`.
- [x] Task: Define Pydantic Request/Response Validation Schemas (`backend/app/schemas.py`)
  - [x] Input schemas for ComplaintCreate, StatusUpdate, AssignmentUpdate, InvestigationUpdate, RedressUpdate, ReviewDecision.
  - [x] Output schemas for ComplaintResponse, AuditLogResponse, StatsResponse.
- [x] Task: Implement Synthetic Banking Data Seeder (`backend/app/seed.py`)
  - [x] Realistic synthetic customers, complaints across checking, credit cards, loans, mortgages, wire transfers.
  - [x] Seed initial complaints into various lifecycle stages with rich synthetic audit history.
- [x] Task: Phase 1 Unit Tests (`backend/tests/test_models_and_seed.py`)
  - [x] Test DB initialization, model constraints, and seed execution.

## Phase 2: Core REST API & Business Logic
- [x] Task: Implement FastAPI Application & CRUD Endpoints (`backend/app/api.py`, `backend/app/main.py`)
  - [x] `GET /api/complaints` with filtering (status, priority, product, search query, assigned_to).
  - [x] `POST /api/complaints` with auto-generated complaint reference number (e.g., `CMP-2026-001`) and audit creation event.
  - [x] `GET /api/complaints/{id}` returning complaint details and full audit log.
  - [x] `PATCH /api/complaints/{id}/assign` to assign/reassign case handler.
- [x] Task: Implement Workflow Transitions & Review API
  - [x] `PATCH /api/complaints/{id}/status` validating permitted transitions.
  - [x] `POST /api/complaints/{id}/investigation` saving root cause & investigation notes.
  - [x] `POST /api/complaints/{id}/redress` saving proposed refund, goodwill, and interest calculations.
  - [x] `POST /api/complaints/{id}/review` handling supervisor approval/rejection with required reason and state movement.
  - [x] `GET /api/stats` returning dashboard KPIs for supervisors.
  - [x] `POST /api/seed` endpoint to reset data on demand.
- [x] Task: Phase 2 API Tests (`backend/tests/test_api.py`)
  - [x] Test all endpoint workflows, state machine validation, supervisor rejection/approval, and audit log generation.

## Phase 3: Reactive React + Vite Workbench UI
- [x] Task: Scaffold React + Vite Frontend (`frontend/`)
  - [x] Initialize Vite + React project with Tailwind CSS and Lucide React icons.
  - [x] Setup API client and state management for complaints, roles, active filters, and audit trail.
- [x] Task: Build Role-Aware Header & Kanban Workspace Components
  - [x] Header with Role Switcher (`Intake Specialist`, `Case Handler`, `Supervisor`, `Auditor`), live KPI metrics, search input, "+ New Complaint" button, and "Reset Synthetic Data" button.
  - [x] 6-Column Kanban Board with drag-and-drop or quick stage transition triggers, priority badges, SLA countdowns, and disputed amount tags.
- [x] Task: Build Case Intake Modal & Case Detail Drawer
  - [x] Intake Modal: Form validation for synthetic customer and complaint data.
  - [x] Case Detail Drawer:
    - Customer and Account summary
    - Investigation findings & Root Cause selection
    - Redress Calculator with live sum
    - Supervisor Review / Sign-off panel (Approve / Reject with mandatory justification)
    - Chronological, color-coded Audit Trail timeline
  - [x] Role-based UI gating and instant reactive feedback.

## Phase 4: Verification, Quality Gate & Documentation
- [x] Task: End-to-End Automated Testing & Build Verification
  - [x] Run backend Pytest test suite with coverage verification (12 test cases passed).
  - [x] Run frontend build test (`npm run build` passed with zero errors).
- [x] Task: Phase 4 Manual Verification & User Walkthrough (`walkthrough.md`)
  - [x] Verify full case lifecycle across all 4 roles.
