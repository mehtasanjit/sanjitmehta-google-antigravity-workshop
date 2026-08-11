"""Pytest fixtures for Lecture Pulse backend tests."""

import os
import sqlite3
import pytest
from fastapi.testclient import TestClient

# Set the environment variable before importing application modules
os.environ["DATABASE_PATH"] = "test_sessions.db"

from backend.app.main import app


@pytest.fixture(autouse=True, scope="session")
def setup_test_database_file():
    """Sets up the test database file and cleans it up after tests."""
    if os.path.exists("test_sessions.db"):
        try:
            os.remove("test_sessions.db")
        except Exception:
            pass

    yield

    if os.path.exists("test_sessions.db"):
        try:
            os.remove("test_sessions.db")
        except Exception:
            pass


@pytest.fixture(autouse=True)
def clean_tables():
    """Cleans tables before each test to ensure isolation."""
    conn = sqlite3.connect("test_sessions.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            code TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pulses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_code TEXT NOT NULL,
            type TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_code TEXT NOT NULL,
            text TEXT NOT NULL,
            upvotes INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("DELETE FROM sessions")
    cursor.execute("DELETE FROM pulses")
    cursor.execute("DELETE FROM questions")
    conn.commit()
    conn.close()


@pytest.fixture
def client():
    """A TestClient for testing the FastAPI application."""
    with TestClient(app) as tc:
        yield tc
