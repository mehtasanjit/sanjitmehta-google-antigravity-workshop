# Implementation Plan - Banking Internal Complaint Tracker MVP

## Phase 1: Project Scaffolding & Environment Setup
- [x] Task 1.1: Backend Environment & Scaffolding (6a0e238)
  - [x] Initialize backend directory (`backend/`)
  - [x] Create Python configuration and dependency files (`requirements.txt`, `pyproject.toml`)
  - [x] Set up basic environment configuration variables (`.env`)
- [x] Task 1.2: Frontend Vite + React Scaffolding (7a0a577)
  - [x] Initialize frontend directory (`frontend/` using Vite + React + TypeScript)
  - [x] Setup npm packages, folder structures, and test configurations (Vitest)
- [x] Task 1.3: Verify Setup Build (b6245fd)
  - [x] Run basic build and linter checks on empty scaffold directories
  - [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Database Schema & FastAPI Backend (TDD-Driven)
- [x] Task 2.1: Write Database & Seeding Tests (Red Phase) (f634a0e)
  - [x] Create test file for database models, SQLite connection, and initial seed logic
  - [x] Run backend tests and confirm failure
- [x] Task 2.2: Implement Database & Seeding (Green Phase) (c98572a)
  - [x] Define SQLAlchemy database models (`Complaint` and `ActivityLog`)
  - [x] Implement database connection engine and seeding script for the 4 mock complaints
  - [x] Run backend tests and verify they pass
- [x] Task 2.3: Write API Endpoint & Transition Tests (Red Phase) (dcbf3ce)
  - [x] Create test file for FastAPI routes (`GET /api/complaints`, `POST /api/complaints`, `POST /api/complaints/{id}/transition`)
  - [x] Run backend tests and confirm failure
- [x] Task 2.4: Implement API Endpoints & State Machine (Green Phase) (9f444fe)
  - [x] Implement the FastAPI routes and business logic for the state machine transitions
  - [x] Run backend tests and verify they pass (100% success, >80% coverage)
  - [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) (9f444fe)

## Phase 3: React Frontend & Dashboard UI (TDD-Driven)
- [x] Task 3.1: Write Layout & Dashboard Tests (Red Phase) (eedae50)
  - [x] Create Vitest test file to verify header, sidebar, and dashboard metrics rendering
  - [x] Confirm frontend tests fail
- [x] Task 3.2: Implement Layout & Dashboard (Green Phase) (0cfb2c8)
  - [x] Write CSS custom properties and core stylesheets for the Charcoal & Mint theme
  - [x] Implement React dashboard frame and summary cards
  - [x] Confirm frontend tests pass
- [x] Task 3.3: Write Kanban Board & Action Button Tests (Red Phase) (57520f3)
  - [x] Create Vitest test file to verify column grouping and click-to-transition interactions
  - [x] Confirm tests fail
- [x] Task 3.4: Implement Interactive Kanban Board & Details Drawer (Green Phase) (a02825f)
  - [x] Implement four-column Kanban board utilizing card action buttons for transitions
  - [x] Implement slide-out details drawer containing complaint details and Activity Log timeline
  - [x] Confirm tests pass
- [~] Task 3.5: Write Registration Form Tests (Red Phase)
  - [ ] Create test file to verify validation and input processing of the complaint form
  - [ ] Confirm tests fail
- [ ] Task 3.6: Implement Complaint Registration Form (Green Phase)
  - [ ] Create the form modal, hook up input validation, and connect it to state
  - [ ] Confirm tests pass
  - [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Full-Stack Integration & Final Verification
- [ ] Task 4.1: Integrate API Clients
  - [ ] Connect React frontend components to FastAPI backend endpoints
  - [ ] Ensure state transitions trigger instant UI updates and re-fetch logs
- [ ] Task 4.2: End-to-End User Scenario Validation
  - [ ] Perform a full user-path scenario run-through: Intake Specialist registers card -> Specialist assigns specialist -> Investigator moves to Investigation -> Investigator resolves case -> Inspect activity logs
  - [ ] Verify complete visual styling on desktop and mobile screens
  - [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
