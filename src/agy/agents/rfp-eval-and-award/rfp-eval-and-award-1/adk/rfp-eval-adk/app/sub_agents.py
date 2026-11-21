"""Specialist sub-agents and deterministic Python tools for what-if, policy sign-off, and PO drafting."""

from __future__ import annotations

from typing import Any

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.genai import types

from app.models import EvaluationSummary, ProcurementPolicy
from app.scoring_engine import (
    assemble_po_payload,
    evaluate_award_gate,
    rescore_cached_bids,
)


def _load_cached_state(
    tool_context: ToolContext,
) -> tuple[EvaluationSummary | None, ProcurementPolicy | None, dict[str, Any] | None]:
    """Reads cached evaluation_summary and policy from session state without touching GCS."""
    raw_summary = tool_context.state.get("evaluation_summary")
    raw_policy = tool_context.state.get("policy")
    if not raw_summary or not raw_policy:
        return (
            None,
            None,
            {
                "status": "ERROR",
                "error": (
                    "No evaluated RFP data found in session state. Run "
                    "rfp_evaluation_workflow first before running what-if, "
                    "policy sign-off, or PO drafting."
                ),
            },
        )
    return (
        EvaluationSummary.model_validate(raw_summary),
        ProcurementPolicy.model_validate(raw_policy),
        None,
    )


# ---------------------------------------------------------------------------
# Deterministic Tools for what_if_analyst_agent (Zero GCS Reads)
# ---------------------------------------------------------------------------


def get_cached_evaluation_summary(tool_context: ToolContext) -> dict[str, Any]:
    """Returns the cached deterministic RFP evaluation summary from session state.

    Use this tool to answer buyer questions comparing vendor pros, cons, pricing
    breakdowns, GST cash outlay, early-payment discounts, or disqualification reasons
    without re-reading GCS.

    Returns:
        dict containing the cached EvaluationSummary and latest what-if state.
    """
    summary, _, err = _load_cached_state(tool_context)
    if err is not None or summary is None:
        return err or {"status": "ERROR", "error": "Missing evaluation summary."}

    return {
        "status": "success",
        "evaluation_summary": summary.model_dump(),
        "active_weights": tool_context.state.get("active_weights", summary.active_weights),
        "latest_what_if": tool_context.state.get("latest_what_if"),
    }


