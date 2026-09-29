"""HTTP routes only: parse the request, call the service, map errors to status codes."""

from fastapi import APIRouter, Response, status

from app import service
from app.schemas import Board, Card, CardCreate, CardUpdate, MoveRequest

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/board", response_model=Board)
def get_board() -> dict:
    return service.get_board()


@router.post("/cards", response_model=Card, status_code=status.HTTP_201_CREATED)
def create_card(payload: CardCreate) -> dict:
    return service.create_card(payload)


@router.patch("/cards/{card_id}", response_model=Card)
def update_card(card_id: str, payload: CardUpdate) -> dict:
    return service.update_card(card_id, payload)


@router.post("/cards/{card_id}/move", response_model=Board)
def move_card(card_id: str, payload: MoveRequest) -> dict:
    return service.move_card(card_id, payload)


@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(card_id: str) -> Response:
    service.delete_card(card_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/board/reset", response_model=Board)
def reset_board() -> dict:
    return service.reset_board()
