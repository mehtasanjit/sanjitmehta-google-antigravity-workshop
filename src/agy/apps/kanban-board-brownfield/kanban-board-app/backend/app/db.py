"""SQLite connection handling, schema, and database path configuration."""

import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "kanban.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS columns (
    id       INTEGER PRIMARY KEY,
    name     TEXT    NOT NULL UNIQUE,
    position INTEGER NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cards (
    id          TEXT    PRIMARY KEY,
    column_id   INTEGER NOT NULL REFERENCES columns(id),
    position    INTEGER NOT NULL,
    title       TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    priority    TEXT    NOT NULL CHECK (priority IN ('Low', 'Medium', 'High')),
    assignee    TEXT    NOT NULL DEFAULT '',
    tags        TEXT    NOT NULL DEFAULT '[]',
    due_date    TEXT,
    created_at  TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL,
    UNIQUE (column_id, position)
);
"""


def db_path() -> Path:
    """Return the database path, read from KANBAN_DB_PATH on every call."""
    return Path(os.environ.get("KANBAN_DB_PATH", str(DEFAULT_DB_PATH)))


def connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    # isolation_level=None: transactions are managed explicitly in transaction().
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    """Open a connection, run the block in one write transaction, then close."""
    conn = connect()
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def create_schema(conn: sqlite3.Connection) -> None:
    for statement in SCHEMA.split(";"):
        if statement.strip():
            conn.execute(statement)
