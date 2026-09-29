"""All SQL for the board. Parameterised queries only; no business decisions."""

import json
import sqlite3
from collections.abc import Iterable, Mapping

EDITABLE_FIELDS = {"title", "description", "priority", "assignee", "tags", "due_date"}


def count_columns(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM columns").fetchone()[0]


def insert_columns(conn: sqlite3.Connection, names: Iterable[str]) -> None:
    conn.executemany(
        "INSERT INTO columns (name, position) VALUES (?, ?)",
        [(name, index) for index, name in enumerate(names)],
    )


def list_columns(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT id, name, position FROM columns ORDER BY position").fetchall()


def get_column(conn: sqlite3.Connection, column_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT id, name, position FROM columns WHERE id = ?", (column_id,)
    ).fetchone()


def list_cards(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT cards.* FROM cards JOIN columns ON columns.id = cards.column_id "
        "ORDER BY columns.position, cards.position"
    ).fetchall()


def get_card(conn: sqlite3.Connection, card_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()


def card_ids_in_column(conn: sqlite3.Connection, column_id: int) -> list[str]:
    rows = conn.execute(
        "SELECT id FROM cards WHERE column_id = ? ORDER BY position", (column_id,)
    ).fetchall()
    return [row["id"] for row in rows]


def insert_card(conn: sqlite3.Connection, card: Mapping) -> None:
    conn.execute(
        "INSERT INTO cards (id, column_id, position, title, description, priority, "
        "assignee, tags, due_date, created_at, updated_at) "
        "VALUES (:id, :column_id, :position, :title, :description, :priority, "
        ":assignee, :tags, :due_date, :created_at, :updated_at)",
        {**card, "tags": json.dumps(card["tags"])},
    )


def update_card_fields(
    conn: sqlite3.Connection, card_id: str, fields: Mapping, updated_at: str
) -> None:
    unknown = set(fields) - EDITABLE_FIELDS
    if unknown:
        raise ValueError(f"Not editable: {sorted(unknown)}")
    values = dict(fields)
    if "tags" in values:
        values["tags"] = json.dumps(values["tags"])
    assignments = ", ".join(f"{name} = :{name}" for name in values)
    sql = f"UPDATE cards SET {assignments}, updated_at = :updated_at WHERE id = :id"
    conn.execute(sql, {**values, "updated_at": updated_at, "id": card_id})


def touch_card(conn: sqlite3.Connection, card_id: str, updated_at: str) -> None:
    conn.execute("UPDATE cards SET updated_at = ? WHERE id = ?", (updated_at, card_id))


def write_positions(conn: sqlite3.Connection, column_orders: Mapping[int, list[str]]) -> None:
    """Persist the full card order for each given column.

    Two phases keep the UNIQUE (column_id, position) constraint satisfied mid-update:
    first move every affected card to a unique negative position, then write the
    final column and position.
    """
    all_ids = [card_id for ids in column_orders.values() for card_id in ids]
    conn.executemany(
        "UPDATE cards SET position = -1 - position WHERE id = ?",
        [(card_id,) for card_id in all_ids],
    )
    conn.executemany(
        "UPDATE cards SET column_id = ?, position = ? WHERE id = ?",
        [
            (column_id, position, card_id)
            for column_id, ids in column_orders.items()
            for position, card_id in enumerate(ids)
        ],
    )


def delete_card(conn: sqlite3.Connection, card_id: str) -> None:
    conn.execute("DELETE FROM cards WHERE id = ?", (card_id,))


def delete_all_cards(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM cards")
