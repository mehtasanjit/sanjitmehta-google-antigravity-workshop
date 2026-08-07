# Grades Assistant (ADK Agent)

The top of the chain — an **ADK 2.x** agent that answers grade questions **on
behalf of the signed-in user**:

```
[ Grades Assistant (ADK) ] ──▶ MCP Server ──▶ REST Service
   McpToolset.header_provider     forwards         validates token +
   injects the user's JWT         the token        enforces authorization
```

## How on-behalf-of works here

`agent.py` builds an `McpToolset` pointed at the deployed MCP server with a
**`header_provider`** callback. On every MCP call, that callback reads the user's
JWT from the current **session state** (`user_jwt`) and sends it as
`Authorization: Bearer …`. The MCP server relays it to the REST service, which
enforces per-user rules. **Same agent, different user token → different data.**

In Gemini Enterprise this is even simpler: the platform forwards the user's OAuth
token automatically, so you'd drop the manual token injection.

## Setup

```bash
cd agent
pip install -r requirements.txt
cp .env.example .env      # then set model auth (Vertex or GOOGLE_API_KEY)
```

Model auth (pick one, in `.env`):
- **Vertex:** `GOOGLE_GENAI_USE_VERTEXAI=TRUE`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`
- **AI Studio:** `GOOGLE_API_KEY=...`

## Run

Verify the ADK↔MCP wiring (no model/LLM needed — lists the MCP tools):
```bash
python run.py --list-tools
```

Talk to it as different users (tokens are minted via the REST service's
`generate_token.py` and injected into session state):
```bash
python run.py --user alice   --prompt "What are my grades?"
python run.py --user dr_reed --prompt "Show me the grades for CHEM-101"
python run.py --user alice   --prompt "What are Bob's grades?"   # refused (403)
python run.py --user dr_reed --prompt "Give Bob 95 in CHEM-101"  # allowed
```

Or use the ADK dev UI / CLI (loads `.env` automatically). For these you provide a
token via `USER_JWT` since they manage their own sessions:
```bash
export USER_JWT=$(../rest-service/scripts/generate_token.py dr_reed)
adk web        # browser UI, pick the "agent" app
adk run agent  # terminal chat
```

## Files

| File | Purpose |
|---|---|
| `agent.py` | defines `root_agent` + the `McpToolset` with token-forwarding `header_provider` |
| `config.py` | `MCP_URL`, `MODEL`, fallback `USER_JWT` |
| `run.py` | CLI runner: mint/accept a token, run a prompt, show tool calls |
| `.env.example` | model-auth + wiring template |

## Notes
- Tokens default to a 60-min TTL. `run.py --user` mints a fresh one each run.
- The agent makes **no** authorization decisions — it only forwards identity. All
  enforcement lives in the REST service; the MCP server is a pass-through.
