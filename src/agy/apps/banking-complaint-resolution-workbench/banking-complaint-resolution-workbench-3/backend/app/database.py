import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Get database URL from environment or fallback to sqlite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./complaints.db")

# For SQLite, we need to allow multi-threaded access for FastAPI
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

def seed_database(db):
    from app.models import Complaint, ActivityLog
    
    # Check if complaints table is already seeded
    if db.query(Complaint).count() > 0:
        return
        
    mock_complaints = [
        Complaint(
            customer_name="John Doe",
            account_number="XXXXXX4321",
            account_type="Checking",
            severity="High",
            status="New",
            description="Identity theft reported on checking account. Unauthorized wire transfer of $10,000 to an unknown account."
        ),
        Complaint(
            customer_name="Jane Smith",
            account_number="XXXXXX8765",
            account_type="Savings",
            severity="Medium",
            status="New",
            description="Incorrect fee charged on my savings account. I was promised no monthly fees if I kept a $1,000 balance, which I did."
        ),
        Complaint(
            customer_name="Robert Johnson",
            account_number="XXXXXX2468",
            account_type="Credit Card",
            severity="Low",
            status="New",
            description="Double transaction for the same purchase at Starbucks. Charged $5.45 twice."
        ),
        Complaint(
            customer_name="Emily Davis",
            account_number="XXXXXX1357",
            account_type="Credit Card",
            severity="High",
            status="New",
            description="My credit card was charged for a flight I never booked. The amount is $1,250 and is currently pending."
        )
    ]
    
    for complaint in mock_complaints:
        db.add(complaint)
        db.commit() # Commit to generate ID
        db.refresh(complaint)
        
        # Add corresponding activity log
        log = ActivityLog(
            complaint_id=complaint.id,
            action="Created",
            performed_by="System",
            comments="Complaint registered during system initialization."
        )
        db.add(log)
        db.commit()
