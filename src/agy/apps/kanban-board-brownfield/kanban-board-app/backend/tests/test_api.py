from fastapi.testclient import TestClient

from app.main import app
from conftest import assert_contiguous, column_by_name


def ids(column: dict) -> list[str]:
    return [card["id"] for card in column["cards"]]


# --- Board and seed ---------------------------------------------------------


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_board_has_fixed_columns_and_seed_cards(board):
    assert board["title"] == "Team Board"
    assert [c["name"] for c in board["columns"]] == ["Backlog", "To Do", "In Progress", "Done"]
    cards = [card for column in board["columns"] for card in column["cards"]]
    assert len(cards) == 20
    assert {card["priority"] for card in cards} == {"Low", "Medium", "High"}
    assert all(column["cards"] for column in board["columns"])
    assert_contiguous(board)


# --- Create -----------------------------------------------------------------


def test_create_card_goes_to_bottom_with_defaults(client, board):
    todo = column_by_name(board, "To Do")
    response = client.post("/api/cards", json={"column_id": todo["id"], "title": "  New task  "})
    assert response.status_code == 201
    card = response.json()
    assert card["title"] == "New task"
    assert card["priority"] == "Medium"
    assert card["position"] == len(todo["cards"])
    assert card["tags"] == [] and card["due_date"] is None
    assert card["created_at"] == card["updated_at"]


def test_create_rejects_blank_title_and_saves_nothing(client, board):
    todo = column_by_name(board, "To Do")
    response = client.post("/api/cards", json={"column_id": todo["id"], "title": "   "})
    assert response.status_code == 422
    assert response.json() == {"detail": "title: Title is required"}
    assert client.get("/api/board").json() == board


def test_create_rejects_invalid_fields(client, board):
    column_id = board["columns"][0]["id"]
    bad_payloads = [
        {"title": "x" * 121},
        {"title": "ok", "priority": "Urgent"},
        {"title": "ok", "description": "d" * 2001},
        {"title": "ok", "assignee": "a" * 61},
        {"title": "ok", "tags": ["t" * 21]},
        {"title": "ok", "due_date": "not-a-date"},
    ]
    for payload in bad_payloads:
        response = client.post("/api/cards", json={"column_id": column_id, **payload})
        assert response.status_code == 422, payload
        assert isinstance(response.json()["detail"], str)


def test_create_dedupes_tags(client, board):
    column_id = board["columns"][0]["id"]
    response = client.post(
        "/api/cards",
        json={"column_id": column_id, "title": "Tags", "tags": ["ui", "UI", " docs ", "ui"]},
    )
    assert response.json()["tags"] == ["ui", "docs"]


