from fastapi import FastAPI, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db, init_db, calculate_sla
from app.models import Complaint, AuditLog, User

app = FastAPI(title="Banking Complaint Resolution Workbench API")

# Schemas
class ComplaintCreate(BaseModel):
    customer_name: str
    account_number: str
    customer_email: str
    customer_phone: str
    title: str
    description: str
    category: str
    subcategory: str
    disputed_amount: float = 0.0
    priority: str = "Medium"  # "Low", "Medium", "High", "Critical"

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

@app.post("/api/complaints", status_code=201)
def create_complaint(
    payload: ComplaintCreate,
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    db: Session = Depends(get_db)
):
    """Log a new customer complaint, generate a unique sequential ID, calculate SLA, and log audit event."""
    # 1. Generate unique sequential ID: CRW-2026-XXXX
    latest_complaint = db.query(Complaint).order_by(Complaint.id.desc()).first()
    if latest_complaint:
        try:
            parts = latest_complaint.id.split("-")
            num = int(parts[-1])
            new_num = num + 1
        except Exception:
            new_num = db.query(Complaint).count() + 1
    else:
        new_num = 1
        
    complaint_id = f"CRW-2026-{new_num:04d}"
    
    # 2. Calculate SLA deadline
    sla_deadline = calculate_sla(payload.priority)
    
    # 3. Create Complaint
    new_case = Complaint(
        id=complaint_id,
        customer_name=payload.customer_name,
        account_number=payload.account_number,
        customer_email=payload.customer_email,
        customer_phone=payload.customer_phone,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        subcategory=payload.subcategory,
        disputed_amount=payload.disputed_amount,
        priority=payload.priority,
        status="Registered",
        sla_deadline=sla_deadline,
        logged_by=x_user_name
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    
    # 4. Write 'Log Complaint' Audit Event
    user_obj = db.query(User).filter(User.username == x_user_name).first()
    actor_name = user_obj.name if user_obj else (x_user_name if x_user_name else "System")
    actor_role = user_obj.role if user_obj else (x_user_role if x_user_role else "System")
    
    audit_log = AuditLog(
        complaint_id=complaint_id,
        user_name=actor_name,
        user_role=actor_role,
        event_type="Log Complaint",
        description=f"Complaint logged by {actor_name} ({actor_role}). Priority set to {payload.priority} with SLA."
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "id": new_case.id,
        "customer_name": new_case.customer_name,
        "account_number": new_case.account_number,
        "customer_email": new_case.customer_email,
        "customer_phone": new_case.customer_phone,
        "title": new_case.title,
        "description": new_case.description,
        "category": new_case.category,
        "subcategory": new_case.subcategory,
        "disputed_amount": new_case.disputed_amount,
        "priority": new_case.priority,
        "status": new_case.status,
        "sla_deadline": new_case.sla_deadline,
        "assigned_to": new_case.assigned_to,
        "logged_by": new_case.logged_by,
        "resolution_notes": new_case.resolution_notes,
        "supervisor_feedback": new_case.supervisor_feedback,
        "created_at": new_case.created_at,
        "updated_at": new_case.updated_at
    }
