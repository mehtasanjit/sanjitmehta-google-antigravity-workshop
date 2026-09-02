import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    reference_number = Column(String, unique=True, index=True, nullable=False)
    customer_name = Column(String, nullable=False)
    customer_id = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    account_type = Column(String, nullable=False)
    product_type = Column(String, nullable=False)
    category = Column(String, nullable=False)
    priority = Column(String, nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    channel = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    narrative = Column(String, nullable=False)
    disputed_amount = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="NEW")  # NEW, IN_INVESTIGATION, UNDER_REVIEW, APPROVED, RESOLVED, ESCALATED
    assigned_to = Column(String, nullable=True)
    root_cause = Column(String, nullable=True)
    investigation_notes = Column(String, nullable=True)
    refund_amount = Column(Float, default=0.0, nullable=False)
    goodwill_amount = Column(Float, default=0.0, nullable=False)
    interest_amount = Column(Float, default=0.0, nullable=False)
    total_redress = Column(Float, default=0.0, nullable=False)
    supervisor_notes = Column(String, nullable=True)
    review_decision = Column(String, default="NONE", nullable=False)  # APPROVED, REJECTED, NONE
    supervisor_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    sla_target_hours = Column(Integer, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    audit_logs = relationship("AuditLog", back_populates="complaint", cascade="all, delete-orphan")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    actor_role = Column(String, nullable=False)
    actor_name = Column(String, nullable=False)
    action_type = Column(String, nullable=False)  # CREATED, ASSIGNED, STATUS_CHANGED, etc.
    from_status = Column(String, nullable=True)
    to_status = Column(String, nullable=True)
    details = Column(String, nullable=True)
    metadata_json = Column(String, nullable=True)

    # Relationships
    complaint = relationship("Complaint", back_populates="audit_logs")
