from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Index, text
from app.db import Base


class Pulse(Base):
    __tablename__ = 'pulses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('lecture_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    status = Column(String(16), nullable=False, default='active')
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("status IN ('active','closed')", name='ck_pulse_status'),
        Index('uq_one_active_pulse', 'session_id', unique=True, sqlite_where=text("status='active'")),
    )


class PulseResponse(Base):
    __tablename__ = 'pulse_responses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pulse_id = Column(Integer, ForeignKey('pulses.id', ondelete='CASCADE'), nullable=False, index=True)
    student_subject = Column(String(64), ForeignKey('users.subject'), nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint('rating BETWEEN 1 AND 5', name='ck_rating_range'),
        UniqueConstraint('pulse_id', 'student_subject', name='uq_pulse_response'),
    )
