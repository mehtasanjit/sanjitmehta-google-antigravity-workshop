import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Complaint, AuditLog

def test_models_exist():
    """Verify that models are defined and can be imported."""
    assert Base is not None, "SQLAlchemy Base model is missing."
    assert User is not None, "User model is missing."
    assert Complaint is not None, "Complaint model is missing."
    assert AuditLog is not None, "AuditLog model is missing."

def test_database_schema_creation():
    """Verify that schema can be created in an in-memory SQLite database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Test model instantiation & persistence
    user = User(username="robert_vance", name="Robert Vance", role="Supervisor")
    session.add(user)
    session.commit()
    
    # Verify User was persisted
    db_user = session.query(User).filter_by(username="robert_vance").first()
    assert db_user is not None
    assert db_user.name == "Robert Vance"
    assert db_user.role == "Supervisor"
