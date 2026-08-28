from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, init_db, seed_database
from app.models import Complaint, ActivityLog
from app.schemas import ComplaintResponse, ComplaintDetailResponse, ComplaintCreate, TransitionRequest

app = FastAPI(title="Banking Internal Complaint Tracker API", version="1.0")

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()
    db = next(get_db())
    try:
        seed_database(db)
    finally:
        db.close()

@app.get("/api/complaints", response_model=List[ComplaintResponse])
def get_complaints(db: Session = Depends(get_db)):
    return db.query(Complaint).order_by(Complaint.id.asc()).all()

@app.get("/api/complaints/{id}", response_model=ComplaintDetailResponse)
def get_complaint(id: int, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Fetch logs and assign to the complaint object
    logs = db.query(ActivityLog).filter(ActivityLog.complaint_id == id).order_by(ActivityLog.id.asc()).all()
    complaint.activity_logs = logs
    return complaint

@app.post("/api/complaints", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def create_complaint(complaint_in: ComplaintCreate, db: Session = Depends(get_db)):
    # Create the complaint
    complaint = Complaint(
        customer_name=complaint_in.customer_name,
        account_number=complaint_in.account_number,
        account_type=complaint_in.account_type,
        severity=complaint_in.severity,
        status="New",
        description=complaint_in.description
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    
    # Create the activity log for registration
    log = ActivityLog(
        complaint_id=complaint.id,
        action="Created",
        performed_by="Intake Agent",
        comments="Complaint registered successfully."
    )
    db.add(log)
    db.commit()
    
    return complaint

@app.post("/api/complaints/{id}/transition", response_model=ComplaintResponse)
def transition_complaint(id: int, body: TransitionRequest, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    current_status = complaint.status
    new_status = body.new_status
    
    # Define state transitions and their corresponding action strings
    transitions_map = {
        "New": {
            "Assigned": "Assigned Specialist"
        },
        "Assigned": {
            "In Progress": "Started Investigation"
        },
        "In Progress": {
            "Resolved": "Resolved Case"
        }
    }
    
    # Check if the requested transition is valid
    if current_status not in transitions_map or new_status not in transitions_map[current_status]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition from '{current_status}' to '{new_status}'."
        )
        
    action_name = transitions_map[current_status][new_status]
    performed_by = body.performed_by or "System"
    
    # Perform transitions and update specialist assignment if relevant
    complaint.status = new_status
    if new_status == "Assigned":
        # Extract specialist name from comments if mentioned, e.g. "Assigning to Senior Specialist Cooper"
        if body.comments and "Specialist Cooper" in body.comments:
            complaint.assigned_to = "Specialist Cooper"
        else:
            complaint.assigned_to = performed_by
            
    db.commit()
    db.refresh(complaint)
    
    # Add activity log for the transition
    log = ActivityLog(
        complaint_id=complaint.id,
        action=action_name,
        performed_by=performed_by,
        comments=body.comments
    )
    db.add(log)
    db.commit()
    db.refresh(complaint)
    
    return complaint
