"""Runtime configuration, sourced from environment variables.

Everything here has a demo-friendly default so the service runs with zero setup,
while still allowing a config-only switch to a real IdP (e.g. Gemini Enterprise /
Google Identity Platform) by changing AUTH_MODE and the JWT_* values.
"""
import os
from pathlib import Path

# --- Auth -----------------------------------------------------------------
# "local" -> validate HS256 tokens minted by scripts/generate_token.py
# "gcp"   -> (future) validate RS256 tokens via a JWKS URL forwarded by GEAP
AUTH_MODE = os.getenv("AUTH_MODE", "local")

# Local (HS256) mode
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Claims validated regardless of mode
JWT_ISSUER = os.getenv("JWT_ISSUER", "grades-auth-local")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "grades-rest")

# GCP (RS256/JWKS) mode — wired later; read here so the swap is config-only
JWKS_URL = os.getenv("JWKS_URL", "")

# --- Data -----------------------------------------------------------------
_DEFAULT_DATA = Path(__file__).resolve().parent / "data" / "seed.json"
DATA_PATH = Path(os.getenv("DATA_PATH", str(_DEFAULT_DATA)))

# --- Server ---------------------------------------------------------------
PORT = int(os.getenv("PORT", "8080"))
