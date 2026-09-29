"""Pydantic request and response models. Validation lives here; no database access."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Priority = Literal["Low", "Medium", "High"]

TITLE_MAX = 120
DESCRIPTION_MAX = 2000
ASSIGNEE_MAX = 60
TAG_MAX = 20
TAGS_MAX_COUNT = 10


def _clean_title(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Title is required")
    if len(value) > TITLE_MAX:
        raise ValueError(f"Title must be at most {TITLE_MAX} characters")
    return value


def _clean_tags(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in values:
        tag = raw.strip()
        if not tag:
            raise ValueError("Tags cannot be blank")
        if len(tag) > TAG_MAX:
            raise ValueError(f"Each tag must be at most {TAG_MAX} characters")
        if tag.lower() not in seen:
            seen.add(tag.lower())
            cleaned.append(tag)
    if len(cleaned) > TAGS_MAX_COUNT:
        raise ValueError(f"A card can have at most {TAGS_MAX_COUNT} tags")
    return cleaned


class CardCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column_id: int
    title: str
    description: str = Field(default="", max_length=DESCRIPTION_MAX)
    priority: Priority = "Medium"
    assignee: str = Field(default="", max_length=ASSIGNEE_MAX)
    tags: list[str] = Field(default_factory=list)
    due_date: date | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return _clean_title(value)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        return _clean_tags(value)

    @field_validator("assignee")
    @classmethod
    def validate_assignee(cls, value: str) -> str:
        return value.strip()


class CardUpdate(BaseModel):
    """Partial update. Column and position are changed only through /move."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX)
    priority: Priority | None = None
    assignee: str | None = Field(default=None, max_length=ASSIGNEE_MAX)
    tags: list[str] | None = None
    due_date: date | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Title is required")
        return _clean_title(value)

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: Priority | None) -> Priority:
        if value is None:
            raise ValueError("Priority cannot be empty")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str:
        return value or ""

    @field_validator("assignee")
    @classmethod
    def validate_assignee(cls, value: str | None) -> str:
        return (value or "").strip()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str] | None) -> list[str]:
        return _clean_tags(value or [])


class MoveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column_id: int
    position: int = Field(ge=0)


class Card(BaseModel):
    id: str
    column_id: int
    position: int
    title: str
    description: str
    priority: Priority
    assignee: str
    tags: list[str]
    due_date: date | None
    created_at: str
    updated_at: str


class Column(BaseModel):
    id: int
    name: str
    position: int
    cards: list[Card]


class Board(BaseModel):
    title: str
    columns: list[Column]
