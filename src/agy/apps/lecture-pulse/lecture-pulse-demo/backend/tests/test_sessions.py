"""Tests for session management API endpoints."""

from fastapi.testclient import TestClient


def test_create_session(client: TestClient):
    """Tests POST /api/sessions endpoint."""
    response = client.post(
        "/api/sessions",
        json={"title": "Introduction to Python", "description": "L1 Basics"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Introduction to Python"
    assert "code" in data
    assert data["code"].startswith("LP-")
    assert len(data["code"]) == 6
    assert "created_at" in data


def test_get_session_details(client: TestClient):
    """Tests GET /api/sessions/{code} endpoint."""
    # First, create a session
    post_resp = client.post(
        "/api/sessions",
        json={"title": "Data Structures", "description": "L2 Lists and Dicts"},
    )
    assert post_resp.status_code == 200
    session_code = post_resp.json()["code"]

    # Fetch the details
    get_resp = client.get(f"/api/sessions/{session_code}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["code"] == session_code
    assert data["title"] == "Data Structures"
    assert data["description"] == "L2 Lists and Dicts"
    assert "created_at" in data
    assert data["pulse_totals"] == {"slower": 0, "confused": 0, "got_it": 0}
    assert data["questions"] == []


def test_get_session_not_found(client: TestClient):
    """Tests GET /api/sessions/{code} with a non-existent code."""
    response = client.get("/api/sessions/LP-999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"
