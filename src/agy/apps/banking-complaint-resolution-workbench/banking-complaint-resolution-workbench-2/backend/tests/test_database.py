import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Under TDD, we write these tests first.
# These imports are expected to fail initially (Red Phase) because app package doesn't exist yet.
try:
    from app.database import Base, init_db, seed_database, get_db
    from app.models import Complaint, ActivityLog
except ImportError:
    # We will raise the ImportError so that pytest fails during the Red Phase
    raise


def test_models_creation():
    # Setup in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        # Create a complaint
        complaint = Complaint(
            customer_name="Alice Smith",
            account_number="XXXXXX1234",
            account_type="Checking",
            severity="High",
            status="New",
            description="Unauthorized charge of $500 on my checking account."
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        
        assert complaint.id is not None
        assert complaint.customer_name == "Alice Smith"
        assert complaint.status == "New"
        assert complaint.created_at is not None
        assert complaint.updated_at is not None
        
        # Create an activity log
        log = ActivityLog(
            complaint_id=complaint.id,
            action="Created",
            performed_by="Intake Agent",
            comments="Complaint registered successfully."
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        
        assert log.id is not None
        assert log.complaint_id == complaint.id
        assert log.action == "Created"
        assert log.timestamp is not None
        
    finally:
        db.close()
        engine.dispose()


def test_database_seeding():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        # First verify it's empty
        complaints_count = db.query(Complaint).count()
        assert complaints_count == 0
        
        # Run seeding logic
        seed_database(db)
        
        # Verify 4 complaints are seeded
        assert db.query(Complaint).count() == 4
        
        # Verify there are activity logs for each seeded complaint
        all_complaints = db.query(Complaint).all()
        for complaint in all_complaints:
            logs = db.query(ActivityLog).filter_by(complaint_id=complaint.id).all()
            assert len(logs) == 1
            assert logs[0].action == "Created"
            
        # Verify varying severities
        severities = [complaint.severity for complaint in all_complaints]
        # Should have at least one High, Medium, Low
        assert "High" in severities
        assert "Medium" in severities
        assert "Low" in severities
        
        # Run seed_database again to verify it is idempotent
        seed_database(db)
        assert db.query(Complaint).count() == 4
        
    finally:
        db.close()
        engine.dispose()
