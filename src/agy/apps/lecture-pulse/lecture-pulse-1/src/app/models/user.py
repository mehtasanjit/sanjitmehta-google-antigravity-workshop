from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint
from app.db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String(64), unique=True, nullable=False)
    role = Column(String(16), nullable=False)
    display_name = Column(String(200), nullable=True)
    email = Column(String(320), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        CheckConstraint("role IN ('instructor','student')", name='ck_user_role'),
    )
