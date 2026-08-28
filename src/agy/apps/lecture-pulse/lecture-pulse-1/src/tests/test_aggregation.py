from app.models import User, Course, LectureSession, Poll, PollOption, PollResponse, PollResponseOption, Pulse, PulseResponse
from app.services.aggregation import poll_results, pulse_sentiment


def test_quiz_correct_answer_rate(db_session):
    owner = User(subject='t1', role='instructor')
    db_session.add(owner)
    db_session.flush()

    course = Course(owner_subject='t1', name='C')
    db_session.add(course)
    db_session.flush()

    sess = LectureSession(course_id=course.id, title='S', status='active', join_code='JC1')
    db_session.add(sess)
    db_session.flush()

    poll = Poll(session_id=sess.id, prompt='Q', poll_type='single', is_quiz=True, status='open')
    db_session.add(poll)
    db_session.flush()

    optA = PollOption(poll_id=poll.id, text='A', is_correct=True, position=0)
    optB = PollOption(poll_id=poll.id, text='B', is_correct=False, position=1)
    optC = PollOption(poll_id=poll.id, text='C', is_correct=False, position=2)
    db_session.add(optA)
    db_session.add(optB)
    db_session.add(optC)
    db_session.flush()

    for sid in ['s1', 's2', 's3']:
        student = User(subject=sid, role='student')
        db_session.add(student)
        db_session.flush()

    r1 = PollResponse(poll_id=poll.id, student_subject='s1')
    r2 = PollResponse(poll_id=poll.id, student_subject='s2')
    r3 = PollResponse(poll_id=poll.id, student_subject='s3')
    db_session.add(r1)
    db_session.add(r2)
    db_session.add(r3)
    db_session.flush()

    pro1 = PollResponseOption(response_id=r1.id, option_id=optA.id)
    pro2 = PollResponseOption(response_id=r2.id, option_id=optA.id)
    pro3 = PollResponseOption(response_id=r3.id, option_id=optB.id)
    db_session.add(pro1)
    db_session.add(pro2)
    db_session.add(pro3)

    db_session.commit()

    res = poll_results(db_session, poll)
    assert res['total_respondents'] == 3
    assert round(res['correct_answer_rate'], 3) == round(2 / 3, 3)
    counts = {o['option_id']: o['count'] for o in res['options']}
    assert counts[optA.id] == 2
    assert counts[optB.id] == 1
    assert counts[optC.id] == 0


def test_pulse_sentiment(db_session):
    owner = User(subject='t2', role='instructor')
    db_session.add(owner)
    db_session.flush()

    course = Course(owner_subject='t2', name='C')
    db_session.add(course)
    db_session.flush()

    sess = LectureSession(course_id=course.id, title='S', status='active', join_code='JC2')
    db_session.add(sess)
    db_session.flush()

    pulse = Pulse(session_id=sess.id, status='active')
    db_session.add(pulse)
    db_session.flush()

    for sid, rating in [('a', 5), ('b', 3), ('c', 3), ('d', 1)]:
        student = User(subject=sid, role='student')
        db_session.add(student)
        db_session.flush()

        resp = PulseResponse(pulse_id=pulse.id, student_subject=sid, rating=rating)
        db_session.add(resp)

    db_session.commit()

    res = pulse_sentiment(db_session, pulse)
    assert res['total'] == 4
    assert res['distribution']['3'] == 2
    assert res['distribution']['5'] == 1
    assert res['distribution']['1'] == 1
    assert res['distribution']['2'] == 0
    assert round(res['average'], 3) == round((5 + 3 + 3 + 1) / 4, 3)
