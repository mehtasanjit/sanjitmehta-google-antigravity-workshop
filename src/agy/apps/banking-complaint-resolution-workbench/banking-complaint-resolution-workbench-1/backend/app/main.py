from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db, init_db
from app.models import Complaint, AuditLog, User

app = FastAPI(title="Banking Complaint Resolution Workbench API")

# Initialize database on startup if running as main server
@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/api/complaints")
def get_complaints(
    status: Optional[str] = Query(None, description="Filter complaints by status"),
    assigned_to: Optional[str] = Query(None, description="Filter complaints by assigned case handler username"),
    db: Session = Depends(get_db)
):
    """Retrieve list of customer complaints, with optional status and assignment filtering."""
    query = db.query(Complaint)
    if status:
        query = query.filter(Complaint.status == status)
    if assigned_to:
        query = query.filter(Complaint.assigned_to == assigned_to)
    
    complaints = query.all()
    
    # Format response lists
    return [
        {
            "id": c.id,
            "customer_name": c.customer_name,
            "account_number": c.account_number,
            "customer_email": c.customer_email,
            "customer_phone": c.customer_phone,
            "title": c.title,
            "description": c.description,
            "category": c.category,
            "subcategory": c.subcategory,
            "disputed_amount": c.disputed_amount,
            "priority": c.priority,
            "status": c.status,
            "sla_deadline": c.sla_deadline,
            "assigned_to": c.assigned_to,
            "logged_by": c.logged_by,
            "resolution_notes": c.resolution_notes,
            "supervisor_feedback": c.supervisor_feedback,
            "created_at": c.created_at,
            "updated_at": c.updated_at
        }
        for c in complaints
    ]

@app.get("/api/complaints/{complaint_id}")
def get_complaint_details(complaint_id: str, db: Session = Depends(get_db)):
    """Retrieve complete details for a single complaint including its chronological audit history."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    # Query all audit logs for this complaint in ascending (chronological) order
    audit_logs = db.query(AuditLog).filter(AuditLog.complaint_id == complaint_id).order_by(AuditLog.timestamp.asc()).all()
    
    return {
        "id": complaint.id,
        "customer_name": complaint.customer_name,
        "account_number": complaint.account_number,
        "customer_email": complaint.customer_email,
        "customer_phone": complaint.customer_phone,
        "title": complaint.title,
        "description": complaint.description,
        "category": complaint.category,
        "subcategory": complaint.subcategory,
        "disputed_amount": complaint.disputed_amount,
        "priority": complaint.priority,
        "status": complaint.status,
        "sla_deadline": complaint.sla_deadline,
        "assigned_to": complaint.assigned_to,
        "logged_by": complaint.logged_by,
        "resolution_notes": complaint.resolution_notes,
        "supervisor_feedback": complaint.supervisor_feedback,
        "created_at": complaint.created_at,
        "updated_at": complaint.updated_at,
        "audit_logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp,
                "user_name": log.user_name,
                "user_role": log.user_role,
                "event_type": log.event_type,
                "description": log.description
            }
            for log in audit_logs
        ]
    }
