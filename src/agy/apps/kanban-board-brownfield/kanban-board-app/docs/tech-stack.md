# Kanban Board — Technical Stack (v1 baseline)

**Status:** Implemented. Exact versions are pinned in `requirements.txt` and `package-lock.json`.

## Runtimes

| Runtime | Version | Source |
|---|---|---|
| Python | 3.13.x (validated on 3.13.7) | Each participant's own virtual environment, written as `<venv-python>` below |
| Node.js | 22.x LTS | Local installation (npm is bundled) |

## Backend (`backend/`)

| Concern | Choice | Notes |
|---|---|---|
| Web framework | FastAPI | Auto-generated OpenAPI docs at `/docs` |
| ASGI server | Uvicorn | `uvicorn app.main:app --reload --port 8000` |
| Validation | Pydantic v2 (via FastAPI) | Request and response schemas |
| Storage | SQLite via Python's built-in `sqlite3` | No ORM; keeps dependencies minimal |
| Tests | pytest + FastAPI `TestClient` (httpx) | Temporary database per test |
| Dependencies | `requirements.txt`, installed with `<venv-python> -m pip install -r requirements.txt` | pip in the user-provided venv; no second package manager |

**Runtime dependencies:** `fastapi`, `uvicorn`
**Test dependencies:** `pytest`, `httpx`

## Frontend (`frontend/`)

| Concern | Choice | Notes |
|---|---|---|
| Build / dev server | Vite | Dev server on `:5173`, proxies `/api` to `:8000` |
| UI | React + TypeScript | Function components and hooks; no state library |
| Styling | Plain CSS (one stylesheet) | No UI framework |
| HTTP | `fetch`, wrapped in `src/api.ts` | No HTTP library |
| Tests | Vitest + React Testing Library + jsdom | `npm test` |
| Package manager | npm, with `package-lock.json` committed | |

**Validated versions (lockfile):** React 19.3, Vite 8.3, TypeScript 7.0, Vitest 5.0, React Testing Library 16.3, jsdom 29.1. **Backend (`requirements.txt`, pinned):** FastAPI 0.137, Uvicorn 0.49, pytest 9.1, httpx 0.28.

**Deliberately not used:** drag-and-drop libraries, CSS frameworks, state-management libraries, ORMs. Each would add surface area without a v1 need.

## Commands

| Task | Command |
|---|---|
| Install backend | `cd backend && <venv-python> -m pip install -r requirements.txt` |
| Run backend | `cd backend && <venv-python> -m uvicorn app.main:app --reload --port 8000` |
| Test backend | `cd backend && <venv-python> -m pytest -q` |
| Install frontend | `cd frontend && npm install` |
| Run frontend | `cd frontend && npm run dev` → http://localhost:5173 |
| Test frontend | `cd frontend && npm test` |
| Build frontend | `cd frontend && npm run build` |

## Conventions

- Python: type hints everywhere; all SQL in `repository.py`; all rules in `service.py`.
- TypeScript: `strict` mode; API types in `types.ts`; only `api.ts` calls `fetch`.
- Tests sit next to their layer (`backend/tests/`, `frontend/src/__tests__/`) and must pass before any change is considered done.
- No secrets, credentials, or real personal data anywhere in the repository.
