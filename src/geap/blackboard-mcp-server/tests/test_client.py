"""Unit tests for the Blackboard client — token forwarding, errors, batching.

Uses httpx.MockTransport so no network or real Blackboard is required.
Async is driven via asyncio.run to avoid a pytest-asyncio dependency.
"""
import asyncio

import httpx
import pytest

from app import blackboard, config
from app.blackboard import BlackboardError


def _client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://bb")


def test_call_api_forwards_bearer_and_headers(monkeypatch):
    monkeypatch.setattr(config, "BLACKBOARD_BASE_URL", "http://bb")
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["auth"] = request.headers.get("authorization")
        captured["accept"] = request.headers.get("accept")
        captured["path"] = request.url.path
        return httpx.Response(200, json={"results": [1, 2, 3]})

    async def run():
        async with _client(handler) as c:
            return await blackboard.call_api("/learn/api/public/v1/users/me", "tok-abc", client=c)

    data = asyncio.run(run())
    assert data["results"] == [1, 2, 3]
    assert captured["auth"] == "Bearer tok-abc"       # forwarded verbatim
    assert captured["accept"] == "application/json"
    assert captured["path"] == "/learn/api/public/v1/users/me"


def test_call_api_raises_on_error(monkeypatch):
    monkeypatch.setattr(config, "BLACKBOARD_BASE_URL", "http://bb")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="Forbidden")

    async def run():
        async with _client(handler) as c:
            await blackboard.call_api("/x", "tok", client=c)

    with pytest.raises(BlackboardError) as ei:
        asyncio.run(run())
    assert ei.value.status == 403
    assert "Forbidden" in ei.value.detail


def test_call_api_requires_base_url(monkeypatch):
    monkeypatch.setattr(config, "BLACKBOARD_BASE_URL", "")

    async def run():
        await blackboard.call_api("/x", "tok")

    with pytest.raises(BlackboardError):
        asyncio.run(run())


def test_map_in_batches_preserves_order_and_batches():
    seen_batches = []

    async def fn(x):
        return x * 2

    async def run():
        return await blackboard.map_in_batches([1, 2, 3, 4, 5], 2, fn)

    assert asyncio.run(run()) == [2, 4, 6, 8, 10]
