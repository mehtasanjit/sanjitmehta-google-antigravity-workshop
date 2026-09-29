"""Board business rules. Every change to board state goes through this module."""

import json
import sqlite3
import uuid
from datetime import date, datetime, timezone

from app import db, repository, seed
from app.schemas import CardCreate, CardUpdate, MoveRequest

BOARD_TITLE = "Team Board"


class NotFoundError(Exception):
    """The requested card or column does not exist."""


class InvalidMoveError(Exception):
    """A move targets a column or position that is not allowed."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _card_to_dict(row: sqlite3.Row) -> dict:
    card = dict(row)
    card["tags"] = json.loads(card["tags"])
    return card


def _board(conn: sqlite3.Connection) -> dict:
    columns = [dict(row) | {"cards": []} for row in repository.list_columns(conn)]
    by_id = {column["id"]: column for column in columns}
    for row in repository.list_cards(conn):
        by_id[row["column_id"]]["cards"].append(_card_to_dict(row))
    return {"title": BOARD_TITLE, "columns": columns}


def _insert_demo_cards(conn: sqlite3.Connection) -> None:
    column_ids = {row["name"]: row["id"] for row in repository.list_columns(conn)}
    positions: dict[int, int] = {}
    now = _now()
    for item in seed.demo_cards(date.today()):
        column_id = column_ids[item["column"]]
        position = positions.get(column_id, 0)
        positions[column_id] = position + 1
        repository.insert_card(
            conn,
            {
                "id": str(uuid.uuid4()),
                "column_id": column_id,
                "position": position,
                "title": item["title"],
                "description": item["description"],
                "priority": item["priority"],
                "assignee": item["assignee"],
                "tags": item["tags"],
                "due_date": item["due_date"],
                "created_at": now,
                "updated_at": now,
            },
        )


def _require_card(conn: sqlite3.Connection, card_id: str) -> sqlite3.Row:
    card = repository.get_card(conn, card_id)
    if card is None:
        raise NotFoundError("Card not found")
    return card


def initialize() -> None:
    """Create the schema; on first start, create the columns and demo cards."""
    with db.transaction() as conn:
        db.create_schema(conn)
        if repository.count_columns(conn) == 0:
            repository.insert_columns(conn, seed.COLUMN_NAMES)
            _insert_demo_cards(conn)


def get_board() -> dict:
    with db.transaction() as conn:
        return _board(conn)


def create_card(data: CardCreate) -> dict:
    with db.transaction() as conn:
        if repository.get_column(conn, data.column_id) is None:
            raise NotFoundError("Column not found")
        now = _now()
        card_id = str(uuid.uuid4())
        repository.insert_card(
            conn,
            {
                "id": card_id,
                "column_id": data.column_id,
                "position": len(repository.card_ids_in_column(conn, data.column_id)),
                "title": data.title,
                "description": data.description,
                "priority": data.priority,
                "assignee": data.assignee,
                "tags": data.tags,
                "due_date": data.due_date.isoformat() if data.due_date else None,
                "created_at": now,
                "updated_at": now,
            },
        )
        return _card_to_dict(repository.get_card(conn, card_id))


def update_card(card_id: str, data: CardUpdate) -> dict:
    with db.transaction() as conn:
        _require_card(conn, card_id)
        fields = data.model_dump(exclude_unset=True)
        if "due_date" in fields and fields["due_date"] is not None:
            fields["due_date"] = fields["due_date"].isoformat()
        if fields:
            repository.update_card_fields(conn, card_id, fields, _now())
        return _card_to_dict(repository.get_card(conn, card_id))


def move_card(card_id: str, move: MoveRequest) -> dict:
    """Move a card to (column_id, position); positions in both columns stay contiguous."""
    with db.transaction() as conn:
        card = _require_card(conn, card_id)
        if repository.get_column(conn, move.column_id) is None:
            raise InvalidMoveError("Target column does not exist")

        source_id = card["column_id"]
        source_ids = repository.card_ids_in_column(conn, source_id)
        same_column = move.column_id == source_id
        target_ids = source_ids if same_column else repository.card_ids_in_column(conn, move.column_id)
        max_position = len(target_ids) - 1 if same_column else len(target_ids)
        if move.position > max_position:
            raise InvalidMoveError(f"Position must be between 0 and {max_position}")

        if same_column and move.position == card["position"]:
            return _board(conn)

        source_ids.remove(card_id)
        if same_column:
            source_ids.insert(move.position, card_id)
            orders = {source_id: source_ids}
        else:
            target_ids.insert(move.position, card_id)
            orders = {source_id: source_ids, move.column_id: target_ids}

        repository.write_positions(conn, orders)
        repository.touch_card(conn, card_id, _now())
        return _board(conn)


def delete_card(card_id: str) -> None:
    with db.transaction() as conn:
        card = _require_card(conn, card_id)
        repository.delete_card(conn, card_id)
        column_id = card["column_id"]
        repository.write_positions(conn, {column_id: repository.card_ids_in_column(conn, column_id)})


def reset_board() -> dict:
    with db.transaction() as conn:
        repository.delete_all_cards(conn)
        _insert_demo_cards(conn)
        return _board(conn)
