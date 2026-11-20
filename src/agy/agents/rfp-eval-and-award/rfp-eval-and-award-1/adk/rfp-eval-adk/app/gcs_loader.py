"""Read-only Google Cloud Storage loader using Application Default Credentials (fail-fast, no mocks)."""

from __future__ import annotations

import os
from urllib.parse import urlparse

from google.cloud import storage
from pydantic import BaseModel, Field

from app.models import ProcurementPolicy

DEFAULT_GCS_PREFIX = "gs://default-project-alpha-1-rfp-eval-and-award-data/rfp-eval-and-award/"
DEFAULT_RFP_ID = "rfp-2026-441"
SUPPORTED_PROPOSAL_EXTENSIONS = (".md", ".csv", ".txt", ".json")


class RawProposalDocument(BaseModel):
    """Raw supplier proposal file loaded from GCS."""

    source_file: str = Field(description="Basename of the proposal blob in GCS.")
    gcs_uri: str = Field(description="Full gs:// URI of the proposal blob.")
    content: str = Field(description="UTF-8 text content of the proposal.")


class RfpGcsBundle(BaseModel):
    """Validated policy and sorted raw supplier proposals fetched from GCS."""

    gcs_base_uri: str
    rfp_folder: str
    policy_gcs_uri: str
    policy: ProcurementPolicy
    proposals: list[RawProposalDocument]


def parse_gcs_prefix(gcs_uri: str, rfp_id: str = DEFAULT_RFP_ID) -> tuple[str, str, str]:
    """Parse a gs:// URI and RFP identifier into (bucket_name, base_prefix, rfp_folder).

    Handles URIs pointing either to the base prefix (gs://bucket/rfp-eval-and-award/)
    or directly to the RFP subfolder (gs://bucket/rfp-eval-and-award/rfp-2026-441/).
    """
    cleaned_uri = gcs_uri.strip()
    if not cleaned_uri.startswith("gs://"):
        raise ValueError(f"Expected a 'gs://' URI, got: {gcs_uri!r}")

    parsed = urlparse(cleaned_uri)
    bucket_name = parsed.netloc.strip()
    if not bucket_name:
        raise ValueError(f"Missing GCS bucket name in URI: {gcs_uri!r}")

    rfp_folder = rfp_id.strip().strip("/").lower()
    if not rfp_folder:
        raise ValueError("rfp_id must be a non-empty identifier such as 'RFP-2026-441'.")

    raw_prefix = parsed.path.strip("/")
    if raw_prefix.lower().endswith(f"/{rfp_folder}"):
        base_prefix = raw_prefix[: -(len(rfp_folder) + 1)]
    elif raw_prefix.lower() == rfp_folder:
        base_prefix = ""
    else:
        base_prefix = raw_prefix

    return bucket_name, base_prefix, rfp_folder


def load_rfp_bundle_from_gcs(
    gcs_prefix: str = DEFAULT_GCS_PREFIX,
    rfp_id: str = DEFAULT_RFP_ID,
    storage_client: storage.Client | None = None,
) -> RfpGcsBundle:
    """Load procurement_policy.json and all supplier proposals for rfp_id from GCS via ADC.

    Raises ValueError on malformed URIs/JSON and FileNotFoundError when policy or proposals
    are absent. Never falls back to mocked or synthetic in-memory data.
    """
    bucket_name, base_prefix, rfp_folder = parse_gcs_prefix(gcs_prefix, rfp_id)

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or None
    client = storage_client or storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)

    policy_blob_path = (
        f"{base_prefix}/policy/procurement_policy.json"
        if base_prefix
        else "policy/procurement_policy.json"
    )
    policy_uri = f"gs://{bucket_name}/{policy_blob_path}"
    policy_blob = bucket.blob(policy_blob_path)
    if not policy_blob.exists(client=client):
        raise FileNotFoundError(f"Procurement policy file not found in GCS: {policy_uri}")

    policy_raw = policy_blob.download_as_text(encoding="utf-8", client=client)
    policy = ProcurementPolicy.model_validate_json(policy_raw)

    proposals_prefix = f"{base_prefix}/{rfp_folder}/" if base_prefix else f"{rfp_folder}/"
    blobs = list(client.list_blobs(bucket_name, prefix=proposals_prefix))

    proposal_blobs: list[tuple[str, storage.Blob]] = []
    for blob in blobs:
        if blob.name.endswith("/"):
            continue
        filename = os.path.basename(blob.name)
        if not filename or not filename.lower().endswith(SUPPORTED_PROPOSAL_EXTENSIONS):
            continue
        proposal_blobs.append((filename, blob))

    proposal_blobs.sort(key=lambda pair: pair[0])
    if not proposal_blobs:
        raise FileNotFoundError(
            f"No supplier proposal files found under gs://{bucket_name}/{proposals_prefix}"
        )

    proposals: list[RawProposalDocument] = []
    for filename, blob in proposal_blobs:
        text = blob.download_as_text(encoding="utf-8", client=client)
        if not text.strip():
            raise ValueError(f"Proposal blob is empty: gs://{bucket_name}/{blob.name}")
        proposals.append(
            RawProposalDocument(
                source_file=filename,
                gcs_uri=f"gs://{bucket_name}/{blob.name}",
                content=text,
            )
        )

    normalized_base = (
        f"gs://{bucket_name}/{base_prefix}/" if base_prefix else f"gs://{bucket_name}/"
    )
    return RfpGcsBundle(
        gcs_base_uri=normalized_base,
        rfp_folder=rfp_folder,
        policy_gcs_uri=policy_uri,
        policy=policy,
        proposals=proposals,
    )
