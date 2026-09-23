# Kanban Board Lab

## Product Overview
Kanban Board Lab is a focused, single-board, single-device Kanban web application designed for individuals and small agile teams to visualize work, limit work in progress (WIP), and move tasks toward completion. It provides an intuitive, tactile card management experience across customizable columns without requiring user accounts, external databases, or remote services.

## Target Audience & Personas
- **Individual Contributors & Small Teams**: Knowledge workers and agile teams needing a lightweight, frictionless board to track tasks, organize backlog items, and manage daily throughput.
- **Solo Developers**: Engineers managing tasks, priorities, and technical debt on local machines with fast, offline-first reliability.

## Key Capabilities & Scope
1. **Board & Column Management**:
   - Default columns: `Backlog`, `To Do`, `In Progress`, `Done`.
   - Ability to rename, reorder, add, and remove columns without losing associated cards.
   - Work-in-Progress (WIP) limit configuration per column with visual indicators and strict movement prevention when limits are reached.
2. **Card Management (CRUD)**:
   - Stable identifier and creation/updated timestamps.
   - Required title (non-empty/non-whitespace), optional rich description, priority (`Low`, `Medium`, `High`), fictional assignee, tags/labels, and optional due date.
   - Visual overdue indicators for past-due items (excluding `Done` or archived items).
3. **Movement & Interaction**:
   - Pointer-based drag-and-drop movement across columns and reordering within columns.
   - First-class keyboard accessible movement alternative (e.g. keyboard shortcuts / action menus).
4. **Search & Multi-Criteria Filtering**:
   - Case-insensitive partial matching across card titles and descriptions.
   - Multi-criteria filtering by priority, assignee, tag, and overdue state using AND semantics.
   - One-click clear filter action; filtering updates visible view without altering WIP counts or underlying ordering.
5. **Archiving & Board Reset**:
   - Card archiving with confirmation dialog; dedicated archive view with restoration capability.
   - Board reset to initial starter state with confirmation modal.
6. **Persistence & Resilience**:
   - Client-side storage via Browser LocalStorage with JSON schema validation.
   - Graceful fallback and state recovery when encountering corrupt or missing persisted data.

## Non-Goals & Out of Scope (Initial Version)
- User accounts, authentication, role-based authorization, or multi-tenant organizations.
- Server-side database, backend APIs, or cross-device / real-time multi-user synchronization.
- External integrations (Slack, GitHub, Jira, email, Google Calendar).
- File attachments, comments, recurring subtasks, or cycle-time analytics.
- AI-generated task generation, automated triage, or workflow automation.
