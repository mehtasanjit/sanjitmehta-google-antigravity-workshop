#!/usr/bin/env python3
"""Mint a demo JWT for the grades REST service (local HS256 mode).

Known users get sensible role + scope defaults; anything else can be built with
explicit flags. The secret/issuer/audience must match the service's config.

Usage:
    python scripts/generate_token.py alice           # student token
    python scripts/generate_token.py dr_reed         # professor token
    python scripts/generate_token.py admin           # admin token
    python scripts/generate_token.py x --role student --scope grades.read.self
    python scripts/generate_token.py alice --ttl 30   # 30-minute expiry

Handy:
    export TOKEN=$(python scripts/generate_token.py alice)
    curl -H "Authorization: Bearer $TOKEN" localhost:8080/me
"""
import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

import base64
import hmac
import hashlib
import json

try:
    import jwt
except ImportError:
    jwt = None


def pure_jwt_encode(payload: dict, secret: str, algorithm: str = "HS256") -> str:
    if algorithm != "HS256":
        raise ValueError(f"Only HS256 algorithm supported in fallback mode, got {algorithm}")
    
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header, separators=(',', ':')).encode('utf-8')).rstrip(b'=').decode('utf-8')
    
    clean_payload = {}
    for k, v in payload.items():
        if isinstance(v, datetime):
            clean_payload[k] = int(v.timestamp())
        else:
            clean_payload[k] = v
            
    payload_b64 = base64.urlsafe_b64encode(json.dumps(clean_payload, separators=(',', ':')).encode('utf-8')).rstrip(b'=').decode('utf-8')
    
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=').decode('utf-8')
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

# The secret must match the service's JWT_SECRET (Secret Manager). No default:
# a hardcoded fallback here would hand anyone a working token-minting tool.
SECRET = os.getenv("JWT_SECRET")
if not SECRET:
    print(
        "Set JWT_SECRET to the service's secret before minting a token, e.g.\n"
        "  export JWT_SECRET=$(gcloud secrets versions access latest "
        "--secret=google-antigravity-workshop-secret-1)",
        file=sys.stderr,
    )
    sys.exit(2)
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ISSUER = os.getenv("JWT_ISSUER", "grades-auth-local")
AUDIENCE = os.getenv("JWT_AUDIENCE", "grades-rest")

DEFAULT_SCOPES = {
    "student": ["grades.read.self"],
    "professor": ["grades.read.course", "grades.write.course"],
    "admin": [
        "grades.read.self",
        "grades.read.course",
        "grades.write.course",
        "grades.admin",
    ],
}

# Known demo users -> (role, display name). Keep in sync with generate_data.py.
KNOWN = {
    "alice": ("student", "Alice Nguyen"),
    "bob": ("student", "Bob Martinez"),
    "carol": ("student", "Carol Diaz"),
    "dr_reed": ("professor", "Dr. Evelyn Reed"),
    "dr_kapoor": ("professor", "Dr. Anil Kapoor"),
    "admin": ("admin", "Registrar Admin"),
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sub", help="subject (user id), e.g. alice / dr_reed / admin")
    ap.add_argument("--role", choices=["student", "professor", "admin"], help="override role")
    ap.add_argument("--scope", action="append", dest="scopes", help="override scope (repeatable)")
    ap.add_argument("--name", help="override display name")
    ap.add_argument("--ttl", type=int, default=60, help="token lifetime in minutes (default 60)")
    args = ap.parse_args()

    known_role, known_name = KNOWN.get(args.sub, (None, None))
    role = args.role or known_role
    if role is None:
        print(f"Unknown user '{args.sub}': pass --role.", file=sys.stderr)
        sys.exit(2)

    scopes = args.scopes if args.scopes else DEFAULT_SCOPES[role]
    name = args.name or known_name or args.sub

    now = datetime.now(timezone.utc)
    claims = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": args.sub,
        "role": role,
        "name": name,
        "scope": " ".join(scopes),
        "iat": now,
        "exp": now + timedelta(minutes=args.ttl),
    }
    if jwt:
        token = jwt.encode(claims, SECRET, algorithm=ALGORITHM)
    else:
        token = pure_jwt_encode(claims, SECRET, algorithm=ALGORITHM)
    print(token)


if __name__ == "__main__":
    main()
