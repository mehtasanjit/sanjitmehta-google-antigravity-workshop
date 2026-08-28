from fastapi import APIRouter, Depends
from app.db import get_db
from app.deps.auth import get_current_principal, require_role
from app.deps.access import require_session_owner, load_session_or_404, is_session_owner, _is_joined
from app.errors import ForbiddenError, FORBIDDEN
from app.schemas.common import ListResponse
from app.schemas.session import SessionOut, SessionTransition, JoinRequest, JoinResponse, ParticipantOut
from app.services.sessions import get_session, transition_session, join_session, list_participants

router = APIRouter(prefix='/sessions', tags=['sessions'])


@router.post('/join', response_model=JoinResponse)
def join(body: JoinRequest, db=Depends(get_db), principal=Depends(require_role('student'))):
    participant = join_session(db, principal, body.join_code)
    session = get_session(db, participant.session_id)
    return JoinResponse(session_id=participant.session_id, status=session.status, joined_at=participant.joined_at)


@router.get('/{session_id}', response_model=SessionOut)
def get_one(session_id: int, db=Depends(get_db), principal=Depends(get_current_principal)):
    session = load_session_or_404(db, session_id)
    if is_session_owner(db, session, principal.subject):
        return session
    if _is_joined(db, session_id, principal.subject):
        return SessionOut(
            id=session.id,
            course_id=session.course_id,
            title=session.title,
            status=session.status,
            join_code=None,
            created_at=session.created_at,
        )
    raise ForbiddenError(FORBIDDEN, 'Not authorized for this session')


@router.post('/{session_id}/transition', response_model=SessionOut)
def transition(body: SessionTransition, session=Depends(require_session_owner), db=Depends(get_db), principal=Depends(get_current_principal)):
    return transition_session(db, principal, session, body.target)


@router.get('/{session_id}/participants', response_model=ListResponse[ParticipantOut])
def participants(session=Depends(require_session_owner), db=Depends(get_db)):
    return {"items": list_participants(db, session.id)}
