from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .api import router as api_router
from .models import Complaint
from .seed import seed_db

# Automatically create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Banking Complaint Resolution Workbench API",
    description="Backend API for managing and resolving customer banking complaints",
    version="1.0.0",
)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        if db.query(Complaint).count() == 0:
            seed_db(db)
    finally:
        db.close()

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "name": "Banking Complaint Resolution Workbench API",
        "status": "healthy",
        "version": "1.0.0",
    }
