"""Deterministic unit tests for GCS URI parsing/fail-fast checks, extractor agent wiring, and tool gates."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from app.agent import MODEL, app, root_agent
from app.gcs_loader import (
    DEFAULT_GCS_PREFIX,
    RawProposalDocument,
    load_rfp_bundle_from_gcs,
    parse_gcs_prefix,
)
from app.models import ProcurementPolicy, SupplierBidIntake
from app.scoring_engine import evaluate_bids
from app.tools import (
    STATE_EVAL_INVOCATION_ID,
    STATE_INTAKES,
    STATE_POLICY,
    STATE_REPORT,
    create_bid_extractor_agent,
    draft_supplier_clarification,
    get_extractor_model,
    record_manager_signoff_decision,
    rescore_what_if,
    select_supplier_for_award,
)
from tests.unit.test_scoring_engine import all_ten_intakes, procurement_policy  # noqa: F401


@dataclass
class _StubToolContext:
    """Minimal deterministic stand-in for ADK ToolContext (state + invocation_id)."""

    invocation_id: str
    state: dict[str, Any] = field(default_factory=dict)


class _MissingBlob:
    def exists(self, client: Any = None) -> bool:
        return False


class _MissingBucket:
    def blob(self, _path: str) -> _MissingBlob:
        return _MissingBlob()


class _MissingStorageClient:
    def bucket(self, _name: str) -> _MissingBucket:
        return _MissingBucket()


def test_parse_gcs_prefix_and_fail_fast_loader() -> None:
    """Verify gs:// URI parsing and fail-fast error raising when GCS blobs are missing."""
    bucket, base_prefix, folder = parse_gcs_prefix(DEFAULT_GCS_PREFIX, "RFP-2026-441")
    assert bucket == "default-project-alpha-1-rfp-eval-and-award-data"
    assert base_prefix == "rfp-eval-and-award"
    assert folder == "rfp-2026-441"

    # Passing the RFP subfolder URI directly still resolves base_prefix for policy lookup
    bucket2, base2, folder2 = parse_gcs_prefix(
        "gs://my-bucket/rfp-eval-and-award/rfp-2026-441/",
        "RFP-2026-441",
    )
    assert bucket2 == "my-bucket"
    assert base2 == "rfp-eval-and-award"
    assert folder2 == "rfp-2026-441"

    with pytest.raises(ValueError, match="gs://"):
        parse_gcs_prefix("/local/path/not-gcs", "rfp-2026-441")

    with pytest.raises(FileNotFoundError, match="Procurement policy file not found"):
        load_rfp_bundle_from_gcs(
            DEFAULT_GCS_PREFIX,
            "rfp-2026-441",
            storage_client=_MissingStorageClient(),  # type: ignore[arg-type]
        )


def test_scaffold_contract_and_tool_free_extractor_config() -> None:
    """Verify preserved scaffolded model/app names, tool schemas, and tool-free extractor config."""
    from google.adk.tools import FunctionTool
    from google.genai._transformers import t_schema

    assert MODEL == "gemini-3.8-flash"
    assert get_extractor_model() == MODEL
    assert root_agent.name == "rfp_eval_adk"
    assert app.name == "app"

    tool_names = [FunctionTool(t)._get_declaration().name for t in root_agent.tools]
    assert tool_names == [
        "evaluate_rfp_proposals",
        "rescore_what_if",
        "select_supplier_for_award",
        "record_manager_signoff_decision",
        "draft_supplier_clarification",
    ]

    gemini_schema = t_schema(None, SupplierBidIntake)
    assert gemini_schema.properties is not None
    assert "source_file" in gemini_schema.properties
    assert "mandatory_line_items" in gemini_schema.properties

    sample_doc = RawProposalDocument(
        source_file="08_nordicsense_quote.json",
        gcs_uri="gs://bucket/rfp-eval-and-award/rfp-2026-441/08_nordicsense_quote.json",
        content='{"vendor_id": "VND-702", "nested": {"sku": "NS-PRO"}}',
    )
    extractor = create_bid_extractor_agent(7, sample_doc)
    assert extractor.name == "bid_extractor_07"
    assert extractor.tools == []
    assert extractor.output_schema is SupplierBidIntake
    assert extractor.include_contents == "none"
    assert extractor.generate_content_config is not None
    assert extractor.generate_content_config.temperature == 0.0


def test_stateful_tools_cache_and_turn_gates(
    procurement_policy: ProcurementPolicy,  # noqa: F811
    all_ten_intakes: list[SupplierBidIntake],  # noqa: F811
) -> None:
    """Verify cached what-if re-scoring and cross-turn human gates on ADK session state."""
    report = evaluate_bids(all_ten_intakes, procurement_policy)
    state: dict[str, Any] = {
        STATE_POLICY: procurement_policy.model_dump(),
        STATE_INTAKES: [i.model_dump() for i in all_ten_intakes],
        STATE_REPORT: report.model_dump(),
        STATE_EVAL_INVOCATION_ID: "turn-1",
    }

    # Turn 1 guard: cannot select supplier or draft PO during initial evaluation turn
    ctx_turn1 = _StubToolContext(invocation_id="turn-1", state=state)
    blocked_same_turn = select_supplier_for_award("DeccanTech", "", ctx_turn1)  # type: ignore[arg-type]
    assert blocked_same_turn["status"] == "error"

    # Turn 2: Cached what-if re-scoring does not re-read GCS
    ctx_turn2 = _StubToolContext(invocation_id="turn-2", state=state)
    what_if_res = rescore_what_if(60.0, None, None, None, None, None, ctx_turn2)  # type: ignore[arg-type]
    assert what_if_res["status"] == "success"
    assert what_if_res["gcs_re_read"] is False
    assert what_if_res["po_drafted"] is False

    # Restore default weights and test Turn 3 selection of >$50K NordicSense
    rescore_what_if(40.0, 20.0, 15.0, 15.0, 10.0, 28, ctx_turn2)  # type: ignore[arg-type]
    ctx_turn3 = _StubToolContext(invocation_id="turn-3", state=state)
    sel_nordic = select_supplier_for_award("VND-702", "Top technical score", ctx_turn3)  # type: ignore[arg-type]
    assert sel_nordic["status"] == "success"
    assert sel_nordic["decision"]["outcome"] == "MANAGER_SIGNOFF_REQUIRED"
    assert sel_nordic["decision"]["po_drafted"] is False

    # Same-turn self-approval is rejected
    same_turn_approve = record_manager_signoff_decision("VND-702", True, "Self-approve", ctx_turn3)  # type: ignore[arg-type]
    assert same_turn_approve["status"] == "error"

    # Next-turn manager approval unlocks PO drafting
    ctx_turn4 = _StubToolContext(invocation_id="turn-4", state=state)
    next_turn_approve = record_manager_signoff_decision(
        "VND-702", True, "Approved by Sourcing Director", ctx_turn4  # type: ignore[arg-type]
    )
    assert next_turn_approve["status"] == "success"
    assert next_turn_approve["decision"]["outcome"] == "MANAGER_SIGNOFF_APPROVED_PO_DRAFTED"
    assert next_turn_approve["decision"]["po_drafted"] is True

    # Clarification tool generates clarification request for Vanguard without drafting PO
    clar_res = draft_supplier_clarification("Vanguard", ctx_turn4)  # type: ignore[arg-type]
    assert clar_res["status"] == "success"
    assert clar_res["po_drafted"] is False
    assert clar_res["clarification_request"]["vendor_id"] == "VND-505"
