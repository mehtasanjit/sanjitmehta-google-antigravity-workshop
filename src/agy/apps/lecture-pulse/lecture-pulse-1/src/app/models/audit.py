from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Index
from app.db import Base


class AuditLog(Base):
    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_subject = Column(String(64), nullable=False, index=True)
    actor_role = Column(String(16), nullable=False)
    action = Column(String(64), nullable=False)
    target_type = Column(String(32), nullable=False)
    target_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        Index('ix_audit_target', 'target_type', 'target_id'),
    )
