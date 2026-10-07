#!/usr/bin/env bash
# Deploy the Blackboard MCP server to Cloud Run (source-based build).
#
# Deployed --allow-unauthenticated: the server is reachable, but every tool call
# requires a per-user Blackboard token forwarded in the Authorization header
# (Gemini Enterprise supplies it), and Blackboard enforces access. No secrets are
# baked into the image; BLACKBOARD_BASE_URL is provided at deploy time from your
# environment (not committed).
#
# Usage:
#   PROJECT_ID=<your-project> REGION=asia-southeast1 \
#   SERVICE=blackboard-mcp \
#   BLACKBOARD_BASE_URL=https://yourinstitution.blackboard.com \
#   ALLOWED_CLIENT_IDS=<blackboard-app-key>[,<another-app-key>] \   # optional
#   ./deploy.sh
#
# ALLOWED_CLIENT_IDS (optional) = the Blackboard REST application key(s) (OAuth
# client_id) that the /oauth2/token proxy may forward. Public, not a secret.
# Leave unset to forward every request (Blackboard still validates credentials);
# set it later to lock the proxy to your app(s).
set -euo pipefail

PROJECT_ID="${PROJECT_ID:?set PROJECT_ID}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-blackboard-mcp}"
BLACKBOARD_BASE_URL="${BLACKBOARD_BASE_URL:?set BLACKBOARD_BASE_URL to your Blackboard instance URL}"
ALLOWED_CLIENT_IDS="${ALLOWED_CLIENT_IDS:-}"

echo "Deploying ${SERVICE} to project=${PROJECT_ID} region=${REGION}"
if [[ -z "${ALLOWED_CLIENT_IDS}" ]]; then
  echo "Note: ALLOWED_CLIENT_IDS not set - /oauth2/token will forward all client IDs."
fi
# '^|^' switches gcloud's env-var delimiter to '|' so ALLOWED_CLIENT_IDS may
# contain commas.
gcloud run deploy "${SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --source=. \
  --allow-unauthenticated \
  --set-env-vars="^|^BLACKBOARD_BASE_URL=${BLACKBOARD_BASE_URL}|MCP_PATH=/mcp|ALLOWED_CLIENT_IDS=${ALLOWED_CLIENT_IDS}" \
  --port=8080

echo
echo "Deployed. Endpoints:"
echo "  URL=\$(gcloud run services describe ${SERVICE} --project=${PROJECT_ID} --region=${REGION} --format='value(status.url)')"
echo "  echo \$URL/mcp            # MCP Server URL in Gemini Enterprise"
echo "  echo \$URL/oauth2/token   # Token URL in Gemini Enterprise"
