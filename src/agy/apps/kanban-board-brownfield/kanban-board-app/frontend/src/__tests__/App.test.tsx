import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import { api } from "../api";
import type { Board, Card } from "../types";

vi.mock("../api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../api")>();
  return {
    ...actual,
    api: {
      getBoard: vi.fn(),
      createCard: vi.fn(),
      updateCard: vi.fn(),
      moveCard: vi.fn(),
      deleteCard: vi.fn(),
      resetBoard: vi.fn(),
    },
  };
});

const mockedApi = vi.mocked(api);

function card(overrides: Partial<Card>): Card {
  return {
    id: overrides.title ?? "id",
    column_id: 1,
    position: 0,
    title: "Card",
    description: "",
    priority: "Medium",
    assignee: "",
    tags: [],
    due_date: null,
    created_at: "2026-01-01T00:00:00+00:00",
    updated_at: "2026-01-01T00:00:00+00:00",
    ...overrides,
  };
}

const board: Board = {
  title: "Team Board",
  columns: [
    {
      id: 1,
      name: "Backlog",
      position: 0,
      cards: [card({ title: "Research dark mode", description: "accessibility notes" })],
    },
    {
      id: 2,
      name: "To Do",
      position: 1,
      cards: [
        card({ title: "Fix login bug", column_id: 2, due_date: "2000-01-01" }),
        card({ title: "Write release notes", column_id: 2, position: 1, due_date: "2999-12-31" }),
      ],
    },
    { id: 3, name: "In Progress", position: 2, cards: [] },
    {
      id: 4,
      name: "Done",
      position: 3,
      cards: [card({ title: "Set up repository", column_id: 4, due_date: "2000-01-01" })],
    },
  ],
};

function columnSection(name: string) {
  return screen.getByRole("region", { name });
}

beforeEach(() => {
  vi.clearAllMocks();
  mockedApi.getBoard.mockResolvedValue(board);
});

describe("App", () => {
  it("renders columns in order with true card counts and an empty state", async () => {
    render(<App />);
    const headings = await screen.findAllByRole("heading", { level: 2 });
    expect(headings.map((h) => h.textContent)).toEqual(["Backlog", "To Do", "In Progress", "Done"]);
    expect(within(columnSection("To Do")).getByLabelText("2 cards")).toBeInTheDocument();
    expect(within(columnSection("In Progress")).getByText("No cards")).toBeInTheDocument();
  });

  it("shows Overdue only for past-due cards outside Done", async () => {
    render(<App />);
    const overdueCard = await screen.findByRole("listitem", { name: "Fix login bug" });
    expect(within(overdueCard).getByText("Overdue")).toBeInTheDocument();
    const futureCard = screen.getByRole("listitem", { name: "Write release notes" });
    expect(within(futureCard).queryByText("Overdue")).not.toBeInTheDocument();
    const doneCard = screen.getByRole("listitem", { name: "Set up repository" });
    expect(within(doneCard).queryByText("Overdue")).not.toBeInTheDocument();
  });

  it("blocks creating a card with a blank title", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(await screen.findByRole("button", { name: "Add card to Backlog" }));
    await user.type(screen.getByLabelText("Title"), "   ");
    await user.click(screen.getByRole("button", { name: "Save" }));
    expect(screen.getByRole("alert")).toHaveTextContent("Title is required");
    expect(mockedApi.createCard).not.toHaveBeenCalled();
  });

  it("creates a card with a trimmed title and reloads the board", async () => {
    const user = userEvent.setup();
    mockedApi.createCard.mockResolvedValue(card({ title: "New task" }));
    render(<App />);
    await user.click(await screen.findByRole("button", { name: "Add card to In Progress" }));
    await user.type(screen.getByLabelText("Title"), "  New task  ");
    await user.click(screen.getByRole("button", { name: "Save" }));
    await waitFor(() =>
      expect(mockedApi.createCard).toHaveBeenCalledWith(
        3,
        expect.objectContaining({ title: "New task", priority: "Medium" }),
      ),
    );
    expect(mockedApi.getBoard).toHaveBeenCalledTimes(2);
  });

  it("filters cards by search without changing counts", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.type(await screen.findByLabelText("Search cards"), "ACCESSIBILITY");
    expect(screen.getByRole("listitem", { name: "Research dark mode" })).toBeInTheDocument();
    expect(screen.queryByRole("listitem", { name: "Fix login bug" })).not.toBeInTheDocument();
    expect(within(columnSection("To Do")).getByText("No matching cards")).toBeInTheDocument();
    expect(within(columnSection("To Do")).getByLabelText("2 cards")).toBeInTheDocument();
  });

  it("moves a card to the bottom of the next column", async () => {
    const user = userEvent.setup();
    mockedApi.moveCard.mockResolvedValue(board);
    render(<App />);
    await user.click(
      await screen.findByRole("button", { name: "Move to next column: Fix login bug" }),
    );
    expect(mockedApi.moveCard).toHaveBeenCalledWith("Fix login bug", 3, 0);
    expect(
      screen.getByRole("button", { name: "Move to previous column: Research dark mode" }),
    ).toBeDisabled();
  });

  it("shows the server error when an action fails", async () => {
    const user = userEvent.setup();
    mockedApi.moveCard.mockRejectedValue(new Error("Position must be between 0 and 1"));
    render(<App />);
    await user.click(await screen.findByRole("button", { name: "Move down: Fix login bug" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Position must be between 0 and 1");
  });
});
