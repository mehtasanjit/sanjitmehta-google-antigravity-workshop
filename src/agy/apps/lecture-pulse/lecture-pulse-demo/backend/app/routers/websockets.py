"""Router for WebSocket connection endpoints."""

import aiosqlite
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from backend.app import database
from backend.app.websocket_manager import manager

router = APIRouter(tags=["websockets"])


@router.websocket("/ws/{session_code}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_code: str,
    db: aiosqlite.Connection = Depends(database.get_db),
):
    """Handles bidirectional WebSocket messages for a session."""
    query = "SELECT 1 FROM sessions WHERE code = ?"
    async with db.execute(query, (session_code,)) as cursor:
        row = await cursor.fetchone()

    if not row:
        await websocket.close(code=4004, reason="Session not found")
        return

    await manager.connect(session_code, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            if event_type == "PULSE_EVENT":
                pulse_type = data.get("pulse_type")
                if pulse_type:
                    insert_query = (
                        "INSERT INTO pulses (session_code, type) "
                        "VALUES (?, ?)"
                    )
                    await db.execute(insert_query, (session_code, pulse_type))
                    await db.commit()

                    # Query updated pulse totals
                    totals = {"slower": 0, "confused": 0, "got_it": 0}
                    totals_query = (
                        "SELECT type, COUNT(*) as count "
                        "FROM pulses WHERE session_code = ? "
                        "GROUP BY type"
                    )
                    async with db.execute(totals_query, (session_code,)) as cursor:
                        rows = await cursor.fetchall()
                        for row_item in rows:
                            p_type = row_item["type"].lower()
                            totals[p_type] = row_item["count"]

                    await manager.broadcast(
                        session_code,
                        {"type": "PULSE_EVENT", "pulse_totals": totals},
                    )

            elif event_type == "NEW_QUESTION":
                text = data.get("text")
                if text:
                    insert_query = (
                        "INSERT INTO questions (session_code, text) "
                        "VALUES (?, ?)"
                    )
                    async with db.execute(
                        insert_query, (session_code, text)
                    ) as cursor:
                        q_id = cursor.lastrowid
                    await db.commit()

                    select_query = "SELECT * FROM questions WHERE id = ?"
                    async with db.execute(select_query, (q_id,)) as cursor:
                        q_row = await cursor.fetchone()

                    await manager.broadcast(
                        session_code,
                        {
                            "type": "NEW_QUESTION",
                            "question": {
                                "id": q_row["id"],
                                "session_code": q_row["session_code"],
                                "text": q_row["text"],
                                "upvotes": q_row["upvotes"],
                                "status": q_row["status"],
                                "created_at": str(q_row["created_at"]),
                            },
                        },
                    )

            elif event_type == "UPVOTE_QUESTION":
                q_id = data.get("question_id")
                if q_id is not None:
                    update_query = (
                        "UPDATE questions SET upvotes = upvotes + 1 "
                        "WHERE id = ?"
                    )
                    await db.execute(update_query, (q_id,))
                    await db.commit()

                    select_query = "SELECT upvotes FROM questions WHERE id = ?"
                    async with db.execute(select_query, (q_id,)) as cursor:
                        q_row = await cursor.fetchone()

                    if q_row:
                        await manager.broadcast(
                            session_code,
                            {
                                "type": "UPVOTE_QUESTION",
                                "question_id": q_id,
                                "upvotes": q_row["upvotes"],
                            },
                        )

            elif event_type == "UPDATE_QUESTION_STATUS":
                q_id = data.get("question_id")
                status = data.get("status")
                if q_id is not None and status:
                    update_query = (
                        "UPDATE questions SET status = ? WHERE id = ?"
                    )
                    await db.execute(update_query, (status, q_id))
                    await db.commit()

                    await manager.broadcast(
                        session_code,
                        {
                            "type": "UPDATE_QUESTION_STATUS",
                            "question_id": q_id,
                            "status": status,
                        },
                    )
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        manager.disconnect(session_code, websocket)
