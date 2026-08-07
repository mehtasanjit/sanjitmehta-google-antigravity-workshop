#!/usr/bin/env python3
"""Smoke-test MCP client: connect over Streamable HTTP, forward a token, call a tool.

Usage:
    python scripts/call_tool.py <server_url> <blackboard_token> --list
    python scripts/call_tool.py <server_url> <blackboard_token> get_my_courses
    python scripts/call_tool.py <server_url> <blackboard_token> get_assignment_due_dates
    python scripts/call_tool.py <server_url> <blackboard_token> get_outstanding_assignments course_id=_456_1
    python scripts/call_tool.py <server_url> <blackboard_token> lookup_user identifier=jsmith

<server_url> includes the /mcp path, e.g. http://localhost:8080/mcp
<blackboard_token> is a real Blackboard access token (this is a live call to Blackboard).
"""
import asyncio
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def _parse_args(pairs: list[str]) -> dict:
    args: dict = {}
    for p in pairs:
        if "=" not in p:
            continue
        k, v = p.split("=", 1)
        args[k] = v
    return args


async def main() -> None:
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(2)
    url, token, tool = sys.argv[1], sys.argv[2], sys.argv[3]
    tool_args = _parse_args(sys.argv[4:])
    headers = {"Authorization": f"Bearer {token}"}

    async with streamablehttp_client(url, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            if tool == "--list":
                tools = await session.list_tools()
                for t in tools.tools:
                    print(f"- {t.name}: {t.description.splitlines()[0] if t.description else ''}")
                return
            result = await session.call_tool(tool, tool_args)
            for c in result.content:
                print(getattr(c, "text", c))


if __name__ == "__main__":
    asyncio.run(main())
