from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from app.db import Base


class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_subject = Column(String(64), ForeignKey('users.subject'), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class Enrollment(Base):
    __tablename__ = 'enrollments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    student_subject = Column(String(64), ForeignKey('users.subject'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint('course_id', 'student_subject', name='uq_enrollment'),
    )
