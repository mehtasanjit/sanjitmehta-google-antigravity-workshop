from conftest import instructor_token, student_token, auth_header


def test_session_lifecycle_and_transitions(client):
    inst_token = instructor_token("inst-1")
    headers_inst = auth_header(inst_token)

    course_resp = client.post("/courses", json={"name": "Web Dev"}, headers=headers_inst)
    assert course_resp.status_code == 201
    course_id = course_resp.json()["id"]

    session_payload = {"title": "HTML Basics"}
    sess_resp = client.post(f"/courses/{course_id}/sessions", json=session_payload, headers=headers_inst)
    assert sess_resp.status_code == 201
    session = sess_resp.json()
    assert session["title"] == "HTML Basics"
    assert session["status"] == "scheduled"
    assert "join_code" in session
    session_id = session["id"]

    # illegal: scheduled -> ended
    trans_resp1 = client.post(f"/sessions/{session_id}/transition", json={"target": "ended"}, headers=headers_inst)
    assert trans_resp1.status_code == 409
    assert "error" in trans_resp1.json()

    # legal: scheduled -> active
    trans_resp2 = client.post(f"/sessions/{session_id}/transition", json={"target": "active"}, headers=headers_inst)
    assert trans_resp2.status_code == 200
    assert trans_resp2.json()["status"] == "active"

    # legal: active -> ended
    trans_resp3 = client.post(f"/sessions/{session_id}/transition", json={"target": "ended"}, headers=headers_inst)
    assert trans_resp3.status_code == 200
    assert trans_resp3.json()["status"] == "ended"

    # illegal: ended -> active
    trans_resp4 = client.post(f"/sessions/{session_id}/transition", json={"target": "active"}, headers=headers_inst)
    assert trans_resp4.status_code == 409
    assert "error" in trans_resp4.json()


def test_join_flow_and_enforcement(client):
    inst_token = instructor_token("inst-1")
    headers_inst = auth_header(inst_token)
    stu_token = student_token("stu-1")
    headers_stu = auth_header(stu_token)
    stu2_token = student_token("stu-2")
    headers_stu2 = auth_header(stu2_token)

    course_resp = client.post("/courses", json={"name": "Database Systems"}, headers=headers_inst)
    course_id = course_resp.json()["id"]

    sess_resp = client.post(f"/courses/{course_id}/sessions", json={"title": "SQL Intro"}, headers=headers_inst)
    session = sess_resp.json()
    session_id = session["id"]
    join_code = session["join_code"]

    enroll_resp = client.post(f"/courses/{course_id}/enrollments", json={"student_subject": "stu-1"}, headers=headers_inst)
    assert enroll_resp.status_code == 201

    # join before active -> 409
    join_resp1 = client.post("/sessions/join", json={"join_code": join_code}, headers=headers_stu)
    assert join_resp1.status_code == 409
    assert "error" in join_resp1.json()

    act_resp = client.post(f"/sessions/{session_id}/transition", json={"target": "active"}, headers=headers_inst)
    assert act_resp.status_code == 200

    # non-enrolled student -> 403
    join_resp2 = client.post("/sessions/join", json={"join_code": join_code}, headers=headers_stu2)
    assert join_resp2.status_code == 403
    assert "error" in join_resp2.json()

    # enrolled student joins -> 200
    join_resp3 = client.post("/sessions/join", json={"join_code": join_code}, headers=headers_stu)
    assert join_resp3.status_code == 200
    assert join_resp3.json()["session_id"] == session_id

    # a non-joined student cannot respond to a poll in this session -> 403
    poll_resp = client.post(
        f"/sessions/{session_id}/polls",
        json={"prompt": "Q", "poll_type": "single", "is_quiz": False,
              "options": [{"text": "a"}, {"text": "b"}]},
        headers=headers_inst,
    )
    assert poll_resp.status_code == 201
    poll_id = poll_resp.json()["id"]
    option_id = poll_resp.json()["options"][0]["id"]
    open_resp = client.post(f"/polls/{poll_id}/open", headers=headers_inst)
    assert open_resp.status_code == 200
    resp = client.post(f"/polls/{poll_id}/responses", json={"option_ids": [option_id]}, headers=headers_stu2)
    assert resp.status_code == 403
    assert "error" in resp.json()


def test_owner_sees_join_code_student_does_not(client, seed_active_session):
    ctx = seed_active_session
    # owner read includes join_code
    owner_view = client.get(f"/sessions/{ctx['session_id']}", headers=auth_header(ctx["instructor_token"]))
    assert owner_view.status_code == 200
    assert owner_view.json().get("join_code") is not None
    # student read omits join_code
    student_view = client.get(f"/sessions/{ctx['session_id']}", headers=auth_header(ctx["student_token"]))
    assert student_view.status_code == 200
    assert student_view.json().get("join_code") is None
