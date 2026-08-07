"""Unit tests for the REST client — token forwarding + error mapping.

Uses httpx.MockTransport so no network or running service is required.
Async is driven via asyncio.run to avoid a pytest-asyncio dependency.
"""
import asyncio

import httpx
import pytest

from app import rest_client
from app.rest_client import RestError


def _client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://test")


def test_forwards_authorization_header():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["auth"] = request.headers.get("authorization")
        captured["path"] = request.url.path
        return httpx.Response(200, json={"sub": "alice", "role": "student"})

    async def run():
        async with _client(handler) as c:
            return await rest_client.whoami("Bearer tok-123", client=c)

    result = asyncio.run(run())
    assert result["sub"] == "alice"
    assert captured["auth"] == "Bearer tok-123"   # forwarded verbatim
    assert captured["path"] == "/me"


def test_upsert_sends_body_and_path():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["path"] = request.url.path
        captured["body"] = request.content
        return httpx.Response(200, json={"student_id": "bob", "score": 91})

    async def run():
        async with _client(handler) as c:
            return await rest_client.upsert_grade("Bearer t", "CHEM-101", "bob", 91, client=c)

    result = asyncio.run(run())
    assert result["score"] == 91
    assert captured["method"] == "POST"
    assert captured["path"] == "/courses/CHEM-101/grades"
    assert b"bob" in captured["body"]


def test_maps_403_to_resterror():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"detail": "You do not teach this course"})

    async def run():
        async with _client(handler) as c:
            await rest_client.course_grades("Bearer t", "CHEM-101", client=c)

    with pytest.raises(RestError) as ei:
        asyncio.run(run())
    assert ei.value.status == 403
    assert "do not teach" in ei.value.detail


def test_maps_401_to_resterror():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Missing or invalid credentials"})

    async def run():
        async with _client(handler) as c:
            await rest_client.whoami("Bearer bad", client=c)

    with pytest.raises(RestError) as ei:
        asyncio.run(run())
    assert ei.value.status == 401
