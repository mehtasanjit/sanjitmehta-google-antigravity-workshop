#!/usr/bin/env bash
# Grant the deployer the IAM roles needed for a DIRECT source-based Cloud Run
# deploy (`gcloud run deploy --source .`). Run by an Owner / Project IAM Admin.
#
# These are the convenient predefined roles for the one-command path (it must
# create its own staging bucket + Artifact Registry repo). For a locked-down
# alternative (resource-scoped writer roles + a named staging bucket), see the
# two-step approach discussed in the project notes.
#
# Usage:
#   PROJECT=<YOUR_PROJECT_ID> MEMBER="user:<YOU>@<YOUR_DOMAIN>" ./grant-iam.sh
set -euo pipefail

PROJECT="${PROJECT:?set PROJECT to your GCP project id}"
MEMBER="${MEMBER:?set MEMBER, e.g. user:you@example.com}"
# Cloud Run runtime service account (Compute default SA), derived from the project.
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')"
RUNTIME_SA="${RUNTIME_SA:-${PROJECT_NUMBER}-compute@developer.gserviceaccount.com}"

echo "Granting deploy roles to ${MEMBER} on ${PROJECT} ..."
for ROLE in roles/run.admin \
            roles/cloudbuild.builds.editor \
            roles/artifactregistry.admin \
            roles/storage.admin; do
  gcloud projects add-iam-policy-binding "$PROJECT" --member="$MEMBER" --role="$ROLE"
done

# actAs on the runtime service account (granted on the SA resource, not project)
gcloud iam service-accounts add-iam-policy-binding "$RUNTIME_SA" \
  --project="$PROJECT" \
  --member="$MEMBER" \
  --role="roles/iam.serviceAccountUser"

echo "Done."
