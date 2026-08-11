# Implementation Plan: Lecture Pulse Core MVP

## Phase 1: Environment & Project Scaffolding
- [ ] Task: Scaffold Python FastAPI backend with SQLite & WebSocket boilerplate
- [ ] Task: Scaffold React + Vite frontend application with routing
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Session Management & Backend API
- [ ] Task: [TDD] Write tests for Session creation & room code lookup
- [ ] Task: Implement Session models, SQLite schema, and FastAPI session routes
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Real-Time WebSocket Engine & Q&A Backend
- [ ] Task: [TDD] Write tests for WebSocket ConnectionManager & message broadcasting
- [ ] Task: Implement FastAPI WebSocket endpoint (`/ws/{session_code}`) with pulse & Q&A message handlers
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Student UI (Join, Pulse Controls & Q&A)
- [ ] Task: [TDD] Write component tests for Student Join, Pulse Gauge buttons, and Q&A submission
- [ ] Task: Build React Student views (`/join` and `/session/:code`) with WebSocket connectivity
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 5: Lecturer Live Dashboard & Presenter Mode
- [ ] Task: [TDD] Write component tests for Lecturer Dashboard & Question moderation
- [ ] Task: Build React Lecturer views (`/create` and `/dashboard/:code`) with Presenter Mode toggle
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 6: System Integration & E2E Verification
- [ ] Task: Execute full end-to-end user flow verification & automated test suite
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
