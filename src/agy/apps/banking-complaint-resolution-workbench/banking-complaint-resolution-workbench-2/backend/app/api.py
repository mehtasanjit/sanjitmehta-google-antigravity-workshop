import datetime
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db

router = APIRouter(prefix="/api")


def generate_reference_number(db: Session) -> str:
    current_year = datetime.datetime.utcnow().year
    # Count how many complaints have a reference number starting with CMP-current_year-
    count = db.query(models.Complaint).filter(
        models.Complaint.reference_number.like(f"CMP-{current_year}-%")
    ).count()
    for i in range(1, 1000):
        ref_num = f"CMP-{current_year}-{(count + i):03d}"
        if not db.query(models.Complaint).filter_by(reference_number=ref_num).first():
            return ref_num
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not generate unique reference number",
    )


def record_audit_log(
    db: Session,
    complaint_id: int,
    actor_role: str,
    actor_name: str,
    action_type: str,
    from_status: Optional[str] = None,
    to_status: Optional[str] = None,
    details: Optional[str] = None,
    metadata_json: Optional[str] = None,
):
    audit_entry = models.AuditLog(
        complaint_id=complaint_id,
        timestamp=datetime.datetime.utcnow(),
        actor_role=actor_role,
        actor_name=actor_name,
        action_type=action_type,
        from_status=from_status,
        to_status=to_status,
        details=details,
        metadata_json=metadata_json,
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry


@router.get("/complaints", response_model=List[schemas.ComplaintResponse])
def get_complaints(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    product: Optional[str] = None,
    search: Optional[str] = None,
    assigned_to: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Complaint)
    if status:
        query = query.filter(models.Complaint.status == status)
    if priority:
        query = query.filter(models.Complaint.priority == priority)
    if product:
        query = query.filter(models.Complaint.product_type == product)
    if assigned_to:
        query = query.filter(models.Complaint.assigned_to == assigned_to)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            models.Complaint.customer_name.ilike(search_pattern)
            | models.Complaint.customer_id.ilike(search_pattern)
            | models.Complaint.subject.ilike(search_pattern)
            | models.Complaint.narrative.ilike(search_pattern)
            | models.Complaint.reference_number.ilike(search_pattern)
        )
    return query.order_by(models.Complaint.created_at.desc()).all()


@router.post("/complaints", response_model=schemas.ComplaintResponse, status_code=status.HTTP_201_CREATED)
def create_complaint(
    complaint_in: schemas.ComplaintCreate, db: Session = Depends(get_db)
):
    ref_num = generate_reference_number(db)
    now = datetime.datetime.utcnow()
    db_complaint = models.Complaint(
        reference_number=ref_num,
        customer_name=complaint_in.customer_name,
        customer_id=complaint_in.customer_id,
        customer_email=complaint_in.customer_email,
        customer_phone=complaint_in.customer_phone,
        account_number=complaint_in.account_number,
        account_type=complaint_in.account_type,
        product_type=complaint_in.product_type,
        category=complaint_in.category,
        priority=complaint_in.priority,
        channel=complaint_in.channel,
        subject=complaint_in.subject,
        narrative=complaint_in.narrative,
        disputed_amount=complaint_in.disputed_amount,
        status="NEW",
        refund_amount=0.0,
        goodwill_amount=0.0,
        interest_amount=0.0,
        total_redress=0.0,
        review_decision="NONE",
        created_at=now,
        updated_at=now,
        sla_target_hours=complaint_in.sla_target_hours,
    )
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)

    # Record CREATED audit log
    record_audit_log(
        db=db,
        complaint_id=db_complaint.id,
        actor_role="Customer",
        actor_name=db_complaint.customer_name,
        action_type="CREATED",
        from_status=None,
        to_status="NEW",
        details="Complaint registered through intake channel.",
    )

    return db_complaint


@router.get("/complaints/{id}", response_model=schemas.ComplaintResponse)
def get_complaint_by_id(id: int, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found"
        )
    return complaint


@router.patch("/complaints/{id}/status", response_model=schemas.ComplaintResponse)
def transition_status(
    id: int, req: schemas.StatusTransitionRequest, db: Session = Depends(get_db)
):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found"
        )

    old_status = complaint.status
    new_status = req.status

    if old_status == new_status:
        return complaint

    complaint.status = new_status
    complaint.updated_at = datetime.datetime.utcnow()

    # If transitioning to RESOLVED, record the resolution date
    if new_status == "RESOLVED":
        complaint.resolved_at = datetime.datetime.utcnow()
    else:
        # If transitioning away from RESOLVED, unset resolved_at (if previously set)
        if old_status == "RESOLVED":
            complaint.resolved_at = None

    db.commit()
    db.refresh(complaint)

    # Determine action type based on target status
    action_type = "STATUS_CHANGED"
    if new_status == "RESOLVED":
        action_type = "RESOLVED"
    elif new_status == "ESCALATED":
        action_type = "ESCALATED"
    elif new_status == "UNDER_REVIEW":
        action_type = "SUBMITTED_FOR_REVIEW"

    record_audit_log(
        db=db,
        complaint_id=complaint.id,
        actor_role=req.actor_role,
        actor_name=req.actor_name,
        action_type=action_type,
        from_status=old_status,
        to_status=new_status,
        details=req.details or f"Status transitioned from {old_status} to {new_status}.",
    )

    return complaint


