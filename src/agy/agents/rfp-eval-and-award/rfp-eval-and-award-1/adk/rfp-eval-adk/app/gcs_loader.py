"""Read-only, fail-fast Google Cloud Storage loader for RFP policy and quotes."""

from __future__ import annotations

import json
from pathlib import Path

from google.cloud import storage

from app.models import ProcurementPolicy, RawQuoteDocument

SUPPORTED_QUOTE_EXTENSIONS = {".md", ".csv", ".txt", ".json"}


def _normalize_prefix(prefix: str) -> str:
    cleaned = prefix.strip().lstrip("/")
    if cleaned and not cleaned.endswith("/"):
        cleaned += "/"
    return cleaned


def load_policy_and_quotes_from_gcs(
    gcs_bucket: str,
    rfp_prefix: str,
    policy_blob_path: str,
) -> tuple[ProcurementPolicy, list[RawQuoteDocument]]:
    """Loads procurement policy JSON and all RFP quote files from GCS (read-only).

    Fails fast on missing bucket/objects, invalid JSON, or empty quote sets.
    Never falls back to mock or hardcoded data.
    """
    if not gcs_bucket or not gcs_bucket.strip():
        raise ValueError("gcs_bucket must be a non-empty GCS bucket name.")
    if not policy_blob_path or not policy_blob_path.strip():
        raise ValueError("policy_blob_path must be a non-empty GCS object path.")
    if not rfp_prefix or not rfp_prefix.strip():
        raise ValueError("rfp_prefix must be a non-empty GCS object prefix.")

    client = storage.Client()
    bucket = client.bucket(gcs_bucket.strip())

    # 1. Load procurement_policy.json (fail-fast)
    policy_path = policy_blob_path.strip().lstrip("/")
    policy_blob = bucket.blob(policy_path)
    if not policy_blob.exists(client=client):
        raise FileNotFoundError(
            f"Procurement policy not found at gs://{gcs_bucket}/{policy_path}"
        )

    raw_policy_text = policy_blob.download_as_text(encoding="utf-8")
    try:
        policy_data = json.loads(raw_policy_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in gs://{gcs_bucket}/{policy_path}: {exc}"
        ) from exc

    policy = ProcurementPolicy.model_validate(policy_data)

    # 2. Load all supported supplier quote blobs under rfp_prefix (read-only, deterministic order)
    normalized_prefix = _normalize_prefix(rfp_prefix)
    blobs = sorted(
        client.list_blobs(bucket, prefix=normalized_prefix),
        key=lambda b: b.name,
    )

    quotes: list[RawQuoteDocument] = []
    for blob in blobs:
        if blob.name.endswith("/"):
            continue
        filename = Path(blob.name).name
        ext = Path(filename).suffix.lower()
        if ext not in SUPPORTED_QUOTE_EXTENSIONS:
            continue
        raw_text = blob.download_as_text(encoding="utf-8")
        if not raw_text.strip():
            raise ValueError(
                f"Quote file gs://{gcs_bucket}/{blob.name} is empty."
            )
        quotes.append(
            RawQuoteDocument(
                source_uri=f"gs://{gcs_bucket}/{blob.name}",
                filename=filename,
                file_format=ext.lstrip("."),
                raw_content=raw_text,
            )
        )

    if not quotes:
        raise FileNotFoundError(
            f"No supported supplier quote files found under "
            f"gs://{gcs_bucket}/{normalized_prefix}"
        )

    return policy, quotes
