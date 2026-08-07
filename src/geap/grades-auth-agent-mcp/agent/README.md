# Grades Assistant (ADK Agent)

The top of the chain — an **ADK 2.x** agent that answers grade questions **on
behalf of the signed-in user**:

```
[ Grades Assistant (ADK) ] ──▶ MCP Server ──▶ REST Service
   McpToolset.header_provider     forwards         validates token +
   injects the user's JWT         the token        enforces authorization
```

This README is a build-and-run-your-own guide. Substitute your own values for the
`<PLACEHOLDERS>` — in particular, point it at **your** deployed MCP server.

## How on-behalf-of works here

`agent.py` builds an `McpToolset` pointed at the MCP server with a
**`header_provider`** callback. On every MCP call, that callback reads the user's
JWT from the current **session state** (`user_jwt`) and sends it as
`Authorization: Bearer …`. The MCP server relays it to REST, which enforces
per-user rules. **Same agent, different user token → different data.**

In Gemini Enterprise this is even simpler: the platform forwards the user's OAuth
token automatically, so you'd drop the manual token injection.

---

## Prerequisites

- **Python 3.12+**
- **A deployed MCP server** (see `../mcp-server`) — you'll need its `/mcp` URL.
- **The REST service's `JWT_SECRET`** — `run.py` mints demo tokens with it.
- **Model access** for Gemini (pick one):
  - **Vertex AI** — enable the API and grant your account `roles/aiplatform.user`:
    ```bash
    gcloud services enable aiplatform.googleapis.com --project <YOUR_PROJECT_ID>
    gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
      --member="user:<YOU>@<YOUR_DOMAIN>" --role="roles/aiplatform.user"
    ```
  - **Google AI Studio** — get an API key from https://aistudio.google.com/apikey

## Setup

```bash
cd agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # installs google-adk (pulls in mcp, google-genai)
cp .env.example .env                    # then edit for your project + MCP URL
```

Edit `.env`:

```bash
# Model auth — pick ONE
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>
GOOGLE_CLOUD_LOCATION=<YOUR_REGION>
# GOOGLE_API_KEY=<your-aistudio-key>    # (use instead of the Vertex lines)

# Agent wiring
MCP_URL=<YOUR_MCP_URL>/mcp
MODEL=gemini-2.5-flash                  # any Gemini model your account can call
```

> `config.py` ships with a default `MCP_URL`. Override it (via `.env`/env or by
> editing the default) to point at **your** MCP server.

## Run

Verify the ADK↔MCP wiring (lists the MCP tools; no model/LLM needed):

```bash
python run.py --list-tools
```

Talk to it as different users. `run.py` mints a token via the REST service's
`generate_token.py` and injects it into session state, so set the matching
`JWT_SECRET`:

```bash
export JWT_SECRET=<YOUR_REST_SECRET>

python run.py --user alice   --prompt "What are my grades?"
python run.py --user dr_reed --prompt "Show me the grades for CHEM-101"
python run.py --user alice   --prompt "Look up grades for student id bob"  # refused (403)
python run.py --user dr_reed --prompt "Give bob 95 in CHEM-101"            # allowed
```

Bring your own token instead of a known user:

```bash
python run.py --token "$SOME_JWT" --prompt "..."
```

## ADK dev UI / CLI

These load `.env` automatically and manage their own sessions, so pass a token via
`USER_JWT`:

```bash
export USER_JWT=$(JWT_SECRET=<YOUR_REST_SECRET> ../rest-service/scripts/generate_token.py dr_reed)
adk web           # browser chat; pick the "agent" app
adk run agent     # terminal chat (run from the parent grades-auth-agent-mcp/ dir)
```

## Files

| File | Purpose |
|---|---|
| `agent.py` | defines `root_agent` + the `McpToolset` with token-forwarding `header_provider` |
| `config.py` | `MCP_URL`, `MODEL`, fallback `USER_JWT` |
| `run.py` | CLI runner: mint/accept a token, run a prompt, show tool calls |
| `.env.example` | model-auth + wiring template |

## Customize

- **Different model:** set `MODEL` (must be enabled for your account/region).
- **Different behavior:** edit `INSTRUCTION` in `agent.py`.
- **More/other tools:** they come from the MCP server — add them there and the
  agent picks them up automatically.

## Notes

- The agent makes **no** authorization decisions — it only forwards identity. All
  enforcement lives in the REST service; the MCP server is a pass-through.
- Tokens default to a 60-min TTL; `run.py --user` mints a fresh one each run.
- `adk web` needs `node` + a browser; if headless, use `run.py`.
