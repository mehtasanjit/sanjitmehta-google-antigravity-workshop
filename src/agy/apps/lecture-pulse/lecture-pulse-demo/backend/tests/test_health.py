"""Tests for application health check endpoint."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Tests the /api/health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
