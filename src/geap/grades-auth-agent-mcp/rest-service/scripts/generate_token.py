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

import jwt

# Defaults mirror app/config.py so tokens validate out of the box.
SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
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
    token = jwt.encode(claims, SECRET, algorithm=ALGORITHM)
    print(token)


if __name__ == "__main__":
    main()
