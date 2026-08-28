import threading
import tempfile
import os
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.db import Base
import app.models  # noqa: F401
from app.models import User, Course, LectureSession, Enrollment, Participant, Poll, PollOption
from app.services.polls import submit_response
from app.deps.auth import Principal


@pytest.fixture(scope="module")
def setup_db():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    engine = create_engine(f'sqlite:///{path}', connect_args={'check_same_thread': False})

    @event.listens_for(engine, 'connect')
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    s = SessionLocal()
    try:
        owner = User(subject='t1', role='instructor')
        s.add(owner)
        s.flush()

        course = Course(owner_subject='t1', name='C')
        s.add(course)
        s.flush()

        sess = LectureSession(course_id=course.id, title='S', status='active', join_code='JCX')
        s.add(sess)
        s.flush()

        poll = Poll(session_id=sess.id, prompt='Q', poll_type='single', is_quiz=False, status='open')
        s.add(poll)
        s.flush()

        opt = PollOption(poll_id=poll.id, text='A', is_correct=False, position=0)
        s.add(opt)
        s.flush()

        for i in range(20):
            stu = User(subject=f'stu-{i}', role='student')
            s.add(stu)
            s.flush()

            enr = Enrollment(course_id=course.id, student_subject=f'stu-{i}')
            s.add(enr)

            part = Participant(session_id=sess.id, student_subject=f'stu-{i}')
            s.add(part)

        s.commit()
        poll_id = poll.id
        option_id = opt.id
    finally:
        s.close()

    yield {
        'SessionLocal': SessionLocal,
        'poll_id': poll_id,
        'option_id': option_id,
        'path': path
    }

    engine.dispose()
    try:
        os.unlink(path)
    except OSError:
        pass


def _load(s, poll_id):
    from app.models import Poll
    return s.query(Poll).get(poll_id)


def test_single_student_double_submit_one_wins(setup_db):
    SessionLocal = setup_db['SessionLocal']
    poll_id = setup_db['poll_id']
    option_id = setup_db['option_id']
    results = []
    lock = threading.Lock()

    def worker():
        s = SessionLocal()
        try:
            poll = _load(s, poll_id)
            submit_response(s, Principal(subject='stu-0', role='student'), poll, [option_id])
            s.commit()
            with lock:
                results.append('ok')
        except Exception as e:
            s.rollback()
            with lock:
                results.append(type(e).__name__)
        finally:
            s.close()

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results.count('ok') == 1

    s = SessionLocal()
    from app.models import PollResponse
    cnt = s.query(PollResponse).filter(PollResponse.poll_id == poll_id, PollResponse.student_subject == 'stu-0').count()
    s.close()
    assert cnt == 1


def test_distinct_students_all_counted(setup_db):
    SessionLocal = setup_db['SessionLocal']
    poll_id = setup_db['poll_id']
    option_id = setup_db['option_id']
    errors = []
    lock = threading.Lock()

    def worker(i):
        s = SessionLocal()
        try:
            poll = _load(s, poll_id)
            submit_response(s, Principal(subject=f'stu-{i}', role='student'), poll, [option_id])
            s.commit()
        except Exception as e:
            s.rollback()
            with lock:
                errors.append(str(e))
        finally:
            s.close()

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    s = SessionLocal()
    from app.models import PollResponse
    total = s.query(PollResponse).filter(PollResponse.poll_id == poll_id).count()
    s.close()
    assert total == 20, errors
