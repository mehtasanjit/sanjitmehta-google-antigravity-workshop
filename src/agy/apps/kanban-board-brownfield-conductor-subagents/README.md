# Kanban Board: Brownfield Demo — Conductor and Subagents

A short Google Antigravity demo that starts from an **existing, working app** and adds a feature to it safely with the Conductor plugin and the eight SDLC subagents: understand the code, specify and plan, implement with subagents, review, and verify in the browser. Each demo copy gets the base `AGENTS.md` guidelines, the workspace memory rule, Conductor, and the subagents. Without the subagents, see [Kanban Board: Brownfield Demo — Conductor](../kanban-board-brownfield-conductor/).

## What's in this folder

```text
kanban-board-brownfield-conductor-subagents/
├── README.md               # This guide
├── setup-workspace.sh      # Creates a numbered demo copy of the app
└── kanban-board-app-N/     # Demo copies (gitignored)
```

The baseline app and the feature specs live in [`../kanban-board-brownfield/`](../kanban-board-brownfield/): `kanban-board-app/` and `feature-specs/`. All three variants copy from that one baseline.

Each demo copy contains the app, `AGENTS.md` (from `src/resources/workspace-guidance/agents/base.md`), the workspace memory rule in `.agents/rules/`, the Conductor plugin in `.agents/plugins/conductor/`, and the SDLC subagents in `.agents/agents/`. The copy is also a Git repository with the app committed as a single baseline, so `git diff` shows exactly what the agent changed. The feature specs are **not** copied, so the agent only sees a feature when you give it one.

## 1. Prerequisites

- Google Antigravity (desktop app or CLI)
- Git
- Python 3.13 in a virtual environment. Below, `<venv-python>` means that interpreter, for example `~/work/python/venvs/venv_1/bin/python`.
- Node.js 22 with npm. If `npm` is not on your `PATH` but you use nvm, run `nvm use 22` first.
- Python 3 and network access to GitHub, for the Conductor download at setup.

## 2. Clone the repository

```bash
git clone git@github.com:mehtasanjit/sanjitmehta-google-antigravity-workshop.git
cd sanjitmehta-google-antigravity-workshop/src/agy/apps/kanban-board-brownfield-conductor-subagents
```

## 3. Install the baseline dependencies (once)

The setup script copies `frontend/node_modules` into each demo copy, so install in the baseline first:

```bash
(cd ../kanban-board-brownfield/kanban-board-app/backend && <venv-python> -m pip install -r requirements.txt)
(cd ../kanban-board-brownfield/kanban-board-app/frontend && npm install)
```

Optional check that the baseline is healthy:

```bash
(cd ../kanban-board-brownfield/kanban-board-app/backend && <venv-python> -m pytest)
(cd ../kanban-board-brownfield/kanban-board-app/frontend && npm test && npm run build)
```

## 4. Create a demo copy

```bash
./setup-workspace.sh             # creates kanban-board-app-1 (then -2, -3, ...)
./setup-workspace.sh --dry-run   # shows the next name without creating anything
```

To pin Conductor, set `CONDUCTOR_REF` to a commit on its `main` branch; Conductor's release tags use an older layout without `plugin.json` and do not work here:

```bash
CONDUCTOR_REF=6e8f9a860bcd ./setup-workspace.sh
```

## 5. Run the app

Use two terminals, both inside `kanban-board-app-N/`:

```bash
# Terminal 1: API on http://localhost:8000 (API docs at /docs)
cd backend && <venv-python> -m uvicorn app.main:app --reload --port 8000

# Terminal 2: UI on http://localhost:5173
cd frontend && npm run dev
```

Open http://localhost:5173. You should see **Team Board** with 20 cards (6 / 6 / 4 / 4) and two cards marked **Overdue**. The first backend start creates and seeds `backend/data/kanban.db`.

> Only one copy can run at a time on ports 8000 and 5173. Stop the previous copy's servers first.

## 6. Open the copy in Antigravity

Open `kanban-board-app-N/` as the workspace (not the repository root). Check that:

- `AGENTS.md` is picked up as the workspace instructions.
- The memory rule in `.agents/rules/` is listed.
- The `/conductor:*` commands are available.
- The subagents in `.agents/agents/` are listed (for example `implementation-engineer`, `test-engineer`, `code-reviewer`).

