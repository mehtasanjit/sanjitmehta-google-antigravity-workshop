"""Runtime configuration — sourced ENTIRELY from environment variables.

Nothing sensitive (base URL, tokens, OAuth app key/secret) is committed. Provide
values via a local `.env` (git-ignored) or the runtime environment. See
`.env.example` for the full set of keys (all with empty values).

Note on OAuth: this server never holds the OAuth Client ID/Secret. In Gemini
Enterprise those live in the connector config; GE runs the OAuth flow and forwards
each user's Blackboard access token in the request `Authorization` header.
"""
import os

# Blackboard Learn instance base URL, e.g. https://yourinstitution.blackboard.com
# NOT committed — must be provided at runtime. Empty => API calls fail fast.
BLACKBOARD_BASE_URL = os.getenv("BLACKBOARD_BASE_URL", "")

# LOCAL/DEV fallback access token, used only when no Authorization header is
# present (e.g. stdio testing). In the GE deployment the per-user token always
# arrives in the header, so this stays empty and unused.
ACCESS_TOKEN = os.getenv("BLACKBOARD_ACCESS_TOKEN", "")

# Streamable-HTTP endpoint path + server port (Cloud Run injects PORT).
MCP_PATH = os.getenv("MCP_PATH", "/mcp")
PORT = int(os.getenv("PORT", "8080"))

# Timeout for Blackboard API calls (seconds).
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30"))

# Concurrency for batched gradebook queries (avoids rate-limits / socket exhaustion).
BATCH_SIZE = int(os.getenv("GRADING_BATCH_SIZE", "5"))

# OPTIONAL. OAuth client IDs (Blackboard REST "Application Key") that the
# /oauth2/token proxy is allowed to forward to Blackboard. Comma-separated (e.g.
# staging + prod app keys). Client IDs are public (they appear in the
# authorization URL), so a plain env var is fine.
# - Empty (default): the proxy forwards every request; Blackboard still validates
#   the client credentials.
# - Set: requests for any other client ID get 401 and never reach Blackboard
#   (prevents the endpoint being used as an open relay). Recommended for prod.
ALLOWED_CLIENT_IDS = frozenset(
    c.strip() for c in os.getenv("ALLOWED_CLIENT_IDS", "").split(",") if c.strip()
)
