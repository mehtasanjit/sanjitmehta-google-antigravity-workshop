# Implementation Plan: Lecture Pulse Core MVP

## Phase 1: Environment & Project Scaffolding
- [x] Task: Scaffold Python FastAPI backend with SQLite & WebSocket boilerplate [7ce410e]
- [x] Task: Scaffold React + Vite frontend application with routing
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Session Management & Backend API
- [x] Task: [TDD] Write tests for Session creation & room code lookup
- [x] Task: Implement Session models, SQLite schema, and FastAPI session routes
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Real-Time WebSocket Engine & Q&A Backend
- [x] Task: [TDD] Write tests for WebSocket ConnectionManager & message broadcasting
- [x] Task: Implement FastAPI WebSocket endpoint (`/ws/{session_code}`) with pulse & Q&A message handlers
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Student UI (Join, Pulse Controls & Q&A)
- [x] Task: [TDD] Write component tests for Student Join, Pulse Gauge buttons, and Q&A submission
- [x] Task: Build React Student views (`/join` and `/session/:code`) with WebSocket connectivity
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 5: Lecturer Live Dashboard & Presenter Mode
- [x] Task: [TDD] Write component tests for Lecturer Dashboard & Question moderation
- [x] Task: Build React Lecturer views (`/create` and `/dashboard/:code`) with Presenter Mode toggle
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 6: System Integration & E2E Verification
- [x] Task: Execute full end-to-end user flow verification & automated test suite
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
