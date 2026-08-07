"""Shared test fixtures. Sets env + seeds a temp dataset before importing the app."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
import pytest

SECRET = "test-secret"
ISSUER = "grades-auth-local"
AUDIENCE = "grades-rest"

SEED = {
    "students": [
        {"id": "alice", "name": "Alice Nguyen", "email": "alice@campus.edu", "year": 2},
        {"id": "bob", "name": "Bob Martinez", "email": "bob@campus.edu", "year": 3},
    ],
    "professors": [
        {"id": "dr_reed", "name": "Dr. Evelyn Reed", "email": "reed@campus.edu"},
        {"id": "dr_kapoor", "name": "Dr. Anil Kapoor", "email": "kapoor@campus.edu"},
    ],
    "courses": [
        {"code": "CHEM-101", "title": "Intro to Chemistry", "professor_id": "dr_reed"},
        {"code": "BIO-110", "title": "Intro to Biology", "professor_id": "dr_kapoor"},
    ],
    "enrollments": [
        {"student_id": "alice", "course_code": "CHEM-101"},
        {"student_id": "bob", "course_code": "CHEM-101"},
    ],
    "grades": [
        {"student_id": "alice", "course_code": "CHEM-101", "score": 92,
         "letter": "A-", "updated_at": "2026-01-01T00:00:00+00:00", "updated_by": "seed"},
        {"student_id": "bob", "course_code": "CHEM-101", "score": 78,
         "letter": "C+", "updated_at": "2026-01-01T00:00:00+00:00", "updated_by": "seed"},
    ],
}


@pytest.fixture(scope="session", autouse=True)
def _env(tmp_path_factory):
    import os
    seed_path = tmp_path_factory.mktemp("data") / "seed.json"
    seed_path.write_text(json.dumps(SEED))
    os.environ.update(
        AUTH_MODE="local",
        JWT_SECRET=SECRET,
        JWT_ISSUER=ISSUER,
        JWT_AUDIENCE=AUDIENCE,
        DATA_PATH=str(seed_path),
    )
    yield


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as c:
        yield c


def make_token(sub, role, scopes, *, secret=SECRET, aud=AUDIENCE, iss=ISSUER, ttl=60):
    now = datetime.now(timezone.utc)
    claims = {
        "iss": iss, "aud": aud, "sub": sub, "role": role,
        "scope": " ".join(scopes), "iat": now,
        "exp": now + timedelta(minutes=ttl),
    }
    return jwt.encode(claims, secret, algorithm="HS256")


@pytest.fixture()
def auth():
    def _headers(sub, role, scopes):
        return {"Authorization": f"Bearer {make_token(sub, role, scopes)}"}
    return _headers
