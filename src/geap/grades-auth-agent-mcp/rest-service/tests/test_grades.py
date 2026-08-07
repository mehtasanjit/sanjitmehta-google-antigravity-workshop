"""Authorization matrix tests — the heart of the on-behalf-of guarantee."""

STUDENT_SCOPES = ["grades.read.self"]
PROF_SCOPES = ["grades.read.course", "grades.write.course"]
ADMIN_SCOPES = ["grades.read.self", "grades.read.course", "grades.write.course", "grades.admin"]


# --- student reading grades ------------------------------------------------
def test_student_reads_own_grades(client, auth):
    r = client.get("/students/alice/grades", headers=auth("alice", "student", STUDENT_SCOPES))
    assert r.status_code == 200
    assert {g["course_code"] for g in r.json()} == {"CHEM-101"}


def test_student_cannot_read_other_student(client, auth):
    r = client.get("/students/bob/grades", headers=auth("alice", "student", STUDENT_SCOPES))
    assert r.status_code == 403


def test_student_missing_scope_denied(client, auth):
    r = client.get("/students/alice/grades", headers=auth("alice", "student", []))
    assert r.status_code == 403


# --- professor reading course grades --------------------------------------
def test_professor_reads_own_course(client, auth):
    r = client.get("/courses/CHEM-101/grades", headers=auth("dr_reed", "professor", PROF_SCOPES))
    assert r.status_code == 200
    assert {g["student_id"] for g in r.json()} == {"alice", "bob"}


def test_professor_cannot_read_course_they_dont_teach(client, auth):
    r = client.get("/courses/CHEM-101/grades", headers=auth("dr_kapoor", "professor", PROF_SCOPES))
    assert r.status_code == 403


def test_professor_reads_student_only_for_taught_courses(client, auth):
    # dr_reed teaches CHEM-101 (alice enrolled) -> sees only that slice
    r = client.get("/students/alice/grades", headers=auth("dr_reed", "professor", PROF_SCOPES))
    assert r.status_code == 200
    assert {g["course_code"] for g in r.json()} == {"CHEM-101"}


def test_professor_denied_student_with_no_shared_course(client, auth):
    r = client.get("/students/alice/grades", headers=auth("dr_kapoor", "professor", PROF_SCOPES))
    assert r.status_code == 403


# --- writing grades --------------------------------------------------------
def test_student_cannot_write(client, auth):
    r = client.post(
        "/courses/CHEM-101/grades",
        headers=auth("alice", "student", STUDENT_SCOPES),
        json={"student_id": "alice", "score": 100},
    )
    assert r.status_code == 403


def test_professor_writes_own_course(client, auth):
    r = client.post(
        "/courses/CHEM-101/grades",
        headers=auth("dr_reed", "professor", PROF_SCOPES),
        json={"student_id": "bob", "score": 91},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["score"] == 91
    assert body["letter"] == "A-"
    assert body["updated_by"] == "dr_reed"  # audit records the real user


def test_professor_cannot_write_unowned_course(client, auth):
    r = client.post(
        "/courses/CHEM-101/grades",
        headers=auth("dr_kapoor", "professor", PROF_SCOPES),
        json={"student_id": "alice", "score": 50},
    )
    assert r.status_code == 403


def test_professor_cannot_write_unenrolled_student(client, auth):
    r = client.post(
        "/courses/CHEM-101/grades",
        headers=auth("dr_reed", "professor", PROF_SCOPES),
        json={"student_id": "carol", "score": 70},
    )
    # carol not in test seed for CHEM-101 -> not enrolled
    assert r.status_code in (403, 404)


# --- admin -----------------------------------------------------------------
def test_admin_reads_any_student(client, auth):
    r = client.get("/students/bob/grades", headers=auth("admin", "admin", ADMIN_SCOPES))
    assert r.status_code == 200


def test_admin_reads_any_course(client, auth):
    r = client.get("/courses/CHEM-101/grades", headers=auth("admin", "admin", ADMIN_SCOPES))
    assert r.status_code == 200


# --- course listing is identity-filtered ----------------------------------
def test_course_list_filtered_for_student(client, auth):
    r = client.get("/courses", headers=auth("alice", "student", STUDENT_SCOPES))
    assert r.status_code == 200
    assert {c["code"] for c in r.json()} == {"CHEM-101"}


def test_course_list_filtered_for_professor(client, auth):
    r = client.get("/courses", headers=auth("dr_reed", "professor", PROF_SCOPES))
    assert r.status_code == 200
    assert {c["code"] for c in r.json()} == {"CHEM-101"}


# --- 404s ------------------------------------------------------------------
def test_unknown_course_404(client, auth):
    r = client.get("/courses/NOPE-999/grades", headers=auth("admin", "admin", ADMIN_SCOPES))
    assert r.status_code == 404
