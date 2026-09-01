# Kanban Board Lab Requirements

## The need

Individuals and small teams need a simple way to see planned work, understand what is currently in progress, and move tasks toward completion. Work tracked in disconnected notes or undifferentiated lists makes priorities, ownership, bottlenecks, and progress difficult to understand.

Kanban Board Lab provides a focused visual workflow in which work is represented by cards arranged in ordered columns. The first version should demonstrate the essential Kanban interactions without requiring accounts, external services, or production infrastructure.

## Users

### Board members

Board members need to:

- understand the current state of work at a glance;
- create and describe a task without unnecessary setup;
- identify priority, ownership, tags, and due dates;
- move and reorder work as its status changes;
- keep too much work from accumulating in an active column;
- find relevant cards quickly; and
- return to the board without losing their changes.

The initial version does not distinguish administrator, manager, and contributor permissions. All demonstrated identities and work items must be fictional.

## Board and card information

The board must have a title and an ordered collection of columns. The initial board should provide `Backlog`, `To Do`, `In Progress`, and `Done` columns, while allowing the user to rename and reorder them.

Each card must include:

- a stable identifier;
- a required title;
- an optional description;
- a priority of `Low`, `Medium`, or `High`;
- an optional fictional assignee;
- zero or more tags;
- an optional due date;
- its current column and position within that column; and
- created and last-updated timestamps.

## Required experience

1. A user can open a board and see its columns, cards, card counts, and active work-in-progress limits.
2. A user can create a card in a selected column. A blank or whitespace-only title must not be accepted.
3. A user can open a card and edit its title, description, priority, assignee, tags, and due date.
4. A user can move a card between columns and reorder cards within a column.
5. Pointer-based movement must have a clear keyboard-accessible alternative.
6. A user can rename and reorder columns without losing their cards.
7. A user can set or remove a work-in-progress limit for a column.
8. When a move would exceed a column's work-in-progress limit, the application must prevent the move and explain why. Existing cards must not be silently removed or relocated.
9. A user can search card titles and descriptions using case-insensitive partial matching.
10. A user can filter cards by priority, assignee, tag, and overdue state. Active search and filters combine using AND semantics.
11. Filtering changes only the visible view. It must not change card state, column counts, ordering, or persisted data.
12. A user can clear all active search and filter controls in one action.
13. A user can archive a card after confirmation. Archived cards do not appear on the active board but remain available in an archive view and can be restored.
14. Board changes remain available after a page refresh on the same device.
15. The application provides useful empty states for an empty column, an empty archive, and a search or filter with no matching cards.
16. The board remains usable at desktop and mobile widths without requiring horizontal page scrolling for basic card operations.

## Workflow rules

- A card belongs to exactly one active column or to the archive.
- A card's stable identifier and creation timestamp do not change when it is edited, moved, archived, or restored.
- Moving or reordering a card must preserve all other card information.
- Column and card ordering must persist across page refreshes.
- A work-in-progress limit applies only to active cards in that column.
- A column at its limit may still move cards out, archive cards, or change its configured limit.
- A due date earlier than the current local date is visually identified as overdue unless the card is in `Done` or archived.
- Search and filter controls may hide cards but must not make hidden cards count differently for work-in-progress enforcement.
- Destructive actions require clear confirmation and must identify what will be affected.

## Accessibility and interaction expectations

- Interactive controls have accessible names and visible keyboard focus.
- Core board operations can be completed without a pointer.
- Status, validation, and work-in-progress-limit messages are communicated in text and are available to assistive technology.
- Priority, overdue state, and column state are not communicated by color alone.
- Dialogs manage focus predictably and can be dismissed without losing unrelated board state.

## Demo data and privacy

- The application may provide optional synthetic starter cards to demonstrate the workflow.
- Names, tasks, tags, and other demonstrated information must be fictional.
- The initial version must not request or transmit credentials, personal information, or proprietary project data.
- A user must be able to reset the board to a documented initial state after confirmation.

## Initial scope

The first version is limited to one locally persisted board. It does not need to support:

- user registration, authentication, or authorization;
- multiple boards or organizations;
- simultaneous multi-user editing or real-time presence;
- a server-side database or cross-device synchronization;
- comments, attachments, subtasks, recurring work, or dependencies;
- email, chat, calendar, issue-tracker, or source-control integrations;
- notifications, reporting, analytics, or cycle-time forecasting;
- import or export;
- offline installation as a native application; or
- AI-generated tasks, priorities, assignments, or workflow decisions.

## Verification expectations

- Add automated coverage at the smallest practical seams for card creation and editing, movement and ordering, work-in-progress enforcement, filtering, archiving and restoration, and persistence.
- Verify the same-column and cross-column movement paths, including the keyboard-accessible path.
- Verify combined search and filters, reset behavior, and the no-match state.
- Verify that hidden cards continue to count toward work-in-progress limits.
- Verify overdue-date behavior around the current local date and the `Done` exception.
- Verify that malformed or unavailable persisted data produces a recoverable state rather than a blank or unusable application.
- Exercise the application at representative desktop and mobile widths and record browser evidence.

## Success criteria

The initial application is successful when a user can create and organize fictional work on a clear Kanban board, move and reorder cards with either pointer or keyboard controls, enforce work-in-progress limits, find cards through combined search and filters, archive and restore work, and return after a refresh without losing valid board state.
