from conftest import student_token, auth_header


def test_full_poll_lifecycle(client, seed_active_session):
    ctx = seed_active_session

    # Add stu-2 (enroll + join)
    enroll_resp = client.post(
        f"/courses/{ctx['course_id']}/enrollments",
        json={'student_subject': 'stu-2'},
        headers=auth_header(ctx['instructor_token'])
    )
    assert enroll_resp.status_code in (200, 201)

    join_resp = client.post(
        '/sessions/join',
        json={'join_code': ctx['join_code']},
        headers=auth_header(student_token('stu-2'))
    )
    assert join_resp.status_code in (200, 201)

    poll_data = {
        "prompt": "Which color do you prefer?",
        "poll_type": "single",
        "is_quiz": False,
        "options": [
            {"text": "Red", "is_correct": False},
            {"text": "Blue", "is_correct": False}
        ]
    }
    create_resp = client.post(
        f"/sessions/{ctx['session_id']}/polls",
        json=poll_data,
        headers=auth_header(ctx['instructor_token'])
    )
    assert create_resp.status_code == 201
    poll = create_resp.json()
    poll_id = poll['id']
    options = poll['options']
    assert len(options) == 2

    open_resp = client.post(
        f"/polls/{poll_id}/open",
        headers=auth_header(ctx['instructor_token'])
    )
    assert open_resp.status_code == 200

    resp1 = client.post(
        f"/polls/{poll_id}/responses",
        json={"option_ids": [options[0]['id']]},
        headers=auth_header(ctx['student_token'])
    )
    assert resp1.status_code == 201

    resp2 = client.post(
        f"/polls/{poll_id}/responses",
        json={"option_ids": [options[0]['id']]},
        headers=auth_header(student_token('stu-2'))
    )
    assert resp2.status_code == 201

    results_resp = client.get(
        f"/polls/{poll_id}/results",
        headers=auth_header(ctx['instructor_token'])
    )
    assert results_resp.status_code == 200
    results = results_resp.json()
    assert results['total_respondents'] == 2

    opt_counts = {opt['option_id']: opt['count'] for opt in results['options']}
    assert opt_counts[options[0]['id']] == 2
    assert opt_counts[options[1]['id']] == 0

    close_resp = client.post(
        f"/polls/{poll_id}/close",
        headers=auth_header(ctx['instructor_token'])
    )
    assert close_resp.status_code == 200

    enroll_resp3 = client.post(
        f"/courses/{ctx['course_id']}/enrollments",
        json={'student_subject': 'stu-3'},
        headers=auth_header(ctx['instructor_token'])
    )
    assert enroll_resp3.status_code in (200, 201)

    join_resp3 = client.post(
        '/sessions/join',
        json={'join_code': ctx['join_code']},
        headers=auth_header(student_token('stu-3'))
    )
    assert join_resp3.status_code in (200, 201)

    resp3 = client.post(
        f"/polls/{poll_id}/responses",
        json={"option_ids": [options[0]['id']]},
        headers=auth_header(student_token('stu-3'))
    )
    assert resp3.status_code == 409
    assert resp3.json()['error']['code'] == 'poll_closed'


def test_duplicate_response_rejected(client, seed_active_session):
    ctx = seed_active_session

    poll_data = {
        "prompt": "Yes or No?",
        "poll_type": "single",
        "is_quiz": False,
        "options": [
            {"text": "Yes", "is_correct": False},
            {"text": "No", "is_correct": False}
        ]
    }
    create_resp = client.post(
        f"/sessions/{ctx['session_id']}/polls",
        json=poll_data,
        headers=auth_header(ctx['instructor_token'])
    )
    assert create_resp.status_code == 201
    poll = create_resp.json()
    poll_id = poll['id']
    options = poll['options']

    open_resp = client.post(
        f"/polls/{poll_id}/open",
        headers=auth_header(ctx['instructor_token'])
    )
    assert open_resp.status_code == 200

    resp1 = client.post(
        f"/polls/{poll_id}/responses",
        json={"option_ids": [options[0]['id']]},
        headers=auth_header(ctx['student_token'])
    )
    assert resp1.status_code == 201

    resp2 = client.post(
        f"/polls/{poll_id}/responses",
        json={"option_ids": [options[0]['id']]},
        headers=auth_header(ctx['student_token'])
    )
    assert resp2.status_code == 409
    assert resp2.json()['error']['code'] == 'duplicate_response'


def test_is_correct_never_exposed(client, seed_active_session):
    ctx = seed_active_session

    poll_data = {
        "prompt": "Quiz Question",
        "poll_type": "single",
        "is_quiz": True,
        "options": [
            {"text": "a", "is_correct": True},
            {"text": "b", "is_correct": False}
        ]
    }
    create_resp = client.post(
        f"/sessions/{ctx['session_id']}/polls",
        json=poll_data,
        headers=auth_header(ctx['instructor_token'])
    )
    assert create_resp.status_code == 201
    poll = create_resp.json()

    for opt in poll['options']:
        assert 'is_correct' not in opt
