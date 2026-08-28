from fastapi import APIRouter, Depends
from app.db import get_db
from app.config import get_settings
from app.security import encode_token
from app.deps.auth import get_current_principal
from app.services.courses import upsert_user
from app.models import User
from app.schemas.auth import TokenRequest, TokenResponse, MeResponse

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token', response_model=TokenResponse)
def issue_token(body: TokenRequest, db=Depends(get_db)):
    upsert_user(db, body.subject, body.role, body.display_name, body.email)
    settings = get_settings()
    token = encode_token(body.subject, body.role, settings)
    return TokenResponse(
        access_token=token,
        token_type='bearer',
        expires_in=settings.JWT_EXPIRES_SECONDS,
        subject=body.subject,
        role=body.role,
    )


@router.get('/me', response_model=MeResponse)
def me(principal=Depends(get_current_principal), db=Depends(get_db)):
    user = db.query(User).filter(User.subject == principal.subject).first()
    return MeResponse(
        subject=principal.subject,
        role=principal.role,
        display_name=(user.display_name if user else None),
    )
