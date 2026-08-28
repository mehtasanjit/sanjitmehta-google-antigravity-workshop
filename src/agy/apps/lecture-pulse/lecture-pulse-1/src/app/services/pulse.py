from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from app.errors import ConflictError, NotFoundError, NOT_FOUND, SESSION_NOT_ACTIVE, DUPLICATE_RATING
from app.models import Pulse, PulseResponse, LectureSession
from app.services.audit import write_audit


def get_pulse(db, pulse_id) -> Pulse:
    pulse = db.query(Pulse).filter(Pulse.id == pulse_id).first()
    if not pulse:
        raise NotFoundError(NOT_FOUND, "Pulse not found")
    return pulse


def trigger_pulse(db, principal, session: LectureSession) -> Pulse:
    if session.status != "active":
        raise ConflictError(SESSION_NOT_ACTIVE, "Session not active")
    prior = db.query(Pulse).filter(Pulse.session_id == session.id, Pulse.status == "active").first()
    if prior:
        prior.status = "closed"
        prior.closed_at = datetime.now(timezone.utc)
        db.flush()
    p = Pulse(session_id=session.id, status="active")
    db.add(p)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ConflictError("pulse_conflict", "An active pulse already exists for this session")
    write_audit(db, principal.subject, principal.role, "pulse.trigger", "pulse", p.id)
    return p


def submit_rating(db, principal, pulse: Pulse, rating) -> PulseResponse:
    if pulse.status != "active":
        raise ConflictError("pulse_closed", "Pulse is closed")
    pr = PulseResponse(pulse_id=pulse.id, student_subject=principal.subject, rating=rating)
    db.add(pr)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ConflictError(DUPLICATE_RATING, "Already rated")
    write_audit(db, principal.subject, principal.role, "pulse.rate", "pulse", pulse.id)
    return pr
