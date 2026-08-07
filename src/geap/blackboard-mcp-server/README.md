# Blackboard MCP Server

A FastMCP server (Streamable HTTP) that exposes **Blackboard Learn** data as MCP
tools. It is a **stateless pass-through**: it reads the caller's Blackboard access
token from the request `Authorization` header and forwards it to the Blackboard
REST API. **Blackboard is the sole authority** for what each token can see.

```
Agent / Gemini Enterprise ──▶ [ Blackboard MCP Server ] ──▶ Blackboard Learn REST API
   forwards the user's           forwards the token             enforces access per token
   Blackboard OAuth token        verbatim; no auth logic
```

No secrets, URLs, or tokens are committed — everything sensitive comes from the
environment / a git-ignored `.env`, or (in production) from Gemini Enterprise.

## How auth works (no token minting here)

This server **never** holds the OAuth Client ID/Secret and **never** mints tokens.
In Gemini Enterprise, the connector is configured with Blackboard's OAuth details
(Authorization URL, Token URL, Client ID/Secret, Scopes). GE runs the OAuth 2.0
Authorization Code flow: each user authorizes **once** (logging into Blackboard),
GE stores that user's Blackboard token, and forwards it on every request as
`Authorization: Bearer …`. This server just consumes it.

Because it's a 3-legged (per-user) token, the server identifies the user via the
`/users/me` family of endpoints — no user id is passed in — and Blackboard scopes
every response to that user. Different users → different forwarded tokens →
different data, automatically. The server keeps **no per-user state**.

## Tools

| Tool | Blackboard endpoint | Notes |
|---|---|---|
| `get_my_courses()` | `GET /learn/api/public/v1/users/me/courses?expand=course` | current user's courses |
| `get_assignment_due_dates(course_id?)` | `GET /learn/api/public/v1/calendars/items?type=Course` | optionally scoped to a course |
| `get_outstanding_assignments(course_id)` | gradebook columns → `…/attempts?status=NeedsGrading` | batched concurrent queries; needs instructor access |
| `lookup_user(identifier)` | `GET /learn/api/public/v1/users?userName=…` | needs admin access |
| `get_course_enrollments(course_id)` | `GET /learn/api/public/v1/courses/{id}/users?expand=user` | needs appropriate access |

All tools are exposed to everyone; **Blackboard enforces access** — a call the
token isn't permitted for returns its own error, surfaced as `{"error","status"}`
(e.g. a student calling `lookup_user` gets a 403).

## Prerequisites

- **Python 3.12+**
- A **Blackboard Learn** instance URL and, for local testing, a valid access token.
- For deploying: **Google Cloud SDK** authenticated, a project with these APIs on:
  ```bash
  gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
                         artifactregistry.googleapis.com --project <YOUR_PROJECT_ID>
  ```
  and the usual Cloud Run deploy roles (`run.admin`, `cloudbuild.builds.editor`,
  `artifactregistry.admin`, `storage.admin`, `iam.serviceAccountUser`).

## Configuration (all via env / `.env`)

| Var | Purpose |
|---|---|
| `BLACKBOARD_BASE_URL` | your Blackboard instance URL (required) |
| `BLACKBOARD_ACCESS_TOKEN` | **local/dev only** fallback token when no header is present; leave empty in prod |
| `MCP_PATH` | Streamable HTTP path (default `/mcp`) |
| `PORT` | listen port (Cloud Run sets this) |
| `REQUEST_TIMEOUT` | Blackboard call timeout, seconds (default 30) |
| `GRADING_BATCH_SIZE` | concurrency for gradebook fan-out (default 5) |

Copy `.env.example` → `.env` and fill in. `.env` is git-ignored.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env
# edit .env: set BLACKBOARD_BASE_URL and (for local testing) BLACKBOARD_ACCESS_TOKEN
set -a && source .env && set +a          # export the vars

uvicorn app.server:app --host 0.0.0.0 --port 8080
# MCP endpoint: http://localhost:8080/mcp
```

Call a tool (this makes a real call to your Blackboard instance):

```bash
TOKEN=<a-real-blackboard-access-token>
python scripts/call_tool.py http://localhost:8080/mcp "$TOKEN" --list
python scripts/call_tool.py http://localhost:8080/mcp "$TOKEN" get_my_courses
python scripts/call_tool.py http://localhost:8080/mcp "$TOKEN" get_outstanding_assignments course_id=_456_1
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest        # token forwarding, error mapping, batching (httpx MockTransport; no network)
```

## Deploy to Cloud Run

```bash
PROJECT_ID=<YOUR_PROJECT_ID> REGION=<YOUR_REGION> \
BLACKBOARD_BASE_URL=https://yourinstitution.blackboard.com \
./deploy.sh
```

`BLACKBOARD_BASE_URL` is passed at deploy time from your environment — not stored
in the repo. Get the endpoint:

```bash
URL=$(gcloud run services describe blackboard-mcp --project <YOUR_PROJECT_ID> \
  --region <YOUR_REGION> --format='value(status.url)')
echo "$URL/mcp"
```

## Register in Gemini Enterprise (custom MCP server, OAuth 2.0)

In the GE connector's Authentication settings, choose **OAuth 2.0** and set:

| GE field | Value |
|---|---|
| MCP Server URL | your deployed `…/mcp` |
| Authorization URL | `https://<blackboard>/learn/api/public/v1/oauth2/authorizationcode` |
| Token URL | `https://<blackboard>/learn/api/public/v1/oauth2/token` |
| Client ID / Secret | your Blackboard REST application key / secret |
| Scopes | e.g. `read` (add `offline` for refresh tokens) |
| PKCE / HTTP Basic | per what your Blackboard instance supports |

GE then handles the per-user OAuth flow and forwards each user's Blackboard token
to this server. The Client ID/Secret live in GE — never in this repo.

## Security notes

- **Stateless & per-request:** identity comes from the forwarded token on every
  call; no global/per-user state, safe for many concurrent users on one instance.
- **Nothing sensitive committed:** base URL, tokens, and OAuth secrets are all
  external (`.env` / GE config), and `.env` is git-ignored.
- **`BLACKBOARD_ACCESS_TOKEN` is dev-only** — in production every request must
  carry the user's token in the header.
