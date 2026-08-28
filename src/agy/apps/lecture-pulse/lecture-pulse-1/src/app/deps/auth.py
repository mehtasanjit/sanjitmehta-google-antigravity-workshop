from dataclasses import dataclass
from fastapi import Header, Depends
from app.config import get_settings
from app.security import decode_token
from app.errors import AuthError, ForbiddenError, UNAUTHORIZED, FORBIDDEN


@dataclass
class Principal:
    subject: str
    role: str


def get_current_principal(authorization: str | None = Header(default=None)) -> Principal:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthError(UNAUTHORIZED, "Missing bearer token")
    token = authorization[len("Bearer "):]
    try:
        payload = decode_token(token, get_settings())
        subject = payload["sub"]
        role = payload["role"]
    except Exception:
        raise AuthError(UNAUTHORIZED, "Invalid token")
    return Principal(subject=subject, role=role)


def require_role(role: str):
    def _dep(principal: Principal = Depends(get_current_principal)) -> Principal:
        if principal.role != role:
            raise ForbiddenError(FORBIDDEN, 'Requires role ' + role)
        return principal
    return _dep
