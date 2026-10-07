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
and sets `BLACKBOARD_BASE_URL`, `MCP_PATH=/mcp` and (if provided)
`ALLOWED_CLIENT_IDS` as env vars on the service.

**`ALLOWED_CLIENT_IDS` (optional)** = your Blackboard REST application key (the
OAuth client ID you enter in Gemini Enterprise).
- **Unset (default):** the `/oauth2/token` proxy forwards every request;
  Blackboard still validates the client ID / secret.
- **Set:** the proxy only forwards those IDs and returns `401 invalid_client`
  for anything else without contacting Blackboard, so it can't be used as an
  open relay. Recommended once the setup is working; just redeploy with it set.

The value is public (it appears in the authorization URL). Comma-separate
several (e.g. staging and prod app keys).

> `--allow-unauthenticated` is intentional: the endpoint must be reachable, but
> every tool call requires a per-user Blackboard token in the `Authorization`
> header (GE supplies it), and Blackboard enforces access.

### Staging and production side by side (recommended)

Deploy one service per Blackboard instance and create one GE connector for each.
Each service is always paired with the connector that points at the same
Blackboard, so you never have to switch anything:

```bash
SERVICE=blackboard-mcp-stg BLACKBOARD_BASE_URL=https://<staging-host> \
  PROJECT_ID=<p> REGION=<r> ./deploy.sh
SERVICE=blackboard-mcp     BLACKBOARD_BASE_URL=https://<prod-host> \
  PROJECT_ID=<p> REGION=<r> ./deploy.sh
# add ALLOWED_CLIENT_IDS=<app-key> to either command to lock its proxy down
```

> Changing `BLACKBOARD_BASE_URL` on a running service does **not** switch
> environments on its own: the GE connector's Authorization URL (which can't be
> edited after creation) and users' stored tokens still belong to the old
> instance.

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
| Token URL | `<URL>/oauth2/token` (points to this server's OAuth proxy endpoint) |
| Client ID / Secret | your Blackboard REST application key / secret |
| Scopes | `read offline` |
| HTTP Basic Auth | optional (the `/oauth2/token` proxy automatically handles Basic Auth) |

> **Why Token URL points to `<URL>/oauth2/token` instead of Blackboard directly:**
> Blackboard Learn strictly enforces HTTP Basic Auth (`Authorization: Basic <base64>`) on its token endpoint.
> Due to GE issue b/553520141, Gemini Enterprise passes client credentials in the POST body for custom MCP servers.
> The `/oauth2/token` endpoint bridges this by receiving GE's parameters, adding the HTTP Basic Auth header, and proxying to Blackboard.


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
