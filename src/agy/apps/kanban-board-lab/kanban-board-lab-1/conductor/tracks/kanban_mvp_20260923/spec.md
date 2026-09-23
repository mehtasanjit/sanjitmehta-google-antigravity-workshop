# Track Specification: Kanban Board Lab MVP

## 1. Overview
Kanban Board Lab MVP is a standalone, single-device Kanban application built using a decoupled architecture:
- **Backend:** Python FastAPI REST API with SQLite database persistence using SQLAlchemy/SQLModel.
- **Frontend:** React 18+, TypeScript, Vite, Tailwind CSS, and `@dnd-kit` (or accessible drag-and-drop).
- **Core Purpose:** Enable individuals and small teams to visualize work, enforce Work-in-Progress (WIP) limits, move and reorder tasks, search/filter cards, archive work, and preserve board state durably across reloads.

## 2. Functional Requirements

### 2.1 Board and Column Management
- Default columns: `Backlog`, `To Do`, `In Progress` (initial WIP limit: 3), and `Done`.
- Support column renaming, adding new columns, reordering columns, and deleting empty columns without losing cards.
- Support configuring, modifying, or removing WIP limits per column.
- Strict WIP enforcement: Prevent card creation or movement into an active column that has reached its WIP limit; display an actionable, empathetic message explaining the blocker.

### 2.2 Card Lifecycle (CRUD)
- Card schema: `id` (UUID/stable ID), `title` (required, non-empty/non-whitespace), `description` (optional), `priority` (`Low`, `Medium`, `High`), `assignee` (optional fictional string), `tags` (array of strings), `dueDate` (optional ISO date string), `columnId`, `order`, `isArchived`, `createdAt`, `updatedAt`.
- Card editing dialog with validation and focus trapping.
- Overdue calculation: Highlight cards whose due date precedes current local date, unless in `Done` or archived.

### 2.3 Movement and Keyboard Parity
- Smooth drag-and-drop pointer interactions for cross-column moves and same-column reordering.
- Keyboard-accessible movement alternative: Context menu or keyboard shortcuts allowing card movement between columns and up/down position shifts.

### 2.4 Search, Filtering, and Views
- Real-time case-insensitive partial search over card titles and descriptions.
- Multi-criteria filtering by priority, assignee, tags, and overdue status combining with AND logic.
- Filtering updates visible cards only; hidden cards must continue to count toward column WIP limits.
- "Clear all filters" button resetting all search and filter inputs in one click.
- Dedicated Archive modal/view to browse archived cards with "Restore" actions.
- Board Reset action restoring default starter columns and sample cards with explicit confirmation.

### 2.5 Seeding and Data Persistence
- Automatic first-launch seeding with default columns and 4-5 fictional starter cards demonstrating priorities, tags, and overdue states.
- Local SQLite database persistence (`kanban.db`) ensuring data survives page refresh and server restarts.

## 3. Non-Functional & Accessibility Requirements
- **Responsive Design:** Operable across desktop viewports and mobile screens down to 375px without horizontal scrolling for core tasks.
- **Accessibility:** Visible focus rings, WCAG 2.1 AA color contrast, non-color dependent priority/overdue indicators, `aria-live` announcements for WIP limits, and ESC dismissal for dialogs.
- **UI Performance:** Optimistic state updates on the frontend with automatic rollback if an API error occurs.

## 4. Acceptance Criteria
1. Blank or whitespace-only card titles are rejected with clear error feedback.
2. Moving a card into a column at its WIP limit is blocked with an explanatory message; no cards are lost or displaced.
3. Hidden cards resulting from search/filters still count against column WIP limits.
4. Overdue cards display distinct non-color badges, except in `Done` or `Archive`.
5. Every pointer move operation has an equivalent keyboard interaction path.
6. Changes persist across browser page reloads and server restarts.
7. Resetting the board restores the documented starter state after explicit user confirmation.

## 5. Out of Scope
- User authentication, user accounts, and multi-tenant security boundaries.
- Remote cloud deployment, external synchronization, and webhooks.
- File attachments, comments, recurring subtasks, and cycle-time reporting.
- AI task automation or automated task generation.
