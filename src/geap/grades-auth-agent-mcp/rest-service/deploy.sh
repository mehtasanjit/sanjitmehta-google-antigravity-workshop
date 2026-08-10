#!/usr/bin/env bash
# Deploy the grades REST service to Cloud Run (source-based build, no local Docker).
#
# The service is deployed --allow-unauthenticated ON PURPOSE: platform (IAM) auth
# gates on a *Google* identity, which is NOT the per-user identity our OBO chain
# needs. Our own JWT layer (validated in app/auth.py) is the real gate. See README.
#
# Usage:
#   PROJECT_ID=my-proj REGION=us-central1 ./deploy.sh
set -euo pipefail

PROJECT_ID="${PROJECT_ID:?set PROJECT_ID}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-grades-rest}"

# The HS256 secret is sourced from Secret Manager, NOT shipped as a plaintext env
# var (a public/weak secret makes the token signature forgeable). The runtime
# service account needs roles/secretmanager.secretAccessor on this secret.
JWT_SECRET_NAME="${JWT_SECRET_NAME:-google-antigravity-workshop-secret-1}"

echo "Deploying ${SERVICE} to project=${PROJECT_ID} region=${REGION} ..."
gcloud run deploy "${SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --source=. \
  --allow-unauthenticated \
  --set-env-vars="AUTH_MODE=local,JWT_ISSUER=grades-auth-local,JWT_AUDIENCE=grades-rest" \
  --set-secrets="JWT_SECRET=${JWT_SECRET_NAME}:latest" \
  --port=8080

echo
echo "Deployed. Try:"
echo "  URL=\$(gcloud run services describe ${SERVICE} --project=${PROJECT_ID} --region=${REGION} --format='value(status.url)')"
echo "  curl \$URL/health"
