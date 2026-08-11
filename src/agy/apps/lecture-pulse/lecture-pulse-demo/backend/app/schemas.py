"""Pydantic schemas for Lecture Pulse API request/response validation."""

from typing import List, Optional, Literal
from pydantic import BaseModel


class SessionCreate(BaseModel):
    """Schema for creating a new session."""
    title: str
    description: Optional[str] = None


class SessionResponse(BaseModel):
    """Schema for session creation response."""
    title: str
    code: str
    created_at: str


class PulseCreate(BaseModel):
    """Schema for submitting a new pulse signal."""
    type: str


class QuestionCreate(BaseModel):
    """Schema for submitting a new question."""
    text: str


class QuestionResponse(BaseModel):
    """Schema for returning question details."""
    id: int
    session_code: str
    text: str
    upvotes: int
    status: str
    created_at: str


class SessionDetailsResponse(BaseModel):
    """Schema for complete session state and totals."""
    code: str
    title: str
    description: Optional[str] = None
    created_at: str
    pulse_totals: dict[str, int]
    questions: List[QuestionResponse]


class WebSocketPulseMessage(BaseModel):
    """Validation schema for pulse event."""
    type: Literal["PULSE_EVENT"]
    pulse_type: Literal["slower", "confused", "got_it"]


class WebSocketNewQuestionMessage(BaseModel):
    """Validation schema for new question event."""
    type: Literal["NEW_QUESTION"]
    text: str


class WebSocketUpvoteQuestionMessage(BaseModel):
    """Validation schema for upvote question event."""
    type: Literal["UPVOTE_QUESTION"]
    question_id: int


class WebSocketUpdateQuestionStatusMessage(BaseModel):
    """Validation schema for updating question status event."""
    type: Literal["UPDATE_QUESTION_STATUS"]
    question_id: int
    status: Literal["answered", "dismissed"]
