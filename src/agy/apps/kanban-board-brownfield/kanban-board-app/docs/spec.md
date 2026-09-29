# Kanban Board — Product Specification (v1 baseline)

**Status:** Implemented (v1 baseline)
**Role in the workshop:** This is the existing application that the brownfield demo starts from. It is deliberately complete, tested, and conventional. **Work-in-progress (WIP) limits are intentionally not built**; they are the feature added live during the demo.

## Purpose

Give an individual or small team one visual board to see planned work, what is in progress, and what is done, and to move work toward completion.

## Users

- **Board member:** any user of the board. v1 has no accounts, roles, or permissions.
- All names, tasks, and tags in the application are fictional.

## Board

- One board titled **"Team Board"**.
- Four fixed columns, in this order: `Backlog`, `To Do`, `In Progress`, `Done`.
- Each column shows its name and its card count.

## Cards

Each card has:

| Field | Rules |
|---|---|
| `id` | Stable identifier, assigned by the server; never changes |
| `title` | Required; 1–120 characters after trimming; blank or whitespace-only is rejected |
| `description` | Optional; up to 2,000 characters |
| `priority` | `Low`, `Medium` (default), or `High` |
| `assignee` | Optional fictional name; up to 60 characters |
| `tags` | Zero to 10 short labels; each 1–20 characters; duplicates removed (case-insensitive) |
| `due_date` | Optional calendar date (`YYYY-MM-DD`) |
| `column_id`, `position` | The card's column and its 0-based order within that column |
| `created_at`, `updated_at` | Server-set UTC timestamps; `created_at` never changes |

## Required behaviour

1. **View board:** opening the app shows all columns, their cards in order, and card counts.
2. **Create card:** a user adds a card to a chosen column. It is placed at the bottom of that column. Invalid input shows a clear message and nothing is saved.
3. **Edit card:** a user opens a card and edits any editable field. `id`, `created_at`, column, and position are unchanged by an edit.
4. **Move card between columns:** a user moves a card to the left or right column. It goes to the bottom of the target column.
5. **Reorder within a column:** a user moves a card up or down within its column.
6. **Keyboard access:** every move and reorder action is available through focusable buttons. No drag-and-drop in v1.
7. **Delete card:** a user deletes a card after a confirmation that names the card.
8. **Overdue indicator:** a card whose due date is earlier than today (local date) shows an "Overdue" label, unless it is in `Done`. The label is text, not colour alone.
9. **Search:** a case-insensitive partial match on title and description. It filters the view only and never changes stored data or card counts.
10. **Persistence:** all changes are saved on the server and survive a page refresh and a server restart.
11. **Reset:** a user resets the board to the documented demo data after confirmation.
12. **Feedback:** loading, empty-column, no-search-match, and error states are shown in text.

## Ordering rules

- Positions within a column are always contiguous: `0..n-1`, with no gaps and no duplicates.
- Moving, deleting, or reordering a card renumbers only the affected columns.
- A move to an invalid column or position is rejected, and nothing changes.

## Demo data

- A reset loads 20 fictional cards spread across all four columns (6 / 6 / 4 / 4).
- At least one card is overdue, one is in `Done` with a past due date (not flagged), and each priority is used.

## Out of scope for v1

- **Work-in-progress limits** (reserved for the demo)
- Archive and restore; filters by priority, assignee, tag, or overdue
- Renaming, reordering, adding, or removing columns
- Drag-and-drop
- Accounts, multiple boards, real-time collaboration, integrations, import/export, AI features

## Deviation from the Kanban Board Lab requirements

`kanban-board-lab/docs/requirements.md` specifies browser-local persistence. This baseline instead persists on a small **FastAPI + SQLite** backend, so that the demo can show backend and frontend work happening in parallel.

## Acceptance criteria

- All behaviour above works in a current Chrome browser at desktop and mobile widths.
- The backend automated tests cover: validation, create, edit, move between columns, reorder, position contiguity, delete, reset, not-found errors, and persistence across restarts.
- The frontend automated tests cover: rendering the board, create-card validation, the overdue label, search, moving, and error display.
- `README.md` documents how to install, run, test, and reset.
