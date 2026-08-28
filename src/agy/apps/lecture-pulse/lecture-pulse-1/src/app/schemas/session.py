from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class SessionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    course_id: int
    title: str
    status: str
    join_code: Optional[str] = None
    created_at: datetime


class SessionTransition(BaseModel):
    target: Literal['active', 'ended']


class JoinRequest(BaseModel):
    join_code: str = Field(..., min_length=1)


class JoinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    session_id: int
    status: str
    joined_at: datetime


class ParticipantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    student_subject: str
    joined_at: datetime
