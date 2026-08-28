# Technology Stack - Banking Internal Complaint Tracker

## 1. Backend Architecture
*   **Language:** Python 3.13.14
*   **API Framework:** FastAPI
    *   *Why:* Fast, highly performant, handles async request loops natively, and automatically generates interactive OpenAPI/Swagger docs at `/docs`.
*   **Database:** SQLite
    *   *Why:* Zero-configuration, single-file relational database. It is robust, transaction-safe (ACID), and requires no separate server processes.
*   **ORM:** SQLAlchemy or SQLModel
    *   *Why:* Provides a clean, pythonic way to interact with SQLite schemas.

## 2. Frontend Architecture
*   **UI Framework:** React.js (TypeScript)
    *   *Why:* Rich component model, powerful reactive state, perfect for building interactive Kanban boards and workflow timelines.
*   **Build Tool:** Vite
    *   *Why:* Next-generation frontend tooling. Offers instant hot module reloading (HMR) and extremely fast production builds.
*   **API Client:** Axios or native `fetch`
    *   *Why:* Simple, clean promise-based HTTP client to communicate with the FastAPI backend.

## 3. Styling & Layout
*   **Styling:** Custom Vanilla CSS (with modern CSS custom properties and Flexbox/Grid).
    *   *Why:* Highly flexible, ensures we can implement the exact "Modern FinTech (Charcoal & Mint)" visual design and custom clean card shadows without adding bloated UI frameworks.

## 4. Development & Running Commands
*   **Backend Run Command:** `uvicorn main:app --reload`
*   **Frontend Run Command:** `npm run dev`
