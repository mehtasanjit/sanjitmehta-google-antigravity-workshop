# Implementation Plan - Banking Internal Complaint Tracker MVP

## Phase 1: Project Scaffolding & Environment Setup
- [x] Task 1.1: Backend Environment & Scaffolding (6a0e238)
  - [x] Initialize backend directory (`backend/`)
  - [x] Create Python configuration and dependency files (`requirements.txt`, `pyproject.toml`)
  - [x] Set up basic environment configuration variables (`.env`)
- [~] Task 1.2: Frontend Vite + React Scaffolding
  - [~] Initialize frontend directory (`frontend/` using Vite + React + TypeScript)
  - [~] Setup npm packages, folder structures, and test configurations (Vitest)
- [ ] Task 1.3: Verify Setup Build
  - [ ] Run basic build and linter checks on empty scaffold directories
  - [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Database Schema & FastAPI Backend (TDD-Driven)
- [ ] Task 2.1: Write Database & Seeding Tests (Red Phase)
  - [ ] Create test file for database models, SQLite connection, and initial seed logic
  - [ ] Run backend tests and confirm failure
- [ ] Task 2.2: Implement Database & Seeding (Green Phase)
  - [ ] Define SQLAlchemy database models (`Complaint` and `ActivityLog`)
  - [ ] Implement database connection engine and seeding script for the 4 mock complaints
  - [ ] Run backend tests and verify they pass
- [ ] Task 2.3: Write API Endpoint & Transition Tests (Red Phase)
  - [ ] Create test file for FastAPI routes (`GET /api/complaints`, `POST /api/complaints`, `POST /api/complaints/{id}/transition`)
  - [ ] Run backend tests and confirm failure
- [ ] Task 2.4: Implement API Endpoints & State Machine (Green Phase)
  - [ ] Implement the FastAPI routes and business logic for the state machine transitions
  - [ ] Run backend tests and verify they pass (100% success, >80% coverage)
  - [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: React Frontend & Dashboard UI (TDD-Driven)
- [ ] Task 3.1: Write Layout & Dashboard Tests (Red Phase)
  - [ ] Create Vitest test file to verify header, sidebar, and dashboard metrics rendering
  - [ ] Confirm frontend tests fail
- [ ] Task 3.2: Implement Color Tokens, Styles, and Page Frame (Green Phase)
  - [ ] Write CSS custom properties and core stylesheets for the Charcoal & Mint theme
  - [ ] Implement React dashboard frame and summary cards
  - [ ] Confirm frontend tests pass
- [ ] Task 3.3: Write Kanban Board & Action Button Tests (Red Phase)
  - [ ] Create Vitest test file to verify column grouping and click-to-transition interactions
  - [ ] Confirm tests fail
- [ ] Task 3.4: Implement Interactive Kanban Board & Details Drawer (Green Phase)
  - [ ] Implement four-column Kanban board utilizing card action buttons for transitions
  - [ ] Implement slide-out details drawer containing complaint details and Activity Log timeline
  - [ ] Confirm tests pass
- [ ] Task 3.5: Write Registration Form Tests (Red Phase)
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
