import type { Card } from "./types";

export const DONE_COLUMN_NAME = "Done";

/** Today's date in the browser's local time zone, as YYYY-MM-DD. */
export function localToday(now: Date = new Date()): string {
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

/** A card is overdue when its due date is before today, unless it is in Done. */
export function isOverdue(card: Card, columnName: string, today: string = localToday()): boolean {
  return card.due_date !== null && card.due_date < today && columnName !== DONE_COLUMN_NAME;
}

/** Case-insensitive partial match on title and description. Blank query matches all. */
export function matchesSearch(card: Card, query: string): boolean {
  const needle = query.trim().toLowerCase();
  if (!needle) return true;
  return (
    card.title.toLowerCase().includes(needle) || card.description.toLowerCase().includes(needle)
  );
}
