"""Pydantic schemas for requests and responses."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

Role = Literal["student", "professor", "admin"]


class Principal(BaseModel):
    """The authenticated caller, derived from the validated token."""
    sub: str
    role: Role
    scopes: list[str] = Field(default_factory=list)
    name: Optional[str] = None

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes


class Grade(BaseModel):
    student_id: str
    student_name: str
    course_code: str
    course_title: str
    score: float
    letter: str
    updated_at: str
    updated_by: str


class Course(BaseModel):
    code: str
    title: str
    professor_id: str
    professor_name: str


class GradeUpsert(BaseModel):
    """Body for entering/updating a grade."""
    student_id: str
    score: float = Field(ge=0, le=100)
