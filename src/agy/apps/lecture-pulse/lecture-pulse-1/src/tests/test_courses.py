from conftest import instructor_token, auth_header


def test_course_lifecycle(client):
    inst1_token = instructor_token("inst-1")
    inst2_token = instructor_token("inst-2")
    headers1 = auth_header(inst1_token)
    headers2 = auth_header(inst2_token)

    course_payload = {"name": "Algorithms 101", "description": "Basic algorithms"}
    resp = client.post("/courses", json=course_payload, headers=headers1)
    assert resp.status_code == 201
    course = resp.json()
    assert course["name"] == "Algorithms 101"
    assert course["description"] == "Basic algorithms"
    assert course["owner_subject"] == "inst-1"
    course_id = course["id"]

    list_resp = client.get("/courses", headers=headers1)
    assert list_resp.status_code == 200
    courses = list_resp.json()["items"]
    assert any(c["id"] == course_id for c in courses)

    get_resp = client.get(f"/courses/{course_id}", headers=headers1)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == course_id

    other_resp = client.get(f"/courses/{course_id}", headers=headers2)
    assert other_resp.status_code in (403, 404)

    enroll_payload = {"student_subject": "stu-1"}
    enroll_resp = client.post(f"/courses/{course_id}/enrollments", json=enroll_payload, headers=headers1)
    assert enroll_resp.status_code == 201

    dup_resp = client.post(f"/courses/{course_id}/enrollments", json=enroll_payload, headers=headers1)
    assert dup_resp.status_code == 409
    assert "error" in dup_resp.json()
    assert "code" in dup_resp.json()["error"]

    list_enroll_resp = client.get(f"/courses/{course_id}/enrollments", headers=headers1)
    assert list_enroll_resp.status_code == 200
    assert isinstance(list_enroll_resp.json()["items"], list)

    del_resp = client.delete(f"/courses/{course_id}/enrollments/stu-1", headers=headers1)
    assert del_resp.status_code == 204
