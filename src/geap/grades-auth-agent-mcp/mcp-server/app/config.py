"""Runtime configuration for the MCP server."""
import os

# The grades REST service this MCP server proxies to. Set REST_BASE_URL to your
# deployed REST URL (e.g. https://grades-rest-<HASH>.<REGION>.run.app) or, for
# local dev, http://localhost:8080. The placeholder default fails fast if unset.
REST_BASE_URL = os.getenv("REST_BASE_URL", "https://REPLACE-ME-grades-rest.run.app")

# Streamable-HTTP endpoint path (GEAP + Cloud Run expect a single /mcp endpoint).
MCP_PATH = os.getenv("MCP_PATH", "/mcp")

# Cloud Run injects PORT; bind all interfaces.
PORT = int(os.getenv("PORT", "8080"))

# Timeout for calls to the REST service (seconds).
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "15"))
