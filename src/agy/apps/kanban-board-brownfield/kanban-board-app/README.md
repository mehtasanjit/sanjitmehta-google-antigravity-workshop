# Kanban Board (brownfield baseline)

A small, complete, tested Kanban board: **FastAPI + SQLite** backend and **React + TypeScript (Vite)** frontend. It is the existing application that the Antigravity brownfield demo starts from.

- What it does: [docs/spec.md](docs/spec.md)
- How it is built: [docs/architecture.md](docs/architecture.md)
- Tools and versions: [docs/tech-stack.md](docs/tech-stack.md)

> Work-in-progress (WIP) limits are intentionally **not** implemented. They are the feature added live in the demo.

## Prerequisites

- Python 3.13 in a virtual environment. Below, `<venv-python>` means that interpreter, for example `~/work/python/venvs/venv_1/bin/python`.
- Node.js 22 with npm.

## Install

```bash
cd backend && <venv-python> -m pip install -r requirements.txt
cd ../frontend && npm install
```

## Run

Use two terminals:

```bash
# Terminal 1: API on http://localhost:8000 (OpenAPI docs at /docs)
cd backend && <venv-python> -m uvicorn app.main:app --reload --port 8000

# Terminal 2: UI on http://localhost:5173 (proxies /api to :8000)
cd frontend && npm run dev
```

On first start the backend creates `backend/data/kanban.db` and seeds 20 fictional cards. Set `KANBAN_DB_PATH` to use a different file.

## Test

```bash
cd backend && <venv-python> -m pytest       # API and business rules (temporary DB per test)
cd frontend && npm test                     # Components (API mocked)
cd frontend && npm run build                # Type-check and production build
```

## Reset the demo data

Use either:

- **Reset board** in the UI (asks for confirmation), or
- `curl -X POST http://localhost:8000/api/board/reset`

To start completely fresh, stop the backend and delete `backend/data/kanban.db`.

## Layout

```text
backend/app/    main.py · api.py · schemas.py · service.py · repository.py · db.py · seed.py
backend/tests/  pytest suite
frontend/src/   api.ts · types.ts · utils.ts · App.tsx · components/ · __tests__/
docs/           spec, architecture, tech stack
```

All board rules live in `backend/app/service.py`. The frontend only displays state and never enforces rules itself.