## 7. Run the demo: story points

The feature request is [`feature-specs/04-story-points.md`](../kanban-board-brownfield/feature-specs/04-story-points.md). Paste its text where the prompts below say `<paste 04-story-points.md>`.

### Step 1: Understand the existing app (about 1 min)

```text
Read AGENTS.md and the docs folder, then skim the code. Give me a short summary of how this
app is structured, where the board rules live, and how it is tested. Don't change anything.
```

### Step 2: Specify and plan (about 3 min)

```text
/conductor:conductor-setup
```

Accept the defaults that match the existing app. Then start a track for the feature:

```text
/conductor:conductor-new-track
Here is a feature request from a teammate. Ask me the questions you need answered, then write
the specification and implementation plan for my approval. Don't write any code yet.

<paste 04-story-points.md>
```

Suggested answers if the agent asks:

| Question | Answer |
|---|---|
| Where are column totals calculated? | In the frontend, from the loaded board. No API change for totals. |
| How do existing databases get the new column? | Add it on startup if it's missing. Existing cards keep their data, with no points. |
| Is 0 a valid estimate? | Yes. Show "0 pts". Empty means not estimated. |
| Where do the badge and total go? | Badge next to the priority; total next to the card count, for example "4 · 13 pts". |
| Which demo cards get points? | Most cards outside Backlog; leave a few unestimated. |

Review the specification and plan, then approve them.

### Step 3: Implement with subagents (about 4 min)

```text
/conductor:conductor-implement
Plan approved. Use the subagents: implementation-engineer for the backend and frontend
changes, test-engineer for the tests. When done, run the backend tests, the frontend tests,
and the frontend build, and report the results.
```

### Step 4: Code review (about 2 min)

```text
/conductor:conductor-review
Also use the code-reviewer subagent to review git diff against the feature request and the
docs. Pay attention to existing data, validation, and anything that could break current
behaviour.
```

### Step 5: Verify in the browser (about 2 min)

Make sure both servers are running (restart the backend if the plan changed startup code), then:

```text
Use the browser to test the running app at http://localhost:5173:
1. Edit "Fix login timeout bug", set 5 points, save. Check the card shows "5 pts" and the
   To Do total goes up by 5.
2. Refresh the page and check the points are still there.
3. Try 1.5 and then 101 as points. Check both are rejected with a clear message.
4. Type "login" in the search box and check the To Do total does not change.
Report what you saw, with a screenshot.
```

### What "done" looks like

- All existing and new tests pass, and the frontend build succeeds.
- Cards show points; column totals are correct and unaffected by search.
- The existing database still works; no cards were lost.
- `git diff` shows changes to the database, backend, and frontend, including tests.

## Resetting between runs

- **Same copy, fresh data:** click **Reset board** in the UI, or `curl -X POST http://localhost:8000/api/board/reset`.
- **Same copy, undo the code changes:** `git restore . && git clean -fd` inside the copy returns it to the baseline (this also deletes any new files the agent created).
- **Start over completely:** run `./setup-workspace.sh` again for a new copy, or delete the old one with `rm -rf kanban-board-app-N`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `npm: command not found` | Run `nvm use 22`, or install Node.js 22. |
| Port 8000 or 5173 already in use | Stop the other servers. The UI must run on 5173, the only origin the backend allows. |
| UI shows "Cannot reach the server" | Start the backend (step 5, terminal 1). |
| After the feature, the backend fails with a missing column error | The startup migration is missing or wrong. Point the agent at it, or delete `backend/data/kanban.db` to recreate it. |
| Setup warns that `node_modules` is missing | Run step 3 first, or run `npm install` inside the copy's `frontend/`. |

## Other feature specs

The other specs in [`feature-specs/`](../kanban-board-brownfield/feature-specs/) use the same flow:

- `01-wip-limits.md`: changes the core board rules. Richer, but takes longer.
- `02-archive-cards.md`: the biggest change: database, ordering rules, and a new view.
- `03-filters.md`: frontend only. The quickest option, but doesn't touch the database or backend.
