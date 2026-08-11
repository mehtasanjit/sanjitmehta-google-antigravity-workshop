"""Main entry point for Lecture Pulse FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database import init_db
from backend.app.routers import sessions, websockets


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes and cleans up application resources."""
    await init_db()
    yield


app = FastAPI(
    title="Lecture Pulse API",
    description="Real-time classroom engagement and feedback platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "ok",
        "service": "lecture-pulse-api",
        "version": "1.0.0"
    }


# Include Routers
app.include_router(sessions.router)
app.include_router(websockets.router)
