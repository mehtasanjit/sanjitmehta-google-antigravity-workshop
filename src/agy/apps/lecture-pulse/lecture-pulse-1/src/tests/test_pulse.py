from conftest import student_token, auth_header


def test_pulse_rating_and_sentiment(client, seed_active_session):
    inst_token = seed_active_session["instructor_token"]
    stu1_token = seed_active_session["student_token"]
    course_id = seed_active_session["course_id"]
    session_id = seed_active_session["session_id"]
    join_code = seed_active_session["join_code"]

    resp = client.post(f"/sessions/{session_id}/pulses", headers=auth_header(inst_token))
    assert resp.status_code == 201
    pulse_data = resp.json()
    assert pulse_data["session_id"] == session_id
    assert pulse_data["status"] == "active"
    pulse_id = pulse_data["id"]

    resp = client.post(f"/pulses/{pulse_id}/responses", json={"rating": 4}, headers=auth_header(stu1_token))
    assert resp.status_code == 201

    resp = client.post(
        f"/courses/{course_id}/enrollments",
        json={"student_subject": "stu-2"},
        headers=auth_header(inst_token)
    )
    assert resp.status_code in (200, 201)

    stu2_token = student_token("stu-2")
    resp = client.post("/sessions/join", json={"join_code": join_code}, headers=auth_header(stu2_token))
    assert resp.status_code in (200, 201)

    resp = client.post(f"/pulses/{pulse_id}/responses", json={"rating": 2}, headers=auth_header(stu2_token))
    assert resp.status_code == 201

    resp = client.get(f"/pulses/{pulse_id}/sentiment", headers=auth_header(inst_token))
    assert resp.status_code == 200
    sentiment = resp.json()
    assert sentiment["pulse_id"] == pulse_id
    assert sentiment["total"] == 2
    assert float(sentiment["average"]) == 3.0
    dist = {str(k): v for k, v in sentiment["distribution"].items()}
    assert dist.get("4") == 1
    assert dist.get("2") == 1


def test_duplicate_rating(client, seed_active_session):
    inst_token = seed_active_session["instructor_token"]
    stu1_token = seed_active_session["student_token"]
    session_id = seed_active_session["session_id"]

    resp = client.post(f"/sessions/{session_id}/pulses", headers=auth_header(inst_token))
    assert resp.status_code == 201
    pulse_id = resp.json()["id"]

    resp = client.post(f"/pulses/{pulse_id}/responses", json={"rating": 4}, headers=auth_header(stu1_token))
    assert resp.status_code == 201

    resp = client.post(f"/pulses/{pulse_id}/responses", json={"rating": 5}, headers=auth_header(stu1_token))
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "duplicate_rating"


def test_rating_out_of_range(client, seed_active_session):
    inst_token = seed_active_session["instructor_token"]
    stu1_token = seed_active_session["student_token"]
    session_id = seed_active_session["session_id"]

    resp = client.post(f"/sessions/{session_id}/pulses", headers=auth_header(inst_token))
    assert resp.status_code == 201
    pulse_id = resp.json()["id"]

    resp = client.post(f"/pulses/{pulse_id}/responses", json={"rating": 6}, headers=auth_header(stu1_token))
    assert resp.status_code == 422


def test_trigger_closes_prior(client, seed_active_session):
    inst_token = seed_active_session["instructor_token"]
    stu1_token = seed_active_session["student_token"]
    session_id = seed_active_session["session_id"]

    resp = client.post(f"/sessions/{session_id}/pulses", headers=auth_header(inst_token))
    assert resp.status_code == 201
    p1_id = resp.json()["id"]

    resp = client.post(f"/sessions/{session_id}/pulses", headers=auth_header(inst_token))
    assert resp.status_code == 201

    resp = client.post(f"/pulses/{p1_id}/responses", json={"rating": 4}, headers=auth_header(stu1_token))
    assert resp.status_code == 409
