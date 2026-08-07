#!/usr/bin/env python3
"""Smoke-test MCP client: connect over Streamable HTTP, forward a token, call a tool.

Usage:
    python scripts/call_tool.py <server_url> <jwt> --list
    python scripts/call_tool.py <server_url> <jwt> whoami
    python scripts/call_tool.py <server_url> <jwt> get_my_grades
    python scripts/call_tool.py <server_url> <jwt> get_course_grades course_code=CHEM-101
    python scripts/call_tool.py <server_url> <jwt> enter_grade course_code=CHEM-101 student_id=bob score=91

The <server_url> should include the /mcp path, e.g.
    http://localhost:8080/mcp
    https://grades-mcp-xxxxx.us-central1.run.app/mcp
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
        # best-effort numeric coercion for convenience (e.g. score=91)
        try:
            v = float(v) if "." in v else int(v)
        except ValueError:
            pass
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