def test_create_in_unknown_column_is_404(client):
    response = client.post("/api/cards", json={"column_id": 999, "title": "Nowhere"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Column not found"}


# --- Edit -------------------------------------------------------------------


def test_edit_changes_fields_but_not_identity_or_placement(client, board):
    original = column_by_name(board, "In Progress")["cards"][1]
    response = client.patch(
        f"/api/cards/{original['id']}",
        json={"title": "Renamed", "priority": "Low", "tags": ["x"], "due_date": "2030-01-31"},
    )
    assert response.status_code == 200
    card = response.json()
    assert (card["title"], card["priority"], card["tags"], card["due_date"]) == (
        "Renamed", "Low", ["x"], "2030-01-31",
    )
    for field in ("id", "created_at", "column_id", "position", "description", "assignee"):
        assert card[field] == original[field]
    assert card["updated_at"] > original["updated_at"]


def test_edit_can_clear_due_date(client, board):
    card = column_by_name(board, "To Do")["cards"][0]
    assert card["due_date"] is not None
    response = client.patch(f"/api/cards/{card['id']}", json={"due_date": None})
    assert response.json()["due_date"] is None


def test_edit_rejects_placement_fields_and_blank_title(client, board):
    card_id = board["columns"][0]["cards"][0]["id"]
    assert client.patch(f"/api/cards/{card_id}", json={"position": 3}).status_code == 422
    assert client.patch(f"/api/cards/{card_id}", json={"title": ""}).status_code == 422
    assert client.patch(f"/api/cards/{card_id}", json={"title": None}).status_code == 422
    assert client.get("/api/board").json() == board


def test_edit_unknown_card_is_404(client):
    response = client.patch("/api/cards/missing", json={"title": "x"})
    assert response.status_code == 404


# --- Move and reorder -------------------------------------------------------


def test_move_to_bottom_of_next_column(client, board):
    todo, doing = column_by_name(board, "To Do"), column_by_name(board, "In Progress")
    card_id = todo["cards"][0]["id"]
    response = client.post(
        f"/api/cards/{card_id}/move",
        json={"column_id": doing["id"], "position": len(doing["cards"])},
    )
    assert response.status_code == 200
    after = response.json()
    assert ids(column_by_name(after, "In Progress")) == ids(doing) + [card_id]
    assert ids(column_by_name(after, "To Do")) == ids(todo)[1:]
    assert_contiguous(after)


def test_reorder_within_column(client, board):
    doing = column_by_name(board, "In Progress")
    *others, last = ids(doing)
    response = client.post(
        f"/api/cards/{last}/move", json={"column_id": doing["id"], "position": 0}
    )
    after = response.json()
    assert ids(column_by_name(after, "In Progress")) == [last, *others]
    assert_contiguous(after)


def test_move_to_same_position_is_a_no_op(client, board):
    card = board["columns"][0]["cards"][0]
    response = client.post(
        f"/api/cards/{card['id']}/move", json={"column_id": card["column_id"], "position": 0}
    )
    assert response.json() == board


def test_invalid_moves_are_rejected_and_change_nothing(client, board):
    todo = column_by_name(board, "To Do")
    card_id = todo["cards"][0]["id"]
    invalid = [
        ({"column_id": todo["id"], "position": len(todo["cards"])}, 422),  # past end, same column
        ({"column_id": board["columns"][0]["id"], "position": 99}, 422),
        ({"column_id": 999, "position": 0}, 422),
        ({"column_id": todo["id"], "position": -1}, 422),
    ]
    for body, expected in invalid:
        assert client.post(f"/api/cards/{card_id}/move", json=body).status_code == expected, body
    assert client.post("/api/cards/missing/move", json={"column_id": todo["id"], "position": 0}).status_code == 404
    assert client.get("/api/board").json() == board


def test_card_can_move_into_empty_column(client, board):
    backlog, todo = column_by_name(board, "Backlog"), column_by_name(board, "To Do")
    for card_id in ids(backlog):
        client.post(f"/api/cards/{card_id}/move", json={"column_id": todo["id"], "position": 0})
    after = client.get("/api/board").json()
    assert column_by_name(after, "Backlog")["cards"] == []
    moved = column_by_name(after, "To Do")["cards"][0]["id"]
    after = client.post(
        f"/api/cards/{moved}/move", json={"column_id": backlog["id"], "position": 0}
    ).json()
    assert ids(column_by_name(after, "Backlog")) == [moved]
    assert_contiguous(after)


# --- Delete, reset, persistence ---------------------------------------------


def test_delete_renumbers_column(client, board):
    doing = column_by_name(board, "In Progress")
    middle = ids(doing)[1]
    assert client.delete(f"/api/cards/{middle}").status_code == 204
    after = client.get("/api/board").json()
    assert ids(column_by_name(after, "In Progress")) == [i for i in ids(doing) if i != middle]
    assert_contiguous(after)
    assert client.delete(f"/api/cards/{middle}").status_code == 404


def test_reset_restores_demo_data(client, board):
    for column in board["columns"]:
        for card_id in ids(column):
            client.delete(f"/api/cards/{card_id}")
    assert all(not c["cards"] for c in client.get("/api/board").json()["columns"])

    reset = client.post("/api/board/reset").json()
    titles = lambda b: [card["title"] for column in b["columns"] for card in column["cards"]]
    assert titles(reset) == titles(board)
    assert_contiguous(reset)


def test_changes_persist_across_restart(db_file):
    with TestClient(app) as first:
        column_id = first.get("/api/board").json()["columns"][0]["id"]
        card = first.post("/api/cards", json={"column_id": column_id, "title": "Survives"}).json()
    with TestClient(app) as second:
        board = second.get("/api/board").json()
    assert card["id"] in ids(board["columns"][0])
