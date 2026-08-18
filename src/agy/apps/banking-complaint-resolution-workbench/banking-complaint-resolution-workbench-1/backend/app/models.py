import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "CSR", "Case Handler", "Supervisor"

    # Relationships
    complaints_assigned = relationship("Complaint", foreign_keys="[Complaint.assigned_to]", back_populates="assignee")
    complaints_logged = relationship("Complaint", foreign_keys="[Complaint.logged_by]", back_populates="logger")

    def __repr__(self):
        return f"<User username={self.username} name={self.name} role={self.role}>"


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String, primary_key=True, index=True)  # CRW-YYYY-XXXX
    customer_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    disputed_amount = Column(Float, default=0.0)
    priority = Column(String, nullable=False)  # "Low", "Medium", "High", "Critical"
    status = Column(String, default="Registered")  # "Registered", "Under Investigation", "Resolution Proposed", "Pending Approval", "Resolved", "Needs Revision"
    sla_deadline = Column(DateTime, nullable=False)
    
    assigned_to = Column(String, ForeignKey("users.username"), nullable=True)
    logged_by = Column(String, ForeignKey("users.username"), nullable=True)
    
    resolution_notes = Column(Text, nullable=True)
    supervisor_feedback = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="complaints_assigned")
    logger = relationship("User", foreign_keys=[logged_by], back_populates="complaints_logged")
    audit_logs = relationship("AuditLog", back_populates="complaint", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Complaint id={self.id} title={self.title} status={self.status}>"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(String, ForeignKey("complaints.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_name = Column(String, nullable=False)
    user_role = Column(String, nullable=False)
    event_type = Column(String, nullable=False)  # e.g., "Log Complaint", "Claim Case", "Add Comment", "Submit Proposal", "Approve Case", "Reject Case"
    description = Column(String, nullable=False)

    # Relationships
    complaint = relationship("Complaint", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog id={self.id} complaint_id={self.complaint_id} event_type={self.event_type}>"
