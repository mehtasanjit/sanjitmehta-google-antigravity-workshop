# Technology Stack: Banking Complaint Resolution Workbench

## 1. Frontend Layer
- **Framework**: React (v18+) with TypeScript for static type safety and component model.
- **Styling**: Vanilla CSS (CSS Modules or standard stylesheet architecture) to deliver custom, lightweight, high-performance banking UI styling, strictly avoiding TailwindCSS as per design conventions.
- **State Management**: React Context / Hooks for clean, localized, and trace-friendly UI state.

## 2. Backend Layer
- **Language**: Python (v3.13.14) using the user's active virtual environment.
- **Framework**: FastAPI (v0.110+) for high-performance async API development, automatic OpenAPI documentation, and typed request validation via Pydantic.
- **ORM / Query Engine**: SQLAlchemy (v2.0+) for clean, Pythonic, and type-safe database mapping and query building.

## 3. Database & Storage
- **Database Engine**: SQLite (serverless, file-based SQL engine) as the primary storage. This is highly suitable for an MVP and supports relational integrity and transactions out-of-the-box.
- **Audit Storage**: Relational SQLite table with a datetime timestamp, user identifier, event type, before/after JSON snapshots, and detailed comments.

## 4. Testing & Toolchain
- **Frontend Testing**: Vitest and React Testing Library.
- **Backend Testing**: Pytest for unit and integration testing.
- **Code Linters & Formatters**: Ruff (Python linting and formatting) and ESLint/Prettier (TypeScript).
