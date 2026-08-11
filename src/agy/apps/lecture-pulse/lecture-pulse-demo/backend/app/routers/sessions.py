"""Router for session management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
import aiosqlite

from backend.app import database, schemas

router = APIRouter(prefix="/api", tags=["sessions"])


@router.post("/sessions", response_model=schemas.SessionResponse)
async def create_session(
    session_data: schemas.SessionCreate,
    db: aiosqlite.Connection = Depends(database.get_db),
):
    """Creates a new lecture session with a unique code."""
    code = await database.generate_unique_code(db)
    insert_query = (
        "INSERT INTO sessions (title, description, code) VALUES (?, ?, ?)"
    )
    async with db.execute(
        insert_query, (session_data.title, session_data.description, code)
    ) as cursor:
        session_id = cursor.lastrowid
    await db.commit()

    select_query = (
        "SELECT title, code, created_at FROM sessions WHERE id = ?"
    )
    async with db.execute(select_query, (session_id,)) as cursor:
        row = await cursor.fetchone()

    return {
        "title": row["title"],
        "code": row["code"],
        "created_at": str(row["created_at"]),
    }


@router.get(
    "/sessions/{code}", response_model=schemas.SessionDetailsResponse
)
async def get_session(
    code: str,
    db: aiosqlite.Connection = Depends(database.get_db),
):
    """Fetches session metadata, pulse totals, and the sorted Q&A feed."""
    session_query = "SELECT * FROM sessions WHERE code = ?"
    async with db.execute(session_query, (code,)) as cursor:
        session_row = await cursor.fetchone()

    if not session_row:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get pulse totals (initialized with standard 3 keys to 0)
    pulse_totals = {"slower": 0, "confused": 0, "got_it": 0}
    pulse_query = (
        "SELECT type, COUNT(*) as count FROM pulses "
        "WHERE session_code = ? GROUP BY type"
    )
    async with db.execute(pulse_query, (code,)) as cursor:
        pulse_rows = await cursor.fetchall()
        for row in pulse_rows:
            p_type = row["type"].lower()
            pulse_totals[p_type] = row["count"]

    # Get questions ordered by upvotes DESC, created_at DESC
    questions_query = (
        "SELECT id, session_code, text, upvotes, status, created_at "
        "FROM questions WHERE session_code = ? "
        "ORDER BY upvotes DESC, created_at DESC"
    )
    questions = []
    async with db.execute(questions_query, (code,)) as cursor:
        question_rows = await cursor.fetchall()
        for row in question_rows:
            questions.append({
                "id": row["id"],
                "session_code": row["session_code"],
                "text": row["text"],
                "upvotes": row["upvotes"],
                "status": row["status"],
                "created_at": str(row["created_at"]),
            })

    return {
        "code": session_row["code"],
        "title": session_row["title"],
        "description": session_row["description"],
        "created_at": str(session_row["created_at"]),
        "pulse_totals": pulse_totals,
        "questions": questions,
    }
