#!/usr/bin/env bash
# Deploy the grades MCP server to Cloud Run (source-based build).
#
# Deployed --allow-unauthenticated for the demo: Gemini Enterprise forwards the
# user's OAuth token, and the REST service is the real gate. Harden later by
# requiring the agent's service-account identity (IAM invoker) in front.
#
# Usage:
#   PROJECT_ID=my-proj REGION=us-central1 \
#   REST_BASE_URL=https://grades-rest-XXXX.us-central1.run.app ./deploy.sh
set -euo pipefail

PROJECT_ID="${PROJECT_ID:?set PROJECT_ID}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-grades-mcp}"
REST_BASE_URL="${REST_BASE_URL:-https://grades-rest-47444200274.us-central1.run.app}"

echo "Deploying ${SERVICE} to project=${PROJECT_ID} region=${REGION}"
echo "  -> REST_BASE_URL=${REST_BASE_URL}"
gcloud run deploy "${SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --source=. \
  --allow-unauthenticated \
  --set-env-vars="REST_BASE_URL=${REST_BASE_URL},MCP_PATH=/mcp" \
  --port=8080

echo
echo "Deployed. MCP endpoint:"
echo "  URL=\$(gcloud run services describe ${SERVICE} --project=${PROJECT_ID} --region=${REGION} --format='value(status.url)')"
echo "  echo \$URL/mcp"
