"""Unit tests for the OAuth2 token proxy endpoint.

Tests that credentials sent in the request body are converted to the
HTTP Basic Authorization header expected by Blackboard Learn.
"""
import asyncio
import base64
import json
import httpx
import pytest
from starlette.datastructures import Headers
from starlette.requests import Request

from app import config
from app.server import oauth2_token_proxy


@pytest.fixture(autouse=True)
def _allowlist(monkeypatch):
    """Default allowlist containing the fake client IDs used by these tests."""
    monkeypatch.setattr(config, "ALLOWED_CLIENT_IDS", frozenset({"my_client_id", "cid"}))


def _make_request(body: bytes, content_type: str = "application/x-www-form-urlencoded", headers: dict = None) -> Request:
    all_headers = {"content-type": content_type}
    if headers:
        all_headers.update(headers)
    raw_headers = [(k.lower().encode("latin-1"), v.encode("latin-1")) for k, v in all_headers.items()]

    async def receive():
        return {"type": "http.request", "body": body}

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/oauth2/token",
        "headers": raw_headers,
    }
    return Request(scope, receive)


def test_token_proxy_converts_body_creds_to_basic_auth(monkeypatch):
    monkeypatch.setattr(config, "BLACKBOARD_BASE_URL", "https://bb.example.com")
    captured = {}

    def mock_handler(request: httpx.Request) -> httpx.Response:
        captured["auth_header"] = request.headers.get("authorization")
        captured["content_type"] = request.headers.get("content-type")
        captured["url"] = str(request.url)
        captured["body"] = request.read().decode("utf-8")
        return httpx.Response(200, json={"access_token": "mock_at", "refresh_token": "mock_rt"})

    req_body = (
        b"grant_type=authorization_code&code=test_code_123"
        b"&client_id=my_client_id&client_secret=my_secret_456"
        b"&redirect_uri=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Foauth-redirect"
    )
    req = _make_request(req_body)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(mock_handler)) as client:
            return await oauth2_token_proxy(req, client=client)

    resp = asyncio.run(run())
    assert resp.status_code == 200
    expected_basic = "Basic " + base64.b64encode(b"my_client_id:my_secret_456").decode("utf-8")
    assert captured["auth_header"] == expected_basic
    assert captured["url"] == "https://bb.example.com/learn/api/public/v1/oauth2/token"
    # Verify client_id and client_secret were stripped from form body
    assert "client_secret" not in captured["body"]
    assert "client_id" not in captured["body"]
    assert "code=test_code_123" in captured["body"]


def test_token_proxy_handles_refresh_token_grant(monkeypatch):
    monkeypatch.setattr(config, "BLACKBOARD_BASE_URL", "https://bb.example.com")
    captured = {}

    def mock_handler(request: httpx.Request) -> httpx.Response:
        captured["auth_header"] = request.headers.get("authorization")
        captured["body"] = request.read().decode("utf-8")
        return httpx.Response(200, json={"access_token": "new_at"})

    req_body = b"grant_type=refresh_token&refresh_token=rt_123&client_id=cid&client_secret=csec"
    req = _make_request(req_body)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(mock_handler)) as client:
            return await oauth2_token_proxy(req, client=client)

    resp = asyncio.run(run())
    assert resp.status_code == 200
    assert captured["auth_header"] == "Basic " + base64.b64encode(b"cid:csec").decode("utf-8")
    assert "refresh_token=rt_123" in captured["body"]


def test_token_proxy_preserves_existing_basic_auth(monkeypatch):
    monkeypatch.setattr(config, "BLACKBOARD_BASE_URL", "https://bb.example.com")
    captured = {}

    def mock_handler(request: httpx.Request) -> httpx.Response:
        captured["auth_header"] = request.headers.get("authorization")
        return httpx.Response(200, json={"access_token": "mock_at"})

    basic = "Basic " + base64.b64encode(b"cid:csec").decode("utf-8")
    req_body = b"grant_type=authorization_code&code=test_code"
    req = _make_request(req_body, headers={"authorization": basic})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(mock_handler)) as client:
            return await oauth2_token_proxy(req, client=client)

    resp = asyncio.run(run())
    assert resp.status_code == 200
    assert captured["auth_header"] == basic


def test_token_proxy_fails_fast_when_no_base_url(monkeypatch):
    monkeypatch.setattr(config, "BLACKBOARD_BASE_URL", "")
    req = _make_request(b"grant_type=authorization_code&code=123")
    resp = asyncio.run(oauth2_token_proxy(req))
    assert resp.status_code == 500
    assert b"BLACKBOARD_BASE_URL is not configured" in resp.body


# --- Allowlist (open-relay protection) ---------------------------------------

def _never_called(request: httpx.Request) -> httpx.Response:
    raise AssertionError("Blackboard must not be contacted for a rejected request")


def _run_with(req, handler):
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await oauth2_token_proxy(req, client=client)
    return asyncio.run(run())


def test_token_proxy_rejects_unknown_client_id(monkeypatch):
    monkeypatch.setattr(config, "BLACKBOARD_BASE_URL", "https://bb.example.com")
    req = _make_request(b"grant_type=authorization_code&code=x&client_id=attacker&client_secret=guess")
    resp = _run_with(req, _never_called)
    assert resp.status_code == 401
    assert json.loads(resp.body)["error"] == "invalid_client"


def test_token_proxy_rejects_unknown_client_in_basic_header(monkeypatch):
    monkeypatch.setattr(config, "BLACKBOARD_BASE_URL", "https://bb.example.com")
    basic = "Basic " + base64.b64encode(b"attacker:guess").decode("utf-8")
    req = _make_request(b"grant_type=authorization_code&code=x", headers={"authorization": basic})
    resp = _run_with(req, _never_called)
    assert resp.status_code == 401


def test_token_proxy_rejects_request_without_client_id(monkeypatch):
    monkeypatch.setattr(config, "BLACKBOARD_BASE_URL", "https://bb.example.com")
    req = _make_request(b"grant_type=authorization_code&code=x")
    resp = _run_with(req, _never_called)
    assert resp.status_code == 401


def test_token_proxy_forwards_all_when_allowlist_empty(monkeypatch):
    monkeypatch.setattr(config, "BLACKBOARD_BASE_URL", "https://bb.example.com")
    monkeypatch.setattr(config, "ALLOWED_CLIENT_IDS", frozenset())
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["auth_header"] = request.headers.get("authorization")
        return httpx.Response(200, json={"access_token": "at"})

    req = _make_request(b"grant_type=authorization_code&code=x&client_id=any_app&client_secret=s")
    resp = _run_with(req, handler)
    assert resp.status_code == 200
    assert captured["auth_header"] == "Basic " + base64.b64encode(b"any_app:s").decode("utf-8")


def test_allowed_client_ids_parsing(monkeypatch):
    import importlib
    monkeypatch.setenv("ALLOWED_CLIENT_IDS", " stg-id , prod-id ,,")
    reloaded = importlib.reload(config)
    try:
        assert reloaded.ALLOWED_CLIENT_IDS == frozenset({"stg-id", "prod-id"})
    finally:
        monkeypatch.delenv("ALLOWED_CLIENT_IDS")
        importlib.reload(config)
