import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "kanban-test.db"
    monkeypatch.setenv("KANBAN_DB_PATH", str(path))
    return path


@pytest.fixture
def client(db_file):
    # The context manager runs the lifespan, which creates and seeds the temporary DB.
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def board(client):
    return client.get("/api/board").json()


def column_by_name(board: dict, name: str) -> dict:
    return next(column for column in board["columns"] if column["name"] == name)


def assert_contiguous(board: dict) -> None:
    for column in board["columns"]:
        positions = [card["position"] for card in column["cards"]]
        assert positions == list(range(len(positions))), column["name"]
        assert all(card["column_id"] == column["id"] for card in column["cards"])
