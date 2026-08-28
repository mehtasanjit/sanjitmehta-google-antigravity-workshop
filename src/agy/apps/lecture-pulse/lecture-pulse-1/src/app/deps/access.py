from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.errors import NotFoundError, ForbiddenError, NOT_FOUND, FORBIDDEN, NOT_JOINED
from app.models import Course, LectureSession, Participant, Poll, Question, Pulse
from app.deps.auth import get_current_principal, Principal


def load_session_or_404(db: Session, session_id: int) -> LectureSession:
    session = db.query(LectureSession).filter(LectureSession.id == session_id).first()
    if not session:
        raise NotFoundError(NOT_FOUND, "Lecture session not found")
    return session


def is_session_owner(db: Session, session: LectureSession, subject: str) -> bool:
    course = db.query(Course).filter(Course.id == session.course_id).first()
    if not course:
        return False
    return course.owner_subject == subject


def require_course_owner(
    course_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal)
) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise NotFoundError(NOT_FOUND, "Course not found")
    if course.owner_subject != principal.subject:
        raise ForbiddenError(FORBIDDEN, "Not course owner")
    return course


def require_session_owner(
    session_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal)
) -> LectureSession:
    session = load_session_or_404(db, session_id)
    if not is_session_owner(db, session, principal.subject):
        raise ForbiddenError(FORBIDDEN, "Not course owner")
    return session


def require_joined_participant(
    session_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal)
) -> LectureSession:
    session = load_session_or_404(db, session_id)
    participant = db.query(Participant).filter(
        Participant.session_id == session_id,
        Participant.student_subject == principal.subject
    ).first()
    if not participant:
        raise ForbiddenError(NOT_JOINED, "Not joined")
    return session


def require_participant_or_owner(
    session_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal)
) -> LectureSession:
    session = load_session_or_404(db, session_id)
    if is_session_owner(db, session, principal.subject):
        return session
    participant = db.query(Participant).filter(
        Participant.session_id == session_id,
        Participant.student_subject == principal.subject
    ).first()
    if not participant:
        raise ForbiddenError(FORBIDDEN, "Not authorized as owner or participant")
    return session


def _is_joined(db: Session, session_id: int, subject: str) -> bool:
    return db.query(Participant).filter(
        Participant.session_id == session_id,
        Participant.student_subject == subject
    ).first() is not None


# ---- Poll resource deps ----

def require_poll_owner(
    poll_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal)
) -> Poll:
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise NotFoundError(NOT_FOUND, "Poll not found")
    session = load_session_or_404(db, poll.session_id)
    if not is_session_owner(db, session, principal.subject):
        raise ForbiddenError(FORBIDDEN, "Not poll owner")
    return poll


def require_poll_participant(
    poll_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal)
) -> Poll:
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise NotFoundError(NOT_FOUND, "Poll not found")
    if not _is_joined(db, poll.session_id, principal.subject):
        raise ForbiddenError(NOT_JOINED, "Not joined")
    return poll


# ---- Question resource deps ----

def require_question_owner(
    question_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal)
) -> Question:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise NotFoundError(NOT_FOUND, "Question not found")
    session = load_session_or_404(db, question.session_id)
    if not is_session_owner(db, session, principal.subject):
        raise ForbiddenError(FORBIDDEN, "Not question owner")
    return question


def require_question_participant_or_owner(
    question_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal)
) -> Question:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise NotFoundError(NOT_FOUND, "Question not found")
    session = load_session_or_404(db, question.session_id)
    if is_session_owner(db, session, principal.subject):
        return question
    if not _is_joined(db, question.session_id, principal.subject):
        raise ForbiddenError(FORBIDDEN, "Not authorized as owner or participant")
    return question


# ---- Pulse resource deps ----

def require_pulse_owner(
    pulse_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal)
) -> Pulse:
    pulse = db.query(Pulse).filter(Pulse.id == pulse_id).first()
    if not pulse:
        raise NotFoundError(NOT_FOUND, "Pulse not found")
    session = load_session_or_404(db, pulse.session_id)
    if not is_session_owner(db, session, principal.subject):
        raise ForbiddenError(FORBIDDEN, "Not pulse owner")
    return pulse


def require_pulse_participant(
    pulse_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal)
) -> Pulse:
    pulse = db.query(Pulse).filter(Pulse.id == pulse_id).first()
    if not pulse:
        raise NotFoundError(NOT_FOUND, "Pulse not found")
    if not _is_joined(db, pulse.session_id, principal.subject):
        raise ForbiddenError(NOT_JOINED, "Not joined")
    return pulse
