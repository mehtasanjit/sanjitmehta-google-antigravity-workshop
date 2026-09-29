import type { Card, Column as ColumnType } from "../types";
import { matchesSearch } from "../utils";
import { CardItem, type MoveDirection } from "./CardItem";

interface Props {
  column: ColumnType;
  isFirst: boolean;
  isLast: boolean;
  search: string;
  onAdd: () => void;
  onMove: (card: Card, direction: MoveDirection) => void;
  onEdit: (card: Card) => void;
  onDelete: (card: Card) => void;
}

export function Column({ column, isFirst, isLast, search, onAdd, onMove, onEdit, onDelete }: Props) {
  const visible = column.cards.filter((card) => matchesSearch(card, search));
  const count = column.cards.length;

  return (
    <section className="column" aria-labelledby={`column-${column.id}`}>
      <header className="column-header">
        <h2 id={`column-${column.id}`}>{column.name}</h2>
        <span className="count" aria-label={`${count} ${count === 1 ? "card" : "cards"}`}>
          {count}
        </span>
      </header>
      <button type="button" className="add" onClick={onAdd} aria-label={`Add card to ${column.name}`}>
        + Add card
      </button>
      {count === 0 && <p className="empty">No cards</p>}
      {count > 0 && visible.length === 0 && <p className="empty">No matching cards</p>}
      <ul className="cards">
        {visible.map((card) => (
          <CardItem
            key={card.id}
            card={card}
            columnName={column.name}
            canMove={{
              left: !isFirst,
              right: !isLast,
              up: card.position > 0,
              down: card.position < count - 1,
            }}
            onMove={(direction) => onMove(card, direction)}
            onEdit={() => onEdit(card)}
            onDelete={() => onDelete(card)}
          />
        ))}
      </ul>
    </section>
  );
}
