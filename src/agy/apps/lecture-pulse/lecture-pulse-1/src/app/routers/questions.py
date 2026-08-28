from fastapi import APIRouter, Depends
from app.db import get_db
from app.deps.auth import get_current_principal
from app.deps.access import require_joined_participant, require_session_owner, require_question_owner, require_question_participant_or_owner
from app.schemas.common import ListResponse
from app.schemas.question import QuestionCreate, QuestionOut, UpvoteOut, ModerateRequest
from app.services.questions import post_question, upvote_question, moderate_question
from app.services.aggregation import question_ranking

router = APIRouter(tags=['questions'])


@router.post('/sessions/{session_id}/questions', response_model=QuestionOut, status_code=201)
def post_q(body: QuestionCreate, session=Depends(require_joined_participant), db=Depends(get_db), principal=Depends(get_current_principal)):
    q = post_question(db, principal, session, body.text)
    return QuestionOut(
        id=q.id,
        session_id=q.session_id,
        author_subject=q.author_subject,
        text=q.text,
        status=q.status,
        upvotes=0,
        created_at=q.created_at,
    )


@router.post('/questions/{question_id}/upvotes', response_model=UpvoteOut, status_code=201)
def upvote(question=Depends(require_question_participant_or_owner), db=Depends(get_db), principal=Depends(get_current_principal)):
    count = upvote_question(db, principal, question)
    return UpvoteOut(question_id=question.id, upvotes=count)


@router.get('/sessions/{session_id}/questions', response_model=ListResponse[QuestionOut])
def ranked(session=Depends(require_session_owner), db=Depends(get_db)):
    return {"items": question_ranking(db, session.id)}


@router.post('/questions/{question_id}/moderate', response_model=QuestionOut)
def moderate(body: ModerateRequest, question=Depends(require_question_owner), db=Depends(get_db), principal=Depends(get_current_principal)):
    q = moderate_question(db, principal, question, body.status)
    return QuestionOut(
        id=q.id,
        session_id=q.session_id,
        author_subject=q.author_subject,
        text=q.text,
        status=q.status,
        upvotes=0,
        created_at=q.created_at,
    )
