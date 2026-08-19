import pytest
from fastapi.testclient import TestClient

# Under TDD, we write these tests first.
# These imports are expected to fail initially (Red Phase) because app.main package doesn't exist yet.
try:
    from app.main import app
    from app.database import get_db, Base, engine, SessionLocal
except ImportError:
    # We will raise the ImportError so that pytest fails during the Red Phase
    raise


@pytest.fixture(name="client")
def client_fixture():
    # Setup clean in-memory database for API testing
    Base.metadata.create_all(bind=engine)
    
    # We yield the TestClient
    with TestClient(app) as client:
        yield client
        
    # Teardown database tables and dispose engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_get_complaints_seeded(client):
    response = client.get("/api/complaints")
    assert response.status_code == 200
    data = response.json()
    # On startup, the database is auto-seeded with 4 complaints
    assert len(data) == 4
    # Check that they have required fields
    for complaint in data:
        assert "id" in complaint
        assert "customer_name" in complaint
        assert "status" in complaint
        assert "severity" in complaint


def test_get_single_complaint_and_logs(client):
    # Fetch all to get an ID
    response = client.get("/api/complaints")
    data = response.json()
    first_id = data[0]["id"]
    
    # Fetch single complaint
    response = client.get(f"/api/complaints/{first_id}")
    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == first_id
    assert "activity_logs" in detail
    assert len(detail["activity_logs"]) >= 1
    assert detail["activity_logs"][0]["action"] == "Created"


def test_create_complaint(client):
    payload = {
        "customer_name": "Marcus Aurelius",
        "account_number": "XXXXXX9999",
        "account_type": "Checking",
        "severity": "Medium",
        "description": "I did not receive my debit card statements for the last three months."
    }
    response = client.post("/api/complaints", json=payload)
    assert response.status_code == 201
    new_complaint = response.json()
    assert new_complaint["id"] is not None
    assert new_complaint["customer_name"] == "Marcus Aurelius"
    assert new_complaint["status"] == "New"
    
    # Verify that an activity log was seeded
    response = client.get(f"/api/complaints/{new_complaint['id']}")
    detail = response.json()
    assert len(detail["activity_logs"]) == 1
    assert detail["activity_logs"][0]["action"] == "Created"
    assert detail["activity_logs"][0]["performed_by"] == "Intake Agent"


def test_transitions_lifecycle(client):
    # Create a new complaint first
    payload = {
        "customer_name": "Lucius Vorenus",
        "account_number": "XXXXXX5555",
        "account_type": "Savings",
        "severity": "Low",
        "description": "Interest rate calculated incorrectly for July."
    }
    response = client.post("/api/complaints", json=payload)
    complaint_id = response.json()["id"]
    
    # Transition 1: New -> Assigned
    response = client.post(
        f"/api/complaints/{complaint_id}/transition",
        json={"new_status": "Assigned", "performed_by": "Intake Specialist", "comments": "Assigning to Senior Specialist Cooper"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Assigned"
    
    # Transition 2: Assigned -> In Progress
    response = client.post(
        f"/api/complaints/{complaint_id}/transition",
        json={"new_status": "In Progress", "performed_by": "Specialist Cooper", "comments": "Starting investigation of interest calculation."}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "In Progress"
    
    # Transition 3: In Progress -> Resolved
    response = client.post(
        f"/api/complaints/{complaint_id}/transition",
        json={"new_status": "Resolved", "performed_by": "Specialist Cooper", "comments": "Resolved. Credited account with the missing $4.12 interest."}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Resolved"
    
    # Verify complete logs timeline
    response = client.get(f"/api/complaints/{complaint_id}")
    detail = response.json()
    logs = detail["activity_logs"]
    assert len(logs) == 4 # Created, Assigned, In Progress, Resolved
    assert logs[0]["action"] == "Created"
    assert logs[1]["action"] == "Assigned Specialist"
    assert logs[2]["action"] == "Started Investigation"
    assert logs[3]["action"] == "Resolved Case"


def test_invalid_transitions(client):
    # Create a new complaint
    payload = {
        "customer_name": "Titus Pullo",
        "account_number": "XXXXXX1111",
        "account_type": "Credit Card",
        "severity": "High",
        "description": "Double charge issue."
    }
    response = client.post("/api/complaints", json=payload)
    complaint_id = response.json()["id"]
    
    # Attempt invalid direct transition: New -> Resolved (Must go New -> Assigned first)
    response = client.post(
        f"/api/complaints/{complaint_id}/transition",
        json={"new_status": "Resolved", "performed_by": "Specialist Cooper", "comments": "Direct resolve attempt"}
    )
    assert response.status_code == 400
    assert "Invalid transition" in response.json()["detail"]
    
    # Attempt fake/invalid status transition
    response = client.post(
        f"/api/complaints/{complaint_id}/transition",
        json={"new_status": "FakeStatus", "performed_by": "Specialist Cooper"}
    )
    assert response.status_code == 400
