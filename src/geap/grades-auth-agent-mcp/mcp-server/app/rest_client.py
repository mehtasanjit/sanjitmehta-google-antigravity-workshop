"""Thin async client for the grades REST service.

Every call forwards the caller's Authorization header verbatim — the REST service
is the authority that validates the token and enforces authorization. This module
adds no auth logic of its own; it only relays identity downstream (the OBO hop).
"""
import httpx

from . import config


class RestError(Exception):
    """A non-2xx response from the REST service, carrying its status + detail."""

    def __init__(self, status: int, detail: str):
        self.status = status
        self.detail = detail
        super().__init__(f"{status}: {detail}")


def _detail(resp: httpx.Response) -> str:
    try:
        body = resp.json()
        if isinstance(body, dict) and "detail" in body:
            return str(body["detail"])
        return str(body)
    except Exception:
        return resp.text or resp.reason_phrase


async def _request(
    method: str,
    path: str,
    auth_header: str,
    *,
    client: httpx.AsyncClient | None = None,
    **kwargs,
):
    url = config.REST_BASE_URL.rstrip("/") + path
    headers = {"Authorization": auth_header}
    own = client is None
    client = client or httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT)
    try:
        resp = await client.request(method, url, headers=headers, **kwargs)
    finally:
        if own:
            await client.aclose()
    if resp.status_code >= 400:
        raise RestError(resp.status_code, _detail(resp))
    return resp.json()


async def whoami(auth_header: str, **kw):
    return await _request("GET", "/me", auth_header, **kw)


async def student_grades(auth_header: str, student_id: str, **kw):
    return await _request("GET", f"/students/{student_id}/grades", auth_header, **kw)


async def course_grades(auth_header: str, course_code: str, **kw):
    return await _request("GET", f"/courses/{course_code}/grades", auth_header, **kw)


async def list_courses(auth_header: str, **kw):
    return await _request("GET", "/courses", auth_header, **kw)


async def upsert_grade(auth_header: str, course_code: str, student_id: str, score: float, **kw):
    return await _request(
        "POST",
        f"/courses/{course_code}/grades",
        auth_header,
        json={"student_id": student_id, "score": score},
        **kw,
    )
