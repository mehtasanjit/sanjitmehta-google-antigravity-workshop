"""Blackboard MCP server (FastMCP, Streamable HTTP).

A stateless pass-through: each tool reads the caller's Blackboard access token
from the request `Authorization` header and forwards it to the Blackboard Learn
REST API. Blackboard is the sole authority for access — a token that isn't
permitted for an action simply gets a 4xx, which we surface as a readable error.

No roles, no per-user state: every request is authenticated independently from
its own forwarded token, so concurrent users never bleed into each other.
"""
from typing import Any, Optional
from urllib.parse import quote

from mcp.server.fastmcp import Context, FastMCP

try:
    from mcp.server.fastmcp.exceptions import ToolError
except Exception:  # pragma: no cover - fallback across SDK versions
    ToolError = RuntimeError  # type: ignore

from . import blackboard, config
from .blackboard import BlackboardError

mcp = FastMCP(
    "blackboard-mcp-server",
    stateless_http=True,
    host="0.0.0.0",
    port=config.PORT,
    streamable_http_path=config.MCP_PATH,
)


def _token(ctx: Context) -> str:
    """The caller's Blackboard access token, from the request Authorization header.

    In Gemini Enterprise this is the per-user token the platform forwards; it is
    read fresh on every request. Falls back to BLACKBOARD_ACCESS_TOKEN only for
    local/dev use when no header is present."""
    request = ctx.request_context.request
    auth = request.headers.get("authorization") if request is not None else None
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    if config.ACCESS_TOKEN:
        return config.ACCESS_TOKEN
    raise ToolError(
        "Missing access token: forward 'Authorization: Bearer <token>' "
        "(or set BLACKBOARD_ACCESS_TOKEN for local dev)."
    )


def _err(e: BlackboardError) -> dict:
    """Surface a Blackboard error (incl. 403 for unauthorized actions) readably."""
    return {"error": e.detail, "status": e.status}


@mcp.tool()
async def get_my_courses(ctx: Context) -> Any:
    """List the current user's active course memberships (with course details)."""
    try:
        data = await blackboard.call_api(
            "/learn/api/public/v1/users/me/courses?expand=course", _token(ctx)
        )
        return data.get("results", [])
    except BlackboardError as e:
        return _err(e)


@mcp.tool()
async def get_assignment_due_dates(ctx: Context, course_id: Optional[str] = None) -> Any:
    """Fetch upcoming assignment due dates / calendar items across enrolled
    courses. Optionally scope to a single course_id (e.g. '_456_1')."""
    endpoint = "/learn/api/public/v1/calendars/items?type=Course"
    if course_id:
        endpoint += f"&courseId={quote(course_id)}"
    try:
        data = await blackboard.call_api(endpoint, _token(ctx))
        return data.get("results", [])
    except BlackboardError as e:
        return _err(e)


@mcp.tool()
async def get_outstanding_assignments(ctx: Context, course_id: str) -> Any:
    """Fetch assignments with unmarked attempts needing grading for a course,
    using batched concurrent queries. Requires instructor-level access to the
    course (Blackboard enforces this)."""
    token = _token(ctx)
    try:
        columns_data = await blackboard.call_api(
            f"/learn/api/public/v2/courses/{quote(course_id)}/gradebook/columns", token
        )
    except BlackboardError as e:
        return _err(e)
    columns = columns_data.get("results", []) or []

    async def fetch(column: dict) -> Optional[dict]:
        col_id = column.get("id")
        try:
            attempts_data = await blackboard.call_api(
                f"/learn/api/public/v2/courses/{quote(course_id)}/gradebook/columns/"
                f"{col_id}/attempts?status=NeedsGrading",
                token,
            )
        except BlackboardError:
            return None  # gracefully ignore non-gradable columns
        attempts = attempts_data.get("results", []) or []
        if not attempts:
            return None
        return {
            "columnId": col_id,
            "columnName": column.get("name"),
            "needsGradingCount": len(attempts),
            "attempts": [
                {
                    "attemptId": a.get("id"),
                    "userId": a.get("userId"),
                    "created": a.get("created"),
                    "status": a.get("status"),
                }
                for a in attempts
            ],
        }

    results = await blackboard.map_in_batches(columns, config.BATCH_SIZE, fetch)
    return [r for r in results if r is not None]


@mcp.tool()
async def lookup_user(ctx: Context, identifier: str) -> Any:
    """Look up a user by username / external account id. Requires admin
    privileges on the token (Blackboard enforces)."""
    try:
        data = await blackboard.call_api(
            f"/learn/api/public/v1/users?userName={quote(identifier)}", _token(ctx)
        )
        return data.get("results", [])
    except BlackboardError as e:
        return _err(e)


@mcp.tool()
async def get_course_enrollments(ctx: Context, course_id: str) -> Any:
    """List a course's enrollments / membership status. Requires appropriate
    access on the token (Blackboard enforces)."""
    try:
        data = await blackboard.call_api(
            f"/learn/api/public/v1/courses/{quote(course_id)}/users?expand=user", _token(ctx)
        )
        return data.get("results", [])
    except BlackboardError as e:
        return _err(e)


# ASGI app for uvicorn / Cloud Run (serves the Streamable HTTP endpoint at /mcp).
app = mcp.streamable_http_app()
