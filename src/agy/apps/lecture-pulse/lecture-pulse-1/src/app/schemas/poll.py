from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class PollOptionIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    is_correct: Optional[bool] = False


class PollCreate(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    poll_type: Literal['single', 'multiple']
    is_quiz: bool = False
    options: List[PollOptionIn] = Field(..., min_length=2)


class PollOptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    text: str
    position: int


class PollOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: int
    prompt: str
    poll_type: str
    is_quiz: bool
    status: str
    options: List[PollOptionOut]
    created_at: datetime


class ResponseCreate(BaseModel):
    option_ids: List[int] = Field(..., min_length=1)


class ResponseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    poll_id: int
    created_at: datetime


class PollOptionCount(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    option_id: int
    text: str
    count: int


class PollResultsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    poll_id: int
    poll_type: str
    is_quiz: bool
    total_respondents: int
    options: List[PollOptionCount]
    correct_answer_rate: Optional[float] = None
