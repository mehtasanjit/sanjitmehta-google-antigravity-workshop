"""Grades Assistant — an ADK agent that acts on behalf of the signed-in user.

The on-behalf-of link: the MCP toolset's `header_provider` reads the user's JWT
from the current session state and sends it as the Authorization header on every
MCP call. The MCP server forwards it to the REST service, which enforces per-user
authorization. Same agent + different user token => different data access.
"""
from typing import Dict, Optional

from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

from . import config


def _auth_headers(ctx: Optional[ReadonlyContext]) -> Dict[str, str]:
    """Provide the Authorization header for MCP calls from the session's user JWT.

    Falls back to config.DEFAULT_JWT (env USER_JWT) when there's no session
    context (e.g. tool discovery). Returns no header if no token is available —
    the MCP/REST layer will then reject data calls with 401, as it should."""
    token = None
    if ctx is not None:
        try:
            token = ctx.state.get("user_jwt")
        except Exception:
            token = None
    token = token or config.DEFAULT_JWT
    return {"Authorization": f"Bearer {token}"} if token else {}


grades_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url=config.MCP_URL),
    header_provider=_auth_headers,
)


INSTRUCTION = """\
You are the Grades Assistant. You help the signed-in user with their grades using
the provided tools. You always act ON BEHALF OF the current user — never invent
grades, and never try to bypass access rules.

Guidance:
- To answer "what are my grades", use `get_my_grades`.
- For a specific student, use `get_student_grades`; for a whole course, use
  `get_course_grades`; to record a grade, use `enter_grade`.
- Use `whoami` if you need to confirm who the user is.
- If a tool returns an object with an "error" and "status" of 403, the user is
  not authorized for that data — explain this politely and do not retry with a
  different identity. A 401 means the user is not authenticated.
- Present grades clearly (course, score, letter). Be concise.
"""

root_agent = LlmAgent(
    name="grades_assistant",
    model=config.MODEL,
    description="Answers grade questions and records grades on behalf of the signed-in user.",
    instruction=INSTRUCTION,
    tools=[grades_toolset],
)
