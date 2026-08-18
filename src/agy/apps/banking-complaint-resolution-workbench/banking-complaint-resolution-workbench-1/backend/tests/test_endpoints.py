import os
import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db, calculate_sla
from app.models import Base, User, Complaint, AuditLog
from app.main import app

DB_FILE = "test_endpoints.db"
DB_URL = f"sqlite:///{DB_FILE}"

# Create a temporary SQLite database on disk for endpoint testing
@pytest.fixture(name="client")
def client_fixture():
    # Ensure any stale test db file is deleted first
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    
    # Seed standard users
    users = [
        User(username="jane_doe", name="Jane Doe", role="CSR"),
        User(username="john_smith", name="John Smith", role="Case Handler"),
        User(username="alice_johnson", name="Alice Johnson", role="Case Handler"),
        User(username="robert_vance", name="Robert Vance", role="Supervisor")
    ]
    for u in users:
        session.add(u)
    session.commit()
    
    now = datetime.datetime.utcnow()
    # Seed complaints
    c1 = Complaint(
        id="CRW-2026-0001",
        customer_name="Marcus Aurelius",
        account_number="ACT-98234-92",
        customer_email="marcus@meditations.com",
        customer_phone="+1-555-0192",
        title="Overcharged Credit Card Annual Fee",
        description="Verbally promised a waiver of the $150 annual fee.",
        category="Credit Cards",
        subcategory="Fee Dispute",
        disputed_amount=150.0,
        priority="Medium",
        status="Registered",
        sla_deadline=calculate_sla("Medium", now),
        logged_by="jane_doe"
    )
    session.add(c1)
    session.commit()
    session.close()
    
    # Override get_db dependency to point to our test DB file
    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()
    
    # Clean up test DB file
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

def test_get_complaints_list_exists():
    """Verify that GET /api/complaints endpoint exists."""
    assert app is not None

def test_get_complaints_endpoint(client):
    """Verify GET /api/complaints list retrieval."""
    response = client.get("/api/complaints")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["id"] == "CRW-2026-0001"
    assert data[0]["customer_name"] == "Marcus Aurelius"
    assert data[0]["status"] == "Registered"

