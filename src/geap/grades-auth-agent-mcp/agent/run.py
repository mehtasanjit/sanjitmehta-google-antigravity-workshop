#!/usr/bin/env python3
"""Run the Grades Assistant from the command line, as a chosen user.

The user's JWT is placed in the session state so the MCP toolset forwards it —
demonstrating on-behalf-of: the same agent returns different data per identity.

Examples:
    # verify ADK <-> MCP wiring (no LLM needed):
    python run.py --list-tools

    # run as a student:
    python run.py --user alice   --prompt "What are my grades?"

    # run as a professor:
    python run.py --user dr_reed --prompt "Show me the grades for CHEM-101"

    # a student trying to peek at someone else (should be refused via 403):
    python run.py --user alice   --prompt "What are Bob's grades?"

    # bring your own token:
    python run.py --token "$JWT" --prompt "..."

Auth for the model (pick one, e.g. in agent/.env):
    Vertex:  GOOGLE_GENAI_USE_VERTEXAI=TRUE, GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION
    Studio:  GOOGLE_API_KEY=...
"""
import argparse
import asyncio
import subprocess
import sys
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parent
PACKAGE_PARENT = AGENT_DIR.parent
# generate_token.py lives in the sibling rest-service.
TOKEN_GEN = AGENT_DIR.parent / "rest-service" / "scripts" / "generate_token.py"

# Import the `agent` package (not this script's dir): put the parent on the path
# and drop the script dir so `agent` resolves to the package, keeping its
# relative imports (`from . import config`) working.
if str(AGENT_DIR) in sys.path:
    sys.path.remove(str(AGENT_DIR))
sys.path.insert(0, str(PACKAGE_PARENT))

# Load agent/.env if python-dotenv is available (ADK CLI does this automatically).
try:
    from dotenv import load_dotenv

    load_dotenv(AGENT_DIR / ".env")
except Exception:
    pass


def mint_token(user: str) -> str:
    if not TOKEN_GEN.exists():
        sys.exit(f"Token generator not found at {TOKEN_GEN}")
    out = subprocess.run(
        [sys.executable, str(TOKEN_GEN), user],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        sys.exit(f"Failed to mint token for {user}: {out.stderr.strip()}")
    return out.stdout.strip()


async def list_tools() -> None:
    from agent.agent import grades_toolset

    tools = await grades_toolset.get_tools()
    print(f"MCP tools visible to the agent ({len(tools)}):")
    for t in tools:
        print(f"  - {t.name}")
    await grades_toolset.close()


async def chat(token: str, user_id: str, prompt: str) -> None:
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    from agent.agent import root_agent

    runner = InMemoryRunner(agent=root_agent, app_name="grades")
    # The user's token rides in session state -> header_provider forwards it.
    await runner.session_service.create_session(
        app_name="grades", user_id=user_id, session_id="s1",
        state={"user_jwt": token},
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    print(f"[user={user_id}] {prompt}\n")
    async for event in runner.run_async(
        user_id=user_id, session_id="s1", new_message=message
    ):
        # Surface tool calls so the OBO hop is visible.
        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "function_call", None):
                    fc = part.function_call
                    print(f"  → tool call: {fc.name}({dict(fc.args or {})})")
                elif getattr(part, "function_response", None):
                    print(f"  ← tool result: {part.function_response.name} returned")
        if event.is_final_response() and event.content and event.content.parts:
            text = "".join(p.text or "" for p in event.content.parts)
            if text:
                print(f"\nAssistant: {text}")

    # Clean up MCP connections held by the toolset.
    from agent.agent import grades_toolset
    await grades_toolset.close()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--user", help="known user to mint a token for (alice/bob/dr_reed/admin)")
    ap.add_argument("--token", help="explicit JWT (overrides --user)")
    ap.add_argument("--prompt", help="what to ask the assistant")
    ap.add_argument("--list-tools", action="store_true", help="just list MCP tools and exit")
    args = ap.parse_args()

    if args.list_tools:
        asyncio.run(list_tools())
        return

    if not args.prompt:
        ap.error("--prompt is required (or use --list-tools)")
    token = args.token or (mint_token(args.user) if args.user else None)
    if not token:
        ap.error("provide --user or --token")
    user_id = args.user or "byo-token-user"

    try:
        asyncio.run(chat(token, user_id, args.prompt))
    except Exception as e:  # surface model-auth issues with a hint
        print(f"\nERROR: {e}", file=sys.stderr)
        print(
            "\nIf this is a model/permission error, configure model auth in "
            "agent/.env (Vertex: GOOGLE_GENAI_USE_VERTEXAI=TRUE + project/location, "
            "or GOOGLE_API_KEY for AI Studio).",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
