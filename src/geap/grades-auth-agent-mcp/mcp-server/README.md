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

## Configuration

| Var | Default | Purpose |
|---|---|---|
| `REST_BASE_URL` | deployed REST URL | the grades service to proxy to |
| `MCP_PATH` | `/mcp` | Streamable HTTP endpoint path |
| `PORT` | `8080` | listen port (Cloud Run sets this) |
| `REQUEST_TIMEOUT` | `15` | REST call timeout (seconds) |

## Run locally

```bash
cd mcp-server
pip install -r requirements-dev.txt

# Point at a local REST service, or omit to use the deployed one
export REST_BASE_URL=http://localhost:8080
uvicorn app.server:app --host 0.0.0.0 --port 8080
# MCP endpoint: http://localhost:8080/mcp
```

Then call a tool with the smoke client (mint tokens from the REST service):

```bash
TOKEN=$(python ../rest-service/scripts/generate_token.py alice)
python scripts/call_tool.py http://localhost:8080/mcp "$TOKEN" --list
python scripts/call_tool.py http://localhost:8080/mcp "$TOKEN" get_my_grades

PROF=$(python ../rest-service/scripts/generate_token.py dr_reed)
python scripts/call_tool.py http://localhost:8080/mcp "$PROF" get_course_grades course_code=CHEM-101
python scripts/call_tool.py http://localhost:8080/mcp "$PROF" enter_grade course_code=CHEM-101 student_id=bob score=91
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest        # token-forwarding + error-mapping unit tests (httpx MockTransport)
```

## Deploy to Cloud Run

```bash
PROJECT_ID=default-project-alpha-1 REGION=us-central1 \
REST_BASE_URL=https://grades-rest-47444200274.us-central1.run.app \
./deploy.sh
```

Deployed `--allow-unauthenticated` (Streamable HTTP requires it be reachable;
the forwarded user token + REST authz are the real gate). Endpoint: `<url>/mcp`.

## Next: register in the GEAP Agent Registry

Once deployed, register `<url>/mcp` (HTTPS, StreamableHTTP) in the Gemini
Enterprise **Agent Registry** and import it into your GE app with OAuth 2.0 so
the platform forwards the user's token. See the project notes for the full flow.

## Auth layers (recap)

1. **Platform** — Cloud Run reachability (open for the demo).
2. **User token** — forwarded by this server to REST for per-user authz (the OBO
   guarantee). Later hardening: also require the agent's **service-account**
   identity (IAM invoker) so only authorized agents can reach this server.
