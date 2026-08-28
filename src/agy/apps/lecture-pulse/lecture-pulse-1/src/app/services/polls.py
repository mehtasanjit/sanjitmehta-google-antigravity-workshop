from sqlalchemy.exc import IntegrityError
from app.errors import (
    ConflictError,
    NotFoundError,
    ValidationAppError,
    NOT_FOUND,
    POLL_CLOSED,
    ILLEGAL_TRANSITION,
    SESSION_NOT_ACTIVE,
    DUPLICATE_RESPONSE,
    VALIDATION_ERROR,
)
from app.models import Poll, PollOption, PollResponse, PollResponseOption, LectureSession
from app.services.audit import write_audit


def get_poll(db, poll_id) -> Poll:
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise NotFoundError(NOT_FOUND, 'Poll not found')
    return poll


def create_poll(db, principal, session: LectureSession, data) -> Poll:
    if session.status == 'ended':
        raise ConflictError(SESSION_NOT_ACTIVE, 'Session ended')

    if not data.options or len(data.options) < 2:
        raise ValidationAppError(VALIDATION_ERROR, 'At least two options required')

    correct_count = sum(1 for opt in data.options if opt.is_correct)
    if data.is_quiz:
        if correct_count != 1:
            raise ValidationAppError(VALIDATION_ERROR, 'Quiz needs exactly one correct option')
    else:
        if correct_count != 0:
            raise ValidationAppError(VALIDATION_ERROR, 'Poll options cannot be marked correct')

    poll = Poll(
        session_id=session.id,
        prompt=data.prompt,
        poll_type=data.poll_type,
        is_quiz=data.is_quiz,
        status='closed'
    )
    db.add(poll)
    db.flush()

    for idx, opt in enumerate(data.options):
        db.add(PollOption(
            poll_id=poll.id,
            text=opt.text,
            is_correct=bool(opt.is_correct),
            position=idx
        ))
    db.flush()

    write_audit(db, principal.subject, principal.role, 'poll.create', 'poll', poll.id)
    return poll


def _load_session_for_poll(db, poll) -> LectureSession:
    return db.query(LectureSession).filter(LectureSession.id == poll.session_id).first()


def open_poll(db, principal, poll: Poll) -> Poll:
    session = _load_session_for_poll(db, poll)
    if not session or session.status != 'active':
        raise ConflictError(SESSION_NOT_ACTIVE, 'Session not active')
    if poll.status != 'closed':
        raise ConflictError(ILLEGAL_TRANSITION, 'Poll already open')

    poll.status = 'open'
    db.flush()
    write_audit(db, principal.subject, principal.role, 'poll.open', 'poll', poll.id)
    return poll


def close_poll(db, principal, poll: Poll) -> Poll:
    if poll.status != 'open':
        raise ConflictError(ILLEGAL_TRANSITION, 'Poll not open')

    poll.status = 'closed'
    db.flush()
    write_audit(db, principal.subject, principal.role, 'poll.close', 'poll', poll.id)
    return poll


def submit_response(db, principal, poll: Poll, option_ids: list[int]) -> PollResponse:
    if poll.status != 'open':
        raise ConflictError(POLL_CLOSED, 'Poll is closed')

    valid_ids = {o.id for o in db.query(PollOption).filter(PollOption.poll_id == poll.id).all()}
    if not option_ids or any(oid not in valid_ids for oid in option_ids):
        raise ValidationAppError(VALIDATION_ERROR, 'Invalid option ids')

    if poll.poll_type == 'single' or poll.is_quiz:
        if len(set(option_ids)) != 1:
            raise ValidationAppError(VALIDATION_ERROR, 'Exactly one option required')
    else:
        if len(set(option_ids)) < 1:
            raise ValidationAppError(VALIDATION_ERROR, 'At least one option required')

    resp = PollResponse(poll_id=poll.id, student_subject=principal.subject)
    db.add(resp)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ConflictError(DUPLICATE_RESPONSE, 'Already responded')

    for oid in set(option_ids):
        db.add(PollResponseOption(response_id=resp.id, option_id=oid))
    db.flush()

    write_audit(db, principal.subject, principal.role, 'poll.respond', 'poll', poll.id)
    return resp
