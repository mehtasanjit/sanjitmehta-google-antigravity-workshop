# Technology Stack: Lecture Pulse

## Core Technologies
- **Backend Language & Runtime**: Python 3.11+
- **Backend Framework**: FastAPI with Uvicorn (ASGI server)
- **Real-Time Protocol**: Native WebSockets (`fastapi.WebSocket` for bi-directional live communication)
- **Frontend Framework**: React + Vite (JavaScript / TypeScript)
- **Styling**: Vanilla CSS / Tailwind CSS for responsive, sleek UI design
- **Database & State Management**: SQLite / In-Memory Session Store for instant low-latency reads and writes

## Testing & Tooling
- **Backend Testing**: `pytest`, `httpx` (Async Client testing)
- **Frontend Testing**: `vitest` / React Testing Library
- **Package Management**: `pip` / `venv` or `poetry`
- **Linting & Code Quality**: `ruff` / `black` (Python), `eslint` (JavaScript/TypeScript)
