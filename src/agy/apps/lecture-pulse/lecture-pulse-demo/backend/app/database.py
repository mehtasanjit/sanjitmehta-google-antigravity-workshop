import os
import random
import string
import aiosqlite
from typing import AsyncGenerator

DB_PATH = os.environ.get("DATABASE_PATH", "sessions.db")


async def init_db() -> None:
    """Initializes the SQLite database schema."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                code TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pulses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_code TEXT NOT NULL,
                type TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_code TEXT NOT NULL,
                text TEXT NOT NULL,
                upvotes INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_code "
            "ON sessions(code)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_pulses_session_code "
            "ON pulses(session_code)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_questions_session_code "
            "ON questions(session_code)"
        )
        await db.commit()


async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """FastAPI Dependency for accessing SQLite database."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def generate_unique_code(db: aiosqlite.Connection) -> str:
    """Generates a unique room code (e.g. LP-X9K2F)."""
    while True:
        chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        code = f"LP-{chars}"
        query = "SELECT 1 FROM sessions WHERE code = ?"
        async with db.execute(query, (code,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return code


generate_session_code = generate_unique_code
