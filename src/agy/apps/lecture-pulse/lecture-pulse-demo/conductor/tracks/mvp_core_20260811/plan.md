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

## Review Fixes Phase (Post-Code Review)
- [x] Task: Increase room code entropy in `backend/app/database.py` (alphanumeric 5-char LP-X9K2F)
- [x] Task: Fix WebSocket DB connection scope in `backend/app/routers/websockets.py` (acquire DB connection per event)
- [x] Task: Enforce Pydantic validation on WebSocket JSON payloads
- [x] Task: Wire real REST API & WebSocket client connections in `frontend/src/`
- [x] Task: Add frontend component/integration tests
- [x] Task: Re-run automated tests & verify end-to-end integration
