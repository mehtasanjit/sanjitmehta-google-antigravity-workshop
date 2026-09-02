# Technology Stack: Banking Complaint Resolution Workbench

## Core Architecture
- **Backend Framework:** FastAPI (Python 3.13)
- **Runtime Interpreter:** `/home/sanjitmehta/work/python/venv_3_13_14_1/bin/python`
- **Application Server:** Uvicorn ASGI Server
- **Data Persistence:** SQLite database (with SQLAlchemy ORM / direct schema management)
- **Data Integrity & Validation:** Pydantic models for request/response schemas
- **Frontend Architecture:** React 18 / 19 + Vite + Tailwind CSS for a modern, reactive, user-friendly, and responsive Kanban workbench SPA
- **Testing Suite:** Pytest + FastAPI TestClient (HTTPX) for backend API; Vitest / React Testing Library for frontend where applicable
- **Data Generation:** Synthetic banking complaint seeder with realistic fake customers, accounts, transactions, and categories
