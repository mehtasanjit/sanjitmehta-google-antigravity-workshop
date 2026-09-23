# Technology Stack: Kanban Board Lab

## Architectural Overview
Kanban Board Lab uses a decoupled client-server architecture:
- **Frontend**: A reactive, accessible Single Page Application built with React 18+, TypeScript, and Vite, styled using Tailwind CSS.
- **Backend**: A lightweight, high-performance Python REST API (FastAPI) enforcing board invariants, column WIP limits, card state transitions, and persistence.
- **Database**: An embedded, lightweight local database (SQLite via SQLAlchemy/SQLModel) storing boards, columns, and cards durably on device.

## Core Components

### Frontend
- **Framework**: React 18+
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Drag & Drop / Keyboard Accessibility**: `@dnd-kit` or native drag-and-drop with keyboard action menus
- **Testing**: Vitest + React Testing Library

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Data Validation & Schemas**: Pydantic v2
- **Testing**: `pytest`, `httpx` (TestClient)

### Database & Persistence
- **Database**: SQLite (local database file `kanban.db`)
- **Data Layer**: SQLAlchemy / SQLModel with SQLite foreign keys and transaction management

### Environment & Tooling
- **Node.js**: v18+ (for frontend toolchain)
- **Python Virtual Environment**: Project-local virtual environment (`.venv`)
