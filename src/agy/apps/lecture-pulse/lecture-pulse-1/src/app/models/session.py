from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from app.db import Base


class LectureSession(Base):
    __tablename__ = 'lecture_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    status = Column(String(16), nullable=False, default='scheduled')
    join_code = Column(String(12), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    activated_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("status IN ('scheduled','active','ended')", name='ck_session_status'),
    )


class Participant(Base):
    __tablename__ = 'participants'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('lecture_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    student_subject = Column(String(64), ForeignKey('users.subject'), nullable=False)
    joined_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('session_id', 'student_subject', name='uq_participant'),
    )
