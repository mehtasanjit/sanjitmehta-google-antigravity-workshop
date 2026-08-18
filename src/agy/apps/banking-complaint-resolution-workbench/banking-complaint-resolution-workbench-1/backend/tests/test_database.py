import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import init_db, SessionLocal, get_db
from app.models import User, Complaint

def test_database_init_exists():
    """Verify database helpers can be imported."""
    assert init_db is not None, "init_db is not defined"
    assert SessionLocal is not None, "SessionLocal is not defined"

def test_database_seeding(tmp_path):
    """Verify that init_db correctly creates schema and seeds mock data."""
    db_file = tmp_path / "test_complaints.db"
    db_url = f"sqlite:///{db_file}"
    
    # Run database initialization & seeding
    engine = init_db(db_url)
    
    # Check that tables and mock data were created
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check seeded users
    users = session.query(User).all()
    assert len(users) >= 4, "Should seed at least 4 users (CSRs, Handlers, Supervisors)"
    
    usernames = [u.username for u in users]
    assert "jane_doe" in usernames
    assert "john_smith" in usernames
    assert "alice_johnson" in usernames
    assert "robert_vance" in usernames
    
    # Check seeded complaints
    complaints = session.query(Complaint).all()
    assert len(complaints) > 0, "Should seed mock complaints"
    for comp in complaints:
        assert comp.id.startswith("CRW-"), "Complaint ID should match CRW format"
        assert comp.sla_deadline is not None, "SLA deadline should be pre-calculated"
