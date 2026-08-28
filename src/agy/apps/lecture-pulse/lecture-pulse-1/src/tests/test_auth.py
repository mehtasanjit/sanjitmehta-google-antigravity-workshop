from conftest import instructor_token, student_token, auth_header


def test_token_issuance_and_me(client):
    payload = {
        "subject": "inst-1",
        "role": "instructor",
        "display_name": "Dr. Smith",
        "email": "smith@example.com"
    }
    response = client.post("/auth/token", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["subject"] == "inst-1"
    assert data["role"] == "instructor"

    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["subject"] == "inst-1"
    assert me_data["role"] == "instructor"
    assert me_data["display_name"] == "Dr. Smith"


def test_auth_me_missing_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert "error" in response.json()


def test_auth_me_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token_123"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401
    assert "error" in response.json()


def test_student_cannot_create_course(client):
    token = student_token("stu-1")
    headers = auth_header(token)
    payload = {"name": "Intro to CS"}
    response = client.post("/courses", json=payload, headers=headers)
    assert response.status_code == 403
    assert "error" in response.json()


def test_unauthorized_cannot_create_course(client):
    payload = {"name": "Intro to CS"}
    response = client.post("/courses", json=payload)
    assert response.status_code == 401
    assert "error" in response.json()


def test_malformed_body_returns_422_envelope(client):
    token = instructor_token("inst-1")
    # missing required 'name'
    response = client.post("/courses", json={}, headers=auth_header(token))
    assert response.status_code == 422
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "validation_error"
    assert "details" in body["error"]
