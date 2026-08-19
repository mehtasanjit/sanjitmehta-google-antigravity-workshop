from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from app.database import Base

class Complaint(Base):
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(255), nullable=False)
    account_number = Column(String(50), nullable=False)
    account_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    status = Column(String(20), default="New", nullable=False)
    description = Column(Text, nullable=False)
    assigned_to = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False)
    performed_by = Column(String(100), nullable=False)
    comments = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
