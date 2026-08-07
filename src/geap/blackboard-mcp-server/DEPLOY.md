# Deploying the Blackboard MCP Server

Source-based Cloud Run deploy. Nothing sensitive is committed — the Blackboard
URL is passed at deploy time, and the per-user token comes from Gemini Enterprise
at runtime (never in the image).

## 1. One-time setup (skip if already done)

```bash
gcloud auth login
gcloud config set project <YOUR_PROJECT_ID>
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com
```

**Deployer IAM roles** (grant once, by a Project Owner / IAM Admin):
`roles/run.admin`, `roles/cloudbuild.builds.editor`, `roles/artifactregistry.admin`,
`roles/storage.admin`, and `roles/iam.serviceAccountUser` on the runtime service
account. See `../grades-auth-agent-mcp/rest-service/grant-iam.sh` for a ready
script (set `PROJECT` and `MEMBER`).

## 2. Deploy

```bash
cd src/geap/blackboard-mcp-server
chmod +x deploy.sh            # first time only

PROJECT_ID=<YOUR_PROJECT_ID> \
REGION=us-central1 \
BLACKBOARD_BASE_URL=https://yourinstitution.blackboard.com \
./deploy.sh
```

This runs `gcloud run deploy blackboard-mcp --source . --allow-unauthenticated`
and sets `BLACKBOARD_BASE_URL` + `MCP_PATH=/mcp` as env vars on the service.

> `--allow-unauthenticated` is intentional: the endpoint must be reachable, but
> every tool call requires a per-user Blackboard token in the `Authorization`
> header (GE supplies it), and Blackboard enforces access.

## 3. Get the endpoint

```bash
URL=$(gcloud run services describe blackboard-mcp \
  --project=<YOUR_PROJECT_ID> --region=us-central1 \
  --format='value(status.url)')
echo "$URL/mcp"
```

## 4. Smoke-test the deployed server

```bash
# from your virtualenv, e.g. after:
#   python -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt
python scripts/call_tool.py "$URL/mcp" "<a-real-blackboard-token>" --list
python scripts/call_tool.py "$URL/mcp" "<a-real-blackboard-token>" get_my_courses
```

A real Blackboard access token is needed here because the call hits your live
Blackboard instance. (Tool listing works without a valid token; tool calls don't.)

## 5. Register in Gemini Enterprise (custom MCP server, OAuth 2.0)

In the GE connector's Authentication settings choose **OAuth 2.0** and set:

| GE field | Value |
|---|---|
| MCP Server URL | `<URL>/mcp` (from step 3) |
| Authorization URL | `https://<blackboard>/learn/api/public/v1/oauth2/authorizationcode` |
| Token URL | `https://<blackboard>/learn/api/public/v1/oauth2/token` |
| Client ID / Secret | your Blackboard REST application key / secret |
| Scopes | e.g. `read` (add `offline` for refresh tokens) |
| PKCE / HTTP Basic | per what your Blackboard instance supports |

GE then runs the per-user OAuth flow and forwards each user's Blackboard token to
the server. The Client ID/Secret live in GE — never in this repo.

## Re-deploying after changes

Just re-run the same command from step 2 — it ships a new revision:

```bash
PROJECT_ID=<YOUR_PROJECT_ID> REGION=us-central1 \
BLACKBOARD_BASE_URL=https://yourinstitution.blackboard.com ./deploy.sh
```

## Reminders

- **Never** pass `BLACKBOARD_ACCESS_TOKEN` to Cloud Run — it's a local-dev-only
  fallback. In production the token always arrives per-request in the header.
- `.env` is git-ignored; keep the base URL / any tokens there for local runs only.
- Deploy from this folder (`blackboard-mcp-server/`) so `--source .` picks up the
  `Dockerfile` and `app/`.
