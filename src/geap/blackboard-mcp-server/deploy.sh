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
#   PROJECT_ID=<your-project> REGION=us-central1 \
#   BLACKBOARD_BASE_URL=https://yourinstitution.blackboard.com ./deploy.sh
set -euo pipefail

PROJECT_ID="${PROJECT_ID:?set PROJECT_ID}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-blackboard-mcp}"
BLACKBOARD_BASE_URL="${BLACKBOARD_BASE_URL:?set BLACKBOARD_BASE_URL to your Blackboard instance URL}"

echo "Deploying ${SERVICE} to project=${PROJECT_ID} region=${REGION}"
gcloud run deploy "${SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --source=. \
  --allow-unauthenticated \
  --set-env-vars="BLACKBOARD_BASE_URL=${BLACKBOARD_BASE_URL},MCP_PATH=/mcp" \
  --port=8080

echo
echo "Deployed. MCP endpoint:"
echo "  URL=\$(gcloud run services describe ${SERVICE} --project=${PROJECT_ID} --region=${REGION} --format='value(status.url)')"
echo "  echo \$URL/mcp"
