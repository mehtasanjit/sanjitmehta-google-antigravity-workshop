from conftest import student_token, auth_header


def add_stu_2(client, seed_active_session):
    course_id = seed_active_session["course_id"]
    join_code = seed_active_session["join_code"]
    inst_token = seed_active_session["instructor_token"]

    resp = client.post(
        f"/courses/{course_id}/enrollments",
        json={"student_subject": "stu-2"},
        headers=auth_header(inst_token)
    )
    assert resp.status_code in (200, 201)

    resp = client.post(
        "/sessions/join",
        json={"join_code": join_code},
        headers=auth_header(student_token("stu-2"))
    )
    assert resp.status_code in (200, 201)


def test_post_and_upvote(client, seed_active_session):
    session_id = seed_active_session["session_id"]
    stu1_token = seed_active_session["student_token"]

    resp = client.post(
        f"/sessions/{session_id}/questions",
        json={"text": "What is Python?"},
        headers=auth_header(stu1_token)
    )
    assert resp.status_code == 201
    qid = resp.json()["id"]

    add_stu_2(client, seed_active_session)

    resp = client.post(
        f"/questions/{qid}/upvotes",
        headers=auth_header(student_token("stu-2"))
    )
    assert resp.status_code == 201
    assert resp.json()["upvotes"] == 1

    resp = client.post(
        f"/questions/{qid}/upvotes",
        headers=auth_header(student_token("stu-2"))
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "duplicate_upvote"


def test_ranking_desc(client, seed_active_session):
    session_id = seed_active_session["session_id"]
    stu1_token = seed_active_session["student_token"]

    add_stu_2(client, seed_active_session)

    resp = client.post(
        f"/sessions/{session_id}/questions",
        json={"text": "Question 1"},
        headers=auth_header(stu1_token)
    )
    assert resp.status_code == 201
    q1_id = resp.json()["id"]

    resp = client.post(
        f"/sessions/{session_id}/questions",
        json={"text": "Question 2"},
        headers=auth_header(stu1_token)
    )
    assert resp.status_code == 201
    q2_id = resp.json()["id"]

    resp = client.post(
        f"/questions/{q2_id}/upvotes",
        headers=auth_header(student_token("stu-2"))
    )
    assert resp.status_code == 201

    inst_token = seed_active_session["instructor_token"]
    resp = client.get(
        f"/sessions/{session_id}/questions",
        headers=auth_header(inst_token)
    )
    assert resp.status_code == 200
    questions = resp.json()["items"]
    assert len(questions) >= 2

    q_ids = [q["id"] for q in questions]
    assert q2_id in q_ids
    assert q1_id in q_ids
    assert q_ids.index(q2_id) < q_ids.index(q1_id)


def test_moderate_owner_only(client, seed_active_session):
    session_id = seed_active_session["session_id"]
    stu1_token = seed_active_session["student_token"]

    resp = client.post(
        f"/sessions/{session_id}/questions",
        json={"text": "Question to moderate"},
        headers=auth_header(stu1_token)
    )
    assert resp.status_code == 201
    qid = resp.json()["id"]

    inst_token = seed_active_session["instructor_token"]
    resp = client.post(
        f"/questions/{qid}/moderate",
        json={"status": "answered"},
        headers=auth_header(inst_token)
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "answered"

    resp = client.post(
        f"/questions/{qid}/moderate",
        json={"status": "dismissed"},
        headers=auth_header(stu1_token)
    )
    assert resp.status_code == 403
