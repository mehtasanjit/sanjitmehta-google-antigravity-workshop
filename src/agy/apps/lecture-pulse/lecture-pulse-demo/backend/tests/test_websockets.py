"""Tests for real-time WebSocket features and event broadcasting."""

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


def test_websocket_endpoints(client: TestClient):
    """Tests full websocket event lifecycle for a valid session."""
    # 1. Create a session first to get a code
    response = client.post(
        "/api/sessions",
        json={"title": "WS Test", "description": "WS Desc"},
    )
    code = response.json()["code"]

    # 2. Connect to the WebSocket
    with client.websocket_connect(f"/ws/{code}") as websocket:
        # Send a pulse event
        websocket.send_json({"type": "PULSE_EVENT", "pulse_type": "slower"})
        data = websocket.receive_json()
        assert data["type"] == "PULSE_EVENT"
        assert data["pulse_totals"]["slower"] == 1

        # Send a new question
        websocket.send_json({
            "type": "NEW_QUESTION",
            "text": "What is WebSockets?",
        })
        data = websocket.receive_json()
        assert data["type"] == "NEW_QUESTION"
        assert data["question"]["text"] == "What is WebSockets?"
        assert data["question"]["upvotes"] == 0
        assert data["question"]["status"] == "active"
        q_id = data["question"]["id"]

        # Send upvote question
        websocket.send_json({"type": "UPVOTE_QUESTION", "question_id": q_id})
        data = websocket.receive_json()
        assert data["type"] == "UPVOTE_QUESTION"
        assert data["question_id"] == q_id
        assert data["upvotes"] == 1

        # Update question status
        websocket.send_json({
            "type": "UPDATE_QUESTION_STATUS",
            "question_id": q_id,
            "status": "answered",
        })
        data = websocket.receive_json()
        assert data["type"] == "UPDATE_QUESTION_STATUS"
        assert data["question_id"] == q_id
        assert data["status"] == "answered"


def test_websocket_non_existent_session(client: TestClient):
    """Tests that connecting to a non-existent session code is rejected."""
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws/LP-999"):
            pass
    assert exc.value.code == 4004
