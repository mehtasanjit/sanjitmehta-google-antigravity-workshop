import type { Board, Card, CardInput } from "./types";

/** Error carrying the server's `detail` message, safe to show to the user. */
export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    throw new ApiError("Cannot reach the server. Is the backend running?", 0);
  }
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      // Keep the generic message when the body is not JSON.
    }
    throw new ApiError(message, response.status);
  }
  return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}

export const api = {
  getBoard: () => request<Board>("/board"),

  createCard: (columnId: number, input: CardInput) =>
    request<Card>("/cards", {
      method: "POST",
      body: JSON.stringify({ column_id: columnId, ...input }),
    }),

  updateCard: (cardId: string, input: CardInput) =>
    request<Card>(`/cards/${encodeURIComponent(cardId)}`, {
      method: "PATCH",
      body: JSON.stringify(input),
    }),

  moveCard: (cardId: string, columnId: number, position: number) =>
    request<Board>(`/cards/${encodeURIComponent(cardId)}/move`, {
      method: "POST",
      body: JSON.stringify({ column_id: columnId, position }),
    }),

  deleteCard: (cardId: string) =>
    request<void>(`/cards/${encodeURIComponent(cardId)}`, { method: "DELETE" }),

  resetBoard: () => request<Board>("/board/reset", { method: "POST" }),
};
