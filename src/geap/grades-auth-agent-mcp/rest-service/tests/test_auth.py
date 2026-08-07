"""Authentication tests — token presence, validity, and identity echo."""
from conftest import make_token


def test_health_is_public(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_me_requires_token(client):
    assert client.get("/me").status_code == 401


def test_me_echoes_identity(client, auth):
    r = client.get("/me", headers=auth("alice", "student", ["grades.read.self"]))
    assert r.status_code == 200
    body = r.json()
    assert body["sub"] == "alice"
    assert body["role"] == "student"


def test_rejects_bad_signature(client):
    tok = make_token("alice", "student", ["grades.read.self"], secret="wrong-secret")
    r = client.get("/me", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 401


def test_rejects_wrong_audience(client):
    tok = make_token("alice", "student", ["grades.read.self"], aud="some-other-api")
    r = client.get("/me", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 401


def test_rejects_expired(client):
    tok = make_token("alice", "student", ["grades.read.self"], ttl=-5)
    r = client.get("/me", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 401


def test_rejects_unknown_role(client):
    tok = make_token("x", "superuser", ["grades.read.self"])
    r = client.get("/me", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 401
