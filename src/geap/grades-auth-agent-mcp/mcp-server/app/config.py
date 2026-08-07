"""Runtime configuration for the MCP server."""
import os

# The grades REST service this MCP server proxies to. Defaults to the deployed
# Cloud Run URL so the server works out of the box; override for local dev
# (e.g. REST_BASE_URL=http://localhost:8080).
REST_BASE_URL = os.getenv(
    "REST_BASE_URL", "https://grades-rest-47444200274.us-central1.run.app"
)

# Streamable-HTTP endpoint path (GEAP + Cloud Run expect a single /mcp endpoint).
MCP_PATH = os.getenv("MCP_PATH", "/mcp")

# Cloud Run injects PORT; bind all interfaces.
PORT = int(os.getenv("PORT", "8080"))

# Timeout for calls to the REST service (seconds).
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "15"))
