import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app import models

# File-based SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_complaints.db"
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


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_read_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_create_complaint(client):
    payload = {
        "customer_name": "James Smith",
        "customer_id": "CUST-9999",
        "customer_email": "james@example.com",
        "customer_phone": "555-9999",
        "account_number": "ACT-12345",
        "account_type": "Checking",
        "product_type": "checking",
        "category": "Service Charge",
        "priority": "MEDIUM",
        "channel": "Online",
        "subject": "Charged twice",
        "narrative": "I got charged a monthly service fee twice on my statement.",
        "disputed_amount": 15.0,
        "sla_target_hours": 168
    }
    res = client.post("/api/complaints", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["reference_number"].startswith("CMP-2026-")
    assert data["customer_name"] == "James Smith"
    assert data["status"] == "NEW"

    # Verify audit log was created
    complaint_id = data["id"]
    audit_res = client.get(f"/api/complaints/{complaint_id}/audit-trail")
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    assert len(audit_data) == 1
    assert audit_data[0]["action_type"] == "CREATED"
    assert audit_data[0]["actor_role"] == "Customer"


def test_get_complaints_and_filters(client, db_session):
    # Setup some complaints directly in the DB
    c1 = models.Complaint(
        reference_number="CMP-2026-101",
        customer_name="Alice Blue",
        customer_id="CUST-101",
        customer_email="alice@example.com",
        customer_phone="555-1011",
        account_number="ACT-101",
        account_type="Credit Card",
        product_type="credit cards",
        category="Fees",
        priority="HIGH",
        channel="Online",
        subject="Annual fee",
        narrative="Disputing annual fee",
        disputed_amount=95.0,
        status="IN_INVESTIGATION",
        assigned_to="Jane Doe",
        sla_target_hours=72,
    )
    c2 = models.Complaint(
        reference_number="CMP-2026-102",
        customer_name="Bob Green",
        customer_id="CUST-102",
        customer_email="bob@example.com",
        customer_phone="555-1022",
        account_number="ACT-102",
        account_type="Checking",
        product_type="checking",
        category="Overdraft",
        priority="LOW",
        channel="Phone",
        subject="Overdraft charge",
        narrative="Disputing overdraft fee",
        disputed_amount=35.0,
        status="NEW",
        assigned_to=None,
        sla_target_hours=120,
    )
    db_session.add_all([c1, c2])
    db_session.commit()

    # Test get all
    res = client.get("/api/complaints")
    assert res.status_code == 200
    assert len(res.json()) == 2

    # Test filter by status
    res = client.get("/api/complaints?status=IN_INVESTIGATION")
    assert len(res.json()) == 1
    assert res.json()[0]["customer_name"] == "Alice Blue"

    # Test filter by priority
    res = client.get("/api/complaints?priority=LOW")
    assert len(res.json()) == 1
    assert res.json()[0]["customer_name"] == "Bob Green"

    # Test filter by assigned_to
    res = client.get("/api/complaints?assigned_to=Jane Doe")
    assert len(res.json()) == 1
    assert res.json()[0]["customer_name"] == "Alice Blue"

    # Test filter by search query (subject search)
    res = client.get("/api/complaints?search=Annual")
    assert len(res.json()) == 1
    assert res.json()[0]["customer_name"] == "Alice Blue"

    # Test filter by search query (customer name search)
    res = client.get("/api/complaints?search=Bob")
    assert len(res.json()) == 1
    assert res.json()[0]["customer_name"] == "Bob Green"


def test_transition_status(client, db_session):
    c = models.Complaint(
        reference_number="CMP-2026-201",
        customer_name="John Doe",
        customer_id="CUST-201",
        customer_email="john@example.com",
        customer_phone="555-2011",
        account_number="ACT-201",
        account_type="Checking",
        product_type="checking",
        category="Fees",
        priority="MEDIUM",
        channel="Online",
        subject="Fees",
        narrative="Narrative",
        disputed_amount=20.0,
        status="NEW",
        sla_target_hours=168,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)

    # Transition to IN_INVESTIGATION
    payload = {
        "status": "IN_INVESTIGATION",
        "actor_role": "Case Handler",
        "actor_name": "Jane Doe",
        "details": "Starting investigation."
    }
    res = client.patch(f"/api/complaints/{c.id}/status", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "IN_INVESTIGATION"

    # Verify audit log
    audit_res = client.get(f"/api/complaints/{c.id}/audit-trail")
    audit_logs = audit_res.json()
    assert len(audit_logs) == 1
    assert audit_logs[-1]["action_type"] == "STATUS_CHANGED"
    assert audit_logs[-1]["from_status"] == "NEW"
    assert audit_logs[-1]["to_status"] == "IN_INVESTIGATION"

    # Transition to RESOLVED and verify resolved_at
    payload_resolve = {
        "status": "RESOLVED",
        "actor_role": "Case Handler",
        "actor_name": "Jane Doe",
        "details": "Resolved. Customer is happy."
    }
    res_resolve = client.patch(f"/api/complaints/{c.id}/status", json=payload_resolve)
    assert res_resolve.status_code == 200
    assert res_resolve.json()["status"] == "RESOLVED"
    assert res_resolve.json()["resolved_at"] is not None


def test_assign_handler(client, db_session):
    c = models.Complaint(
        reference_number="CMP-2026-301",
        customer_name="Peter Parker",
        customer_id="CUST-301",
        customer_email="peter@example.com",
        customer_phone="555-3011",
        account_number="ACT-301",
        account_type="Checking",
        product_type="checking",
        category="Fees",
        priority="MEDIUM",
        channel="Online",
        subject="Fees",
        narrative="Narrative",
        disputed_amount=20.0,
        status="NEW",
        sla_target_hours=168,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)

    payload = {
        "assigned_to": "Jane Doe",
        "actor_role": "Supervisor",
        "actor_name": "Sarah Jenkins",
        "details": "Assigning to Jane due to workload balance."
    }
    res = client.patch(f"/api/complaints/{c.id}/assign", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["assigned_to"] == "Jane Doe"
    # Auto-transition status from NEW to IN_INVESTIGATION
    assert data["status"] == "IN_INVESTIGATION"

    # Verify audit log
    audit_res = client.get(f"/api/complaints/{c.id}/audit-trail")
    audit_logs = audit_res.json()
    assert len(audit_logs) == 1
    assert audit_logs[0]["action_type"] == "ASSIGNED"
    assert audit_logs[0]["from_status"] == "NEW"
    assert audit_logs[0]["to_status"] == "IN_INVESTIGATION"


def test_save_investigation(client, db_session):
    c = models.Complaint(
        reference_number="CMP-2026-401",
        customer_name="Bruce Wayne",
        customer_id="CUST-401",
        customer_email="bruce@example.com",
        customer_phone="555-4011",
        account_number="ACT-401",
        account_type="Checking",
        product_type="checking",
        category="Fees",
        priority="MEDIUM",
        channel="Online",
        subject="Fees",
        narrative="Narrative",
        disputed_amount=20.0,
        status="IN_INVESTIGATION",
        sla_target_hours=168,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)

    payload = {
        "root_cause": "System batch error",
        "investigation_notes": "We saw the system ran the charge twice due to a scheduler crash.",
        "actor_role": "Case Handler",
        "actor_name": "Jane Doe"
    }
    res = client.post(f"/api/complaints/{c.id}/investigation", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["root_cause"] == "System batch error"
    assert data["investigation_notes"] == "We saw the system ran the charge twice due to a scheduler crash."

    # Verify audit log
    audit_res = client.get(f"/api/complaints/{c.id}/audit-trail")
    assert audit_res.json()[-1]["action_type"] == "INVESTIGATION_UPDATED"


def test_save_redress_calculation(client, db_session):
    c = models.Complaint(
        reference_number="CMP-2026-501",
        customer_name="Tony Stark",
        customer_id="CUST-501",
        customer_email="tony@example.com",
        customer_phone="555-5011",
        account_number="ACT-501",
        account_type="Checking",
        product_type="checking",
        category="Fees",
        priority="MEDIUM",
        channel="Online",
        subject="Fees",
        narrative="Narrative",
        disputed_amount=20.0,
        status="IN_INVESTIGATION",
        sla_target_hours=168,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)

    payload = {
        "refund_amount": 20.0,
        "goodwill_amount": 10.0,
        "interest_amount": 2.50,
        "actor_role": "Case Handler",
        "actor_name": "Jane Doe"
    }
    res = client.post(f"/api/complaints/{c.id}/redress", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["refund_amount"] == 20.0
    assert data["goodwill_amount"] == 10.0
    assert data["interest_amount"] == 2.50
    assert data["total_redress"] == 32.50

    # Verify audit log has metadata_json
    audit_res = client.get(f"/api/complaints/{c.id}/audit-trail")
    last_log = audit_res.json()[-1]
    assert last_log["action_type"] == "REDRESS_CALCULATED"
    assert "refund_amount" in last_log["metadata_json"]


def test_supervisor_review(client, db_session):
    c = models.Complaint(
        reference_number="CMP-2026-601",
        customer_name="Diana Prince",
        customer_id="CUST-601",
        customer_email="diana@example.com",
        customer_phone="555-6011",
        account_number="ACT-601",
        account_type="Checking",
        product_type="checking",
        category="Fees",
        priority="MEDIUM",
        channel="Online",
        subject="Fees",
        narrative="Narrative",
        disputed_amount=20.0,
        status="UNDER_REVIEW",
        sla_target_hours=168,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)

    # Rejection should fail if supervisor_notes (rejection reason) is missing
    payload_bad_reject = {
        "review_decision": "REJECTED",
        "supervisor_name": "Sarah Jenkins",
        "supervisor_notes": None
    }
    res_bad = client.post(f"/api/complaints/{c.id}/review", json=payload_bad_reject)
    assert res_bad.status_code == 400
    assert "reason is required" in res_bad.json()["detail"]

    # Rejection should pass if notes are provided, and status changes back to IN_INVESTIGATION
    payload_good_reject = {
        "review_decision": "REJECTED",
        "supervisor_name": "Sarah Jenkins",
        "supervisor_notes": "Please verify if the interest amount was computed correctly."
    }
    res_reject = client.post(f"/api/complaints/{c.id}/review", json=payload_good_reject)
    assert res_reject.status_code == 200
    assert res_reject.json()["status"] == "IN_INVESTIGATION"
    assert res_reject.json()["review_decision"] == "REJECTED"

    # Approval
    # First transition back to UNDER_REVIEW
    c.status = "UNDER_REVIEW"
    db_session.commit()

    payload_approve = {
        "review_decision": "APPROVED",
        "supervisor_name": "Sarah Jenkins",
        "supervisor_notes": "Everything looks perfect. Well investigated."
    }
    res_approve = client.post(f"/api/complaints/{c.id}/review", json=payload_approve)
    assert res_approve.status_code == 200
    assert res_approve.json()["status"] == "APPROVED"
    assert res_approve.json()["review_decision"] == "APPROVED"


def test_get_stats(client, db_session):
    # Setup multiple complaints with various statuses
    c1 = models.Complaint(
        reference_number="CMP-2026-701",
        customer_name="C1", customer_id="C1", customer_email="c1@example.com", customer_phone="1", account_number="1",
        account_type="Checking", product_type="checking", category="A", priority="LOW", channel="O", subject="S", narrative="N",
        disputed_amount=10.0, status="RESOLVED", refund_amount=10.0, goodwill_amount=5.0, total_redress=15.0, sla_target_hours=168,
    )
    c2 = models.Complaint(
        reference_number="CMP-2026-702",
        customer_name="C2", customer_id="C2", customer_email="c2@example.com", customer_phone="2", account_number="2",
        account_type="Checking", product_type="checking", category="A", priority="LOW", channel="O", subject="S", narrative="N",
        disputed_amount=20.0, status="RESOLVED", refund_amount=20.0, goodwill_amount=10.0, total_redress=30.0, sla_target_hours=168,
    )
    c3 = models.Complaint(
        reference_number="CMP-2026-703",
        customer_name="C3", customer_id="C3", customer_email="c3@example.com", customer_phone="3", account_number="3",
        account_type="Checking", product_type="checking", category="A", priority="LOW", channel="O", subject="S", narrative="N",
        disputed_amount=20.0, status="IN_INVESTIGATION", total_redress=20.0, sla_target_hours=168,  # Not resolved, shouldn't count for redress paid
    )
    db_session.add_all([c1, c2, c3])
    db_session.commit()

    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 3
    assert data["resolved"] == 2
    assert data["in_investigation"] == 1
    assert data["total_redress_paid"] == 45.0  # 15.0 + 30.0


def test_seed_endpoint(client):
    res = client.post("/api/seed")
    assert res.status_code == 200
    assert "seeded successfully" in res.json()["message"]

    # Verify they exist via the GET endpoint
    get_res = client.get("/api/complaints")
    assert len(get_res.json()) == 17
