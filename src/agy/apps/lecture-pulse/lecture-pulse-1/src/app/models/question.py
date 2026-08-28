from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from app.db import Base


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('lecture_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    author_subject = Column(String(64), ForeignKey('users.subject'), nullable=False)
    text = Column(String(2000), nullable=False)
    status = Column(String(16), nullable=False, default='open')
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("status IN ('open','answered','dismissed')", name='ck_question_status'),
    )


class QuestionUpvote(Base):
    __tablename__ = 'question_upvotes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, index=True)
    voter_subject = Column(String(64), ForeignKey('users.subject'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('question_id', 'voter_subject', name='uq_upvote'),
    )
