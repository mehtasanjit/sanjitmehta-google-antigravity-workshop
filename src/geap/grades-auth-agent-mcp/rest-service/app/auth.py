"""Authentication: validate the bearer token and build a Principal.

This is deliberately pluggable. `verify_token` switches on AUTH_MODE so the same
API code validates a locally-minted HS256 token (demo) or, later, a real OAuth
token forwarded by Gemini Enterprise (RS256 via JWKS) — a config-only change.
"""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import config
from .models import Principal

_bearer = HTTPBearer(auto_error=False)

_UNAUTH = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Missing or invalid credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def _decode_local(token: str) -> dict:
    return jwt.decode(
        token,
        config.JWT_SECRET,
        algorithms=[config.JWT_ALGORITHM],
        audience=config.JWT_AUDIENCE,
        issuer=config.JWT_ISSUER,
        options={"require": ["exp", "sub", "iss", "aud"]},
    )


def _claims_to_principal(claims: dict) -> Principal:
    role = claims.get("role")
    if role not in ("student", "professor", "admin"):
        raise _UNAUTH
    # OAuth-standard space-delimited scope string; tolerate a list too.
    raw_scope = claims.get("scope", "")
    scopes = raw_scope.split() if isinstance(raw_scope, str) else list(raw_scope)
    return Principal(
        sub=claims["sub"],
        role=role,
        scopes=scopes,
        name=claims.get("name"),
    )


def verify_token(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> Principal:
    """FastAPI dependency: returns the authenticated Principal or raises 401."""
    if creds is None or not creds.credentials:
        raise _UNAUTH
    try:
        if config.AUTH_MODE == "local":
            claims = _decode_local(creds.credentials)
        else:  # pragma: no cover - GCP/JWKS path wired in a later step
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"AUTH_MODE={config.AUTH_MODE} not implemented yet",
            )
    except jwt.PyJWTError:
        raise _UNAUTH
    return _claims_to_principal(claims)
