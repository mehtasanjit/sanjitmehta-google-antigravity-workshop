export type Priority = "Low" | "Medium" | "High";

export const PRIORITIES: Priority[] = ["Low", "Medium", "High"];

export interface Card {
  id: string;
  column_id: number;
  position: number;
  title: string;
  description: string;
  priority: Priority;
  assignee: string;
  tags: string[];
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface Column {
  id: number;
  name: string;
  position: number;
  cards: Card[];
}

export interface Board {
  title: string;
  columns: Column[];
}

/** Editable card fields, as sent to create and update. */
export interface CardInput {
  title: string;
  description: string;
  priority: Priority;
  assignee: string;
  tags: string[];
  due_date: string | null;
}
