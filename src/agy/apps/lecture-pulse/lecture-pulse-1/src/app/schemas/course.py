from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str]
    owner_subject: str
    created_at: datetime


class EnrollmentCreate(BaseModel):
    student_subject: str = Field(..., min_length=1)


class EnrollmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    course_id: int
    student_subject: str
    created_at: datetime
