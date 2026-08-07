# Grades MCP Server

The **on-behalf-of hop** in the chain:

```
Agent ──▶ [ Grades MCP Server ] ──▶ Grades REST Service
             forwards the user's       validates token +
             bearer token verbatim     enforces authorization
```

FastMCP over **Streamable HTTP** (`stateless_http`), exposing grade tools. It
holds no data and makes **no authorization decisions** — it extracts the caller's
`Authorization` header from the live MCP request and relays it to the REST
service, which is the authority. In Gemini Enterprise that header is the user's
OAuth token, which the platform forwards automatically.

This README is a build-and-deploy-your-own guide. Substitute your own values for
the `<PLACEHOLDERS>` — in particular, point it at **your** deployed REST service.

---

## Prerequisites

- **Python 3.12+**
- **A deployed Grades REST service** (see `../rest-service`) — you'll need its URL
  and the `JWT_SECRET` you deployed it with (to mint test tokens).
- **Google Cloud SDK** authenticated, with a project that has these APIs on:
  ```bash
  gcloud config set project <YOUR_PROJECT_ID>
  gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
                         artifactregistry.googleapis.com
  ```
- Deployer IAM roles: same set as the REST service (`run.admin`,
  `cloudbuild.builds.editor`, `artifactregistry.admin`, `storage.admin`,
  `iam.serviceAccountUser` on the runtime SA — see `../rest-service/grant-iam.sh`).

## Tools

| Tool | REST call | Intended caller |
|---|---|---|
| `whoami()` | `GET /me` | anyone — proves the forwarded identity |
| `get_my_grades()` | `/me` → `GET /students/{sub}/grades` | student |
| `get_student_grades(student_id)` | `GET /students/{id}/grades` | professor / admin |
| `get_course_grades(course_code)` | `GET /courses/{code}/grades` | owning professor / admin |
| `list_my_courses()` | `GET /courses` | anyone (filtered) |
| `enter_grade(course_code, student_id, score)` | `POST /courses/{code}/grades` | owning professor / admin |

Downstream 401/403/404 are returned as `{"error", "status"}` so the agent can
explain *why* (e.g. "You do not teach this course").

## Project layout

```
mcp-server/
├── app/
│   ├── server.py     # FastMCP + tools; extracts & forwards the user token
│   ├── rest_client.py# async httpx client — relays Authorization verbatim
│   ├── config.py     # REST_BASE_URL, MCP_PATH, PORT
│   └── __init__.py
├── scripts/call_tool.py  # MCP smoke client
├── tests/            # token-forwarding + error-mapping unit tests
├── Dockerfile
├── deploy.sh
└── requirements*.txt
```

## Configuration

| Var | Default | Purpose |
|---|---|---|
| `REST_BASE_URL` | *(a demo URL)* | **your** grades REST service — set this |
| `MCP_PATH` | `/mcp` | Streamable HTTP endpoint path |
| `PORT` | `8080` | listen port (Cloud Run sets this) |
| `REQUEST_TIMEOUT` | `15` | REST call timeout (seconds) |

> `app/config.py` ships with a default `REST_BASE_URL`. For your own deployment,
> **always override it** (env var below, or edit the default) to point at your REST
> service — otherwise you'll call someone else's.

---

## Run locally

```bash
cd mcp-server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# Point at YOUR REST service (local or deployed)
export REST_BASE_URL=<YOUR_REST_URL>          # e.g. http://localhost:8080
uvicorn app.server:app --host 0.0.0.0 --port 8080
# MCP endpoint: http://localhost:8080/mcp
```

Call a tool with the smoke client. Mint tokens from the REST service using the
**same `JWT_SECRET`** that service was deployed with:

```bash
GEN=../rest-service/scripts/generate_token.py
TOKEN=$(JWT_SECRET=<YOUR_SECRET> python $GEN alice)
python scripts/call_tool.py http://localhost:8080/mcp "$TOKEN" --list
python scripts/call_tool.py http://localhost:8080/mcp "$TOKEN" get_my_grades

PROF=$(JWT_SECRET=<YOUR_SECRET> python $GEN dr_reed)
python scripts/call_tool.py http://localhost:8080/mcp "$PROF" get_course_grades course_code=CHEM-101
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest        # token-forwarding + error-mapping (httpx MockTransport; no network)
```

---

## Deploy to Cloud Run

```bash
PROJECT_ID=<YOUR_PROJECT_ID> REGION=<YOUR_REGION> \
REST_BASE_URL=<YOUR_REST_URL> \
./deploy.sh
```

`deploy.sh` runs `gcloud run deploy grades-mcp --source . --allow-unauthenticated`
and injects `REST_BASE_URL`. Deployed open because Streamable HTTP must be
reachable; the forwarded user token + REST authz are the real gate.

Get your MCP endpoint:

```bash
URL=$(gcloud run services describe grades-mcp --project=<YOUR_PROJECT_ID> \
  --region=<YOUR_REGION> --format='value(status.url)')
echo "$URL/mcp"
```

Smoke-test the deployed server:

```bash
TOKEN=$(JWT_SECRET=<YOUR_SECRET> python ../rest-service/scripts/generate_token.py alice)
python scripts/call_tool.py "$URL/mcp" "$TOKEN" get_my_grades
```

---

## Connect from MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```
- Transport: **Streamable HTTP**
- URL: `<YOUR_MCP_URL>/mcp`
- Authentication → **Bearer Token**: a JWT from `generate_token.py` (required for
  tool calls; `tools/list` works without one)

## Next: register in the GEAP Agent Registry

Once deployed, register `<YOUR_MCP_URL>/mcp` (HTTPS, StreamableHTTP) in the Gemini
Enterprise **Agent Registry** and import it into your GE app with OAuth 2.0 so the
platform forwards the user's token. To validate those real tokens, switch the REST
service to `AUTH_MODE=gcp` (JWKS). See the top-level README.

## Auth layers (recap)

1. **Platform** — Cloud Run reachability (open for the demo).
2. **User token** — forwarded by this server to REST for per-user authz (the OBO
   guarantee). Later hardening: also require the agent's **service-account**
   identity (IAM invoker) so only authorized agents can reach this server.
