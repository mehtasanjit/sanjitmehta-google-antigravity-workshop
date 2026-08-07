"""Agent configuration (env-driven)."""
import os

# Deployed grades MCP server (Streamable HTTP). Override for local dev.
MCP_URL = os.getenv("MCP_URL", "https://grades-mcp-47444200274.us-central1.run.app/mcp")

# Gemini model driving the agent. Override via env if a different one is enabled.
MODEL = os.getenv("MODEL", "gemini-2.5-flash")

# Fallback bearer token when the session state carries none (e.g. `adk web`).
# run.py injects the per-user token into session state instead of using this.
DEFAULT_JWT = os.getenv("USER_JWT", "")
