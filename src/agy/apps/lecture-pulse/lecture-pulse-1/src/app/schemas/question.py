from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class QuestionCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: int
    author_subject: str
    text: str
    status: str
    upvotes: int
    created_at: datetime


class UpvoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    question_id: int
    upvotes: int


class ModerateRequest(BaseModel):
    status: Literal['answered', 'dismissed']
