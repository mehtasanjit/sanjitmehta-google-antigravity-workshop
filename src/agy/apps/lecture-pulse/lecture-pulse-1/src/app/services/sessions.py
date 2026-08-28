import secrets
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from app.config import get_settings
from app.errors import (
    ConflictError,
    NotFoundError,
    ForbiddenError,
    NOT_FOUND,
    ILLEGAL_TRANSITION,
    SESSION_NOT_ACTIVE,
    NOT_ENROLLED,
)
from app.models import Course, LectureSession, Participant, Enrollment
from app.deps.auth import Principal
from app.services.audit import write_audit


def create_session(db, principal: Principal, course: Course, title) -> LectureSession:
    max_retries = 5
    for i in range(max_retries):
        join_code = secrets.token_urlsafe(16)[:get_settings().JOIN_CODE_LENGTH].upper()
        s = LectureSession(
            course_id=course.id,
            title=title,
            status='scheduled',
            join_code=join_code
        )
        db.add(s)
        try:
            db.flush()
            write_audit(db, principal.subject, principal.role, 'session.create', 'session', s.id)
            return s
        except IntegrityError:
            db.rollback()
            if i == max_retries - 1:
                raise ConflictError("duplicate_join_code", "Failed to generate a unique join code")
            continue


def list_sessions(db, course_id) -> list:
    return db.query(LectureSession).filter(LectureSession.course_id == course_id).order_by(LectureSession.id).all()


def get_session(db, session_id) -> LectureSession:
    session = db.query(LectureSession).filter(LectureSession.id == session_id).first()
    if not session:
        raise NotFoundError(NOT_FOUND, "Session not found")
    return session


def transition_session(db, principal, session: LectureSession, target) -> LectureSession:
    legal = {('scheduled', 'active'), ('active', 'ended')}
    if (session.status, target) not in legal:
        raise ConflictError(ILLEGAL_TRANSITION, f'Cannot go {session.status}->{target}')

    session.status = target
    now = datetime.now(timezone.utc)
    if target == 'active':
        session.activated_at = now
    elif target == 'ended':
        session.ended_at = now

    db.flush()
    write_audit(db, principal.subject, principal.role, 'session.transition', 'session', session.id)
    return session


def join_session(db, principal, join_code) -> Participant:
    session = db.query(LectureSession).filter(LectureSession.join_code == join_code).first()
    if not session:
        raise NotFoundError(NOT_FOUND, 'Invalid join code')

    enrolled = db.query(Enrollment).filter(
        Enrollment.course_id == session.course_id,
        Enrollment.student_subject == principal.subject
    ).first()
    if not enrolled:
        raise ForbiddenError(NOT_ENROLLED, 'Not enrolled in course')

    if session.status != 'active':
        raise ConflictError(SESSION_NOT_ACTIVE, 'Session not active')

    existing = db.query(Participant).filter(
        Participant.session_id == session.id,
        Participant.student_subject == principal.subject
    ).first()
    if existing:
        return existing

    participant = Participant(
        session_id=session.id,
        student_subject=principal.subject,
        joined_at=datetime.now(timezone.utc)
    )
    db.add(participant)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        existing = db.query(Participant).filter(
            Participant.session_id == session.id,
            Participant.student_subject == principal.subject
        ).first()
        if existing:
            return existing
        raise

    write_audit(db, principal.subject, principal.role, 'session.join', 'session', session.id)
    return participant


def list_participants(db, session_id) -> list:
    return db.query(Participant).filter(Participant.session_id == session_id).order_by(Participant.id).all()
