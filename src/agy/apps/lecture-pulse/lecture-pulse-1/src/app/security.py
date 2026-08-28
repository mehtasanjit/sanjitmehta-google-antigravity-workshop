from datetime import datetime, timedelta, timezone
import jwt
from app.config import Settings


def encode_token(subject: str, role: str, settings: Settings) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "iss": settings.JWT_ISSUER,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=settings.JWT_EXPIRES_SECONDS)).timestamp())
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, settings: Settings) -> dict:
    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
        issuer=settings.JWT_ISSUER,
        options={"require": ["exp", "iss", "sub"]},
    )
    return payload
