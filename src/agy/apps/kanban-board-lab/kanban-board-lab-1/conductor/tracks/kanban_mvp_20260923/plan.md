# Implementation Plan: Kanban Board Lab MVP

## Phase 1: Environment & Project Scaffolding
- [x] Task: Setup Backend Project Structure [e7b8d99]
  - [x] Initialize Python backend directory with FastAPI, Uvicorn, SQLAlchemy, Pydantic, and pytest configuration
  - [x] Configure execution targeting explicit Python binary `/usr/local/google/home/sanjitmehta/work/python/venvs/venv_1/bin/python`
  - [x] Verify test runner runs cleanly with a smoke test
- [ ] Task: Setup Frontend Project Structure
  - [ ] Initialize React 18+ TypeScript application with Vite and Tailwind CSS
  - [ ] Configure Vitest and React Testing Library test harness
  - [ ] Configure Lucide icons and basic layout shell
  - [ ] Verify frontend test runner passes with a smoke test
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Backend API & SQLite Persistence (TDD)
- [ ] Task: Write Failing Tests for SQLite Models and Seeding (Red Phase)
  - [ ] Write unit tests for Board, Column, and Card models, constraints, and timestamps
  - [ ] Write unit tests for initial seed data generation (4 columns, starter cards, WIP limit)
  - [ ] Confirm all tests fail before implementation
- [ ] Task: Implement Models, Database Engine, and Seed Service (Green Phase)
  - [ ] Implement SQLAlchemy/SQLModel models with foreign keys and SQLite schema initialization
  - [ ] Implement seed data fixture populating starter columns and cards
  - [ ] Run test suite and confirm all tests pass
- [ ] Task: Write Failing Tests for REST API Endpoints and Invariants (Red Phase)
  - [ ] Write integration tests for column CRUD and reordering
  - [ ] Write integration tests for card CRUD and column movement
  - [ ] Write integration tests for column WIP limit enforcement (verifying 400 Bad Request with explanatory detail on overflow)
  - [ ] Write integration tests for card archive, restore, and board reset
  - [ ] Confirm all tests fail
- [ ] Task: Implement FastAPI Routes and Business Logic (Green Phase)
  - [ ] Implement `/api/board`, `/api/columns`, and `/api/cards` router endpoints
  - [ ] Enforce WIP limit invariant check in card move/create service logic
  - [ ] Implement `/api/cards/{id}/archive`, `/api/cards/{id}/restore`, and `/api/board/reset` endpoints
  - [ ] Run test suite and confirm 100% route tests pass
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Frontend Core Board & Movement (TDD)
- [ ] Task: Write Failing Tests for Board State and Column/Card UI (Red Phase)
  - [ ] Write tests for Board, Column, and Card components
  - [ ] Write tests for card creation modal with title whitespace rejection
  - [ ] Confirm tests fail
- [ ] Task: Implement Board, Column, and Card Components (Green Phase)
  - [ ] Build responsive column grid with column card counts and WIP limit badges
  - [ ] Build card component showing title, priority badge, tags, fictional assignee, and due date
  - [ ] Build card creation and edit modal with accessible focus trapping
  - [ ] Verify tests pass
- [ ] Task: Write Failing Tests for Drag & Drop and Keyboard Movement (Red Phase)
  - [ ] Write tests for pointer drag-and-drop movement within and across columns
  - [ ] Write tests for accessible keyboard navigation controls (move column, move up/down)
  - [ ] Write tests for WIP limit error notification and prevention on drop/move
  - [ ] Confirm tests fail
- [ ] Task: Implement Drag & Drop, Keyboard Parity, and WIP Enforcement (Green Phase)
  - [ ] Implement `@dnd-kit` (or accessible drag-and-drop provider) for columns and cards
  - [ ] Implement keyboard action menu with ARIA attributes and focus management
  - [ ] Integrate optimistic UI updates with backend sync and revert on WIP overflow
  - [ ] Add `aria-live` region for WIP error alerts and screen-reader announcements
  - [ ] Verify tests pass
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Search, Filtering, Archiving & Board Reset (TDD)
- [ ] Task: Write Failing Tests for Search, Filtering, and Overdue Logic (Red Phase)
  - [ ] Write unit tests for case-insensitive partial search over title and description
  - [ ] Write unit tests for multi-criteria filters (priority, assignee, tag, overdue) combining with AND logic
  - [ ] Write tests verifying hidden cards continue to count toward column WIP limits
  - [ ] Write tests for overdue date highlighting (excluding Done and Archive)
  - [ ] Confirm tests fail
- [ ] Task: Implement Search Bar, Multi-Filter Toolbar, and Overdue Highlights (Green Phase)
  - [ ] Build search input and filter bar with clear-all button
  - [ ] Apply client-side filter predicate preserving column WIP counts
  - [ ] Add visual and text-accessible overdue badges to past-due cards
  - [ ] Verify tests pass
- [ ] Task: Write Failing Tests for Archive Drawer and Reset Confirmation (Red Phase)
  - [ ] Write tests for card archiving confirmation dialog
  - [ ] Write tests for Archive modal displaying archived cards and restore buttons
  - [ ] Write tests for Board Reset confirmation dialog restoring starter state
  - [ ] Confirm tests fail
- [ ] Task: Implement Archiving, Archive View, and Board Reset (Green Phase)
  - [ ] Build confirmation dialogs for archiving and board reset
  - [ ] Build Archive drawer/modal with search and restore functionality
  - [ ] Connect board reset to backend `/api/board/reset` endpoint
  - [ ] Verify tests pass
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 5: End-to-End Integration, Responsiveness & Verification
- [ ] Task: Write End-to-End Integration Tests
  - [ ] Test full user flow: create card -> move to In Progress -> trigger WIP limit -> move to Done -> archive
  - [ ] Test state recovery and persistence across simulated reload
- [ ] Task: Responsive Layout & Accessibility Verification
  - [ ] Verify mobile viewport rendering (375px width) without horizontal page overflow
  - [ ] Verify WCAG AA color contrast ratios in both Light and Dark modes
  - [ ] Verify keyboard-only navigation end-to-end
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
