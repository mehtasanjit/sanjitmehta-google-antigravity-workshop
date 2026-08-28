from fastapi import APIRouter, Depends
from app.db import get_db
from app.deps.auth import get_current_principal
from app.deps.access import require_session_owner, require_poll_owner, require_poll_participant
from app.models import PollOption
from app.schemas.poll import PollCreate, PollOut, PollOptionOut, ResponseCreate, ResponseOut, PollResultsOut
from app.services.polls import create_poll, open_poll, close_poll, submit_response
from app.services.aggregation import poll_results

router = APIRouter(tags=['polls'])


def _poll_out(db, poll) -> PollOut:
    opts = db.query(PollOption).filter(PollOption.poll_id == poll.id).order_by(PollOption.position).all()
    return PollOut(
        id=poll.id,
        session_id=poll.session_id,
        prompt=poll.prompt,
        poll_type=poll.poll_type,
        is_quiz=poll.is_quiz,
        status=poll.status,
        options=[PollOptionOut(id=o.id, text=o.text, position=o.position) for o in opts],
        created_at=poll.created_at,
    )


@router.post('/sessions/{session_id}/polls', response_model=PollOut, status_code=201)
def create(body: PollCreate, session=Depends(require_session_owner), db=Depends(get_db), principal=Depends(get_current_principal)):
    poll = create_poll(db, principal, session, body)
    return _poll_out(db, poll)


@router.post('/polls/{poll_id}/open', response_model=PollOut)
def open_p(poll=Depends(require_poll_owner), db=Depends(get_db), principal=Depends(get_current_principal)):
    p = open_poll(db, principal, poll)
    return _poll_out(db, p)


@router.post('/polls/{poll_id}/close', response_model=PollOut)
def close_p(poll=Depends(require_poll_owner), db=Depends(get_db), principal=Depends(get_current_principal)):
    p = close_poll(db, principal, poll)
    return _poll_out(db, p)


@router.post('/polls/{poll_id}/responses', response_model=ResponseOut, status_code=201)
def respond(body: ResponseCreate, poll=Depends(require_poll_participant), db=Depends(get_db), principal=Depends(get_current_principal)):
    return submit_response(db, principal, poll, body.option_ids)


@router.get('/polls/{poll_id}/results', response_model=PollResultsOut)
def results(poll=Depends(require_poll_owner), db=Depends(get_db)):
    return poll_results(db, poll)
