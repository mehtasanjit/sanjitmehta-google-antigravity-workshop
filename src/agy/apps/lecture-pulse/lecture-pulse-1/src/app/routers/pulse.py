from fastapi import APIRouter, Depends
from app.db import get_db
from app.deps.auth import get_current_principal
from app.deps.access import require_session_owner, require_pulse_owner, require_pulse_participant
from app.schemas.pulse import PulseOut, PulseResponseCreate, PulseResponseOut, PulseSentimentOut
from app.services.pulse import trigger_pulse, submit_rating
from app.services.aggregation import pulse_sentiment

router = APIRouter(tags=['pulse'])


@router.post('/sessions/{session_id}/pulses', response_model=PulseOut, status_code=201)
def trigger(session=Depends(require_session_owner), db=Depends(get_db), principal=Depends(get_current_principal)):
    return trigger_pulse(db, principal, session)


@router.post('/pulses/{pulse_id}/responses', response_model=PulseResponseOut, status_code=201)
def rate(body: PulseResponseCreate, pulse=Depends(require_pulse_participant), db=Depends(get_db), principal=Depends(get_current_principal)):
    return submit_rating(db, principal, pulse, body.rating)


@router.get('/pulses/{pulse_id}/sentiment', response_model=PulseSentimentOut)
def sentiment(pulse=Depends(require_pulse_owner), db=Depends(get_db)):
    return pulse_sentiment(db, pulse)
