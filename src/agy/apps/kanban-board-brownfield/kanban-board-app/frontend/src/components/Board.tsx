import type { Board as BoardType, Card, Column as ColumnType } from "../types";
import type { MoveDirection } from "./CardItem";
import { Column } from "./Column";

interface Props {
  board: BoardType;
  search: string;
  onAdd: (column: ColumnType) => void;
  onMove: (card: Card, direction: MoveDirection) => void;
  onEdit: (card: Card) => void;
  onDelete: (card: Card) => void;
}

export function Board({ board, search, onAdd, onMove, onEdit, onDelete }: Props) {
  const last = board.columns.length - 1;
  return (
    <main className="board">
      {board.columns.map((column, index) => (
        <Column
          key={column.id}
          column={column}
          isFirst={index === 0}
          isLast={index === last}
          search={search}
          onAdd={() => onAdd(column)}
          onMove={onMove}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </main>
  );
}
