import type { Card } from "../types";
import { isOverdue } from "../utils";

export type MoveDirection = "left" | "right" | "up" | "down";

interface Props {
  card: Card;
  columnName: string;
  canMove: Record<MoveDirection, boolean>;
  onMove: (direction: MoveDirection) => void;
  onEdit: () => void;
  onDelete: () => void;
}

const MOVE_BUTTONS: { direction: MoveDirection; symbol: string; label: string }[] = [
  { direction: "left", symbol: "←", label: "Move to previous column" },
  { direction: "up", symbol: "↑", label: "Move up" },
  { direction: "down", symbol: "↓", label: "Move down" },
  { direction: "right", symbol: "→", label: "Move to next column" },
];

export function CardItem({ card, columnName, canMove, onMove, onEdit, onDelete }: Props) {
  const overdue = isOverdue(card, columnName);

  return (
    <li className="card" aria-label={card.title}>
      <div className="card-header">
        <h3>{card.title}</h3>
        <span className={`priority priority-${card.priority.toLowerCase()}`}>{card.priority}</span>
      </div>
      {card.description && <p className="description">{card.description}</p>}
      <div className="meta">
        {card.assignee && <span>👤 {card.assignee}</span>}
        {card.due_date && <span>Due {card.due_date}</span>}
        {overdue && <span className="overdue">Overdue</span>}
      </div>
      {card.tags.length > 0 && (
        <ul className="tags" aria-label="Tags">
          {card.tags.map((tag) => (
            <li key={tag}>{tag}</li>
          ))}
        </ul>
      )}
      <div className="card-actions">
        {MOVE_BUTTONS.map(({ direction, symbol, label }) => (
          <button
            key={direction}
            type="button"
            aria-label={`${label}: ${card.title}`}
            title={label}
            disabled={!canMove[direction]}
            onClick={() => onMove(direction)}
          >
            {symbol}
          </button>
        ))}
        <span className="spacer" />
        <button type="button" onClick={onEdit} aria-label={`Edit ${card.title}`}>
          Edit
        </button>
        <button type="button" onClick={onDelete} aria-label={`Delete ${card.title}`}>
          Delete
        </button>
      </div>
    </li>
  );
}
