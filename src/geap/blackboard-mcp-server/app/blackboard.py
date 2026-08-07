"""Async client for the Blackboard Learn REST API.

Forwards the caller's access token as a Bearer credential on every request — the
Blackboard instance is the authority for what that token can see. This module
adds no auth logic of its own.
"""
import asyncio
from typing import Awaitable, Callable, Optional

import httpx

from . import config


class BlackboardError(Exception):
    """A non-2xx response (or misconfiguration) from Blackboard."""

    def __init__(self, status: int, detail: str):
        self.status = status
        self.detail = detail
        super().__init__(f"Blackboard API Error ({status}): {detail}")


async def call_api(
    endpoint: str,
    access_token: str,
    *,
    client: Optional[httpx.AsyncClient] = None,
):
    """GET a Blackboard endpoint and return parsed JSON.

    `endpoint` is a path beginning with '/', e.g. '/learn/api/public/v1/users/me'.
    """
    base = config.BLACKBOARD_BASE_URL
    if not base:
        raise BlackboardError(0, "BLACKBOARD_BASE_URL is not configured (set it in .env)")
    url = base.rstrip("/") + endpoint
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    own = client is None
    client = client or httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT)
    try:
        resp = await client.get(url, headers=headers)
    finally:
        if own:
            await client.aclose()
    if resp.status_code >= 400:
        raise BlackboardError(resp.status_code, resp.text)
    return resp.json()


async def map_in_batches(
    items: list,
    batch_size: int,
    fn: Callable[[object], Awaitable[object]],
) -> list:
    """Run `fn` over `items` concurrently in fixed-size batches, preserving order.

    Prevents API rate-limiting / socket exhaustion when fanning out many calls.
    """
    results: list = []
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        results.extend(await asyncio.gather(*(fn(item) for item in batch)))
    return results
