# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Read-only Google Cloud Storage loader for procurement policy and RFP quotes.

Fails fast when credentials, bucket, policy JSON, or quote documents are
missing. Never writes to GCS and never falls back to mock data.
"""

from __future__ import annotations

import json
import os
from pathlib import PurePosixPath

from google.cloud import storage

from app.models import ProcurementPolicy, RawQuoteDocument

DEFAULT_GCS_BUCKET = "default-project-alpha-1-rfp-eval-and-award-data"
DEFAULT_POLICY_BLOB = "rfp-eval-and-award/policy/procurement_policy.json"
DEFAULT_QUOTES_PREFIX = "rfp-eval-and-award/rfp-2026-441/"
SUPPORTED_QUOTE_EXTENSIONS = frozenset({".md", ".csv", ".txt", ".json"})


def _storage_client(project: str | None = None) -> storage.Client:
    """Create a read-only ADC GCS client for the configured project."""
    resolved_project = project or os.environ.get("GOOGLE_CLOUD_PROJECT")
    return storage.Client(project=resolved_project)


def resolve_gcs_config() -> tuple[str, str, str]:
    """Resolve GCS bucket, policy blob, and quotes prefix from env or defaults."""
    bucket = os.environ.get("RFP_GCS_BUCKET", DEFAULT_GCS_BUCKET).strip()
    policy_blob = os.environ.get("RFP_POLICY_BLOB", DEFAULT_POLICY_BLOB).strip()
    quotes_prefix = os.environ.get("RFP_QUOTES_PREFIX", DEFAULT_QUOTES_PREFIX).strip()
    if not bucket:
        raise ValueError("RFP_GCS_BUCKET must be non-empty.")
    if not policy_blob:
        raise ValueError("RFP_POLICY_BLOB must be non-empty.")
    if not quotes_prefix:
        raise ValueError("RFP_QUOTES_PREFIX must be non-empty.")
    if not quotes_prefix.endswith("/"):
        quotes_prefix = f"{quotes_prefix}/"
    return bucket, policy_blob, quotes_prefix


def load_procurement_policy(
    bucket_name: str | None = None,
    policy_blob_name: str | None = None,
    *,
    client: storage.Client | None = None,
) -> ProcurementPolicy:
    """Load and validate procurement_policy.json from GCS (read-only, fail-fast)."""
    default_bucket, default_policy_blob, _ = resolve_gcs_config()
    resolved_bucket = bucket_name or default_bucket
    resolved_blob = policy_blob_name or default_policy_blob

    gcs = client or _storage_client()
    blob = gcs.bucket(resolved_bucket).blob(resolved_blob)
    if not blob.exists():
        raise FileNotFoundError(
            f"Procurement policy not found at gs://{resolved_bucket}/{resolved_blob}"
        )

    raw_text = blob.download_as_text(encoding="utf-8")
    payload = json.loads(raw_text)
    return ProcurementPolicy.model_validate(payload)


def load_rfp_quotes(
    bucket_name: str | None = None,
    quotes_prefix: str | None = None,
    *,
    client: storage.Client | None = None,
) -> list[RawQuoteDocument]:
    """List and download all supported supplier quote files from GCS (read-only)."""
    default_bucket, _, default_prefix = resolve_gcs_config()
    resolved_bucket = bucket_name or default_bucket
    resolved_prefix = quotes_prefix or default_prefix
    if not resolved_prefix.endswith("/"):
        resolved_prefix = f"{resolved_prefix}/"

    gcs = client or _storage_client()
    blobs = sorted(
        gcs.list_blobs(resolved_bucket, prefix=resolved_prefix),
        key=lambda b: b.name,
    )

    documents: list[RawQuoteDocument] = []
    for blob in blobs:
        if blob.name.endswith("/"):
            continue
        filename = PurePosixPath(blob.name).name
        suffix = PurePosixPath(blob.name).suffix.lower()
        if suffix not in SUPPORTED_QUOTE_EXTENSIONS:
            continue
        content = blob.download_as_text(encoding="utf-8")
        if not content.strip():
            raise ValueError(
                f"Quote file gs://{resolved_bucket}/{blob.name} is empty."
            )
        documents.append(
            RawQuoteDocument(
                filename=filename,
                gcs_uri=f"gs://{resolved_bucket}/{blob.name}",
                content=content,
            )
        )

    if not documents:
        raise FileNotFoundError(
            f"No supported supplier quote files found under "
            f"gs://{resolved_bucket}/{resolved_prefix}"
        )
    return documents
