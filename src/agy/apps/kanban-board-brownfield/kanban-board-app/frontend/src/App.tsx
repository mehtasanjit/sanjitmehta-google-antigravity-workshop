import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import { Board } from "./components/Board";
import { CardDialog } from "./components/CardDialog";
import type { MoveDirection } from "./components/CardItem";
import { ConfirmDialog } from "./components/ConfirmDialog";
import type { Board as BoardType, Card, CardInput, Column } from "./types";

type Dialog =
  | { kind: "create"; column: Column }
  | { kind: "edit"; card: Card }
  | { kind: "delete"; card: Card }
  | { kind: "reset" }
  | null;

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : "Something went wrong";
}

export default function App() {
  const [board, setBoard] = useState<BoardType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [dialog, setDialog] = useState<Dialog>(null);

  const loadBoard = useCallback(async () => {
    try {
      setBoard(await api.getBoard());
      setError(null);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadBoard();
  }, [loadBoard]);

  /** Run a board action; on failure show the error and leave state unchanged. */
  async function run(action: () => Promise<BoardType | void>) {
    try {
      const result = await action();
      if (result) setBoard(result);
      else await loadBoard();
      setError(null);
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  function handleMove(card: Card, direction: MoveDirection) {
    if (!board) return;
    const index = board.columns.findIndex((column) => column.id === card.column_id);
    if (direction === "left" || direction === "right") {
      const target = board.columns[index + (direction === "left" ? -1 : 1)];
      if (!target) return;
      void run(() => api.moveCard(card.id, target.id, target.cards.length));
    } else {
      const position = card.position + (direction === "up" ? -1 : 1);
      void run(() => api.moveCard(card.id, card.column_id, position));
    }
  }

  async function handleSave(input: CardInput) {
    if (dialog?.kind === "create") await api.createCard(dialog.column.id, input);
    else if (dialog?.kind === "edit") await api.updateCard(dialog.card.id, input);
    // Errors propagate to CardDialog, which shows them and stays open.
    setDialog(null);
    await loadBoard();
  }

  return (
    <div className="app">
      <header className="toolbar">
        <h1>{board?.title ?? "Team Board"}</h1>
        <input
          type="search"
          placeholder="Search cards"
          aria-label="Search cards"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button type="button" onClick={() => setDialog({ kind: "reset" })} disabled={!board}>
          Reset board
        </button>
      </header>

      {error && (
        <div className="banner" role="alert">
          <span>{error}</span>
          <button type="button" onClick={() => setError(null)} aria-label="Dismiss error">
            ×
          </button>
        </div>
      )}

      {loading && <p className="status">Loading board…</p>}

      {board && (
        <Board
          board={board}
          search={search}
          onAdd={(column) => setDialog({ kind: "create", column })}
          onMove={handleMove}
          onEdit={(card) => setDialog({ kind: "edit", card })}
          onDelete={(card) => setDialog({ kind: "delete", card })}
        />
      )}

      {(dialog?.kind === "create" || dialog?.kind === "edit") && (
        <CardDialog
          heading={dialog.kind === "create" ? `Add card to ${dialog.column.name}` : "Edit card"}
          card={dialog.kind === "edit" ? dialog.card : undefined}
          onSave={handleSave}
          onCancel={() => setDialog(null)}
        />
      )}

      {dialog?.kind === "delete" && (
        <ConfirmDialog
          message={`Delete "${dialog.card.title}"? This cannot be undone.`}
          confirmLabel="Delete"
          onCancel={() => setDialog(null)}
          onConfirm={() => {
            const { card } = dialog;
            setDialog(null);
            void run(() => api.deleteCard(card.id));
          }}
        />
      )}

      {dialog?.kind === "reset" && (
        <ConfirmDialog
          message="Reset the board to the demo data? All current cards will be replaced."
          confirmLabel="Reset"
          onCancel={() => setDialog(null)}
          onConfirm={() => {
            setDialog(null);
            void run(() => api.resetBoard());
          }}
        />
      )}
    </div>
  );
}
