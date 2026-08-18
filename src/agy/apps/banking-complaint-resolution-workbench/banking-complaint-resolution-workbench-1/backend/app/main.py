import datetime
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

class CommentCreate(BaseModel):
    comment: str

class ProposalCreate(BaseModel):
    resolution_notes: str

class RejectionCreate(BaseModel):
    feedback: str

def format_complaint(c: Complaint):
    """Helper to format a SQLAlchemy Complaint instance into a standard dictionary."""
    return {
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

# Initialize database on startup if running as main server
@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Retrieve real-time summary counts for the dashboard metric widgets."""
    now = datetime.datetime.utcnow()
    one_day_from_now = now + datetime.timedelta(days=1)
    
    # Active Cases: Registered, Under Investigation, Needs Revision
    active_count = db.query(Complaint).filter(Complaint.status.in_(["Registered", "Under Investigation", "Needs Revision"])).count()
    
    # Pending Approval: Resolution Proposed
    pending_count = db.query(Complaint).filter(Complaint.status == "Resolution Proposed").count()
    
    # SLA Critical: Active cases with SLA deadline less than 24 hours away
    sla_critical_count = db.query(Complaint).filter(
        Complaint.status.in_(["Registered", "Under Investigation", "Needs Revision"]),
        Complaint.sla_deadline <= one_day_from_now
    ).count()
    
    # Resolved Cases: Resolved
    resolved_count = db.query(Complaint).filter(Complaint.status == "Resolved").count()
    
    return {
        "active_cases": active_count,
        "pending_approval": pending_count,
        "sla_critical": sla_critical_count,
        "resolved_cases": resolved_count
    }

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
    
    return [format_complaint(c) for c in complaints]

@app.get("/api/complaints/{complaint_id}")
def get_complaint_details(complaint_id: str, db: Session = Depends(get_db)):
    """Retrieve complete details for a single complaint including its chronological audit history."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    # Query all audit logs for this complaint in ascending (chronological) order
    audit_logs = db.query(AuditLog).filter(AuditLog.complaint_id == complaint_id).order_by(AuditLog.timestamp.asc()).all()
    
    details = format_complaint(complaint)
    details["audit_logs"] = [
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
    return details

@app.post("/api/complaints", status_code=201)
def create_complaint(
    payload: ComplaintCreate,
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    db: Session = Depends(get_db)
):
    """Log a new customer complaint, generate a unique sequential ID, calculate SLA, and log audit event."""
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
    
    sla_deadline = calculate_sla(payload.priority)
    
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
    
    # Write Audit Event
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
    
    return format_complaint(new_case)

@app.post("/api/complaints/{complaint_id}/claim")
def claim_complaint(
    complaint_id: str,
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    db: Session = Depends(get_db)
):
    """Claim/assign a case to the active case handler, transitioning status to 'Under Investigation'."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    complaint.status = "Under Investigation"
    complaint.assigned_to = x_user_name
    db.commit()
    db.refresh(complaint)
    
    # Write Audit Log
    user_obj = db.query(User).filter(User.username == x_user_name).first()
    actor_name = user_obj.name if user_obj else (x_user_name if x_user_name else "System")
    actor_role = user_obj.role if user_obj else (x_user_role if x_user_role else "System")
    
    audit_log = AuditLog(
        complaint_id=complaint_id,
        user_name=actor_name,
        user_role=actor_role,
        event_type="Claim Case",
        description=f"Case claimed by {actor_name} ({actor_role}). Status changed to Under Investigation."
    )
    db.add(audit_log)
    db.commit()
    
    return format_complaint(complaint)

@app.post("/api/complaints/{complaint_id}/comment")
def add_complaint_comment(
    complaint_id: str,
    payload: CommentCreate,
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    db: Session = Depends(get_db)
):
    """Append a custom user comment directly to the complaint's audit log timeline."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    user_obj = db.query(User).filter(User.username == x_user_name).first()
    actor_name = user_obj.name if user_obj else (x_user_name if x_user_name else "System")
    actor_role = user_obj.role if user_obj else (x_user_role if x_user_role else "System")
    
    audit_log = AuditLog(
        complaint_id=complaint_id,
        user_name=actor_name,
        user_role=actor_role,
        event_type="Add Comment",
        description=f"Comment added by {actor_name} ({actor_role}): {payload.comment}"
    )
    db.add(audit_log)
    db.commit()
    
    return {"status": "success", "detail": "Comment added successfully"}

@app.post("/api/complaints/{complaint_id}/propose")
def propose_resolution(
    complaint_id: str,
    payload: ProposalCreate,
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    db: Session = Depends(get_db)
):
    """Submit proposed resolution notes, transitioning status to 'Resolution Proposed'."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    complaint.status = "Resolution Proposed"
    complaint.resolution_notes = payload.resolution_notes
    db.commit()
    db.refresh(complaint)
    
    # Write Audit Log
    user_obj = db.query(User).filter(User.username == x_user_name).first()
    actor_name = user_obj.name if user_obj else (x_user_name if x_user_name else "System")
    actor_role = user_obj.role if user_obj else (x_user_role if x_user_role else "System")
    
    audit_log = AuditLog(
        complaint_id=complaint_id,
        user_name=actor_name,
        user_role=actor_role,
        event_type="Submit Proposal",
        description=f"Resolution proposed by {actor_name} ({actor_role}). Notes: {payload.resolution_notes}"
    )
    db.add(audit_log)
    db.commit()
    
    return format_complaint(complaint)

@app.post("/api/complaints/{complaint_id}/approve")
def approve_resolution(
    complaint_id: str,
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    db: Session = Depends(get_db)
):
    """Supervisor approves the resolution, transitioning status to 'Resolved' (RBAC Checked)."""
    # Role check: only supervisors can approve resolutions
    if x_user_role != "Supervisor":
        raise HTTPException(status_code=403, detail="Only supervisors can approve resolutions")
        
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    complaint.status = "Resolved"
    db.commit()
    db.refresh(complaint)
    
    # Write Audit Log
    user_obj = db.query(User).filter(User.username == x_user_name).first()
    actor_name = user_obj.name if user_obj else (x_user_name if x_user_name else "System")
    actor_role = user_obj.role if user_obj else (x_user_role if x_user_role else "System")
    
    audit_log = AuditLog(
        complaint_id=complaint_id,
        user_name=actor_name,
        user_role=actor_role,
        event_type="Approve Case",
        description=f"Resolution approved and case closed by {actor_name} ({actor_role})."
    )
    db.add(audit_log)
    db.commit()
    
    return format_complaint(complaint)

@app.post("/api/complaints/{complaint_id}/reject")
def reject_resolution(
    complaint_id: str,
    payload: RejectionCreate,
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    db: Session = Depends(get_db)
):
    """Supervisor rejects the resolution, transitioning status to 'Needs Revision' (RBAC Checked)."""
    # Role check: only supervisors can reject resolutions
    if x_user_role != "Supervisor":
        raise HTTPException(status_code=403, detail="Only supervisors can reject resolutions")
        
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    complaint.status = "Needs Revision"
    complaint.supervisor_feedback = payload.feedback
    db.commit()
    db.refresh(complaint)
    
    # Write Audit Log
    user_obj = db.query(User).filter(User.username == x_user_name).first()
    actor_name = user_obj.name if user_obj else (x_user_name if x_user_name else "System")
    actor_role = user_obj.role if user_obj else (x_user_role if x_user_role else "System")
    
    audit_log = AuditLog(
        complaint_id=complaint_id,
        user_name=actor_name,
        user_role=actor_role,
        event_type="Reject Case",
        description=f"Resolution rejected by {actor_name} ({actor_role}). Feedback: {payload.feedback}"
    )
    db.add(audit_log)
    db.commit()
    
    return format_complaint(complaint)
