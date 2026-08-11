"""Database models representing domain entities."""

from typing import Optional
from pydantic import BaseModel


class SessionModel(BaseModel):
    """Database model for a Session."""
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    code: str
    created_at: Optional[str] = None


class PulseModel(BaseModel):
    """Database model for a Pulse."""
    id: Optional[int] = None
    session_code: str
    type: str
    timestamp: Optional[str] = None


class QuestionModel(BaseModel):
    """Database model for a Question."""
    id: Optional[int] = None
    session_code: str
    text: str
    upvotes: int = 0
    status: str = "active"
    created_at: Optional[str] = None