def test_get_complaint_details_endpoint(client):
    """Verify GET /api/complaints/{id} details retrieval."""
    response = client.get("/api/complaints/CRW-2026-0001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "CRW-2026-0001"
    assert "audit_logs" in data
    assert len(data["audit_logs"]) >= 0

def test_get_complaint_not_found(client):
    """Verify GET /api/complaints/{id} returns 404 for invalid ID."""
    response = client.get("/api/complaints/CRW-INVALID-999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"

def test_create_complaint_endpoint(client):
    """Verify POST /api/complaints successfully logs a complaint and writes audit log."""
    new_complaint = {
        "customer_name": "Julius Caesar",
        "account_number": "ACT-11111-22",
        "customer_email": "julius@rome.gov",
        "customer_phone": "+1-555-4444",
        "title": "Unauthorised Senate Expense Posting",
        "description": "Unexplained debit of $500 for robes posting to debit card.",
        "category": "Credit Cards",
        "subcategory": "Unauthorised Charge",
        "disputed_amount": 500.0,
        "priority": "Critical"
    }
    
    response = client.post(
        "/api/complaints",
        json=new_complaint,
        headers={"X-User-Name": "jane_doe", "X-User-Role": "CSR"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"].startswith("CRW-")
    assert data["customer_name"] == "Julius Caesar"
    assert data["priority"] == "Critical"
    assert data["status"] == "Registered"
    assert data["logged_by"] == "jane_doe"
    assert data["sla_deadline"] is not None
    
    # Verify audit log was written by calling details endpoint
    details_response = client.get(f"/api/complaints/{data['id']}")
    assert details_response.status_code == 200
    details_data = details_response.json()
    assert len(details_data["audit_logs"]) == 1
    assert details_data["audit_logs"][0]["event_type"] == "Log Complaint"
    assert details_data["audit_logs"][0]["user_name"] == "Jane Doe"

def test_claim_complaint_endpoint(client):
    """Verify POST /api/complaints/{id}/claim assigns the handler and changes status."""
    response = client.post(
        "/api/complaints/CRW-2026-0001/claim",
        headers={"X-User-Name": "john_smith", "X-User-Role": "Case Handler"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Under Investigation"
    assert data["assigned_to"] == "john_smith"
    
    # Verify 'Claim Case' audit log
    details_response = client.get("/api/complaints/CRW-2026-0001")
    details = details_response.json()
    assert any(log["event_type"] == "Claim Case" for log in details["audit_logs"])

def test_add_comment_endpoint(client):
    """Verify POST /api/complaints/{id}/comment appends comment to audit logs."""
    response = client.post(
        "/api/complaints/CRW-2026-0001/comment",
        json={"comment": "Called merchant back to check transaction status."},
        headers={"X-User-Name": "john_smith", "X-User-Role": "Case Handler"}
    )
    assert response.status_code == 200
    
    # Verify 'Add Comment' log exists in history
    details_response = client.get("/api/complaints/CRW-2026-0001")
    details = details_response.json()
    assert any("merchant" in log["description"] for log in details["audit_logs"])

def test_resolution_propose_approve_reject_flow(client):
    """Verify full supervisor review lifecycle (Propose -> Reject -> Propose -> Approve)."""
    # 1. Propose resolution
    response = client.post(
        "/api/complaints/CRW-2026-0001/propose",
        json={"resolution_notes": "We will waive the fee as customer is eligible."},
        headers={"X-User-Name": "john_smith", "X-User-Role": "Case Handler"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Resolution Proposed"
    assert response.json()["resolution_notes"] == "We will waive the fee as customer is eligible."
    
    # 2. Reject proposal (Should check Supervisor role)
    # Attempt with CSR (should fail with 403)
    reject_fail = client.post(
        "/api/complaints/CRW-2026-0001/reject",
        json={"feedback": "Need merchant proof of fee promise."},
        headers={"X-User-Name": "jane_doe", "X-User-Role": "CSR"}
    )
    assert reject_fail.status_code == 403
    
    # Attempt with Supervisor (should succeed)
    reject_ok = client.post(
        "/api/complaints/CRW-2026-0001/reject",
        json={"feedback": "Need merchant proof of fee promise."},
        headers={"X-User-Name": "robert_vance", "X-User-Role": "Supervisor"}
    )
    assert reject_ok.status_code == 200
    assert reject_ok.json()["status"] == "Needs Revision"
    assert reject_ok.json()["supervisor_feedback"] == "Need merchant proof of fee promise."
    
    # 3. Propose again
    response_2 = client.post(
        "/api/complaints/CRW-2026-0001/propose",
        json={"resolution_notes": "Added merchant email verification. Waiving fee."},
        headers={"X-User-Name": "john_smith", "X-User-Role": "Case Handler"}
    )
    assert response_2.status_code == 200
    assert response_2.json()["status"] == "Resolution Proposed"
    
    # 4. Approve resolution (Should check Supervisor role)
    # Attempt with Case Handler (should fail)
    approve_fail = client.post(
        "/api/complaints/CRW-2026-0001/approve",
        headers={"X-User-Name": "john_smith", "X-User-Role": "Case Handler"}
    )
    assert approve_fail.status_code == 403
    
    # Attempt with Supervisor (should succeed)
    approve_ok = client.post(
        "/api/complaints/CRW-2026-0001/approve",
        headers={"X-User-Name": "robert_vance", "X-User-Role": "Supervisor"}
    )
    assert approve_ok.status_code == 200
    assert approve_ok.json()["status"] == "Resolved"

def test_dashboard_stats_endpoint(client):
    """Verify GET /api/dashboard/stats returns correct totals."""
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "active_cases" in stats
    assert "pending_approval" in stats
    assert "sla_critical" in stats
    assert "resolved_cases" in stats
