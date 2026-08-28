from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app.errors import ConflictError, NotFoundError, NOT_FOUND, SESSION_NOT_ACTIVE, ILLEGAL_TRANSITION, DUPLICATE_UPVOTE
from app.models import Question, QuestionUpvote, LectureSession
from app.services.audit import write_audit


def get_question(db, question_id) -> Question:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise NotFoundError(NOT_FOUND, "Question not found")
    return question


def post_question(db, principal, session: LectureSession, text) -> Question:
    if session.status != "active":
        raise ConflictError(SESSION_NOT_ACTIVE, "Session not active")
    q = Question(session_id=session.id, author_subject=principal.subject, text=text, status="open")
    db.add(q)
    db.flush()
    write_audit(db, principal.subject, principal.role, "question.post", "question", q.id)
    return q


def upvote_question(db, principal, question: Question) -> int:
    uv = QuestionUpvote(question_id=question.id, voter_subject=principal.subject)
    db.add(uv)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ConflictError(DUPLICATE_UPVOTE, "Already upvoted")
    write_audit(db, principal.subject, principal.role, "question.upvote", "question", question.id)
    count = db.query(func.count(QuestionUpvote.id)).filter(QuestionUpvote.question_id == question.id).scalar() or 0
    return count


def moderate_question(db, principal, question: Question, status) -> Question:
    if question.status != "open":
        raise ConflictError(ILLEGAL_TRANSITION, "Question not open")
    question.status = status
    db.flush()
    write_audit(db, principal.subject, principal.role, "question.moderate", "question", question.id)
    return question
