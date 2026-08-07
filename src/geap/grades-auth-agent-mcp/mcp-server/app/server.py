"""Grades MCP server (FastMCP, Streamable HTTP).

The on-behalf-of hop: each tool extracts the user's bearer token from the
incoming MCP request and forwards it to the grades REST service, which enforces
per-user authorization. This server holds no grades data and makes no authz
decisions of its own.
"""
from typing import Any

from mcp.server.fastmcp import Context, FastMCP

try:  # exception type used for hard client errors (e.g. no token at all)
    from mcp.server.fastmcp.exceptions import ToolError
except Exception:  # pragma: no cover - fallback across SDK versions
    ToolError = RuntimeError  # type: ignore

from . import config, rest_client
from .rest_client import RestError

mcp = FastMCP(
    "grades-auth",
    stateless_http=True,
    host="0.0.0.0",
    port=config.PORT,
    streamable_http_path=config.MCP_PATH,
)


def _bearer(ctx: Context) -> str:
    """Extract the caller's Authorization header from the live HTTP request.

    In Gemini Enterprise this is the user's OAuth token that the platform
    forwards; locally it's whatever the MCP client sent. Missing token is a
    misconfiguration, so we fail loudly."""
    request = ctx.request_context.request
    auth = request.headers.get("authorization") if request is not None else None
    if not auth:
        raise ToolError(
            "Missing Authorization header. The MCP client must forward the "
            "user's bearer token so it can be relayed to the grades service."
        )
    return auth


def _err(e: RestError) -> dict:
    """Turn a downstream REST error into a readable tool result."""
    return {"error": e.detail, "status": e.status}


@mcp.tool()
async def whoami(ctx: Context) -> Any:
    """Return the identity this request is acting on behalf of, as seen by the
    grades service (proves the token was forwarded end-to-end)."""
    try:
        return await rest_client.whoami(_bearer(ctx))
    except RestError as e:
        return _err(e)


@mcp.tool()
async def get_my_grades(ctx: Context) -> Any:
    """Return the grades of the currently authenticated student."""
    auth = _bearer(ctx)
    try:
        me = await rest_client.whoami(auth)
        return await rest_client.student_grades(auth, me["sub"])
    except RestError as e:
        return _err(e)


@mcp.tool()
async def get_student_grades(ctx: Context, student_id: str) -> Any:
    """Return a specific student's grades (professors see only their taught
    courses; admins see all). Authorization is enforced by the grades service."""
    try:
        return await rest_client.student_grades(_bearer(ctx), student_id)
    except RestError as e:
        return _err(e)


@mcp.tool()
async def get_course_grades(ctx: Context, course_code: str) -> Any:
    """Return all grades for a course (only the owning professor or an admin is
    permitted). e.g. course_code='CHEM-101'."""
    try:
        return await rest_client.course_grades(_bearer(ctx), course_code)
    except RestError as e:
        return _err(e)


@mcp.tool()
async def list_my_courses(ctx: Context) -> Any:
    """List the courses visible to the caller (enrolled, for students; taught,
    for professors; all, for admins)."""
    try:
        return await rest_client.list_courses(_bearer(ctx))
    except RestError as e:
        return _err(e)


@mcp.tool()
async def enter_grade(ctx: Context, course_code: str, student_id: str, score: float) -> Any:
    """Enter or update a grade (0-100) for a student in a course. Only the owning
    professor or an admin may do this; the grades service records the acting user."""
    try:
        return await rest_client.upsert_grade(_bearer(ctx), course_code, student_id, score)
    except RestError as e:
        return _err(e)


# ASGI app for uvicorn / Cloud Run (serves the Streamable HTTP endpoint at /mcp).
app = mcp.streamable_http_app()