@router.patch("/complaints/{id}/assign", response_model=schemas.ComplaintResponse)
def assign_handler(
    id: int, req: schemas.AssignHandlerRequest, db: Session = Depends(get_db)
):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found"
        )

    old_status = complaint.status
    complaint.assigned_to = req.assigned_to
    complaint.updated_at = datetime.datetime.utcnow()

    # Auto-transition status from NEW to IN_INVESTIGATION if assigned
    new_status = old_status
    if old_status == "NEW":
        new_status = "IN_INVESTIGATION"
        complaint.status = new_status

    db.commit()
    db.refresh(complaint)

    # Log assignment audit log
    record_audit_log(
        db=db,
        complaint_id=complaint.id,
        actor_role=req.actor_role,
        actor_name=req.actor_name,
        action_type="ASSIGNED",
        from_status=old_status if old_status != new_status else None,
        to_status=new_status if old_status != new_status else None,
        details=req.details or f"Case assigned to {req.assigned_to}.",
    )

    return complaint


@router.post("/complaints/{id}/investigation", response_model=schemas.ComplaintResponse)
def save_investigation(
    id: int, req: schemas.InvestigationRequest, db: Session = Depends(get_db)
):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found"
        )

    complaint.root_cause = req.root_cause
    complaint.investigation_notes = req.investigation_notes
    complaint.updated_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(complaint)

    record_audit_log(
        db=db,
        complaint_id=complaint.id,
        actor_role=req.actor_role,
        actor_name=req.actor_name,
        action_type="INVESTIGATION_UPDATED",
        details=f"Investigation notes updated. Root cause identified: {req.root_cause}",
    )

    return complaint


@router.post("/complaints/{id}/redress", response_model=schemas.ComplaintResponse)
def save_redress(
    id: int, req: schemas.RedressRequest, db: Session = Depends(get_db)
):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found"
        )

    complaint.refund_amount = req.refund_amount
    complaint.goodwill_amount = req.goodwill_amount
    complaint.interest_amount = req.interest_amount
    complaint.total_redress = req.refund_amount + req.goodwill_amount + req.interest_amount
    complaint.updated_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(complaint)

    metadata = {
        "refund_amount": req.refund_amount,
        "goodwill_amount": req.goodwill_amount,
        "interest_amount": req.interest_amount,
        "total_redress": complaint.total_redress,
    }

    record_audit_log(
        db=db,
        complaint_id=complaint.id,
        actor_role=req.actor_role,
        actor_name=req.actor_name,
        action_type="REDRESS_CALCULATED",
        details=f"Redress calculated: Total Redress = ${complaint.total_redress:.2f}",
        metadata_json=json.dumps(metadata),
    )

    return complaint


@router.post("/complaints/{id}/review", response_model=schemas.ComplaintResponse)
def supervisor_review(
    id: int, req: schemas.SupervisorReviewRequest, db: Session = Depends(get_db)
):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found"
        )

    decision = req.review_decision
    if decision == "REJECTED" and not req.supervisor_notes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supervisor notes/rejection reason is required for rejection",
        )

    old_status = complaint.status
    complaint.review_decision = decision
    complaint.supervisor_name = req.supervisor_name
    complaint.supervisor_notes = req.supervisor_notes
    complaint.updated_at = datetime.datetime.utcnow()

    actor_name = req.actor_name or req.supervisor_name

    if decision == "APPROVED":
        new_status = "APPROVED"
        complaint.status = new_status
        action_type = "SUPERVISOR_APPROVED"
        details = f"Supervisor approval by {req.supervisor_name}."
    else:  # REJECTED
        new_status = "IN_INVESTIGATION"
        complaint.status = new_status
        action_type = "SUPERVISOR_REJECTED"
        details = f"Supervisor rejection by {req.supervisor_name}. Reason: {req.supervisor_notes}"

    db.commit()
    db.refresh(complaint)

    record_audit_log(
        db=db,
        complaint_id=complaint.id,
        actor_role=req.actor_role,
        actor_name=actor_name,
        action_type=action_type,
        from_status=old_status,
        to_status=new_status,
        details=details,
    )

    return complaint


@router.get("/complaints/{id}/audit-trail", response_model=List[schemas.AuditLogResponse])
def get_audit_trail(id: int, db: Session = Depends(get_db)):
    # Check if complaint exists first
    complaint = db.query(models.Complaint).filter(models.Complaint.id == id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found"
        )
    return (
        db.query(models.AuditLog)
        .filter(models.AuditLog.complaint_id == id)
        .order_by(models.AuditLog.timestamp.asc())
        .all()
    )


@router.get("/stats", response_model=schemas.WorkbenchStatsResponse)
def get_stats(db: Session = Depends(get_db)):
    complaints = db.query(models.Complaint).all()
    total = len(complaints)
    under_review = sum(1 for c in complaints if c.status == "UNDER_REVIEW")
    in_investigation = sum(1 for c in complaints if c.status == "IN_INVESTIGATION")
    resolved = sum(1 for c in complaints if c.status == "RESOLVED")
    escalated = sum(1 for c in complaints if c.status == "ESCALATED")
    # Redress paid is total redress for resolved complaints
    total_redress_paid = sum(c.total_redress for c in complaints if c.status == "RESOLVED")

    return schemas.WorkbenchStatsResponse(
        total=total,
        under_review=under_review,
        in_investigation=in_investigation,
        resolved=resolved,
        escalated=escalated,
        total_redress_paid=total_redress_paid,
    )


@router.post("/seed")
def seed(db: Session = Depends(get_db)):
    from .seed import seed_db
    try:
        seed_db(db)
        return {"message": "Database reset and seeded successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed database: {str(e)}",
        )
