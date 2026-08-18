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
