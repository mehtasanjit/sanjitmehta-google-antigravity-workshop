import os

os.environ.setdefault('JWT_SECRET', 'test-secret-0123456789abcdef0123456789')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('LOG_JSON', 'false')
os.environ.setdefault('APP_ENV', 'test')

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient


@pytest.fixture
def engine():
    engine_instance = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool
    )

    @event.listens_for(engine_instance, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    from app.db import Base
    import app.models  # noqa: F401
    Base.metadata.create_all(engine_instance)
    yield engine_instance
    Base.metadata.drop_all(engine_instance)


@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(engine):
    from app.main import create_app
    from app.db import get_db
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        s = TestingSessionLocal()
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


from app.config import get_settings
from app.security import encode_token


def instructor_token(subject='inst-1'):
    return encode_token(subject, 'instructor', get_settings())


def student_token(subject='stu-1'):
    return encode_token(subject, 'student', get_settings())


def auth_header(token):
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def make_instructor_token():
    return instructor_token


@pytest.fixture
def make_student_token():
    return student_token


@pytest.fixture
def make_auth_header():
    return auth_header


@pytest.fixture
def seed_active_session(client):
    """Create a course, enroll a student, create + activate a session, and join
    the student. Returns ids, tokens and the join code for downstream tests."""
    inst_token = instructor_token('inst-1')
    stu_token = student_token('stu-1')

    # 1. instructor creates a course
    course_res = client.post(
        "/courses",
        json={"name": "Test Course", "description": "Test Description"},
        headers=auth_header(inst_token),
    )
    assert course_res.status_code == 201, course_res.text
    course_id = course_res.json()["id"]

    # 2. instructor enrolls the student
    enroll_res = client.post(
        f"/courses/{course_id}/enrollments",
        json={"student_subject": "stu-1"},
        headers=auth_header(inst_token),
    )
    assert enroll_res.status_code == 201, enroll_res.text

    # 3. instructor creates a session
    session_res = client.post(
        f"/courses/{course_id}/sessions",
        json={"title": "Test Session"},
        headers=auth_header(inst_token),
    )
    assert session_res.status_code == 201, session_res.text
    session_data = session_res.json()
    session_id = session_data["id"]
    join_code = session_data["join_code"]

    # 4. instructor activates the session
    activate_res = client.post(
        f"/sessions/{session_id}/transition",
        json={"target": "active"},
        headers=auth_header(inst_token),
    )
    assert activate_res.status_code == 200, activate_res.text

    # 5. student joins the active session
    join_res = client.post(
        "/sessions/join",
        json={"join_code": join_code},
        headers=auth_header(stu_token),
    )
    assert join_res.status_code == 200, join_res.text

    return {
        "instructor_token": inst_token,
        "student_token": stu_token,
        "course_id": course_id,
        "session_id": session_id,
        "join_code": join_code,
        "instructor_subject": "inst-1",
        "student_subject": "stu-1",
    }
