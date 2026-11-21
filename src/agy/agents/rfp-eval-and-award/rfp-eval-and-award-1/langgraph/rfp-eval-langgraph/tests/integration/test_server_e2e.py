# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""End-to-end test against the server this project actually runs.

Replaces the deployment target's copy, which drives routes only an ADK server
has. This app serves A2A, at the paths the deploy entrypoint advertises.
"""

import asyncio
import logging
import os
import subprocess
import sys
import threading
import time
import uuid
from collections.abc import Iterator
from typing import Any

import httpx
import pytest
import requests
from a2a.client import ClientConfig, create_client
from a2a.types import (
    Message,
    Part,
    Role,
    SendMessageRequest,
    StreamResponse,
    TaskState,
)
from requests.exceptions import RequestException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000"
A2A_RPC_URL = BASE_URL + "/a2a/app/"
AGENT_CARD_URL = A2A_RPC_URL + ".well-known/agent-card.json"


def log_output(pipe: Any, log_func: Any) -> None:
    for line in iter(pipe.readline, ""):
        log_func(line.strip())


def start_server() -> subprocess.Popen[str]:
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.fast_api_app:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]
    env = os.environ.copy()
    env["INTEGRATION_TEST"] = "TRUE"
    # The agent card advertises this, and the A2A client follows it.
    env["APP_URL"] = BASE_URL
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
    )
    threading.Thread(
        target=log_output, args=(process.stdout, logger.info), daemon=True
    ).start()
    threading.Thread(
        target=log_output, args=(process.stderr, logger.error), daemon=True
    ).start()
    return process


def wait_for_server(timeout: int = 90, interval: int = 1) -> bool:
    """The card is only served once the lifespan has built the graph."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if requests.get(AGENT_CARD_URL, timeout=10).status_code == 200:
                logger.info("Server is ready")
                return True
        except RequestException:
            pass
        time.sleep(interval)
    logger.error(f"Server did not become ready within {timeout} seconds")
    return False


@pytest.fixture(scope="session")
def server_fixture(request: Any) -> Iterator[subprocess.Popen[str]]:
    logger.info("Starting server process")
    server_process = start_server()
    if not wait_for_server():
        pytest.fail("Server failed to start")

    def stop_server() -> None:
        server_process.terminate()
        server_process.wait()

    request.addfinalizer(stop_server)
    yield server_process


def test_a2a_chat_stream(server_fixture: subprocess.Popen[str]) -> None:
    """The graph answers over the A2A JSON-RPC streaming protocol."""

    async def _stream() -> list[StreamResponse]:
        config = ClientConfig(
            streaming=True, httpx_client=httpx.AsyncClient(timeout=60.0)
        )
        client = await create_client(A2A_RPC_URL.rstrip("/"), config)
        message = Message(
            message_id=f"msg-user-{uuid.uuid4()}",
            role=Role.ROLE_USER,
            parts=[Part(text="Hi!")],
        )
        return [
            chunk
            async for chunk in client.send_message(SendMessageRequest(message=message))
        ]

    responses = asyncio.run(_stream())
    assert responses, "No responses received from stream"

    def _is_completed(chunk: StreamResponse) -> bool:
        if chunk.HasField("status_update"):
            return chunk.status_update.status.state == TaskState.TASK_STATE_COMPLETED
        if chunk.HasField("task"):
            return chunk.task.status.state == TaskState.TASK_STATE_COMPLETED
        return False

    assert any(_is_completed(chunk) for chunk in responses), (
        "No completed task received from stream"
    )


def test_agent_card(server_fixture: subprocess.Popen[str]) -> None:
    """Deploy and `agents-cli run --mode a2a` both read this card."""
    response = requests.get(AGENT_CARD_URL, timeout=10)
    assert response.status_code == 200, f"A2A endpoint returned {response.status_code}"

    served_agent_card = response.json()
    for field in (
        "name",
        "description",
        "skills",
        "capabilities",
        "version",
        "supportedInterfaces",
    ):
        assert field in served_agent_card, f"Missing field in agent card: {field}"


def test_health(server_fixture: subprocess.Popen[str]) -> None:
    """Cloud Run and GKE probe this."""
    assert requests.get(f"{BASE_URL}/health", timeout=10).status_code == 200
