from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, CheckConstraint, UniqueConstraint
from app.db import Base


class Poll(Base):
    __tablename__ = 'polls'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('lecture_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    prompt = Column(String(1000), nullable=False)
    poll_type = Column(String(16), nullable=False)
    is_quiz = Column(Boolean, nullable=False, default=False)
    status = Column(String(16), nullable=False, default='closed')
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("poll_type IN ('single','multiple')", name='ck_poll_type'),
        CheckConstraint("status IN ('closed','open')", name='ck_poll_status'),
    )


class PollOption(Base):
    __tablename__ = 'poll_options'

    id = Column(Integer, primary_key=True, autoincrement=True)
    poll_id = Column(Integer, ForeignKey('polls.id', ondelete='CASCADE'), nullable=False, index=True)
    text = Column(String(500), nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    position = Column(Integer, nullable=False)


class PollResponse(Base):
    __tablename__ = 'poll_responses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    poll_id = Column(Integer, ForeignKey('polls.id', ondelete='CASCADE'), nullable=False, index=True)
    student_subject = Column(String(64), ForeignKey('users.subject'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('poll_id', 'student_subject', name='uq_poll_response'),
    )


class PollResponseOption(Base):
    __tablename__ = 'poll_response_options'

    id = Column(Integer, primary_key=True, autoincrement=True)
    response_id = Column(Integer, ForeignKey('poll_responses.id', ondelete='CASCADE'), nullable=False, index=True)
    option_id = Column(Integer, ForeignKey('poll_options.id', ondelete='CASCADE'), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint('response_id', 'option_id', name='uq_response_option'),
    )
