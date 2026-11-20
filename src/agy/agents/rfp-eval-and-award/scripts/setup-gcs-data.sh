#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DATA_DIR="${PROJECT_DIR}/data"
RFP_DIR="${DATA_DIR}/rfp-2026-441"
POLICY_FILE="${DATA_DIR}/policy/procurement_policy.json"

GCP_PROJECT=""
BUCKET_NAME=""
LOCATION="US"
PREFIX="rfp-eval-and-award"
DRY_RUN=false

usage() {
  cat <<'EOF'
Usage: ./scripts/setup-gcs-data.sh [OPTIONS]

Prepares the GCS data bucket for the RFP Evaluation and Award Agent workshop.
By default, creates a new US multi-region bucket (if it does not exist) and
uploads all 10 synthetic supplier proposals plus procurement_policy.json,
overwriting existing files by default.

Options:
  --project <PROJECT_ID>   GCP project ID (defaults to active gcloud project)
  --bucket <BUCKET_NAME>   GCS bucket name without gs:// prefix
                           (defaults to <project>-rfp-eval-and-award-data)
  --location <LOCATION>    GCS bucket location when creating (default: US)
  --prefix <PREFIX>        Object prefix inside the bucket (default: rfp-eval-and-award)
  --dry-run                Print planned bucket and upload commands without executing
  -h, --help               Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      [[ $# -ge 2 ]] || { echo "Error: --project requires a value." >&2; exit 1; }
      GCP_PROJECT="$2"
      shift 2
      ;;
    --bucket)
      [[ $# -ge 2 ]] || { echo "Error: --bucket requires a value." >&2; exit 1; }
      BUCKET_NAME="${2#gs://}"
      BUCKET_NAME="${BUCKET_NAME%/}"
      shift 2
      ;;
    --location)
      [[ $# -ge 2 ]] || { echo "Error: --location requires a value." >&2; exit 1; }
      LOCATION="$2"
      shift 2
      ;;
    --prefix)
      [[ $# -ge 2 ]] || { echo "Error: --prefix requires a value." >&2; exit 1; }
      PREFIX="${2#/}"
      PREFIX="${PREFIX%/}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: unknown argument '$1'" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ ! -d "${RFP_DIR}" ]]; then
  echo "Error: missing RFP data directory: ${RFP_DIR}" >&2
  exit 1
fi

if [[ ! -f "${POLICY_FILE}" ]]; then
  echo "Error: missing policy file: ${POLICY_FILE}" >&2
  exit 1
fi

if ! command -v gcloud >/dev/null 2>&1; then
  echo "Error: gcloud CLI is required. Install Google Cloud SDK and run 'gcloud auth login'." >&2
  exit 1
fi

if [[ -z "${GCP_PROJECT}" ]]; then
  GCP_PROJECT="$(gcloud config get-value project 2>/dev/null || true)"
  if [[ -z "${GCP_PROJECT}" || "${GCP_PROJECT}" == "(unset)" ]]; then
    echo "Error: no GCP project configured. Pass --project <PROJECT_ID> or run 'gcloud config set project <PROJECT_ID>'." >&2
    exit 1
  fi
fi

if [[ -z "${BUCKET_NAME}" ]]; then
  SANITIZED_PROJECT="$(printf '%s' "${GCP_PROJECT}" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')"
  BUCKET_NAME="${SANITIZED_PROJECT}-rfp-eval-and-award-data"
fi

BUCKET_URI="gs://${BUCKET_NAME}"
if [[ -n "${PREFIX}" ]]; then
  BASE_URI="${BUCKET_URI}/${PREFIX}"
else
  BASE_URI="${BUCKET_URI}"
fi
RFP_DEST_URI="${BASE_URI}/rfp-2026-441/"
POLICY_DEST_URI="${BASE_URI}/policy/procurement_policy.json"

shopt -s nullglob
PROPOSAL_FILES=("${RFP_DIR}"/*)
shopt -u nullglob

if [[ ${#PROPOSAL_FILES[@]} -eq 0 ]]; then
  echo "Error: no supplier proposal files found in ${RFP_DIR}" >&2
  exit 1
fi

echo "RFP Evaluation and Award Agent: GCS Data Setup"
echo "  Project:   ${GCP_PROJECT}"
echo "  Bucket:    ${BUCKET_URI} (location: ${LOCATION})"
echo "  Proposals: ${#PROPOSAL_FILES[@]} files -> ${RFP_DEST_URI}"
echo "  Policy:    procurement_policy.json -> ${POLICY_DEST_URI}"

if [[ "${DRY_RUN}" == "true" ]]; then
  echo ""
  echo "[dry-run] Would check/create bucket:"
  echo "  gcloud storage buckets create ${BUCKET_URI} --project=${GCP_PROJECT} --location=${LOCATION} --uniform-bucket-level-access"
  echo "[dry-run] Would upload (overwriting existing objects):"
  echo "  gcloud storage cp ${RFP_DIR}/* ${RFP_DEST_URI}"
  echo "  gcloud storage cp ${POLICY_FILE} ${POLICY_DEST_URI}"
  exit 0
fi

if gcloud storage buckets describe "${BUCKET_URI}" --project="${GCP_PROJECT}" >/dev/null 2>&1; then
  echo "Bucket ${BUCKET_URI} already exists; keeping existing bucket and overwriting files."
else
  echo "Creating bucket ${BUCKET_URI} in location ${LOCATION}..."
  gcloud storage buckets create "${BUCKET_URI}" \
    --project="${GCP_PROJECT}" \
    --location="${LOCATION}" \
    --uniform-bucket-level-access
fi

echo "Uploading ${#PROPOSAL_FILES[@]} supplier proposals (overwriting existing objects)..."
gcloud storage cp "${PROPOSAL_FILES[@]}" "${RFP_DEST_URI}"

echo "Uploading procurement_policy.json (overwriting existing object)..."
gcloud storage cp "${POLICY_FILE}" "${POLICY_DEST_URI}"

echo ""
echo "GCS data setup complete."
echo "Use this base GCS URI when prompting the agent:"
echo "  ${BASE_URI}/"
echo "  Proposals: ${RFP_DEST_URI}"
echo "  Policy:    ${POLICY_DEST_URI}"
