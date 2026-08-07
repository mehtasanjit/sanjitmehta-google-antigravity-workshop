"""Agent configuration (env-driven)."""
import os

# Grades MCP server endpoint (Streamable HTTP). Set MCP_URL to your deployed
# server, e.g. https://grades-mcp-<HASH>.<REGION>.run.app/mcp (or a local
# http://localhost:8080/mcp). The placeholder default fails fast if unset.
MCP_URL = os.getenv("MCP_URL", "https://REPLACE-ME-grades-mcp.run.app/mcp")

# Gemini model driving the agent. Override via env if a different one is enabled.
MODEL = os.getenv("MODEL", "gemini-2.5-flash")

# Fallback bearer token when the session state carries none (e.g. `adk web`).
# run.py injects the per-user token into session state instead of using this.
DEFAULT_JWT = os.getenv("USER_JWT", "")
