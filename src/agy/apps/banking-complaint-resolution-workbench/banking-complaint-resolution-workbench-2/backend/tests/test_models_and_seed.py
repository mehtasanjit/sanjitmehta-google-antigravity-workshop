import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app import models
from backend.app.seed import seed_db

# Use file-based SQLite for model testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_models_seed.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_models_creation_and_relationships(db_session):
    # Test creating a complaint
    complaint = models.Complaint(
        reference_number="CMP-TEST-001",
        customer_name="Test Customer",
        customer_id="CUST-111",
        customer_email="test@example.com",
        customer_phone="123-4567",
        account_number="ACT-000",
        account_type="Checking",
        product_type="checking",
        category="Fees",
        priority="LOW",
        channel="Online",
        subject="Disputed fee",
        narrative="Test narrative",
        disputed_amount=10.0,
        status="NEW",
        sla_target_hours=168,
    )
    db_session.add(complaint)
    db_session.commit()
    db_session.refresh(complaint)

    assert complaint.id is not None
    assert complaint.status == "NEW"
    assert complaint.total_redress == 0.0

    # Test creating an audit log
    audit_log = models.AuditLog(
        complaint_id=complaint.id,
        actor_role="System",
        actor_name="Automated System",
        action_type="CREATED",
        from_status=None,
        to_status="NEW",
        details="Complaint registered.",
    )
    db_session.add(audit_log)
    db_session.commit()
    db_session.refresh(audit_log)

    assert audit_log.id is not None
    assert audit_log.complaint_id == complaint.id

    # Test relationship
    assert len(complaint.audit_logs) == 1
    assert complaint.audit_logs[0].id == audit_log.id

    # Test cascade delete
    db_session.delete(complaint)
    db_session.commit()

    # The audit log should be deleted due to cascade
    remaining_logs = db_session.query(models.AuditLog).filter_by(id=audit_log.id).all()
    assert len(remaining_logs) == 0


def test_seed_db_reproducibility(db_session):
    # Run the seed function
    seed_db(db_session)

    # Verify that exactly 17 records were seeded
    complaints = db_session.query(models.Complaint).all()
    assert len(complaints) == 17

    # Verify that different product types are represented
    product_types = {c.product_type for c in complaints}
    assert "checking" in product_types
    assert "credit cards" in product_types
    assert "mortgages" in product_types
    assert "personal loans" in product_types
    assert "wire transfers" in product_types
    assert "fraud claims" in product_types

    # Verify all workflow statuses are represented
    statuses = {c.status for c in complaints}
    assert "NEW" in statuses
    assert "IN_INVESTIGATION" in statuses
    assert "UNDER_REVIEW" in statuses
    assert "APPROVED" in statuses
    assert "RESOLVED" in statuses
    assert "ESCALATED" in statuses

    # Verify rich audit logs are populated
    for complaint in complaints:
        assert len(complaint.audit_logs) >= 1
        # Check that audit logs are sorted chronologically
        timestamps = [log.timestamp for log in complaint.audit_logs]
        # In python, list is sorted if sorted(list) == list
        assert timestamps == sorted(timestamps)

    # Verify seed resets correctly
    seed_db(db_session)
    complaints_after = db_session.query(models.Complaint).all()
    assert len(complaints_after) == 17
