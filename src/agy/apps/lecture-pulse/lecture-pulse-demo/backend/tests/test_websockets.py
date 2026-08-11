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


def test_websocket_payload_validation(client: TestClient):
    """Tests that invalid WebSocket payloads are gracefully ignored and valid ones are processed."""
    # 1. Create a session first to get a code
    response = client.post(
        "/api/sessions",
        json={"title": "WS Validation Test", "description": "Desc"},
    )
    code = response.json()["code"]

    # 2. Connect to the WebSocket
    with client.websocket_connect(f"/ws/{code}") as websocket:
        # Send a pulse event with an invalid pulse_type
        websocket.send_json({"type": "PULSE_EVENT", "pulse_type": "invalid_type"})

        # Send a valid pulse event to ensure the connection is still alive and processing
        websocket.send_json({"type": "PULSE_EVENT", "pulse_type": "got_it"})

        # We should receive the broadcast for the valid pulse event
        data = websocket.receive_json()
        assert data["type"] == "PULSE_EVENT"
        assert data["pulse_totals"]["got_it"] == 1
        assert data["pulse_totals"]["slower"] == 0

        # Create a question
        websocket.send_json({
            "type": "NEW_QUESTION",
            "text": "What is validation?",
        })
        q_data = websocket.receive_json()
        q_id = q_data["question"]["id"]

        # Send an update with an invalid status
        websocket.send_json({
            "type": "UPDATE_QUESTION_STATUS",
            "question_id": q_id,
            "status": "active",
        })

        # Send a valid status update
        websocket.send_json({
            "type": "UPDATE_QUESTION_STATUS",
            "question_id": q_id,
            "status": "dismissed",
        })

        # We should only get a message for the valid "dismissed" status update
        data = websocket.receive_json()
        assert data["type"] == "UPDATE_QUESTION_STATUS"
        assert data["question_id"] == q_id
        assert data["status"] == "dismissed"


@pytest.mark.asyncio
async def test_e2e_complete_flow():
    """Test full flow: create/join session, and live interaction over WebSockets."""
    from httpx import AsyncClient
    from backend.app.main import app
    
    try:
        from httpx import ASGITransport
        transport = ASGITransport(app=app)
        async_client_kwargs = {"transport": transport, "base_url": "http://test"}
    except ImportError:
        async_client_kwargs = {"app": app, "base_url": "http://test"}

    # 1. Create a session using AsyncClient
    async with AsyncClient(**async_client_kwargs) as ac:
        create_res = await ac.post(
            "/api/sessions",
            json={"title": "E2E Lecture", "description": "E2E async integration test"},
        )
        assert create_res.status_code == 200
        session_data = create_res.json()
        code = session_data["code"]
        assert session_data["title"] == "E2E Lecture"
        assert code is not None

        # Join Session (fetch session details)
        get_res = await ac.get(f"/api/sessions/{code}")
        assert get_res.status_code == 200
        details = get_res.json()
        assert details["title"] == "E2E Lecture"
        assert details["pulse_totals"] == {"slower": 0, "confused": 0, "got_it": 0}

    # 2. Open WebSocket connection to test real-time broadcasts
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/{code}") as ws:
            # Send a pulse via websocket
            # (Note: Frontend sends lowercase type 'pulse' and 'pulse_type')
            ws.send_json({"type": "pulse", "pulse_type": "got_it"})
            data = ws.receive_json()
            assert data["type"] == "PULSE_EVENT"
            assert data["pulse_totals"]["got_it"] == 1

            # Submit a question via websocket
            ws.send_json({"type": "new_question", "text": "Is this E2E test running?"})
            data = ws.receive_json()
            assert data["type"] == "NEW_QUESTION"
            assert data["question"]["text"] == "Is this E2E test running?"
            q_id = data["question"]["id"]

            # Upvote the question via websocket
            ws.send_json({"type": "upvote_question", "question_id": q_id})
            data = ws.receive_json()
            assert data["type"] == "UPVOTE_QUESTION"
            assert data["question_id"] == q_id
            assert data["upvotes"] == 1

            # Moderate the question status (answered) via websocket
            ws.send_json({
                "type": "update_question_status",
                "question_id": q_id,
                "status": "answered"
            })
            data = ws.receive_json()
            assert data["type"] == "UPDATE_QUESTION_STATUS"
            assert data["question_id"] == q_id
            assert data["status"] == "answered"