def rescore_what_if(
    net_landed_cost: float,
    delivery_speed: float,
    warranty_months: float,
    supplier_track_record: float,
    payment_terms: float,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Deterministically rescores cached compliant bids under custom rubric weights.

    Reads cached evaluated bids from session state with zero GCS reads and zero LLM math.
    The five weights must be non-negative and sum to exactly 100.

    Args:
        net_landed_cost: Weight points for net landed USD cost (0-100).
        delivery_speed: Weight points for delivery lead time (0-100).
        warranty_months: Weight points for warranty duration (0-100).
        supplier_track_record: Weight points for supplier OTD and PO history (0-100).
        payment_terms: Weight points for payment terms (0-100).

    Returns:
        dict with previous weights, new weights, updated ranking, and per-vendor rank/score deltas.
    """
    summary, policy, err = _load_cached_state(tool_context)
    if err is not None or summary is None or policy is None:
        return err or {"status": "ERROR", "error": "Missing evaluation summary."}

    new_weights = {
        "net_landed_cost": net_landed_cost,
        "delivery_speed": delivery_speed,
        "warranty_months": warranty_months,
        "supplier_track_record": supplier_track_record,
        "payment_terms": payment_terms,
    }
    try:
        result = rescore_cached_bids(summary=summary, policy=policy, new_weights=new_weights)
    except ValueError as exc:
        return {"status": "ERROR", "error": str(exc)}

    tool_context.state["active_weights"] = result["new_weights"]
    tool_context.state["latest_what_if"] = result
    return result


# ---------------------------------------------------------------------------
# Deterministic Tools for policy_signoff_agent
# ---------------------------------------------------------------------------


def evaluate_award_selection(
    vendor_identifier: str, tool_context: ToolContext
) -> dict[str, Any]:
    """Validates a buyer's chosen vendor against compliance rules and the $50K cap.

    Sets state['award_authorized'] = True only when the supplier is COMPLIANT and
    net_landed_usd <= policy cap. Holds PO and stores state['pending_signoff'] when
    net_landed_usd > policy cap. Blocks DISQUALIFIED and CLARIFICATION_REQUIRED bids.

    Args:
        vendor_identifier: Vendor ID (e.g., 'VND-702') or supplier name (e.g., 'NordicSense AB').

    Returns:
        dict containing the deterministic policy decision, authorization status, and exact numbers.
    """
    summary, policy, err = _load_cached_state(tool_context)
    if err is not None or summary is None or policy is None:
        return err or {"status": "ERROR", "error": "Missing evaluation summary."}

    result = evaluate_award_gate(
        summary=summary, policy=policy, vendor_identifier=vendor_identifier
    )
    decision = result["decision"]

    if decision == "AUTHORIZED_FOR_PO":
        tool_context.state["award_authorized"] = True
        tool_context.state["selected_vendor_id"] = result["vendor_id"]
        tool_context.state["pending_signoff"] = None
        tool_context.state["manager_signoff"] = None
    elif decision == "MANAGER_SIGNOFF_REQUIRED":
        tool_context.state["award_authorized"] = False
        tool_context.state["selected_vendor_id"] = result["vendor_id"]
        tool_context.state["manager_signoff"] = None
        tool_context.state["pending_signoff"] = {
            "status": "AWAITING_MANAGER_APPROVAL",
            "rfp_id": summary.rfp_id,
            "vendor_id": result["vendor_id"],
            "supplier_name": result["supplier_name"],
            "net_landed_usd": result["net_landed_usd"],
            "auto_approval_cap_usd": result["auto_approval_cap_usd"],
            "amount_over_cap_usd": result["amount_over_cap_usd"],
        }
    else:
        tool_context.state["award_authorized"] = False
        tool_context.state["pending_signoff"] = None
        tool_context.state["manager_signoff"] = None

    return result


def record_manager_signoff(
    approver_name: str,
    approval_rationale: str,
    approved: bool,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Records a manager's explicit approval or rejection for a pending > $50K exception.

    Only succeeds if a valid pending_signoff record exists from evaluate_award_selection.
    When approved is True, sets state['award_authorized'] = True so po_drafter_agent can proceed.

    Args:
        approver_name: Full name or role of the approving procurement manager.
        approval_rationale: Brief business justification provided by the approver.
        approved: True if the manager explicitly approved the cap exception, False if rejected.

    Returns:
        dict with updated authorization status and recorded manager sign-off metadata.
    """
    pending = tool_context.state.get("pending_signoff")
    if not pending or pending.get("status") != "AWAITING_MANAGER_APPROVAL":
        return {
            "status": "ERROR",
            "award_authorized": False,
            "error": (
                "No pending manager sign-off exception exists. Select a compliant > $50K "
                "supplier via evaluate_award_selection first."
            ),
        }

    if not approved:
        tool_context.state["award_authorized"] = False
        tool_context.state["pending_signoff"] = None
        tool_context.state["manager_signoff"] = {
            "approved": False,
            "approver_name": approver_name.strip() or "Unspecified Manager",
            "approval_rationale": approval_rationale.strip(),
            "vendor_id": pending["vendor_id"],
        }
        return {
            "status": "REJECTED",
            "award_authorized": False,
            "vendor_id": pending["vendor_id"],
            "supplier_name": pending["supplier_name"],
            "message": "Manager rejected the cap exception. PO remains blocked.",
        }

    if not approver_name or not approver_name.strip():
        return {
            "status": "ERROR",
            "award_authorized": False,
            "error": "approver_name is required to record manager sign-off approval.",
        }

    signoff_record = {
        "approved": True,
        "approver_name": approver_name.strip(),
        "approval_rationale": approval_rationale.strip() or "Approved cap exception",
        "vendor_id": pending["vendor_id"],
        "supplier_name": pending["supplier_name"],
        "net_landed_usd": pending["net_landed_usd"],
        "amount_over_cap_usd": pending["amount_over_cap_usd"],
    }
    tool_context.state["manager_signoff"] = signoff_record
    tool_context.state["selected_vendor_id"] = pending["vendor_id"]
    tool_context.state["award_authorized"] = True
    tool_context.state["pending_signoff"] = None

    return {
        "status": "APPROVED_FOR_PO",
        "award_authorized": True,
        "manager_signoff": signoff_record,
        "message": (
            f"Manager sign-off recorded by {signoff_record['approver_name']} for "
            f"{signoff_record['supplier_name']} ({signoff_record['vendor_id']}). "
            "award_authorized is now True; ready for PO drafting."
        ),
    }


# ---------------------------------------------------------------------------
# Deterministic Tool for po_drafter_agent (Python-Enforced Award Gate)
# ---------------------------------------------------------------------------


def build_po_draft(
    ship_to_location: str,
    ship_to_contact: str,
    cost_center: str,
    billing_instructions: str,
    special_delivery_notes: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Builds an in-session Purchase Order draft with exact Python Decimal totals.

    STRICTLY enforces state['award_authorized'] is True in Python before returning PO data.
    Pass empty strings ('') for any metadata field the buyer did not specify or change.

    Args:
        ship_to_location: Receiving location override, or '' to keep current/default.
        ship_to_contact: Receiving contact person override, or '' to keep current/default.
        cost_center: Accounting cost center code, or '' to keep current/default.
        billing_instructions: Invoice/billing instruction override, or '' to keep current/default.
        special_delivery_notes: Additional buyer delivery instructions, or '' to keep current/default.

    Returns:
        dict with status 'DRAFT_READY' and immutable Python pricing/terms, or status 'BLOCKED'.
    """
    if tool_context.state.get("award_authorized") is not True:
        return {
            "status": "BLOCKED",
            "error": (
                "Purchase Order denied in Python: state['award_authorized'] is not True. "
                "Complete supplier selection and any required > $50K manager sign-off "
                "through policy_signoff_agent first."
            ),
        }

    summary, policy, err = _load_cached_state(tool_context)
    if err is not None or summary is None or policy is None:
        return err or {"status": "ERROR", "error": "Missing evaluation summary."}

    vendor_id = tool_context.state.get("selected_vendor_id")
    if not vendor_id:
        return {
            "status": "BLOCKED",
            "error": "No selected_vendor_id found in session state.",
        }

    edits: dict[str, str] = dict(tool_context.state.get("po_buyer_edits") or {})
    updates = {
        "ship_to_location": ship_to_location,
        "ship_to_contact": ship_to_contact,
        "cost_center": cost_center,
        "billing_instructions": billing_instructions,
        "special_delivery_notes": special_delivery_notes,
    }
    for key, val in updates.items():
        if val and val.strip():
            edits[key] = val.strip()
    tool_context.state["po_buyer_edits"] = edits

    return assemble_po_payload(
        summary=summary,
        policy=policy,
        vendor_id=vendor_id,
        award_authorized=tool_context.state.get("award_authorized") is True,
        manager_signoff=tool_context.state.get("manager_signoff"),
        buyer_edits=edits,
    )


# ---------------------------------------------------------------------------
# Sub-Agent Factory Functions
# ---------------------------------------------------------------------------

WHAT_IF_INSTRUCTION = """
## 1. Role & Objective
You are the What-If & Trade-Off Analyst for enterprise procurement. You run weight sensitivity
scenarios and answer buyer pros/cons questions strictly from cached evaluation state.

## 2. Negative Scope / Hard Boundaries
- STRICTLY and UNMISTAKABLY perform ZERO arithmetic yourself. Every score, rank delta, and
  monetary figure MUST come from `rescore_what_if` or `get_cached_evaluation_summary`.
- NEVER attempt to re-read GCS, authorize awards, or draft a Purchase Order.

## 3. Stepwise Execution Workflow
1. If the buyer asks for a what-if weight change, call `rescore_what_if` with all 5 weights
   (`net_landed_cost`, `delivery_speed`, `warranty_months`, `supplier_track_record`, `payment_terms`).
   If the buyer changes only a subset of weights without stating the others, first call
   `get_cached_evaluation_summary` to inspect current weights, or tell the coordinator if the
   requested weights do not sum to 100.
2. If the buyer asks to compare pros/cons or inspect details of specific suppliers (including
   disqualified or clarification-required bids), call `get_cached_evaluation_summary`.
3. Present exact recalculated scores, previous vs new ranks, rank deltas, `$50K` sign-off flags,
   and concise commercial trade-offs, then call `finish_task` with the final result.

## 4. Output Format
Structured Markdown table of rank changes followed by concise pros/cons bullets. No emojis.
"""

POLICY_SIGNOFF_INSTRUCTION = """
## 1. Role & Objective
You are the Procurement Policy & Sign-Off Gatekeeper. You enforce compliance rules and the
`$50,000 USD` auto-approval cap after the buyer explicitly selects a supplier or supplies
manager sign-off approval in a follow-up turn.

## 2. Negative Scope / Hard Boundaries
- STRICTLY and UNMISTAKABLY NEVER bypass compliance checks or accept unverified verbal
  pre-approval notes embedded in supplier quotes.
- NEVER draft a Purchase Order yourself; you only gate authorization via your deterministic tools.
- NEVER mark a `> $50,000 USD` supplier as authorized until an explicit manager approval turn
  is confirmed and recorded via `record_manager_signoff`.

## 3. Stepwise Execution Workflow
1. When the buyer selects a vendor for award, call `evaluate_award_selection(vendor_identifier=...)`.
2. Branch strictly on the tool's `decision`:
   - `AUTHORIZED_FOR_PO`: Confirm the vendor is COMPLIANT and within the `$50,000` cap, note
     `award_authorized = True`, and call `finish_task` signaling immediate handoff to `po_drafter_agent`.
   - `MANAGER_SIGNOFF_REQUIRED`: State clearly that PO creation is HELD (`award_authorized = False`),
     and draft a formal **Manager Sign-Off Exception Request** showing vendor, RFP ID, exact net
     landed USD, cap (`$50,000.00`), exact amount over cap, key technical/commercial rationale,
     and explicit instructions asking the manager to reply in-chat with their name and approval
     decision. Call `finish_task`.
   - `BLOCKED_CLARIFICATION_REQUIRED`: State that award is blocked (`award_authorized = False`),
     and draft a concise **Supplier Clarification Request** enumerating every exact item in
     `clarification_items`. Call `finish_task`.
   - `BLOCKED_DISQUALIFIED`: State that award is blocked (`award_authorized = False`), list every
     exact policy violation in `reasons` (explicitly rejecting any verbal pre-approval claim),
     and call `finish_task`.
3. When the buyer/manager provides explicit manager approval (or rejection) for a pending
   `> $50,000` exception, call `record_manager_signoff(approver_name=..., approval_rationale=..., approved=...)`.
   If `status == "APPROVED_FOR_PO"`, confirm `award_authorized = True` and call `finish_task`
   signaling immediate handoff to `po_drafter_agent`.

## 4. Output Format
Clear structured Markdown matching the exact policy outcome. No emojis.
"""

PO_DRAFTER_INSTRUCTION = """
## 1. Role & Objective
You are the Purchase Order Drafter. Once `state['award_authorized']` is `True`, you generate an
in-session Purchase Order draft using exact deterministic Python totals and support multi-turn
buyer edits to non-pricing metadata (ship-to location, ship-to contact, cost center, billing
instructions, and special delivery notes).

## 2. Negative Scope / Hard Boundaries
- STRICTLY and UNMISTAKABLY NEVER compute or modify unit prices, quantities, FX rates, taxes,
  or net landed totals yourself. Always rely on `build_po_draft`.
- NEVER fabricate a PO if `build_po_draft` returns `status == "BLOCKED"`.
- NEVER claim the PO was written to GCS or submitted to an external ERP system. State clearly
  that this is an in-session draft only.

## 3. Stepwise Execution Workflow
1. Always invoke `build_po_draft(...)` first, passing any buyer-requested metadata overrides
   and empty strings `""` for unchanged fields.
2. If `build_po_draft` returns `status == "BLOCKED"`, explain the exact blocker to the buyer
   and transfer back to `rfp_eval_adk` so selection/sign-off can be completed first.
3. If `status == "DRAFT_READY"`, render a clean, complete Purchase Order draft containing:
   - PO Reference, Status (`IN-SESSION DRAFT ONLY`), RFP ID & Title, Policy Version
   - Supplier Name, Vendor ID, Location, Incoterm, Certifications
   - Exact Quantity Billed, Native Currency Mandatory Subtotal & Adjustments, FX Rate,
     Net Landed USD Total, Effective Unit Cost USD
   - Separate Recoverable Tax / Gross Cash Outlay section whenever `gross_cash_outlay_usd` is present
   - Delivery SLA (days), Warranty (months), Payment Terms (and optional early-pay note if present)
   - Manager Sign-Off Approval section whenever `manager_signoff` is present
   - Buyer Metadata (`ship_to_location`, `ship_to_contact`, `cost_center`, `billing_instructions`,
     `special_delivery_notes`)
4. Invite the buyer to request metadata edits (cost center, ship-to contact, delivery notes)
   in follow-up turns. If the buyer instead asks to change vendors, run what-if weights, or
   re-evaluate the RFP, transfer back to `rfp_eval_adk`.

## 4. Output Format
Clean structured Markdown Purchase Order document. No emojis.
"""


def create_what_if_analyst_agent(model_name: str) -> LlmAgent:
    """Creates the task-mode what-if and pros/cons specialist sub-agent."""
    return LlmAgent(
        name="what_if_analyst_agent",
        model=Gemini(
            model=model_name,
            retry_options=types.HttpRetryOptions(attempts=3),
        ),
        mode="task",
        description=(
            "Runs deterministic what-if weight sensitivity analysis and answers buyer pros/cons "
            "questions using cached evaluation state with zero GCS re-reads."
        ),
        generate_content_config=types.GenerateContentConfig(temperature=0.0),
        instruction=WHAT_IF_INSTRUCTION,
        tools=[rescore_what_if, get_cached_evaluation_summary],
    )


def create_policy_signoff_agent(model_name: str) -> LlmAgent:
    """Creates the task-mode policy threshold and manager sign-off gatekeeper sub-agent."""
    return LlmAgent(
        name="policy_signoff_agent",
        model=Gemini(
            model=model_name,
            retry_options=types.HttpRetryOptions(attempts=3),
        ),
        mode="task",
        description=(
            "Validates buyer vendor selection against compliance rules and the $50,000 cap, "
            "authorizes <= $50K compliant bids for PO drafting, holds > $50K bids with a "
            "Manager Sign-Off Exception Request until manager approval is confirmed, and blocks "
            "invalid or incomplete bids (drafting a Supplier Clarification Request when applicable)."
        ),
        generate_content_config=types.GenerateContentConfig(temperature=0.0),
        instruction=POLICY_SIGNOFF_INSTRUCTION,
        tools=[evaluate_award_selection, record_manager_signoff],
    )


def create_po_drafter_agent(model_name: str) -> LlmAgent:
    """Creates the chat-mode in-session PO drafter sub-agent with Python award gate."""
    return LlmAgent(
        name="po_drafter_agent",
        model=Gemini(
            model=model_name,
            retry_options=types.HttpRetryOptions(attempts=3),
        ),
        mode="chat",
        description=(
            "Drafts an in-session Purchase Order with exact Python Decimal totals only when "
            "state['award_authorized'] is True, and supports multi-turn buyer metadata edits."
        ),
        generate_content_config=types.GenerateContentConfig(temperature=0.0),
        instruction=PO_DRAFTER_INSTRUCTION,
        tools=[build_po_draft],
    )
