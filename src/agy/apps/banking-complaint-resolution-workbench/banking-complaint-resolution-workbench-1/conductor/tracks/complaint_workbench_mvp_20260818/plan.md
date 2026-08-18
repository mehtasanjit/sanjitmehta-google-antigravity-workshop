# Implementation Plan: Banking Complaint Resolution Workbench MVP

## Phase 1: Database Setup & Mock Data (TDD)
- [x] Task 1.1: Define SQLAlchemy models for Complaints, Audit Logs, and Users. (ec71215)
- [x] Task 1.2: Implement SQLite database initialization and populate with robust mock data (Jane Doe, John Smith, Alice Johnson, Robert Vance). (3651160)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) (63bf5ff)

## Phase 2: FastAPI Backend REST Endpoints (TDD)
- [x] Task 2.1: Implement GET /api/complaints and GET /api/complaints/{id} endpoints. (e83f7ec)
- [x] Task 2.2: Implement POST /api/complaints with automatic SLA calculation based on priority. (eb9bbf4)
- [x] Task 2.3: Implement POST /api/complaints/{id}/claim and POST /api/complaints/{id}/comment. (6cb738e)
- [x] Task 2.4: Implement POST /api/complaints/{id}/propose, approve, and reject endpoints (incorporating Supervisor RBAC check). (6cb738e)
- [x] Task 2.5: Implement GET /api/dashboard/stats for real-time dashboard indicators. (6cb738e)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Frontend Layout & Dashboard UI
- [ ] Task 3.1: Scaffold React application with persistent Header, Sidebar, and Header Role Switcher Context.
- [ ] Task 3.2: Implement Dashboard View featuring summary cards and searchable/filterable complaint table.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Case Investigation & Audit Timeline UI
- [ ] Task 4.1: Implement Case Detail split-screen master-detail layout.
- [ ] Task 4.2: Implement Case Details visual, scrollable vertical audit timeline feed.
- [ ] Task 4.3: Implement Action panels (Claim, Propose Resolution modal, and Supervisor Approve/Reject dialogs).
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
