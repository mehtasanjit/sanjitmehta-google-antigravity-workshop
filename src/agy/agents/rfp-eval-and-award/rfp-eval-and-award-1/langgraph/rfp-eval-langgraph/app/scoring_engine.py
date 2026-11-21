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

"""Deterministic Decimal procurement engine: normalization, compliance, scoring, gating, and PO drafting."""

from __future__ import annotations

import math
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from app.models import (
    AwardGateDecision,
    CostBreakdown,
    EvaluatedBid,
    ExtractedQuoteFacts,
    ProcurementPolicy,
    PurchaseOrderDraft,
    ScoreBreakdown,
    ScoringWeights,
)

TWO_PLACES = Decimal("0.01")
ZERO = Decimal("0.00")
HUNDRED = Decimal("100")


def _q2(value: Decimal) -> Decimal:
    """Round a Decimal to 2 decimal places using ROUND_HALF_UP."""
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def _to_decimal(raw: str | Decimal | int | float, field_name: str) -> Decimal:
    """Parse a numeric string/value strictly into Decimal."""
    if isinstance(raw, Decimal):
        return raw
    cleaned = str(raw).strip().replace(",", "").replace("$", "").replace("%", "")
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid decimal value for {field_name}: {raw!r}") from exc


def _to_fraction(percent_str: str, field_name: str) -> Decimal:
    """Convert a percentage string ('6' or '0.06') into a fractional Decimal.

    Values > 1 are treated as percentages (e.g. '6' -> 0.06, '18' -> 0.18).
    Values in (0, 1] are treated as fractional rates if <= 1 and explicitly fractional,
    except '1' which is treated as 1% (0.01).
    """
    val = _to_decimal(percent_str, field_name)
    if val < 0:
        raise ValueError(f"{field_name} cannot be negative: {val}")
    if val < Decimal("1") and "." in str(percent_str).strip():
        return val
    return val / HUNDRED


def _normalize_payment_terms(raw_terms: str, policy: ProcurementPolicy) -> str:
    """Map extracted payment terms string to a canonical key in the policy rubric."""
    cleaned = raw_terms.strip()
    valid_keys = list(policy.scoring_rubric.payment_terms_points.keys())
    lower_map = {k.lower(): k for k in valid_keys}
    if cleaned.lower() in lower_map:
        return lower_map[cleaned.lower()]
    lower = cleaned.lower()
    if "advance" in lower or "prepay" in lower or "upfront" in lower:
        return lower_map.get("advance", "Advance")
    for key in valid_keys:
        if key.lower() in lower:
            return key
    return cleaned


def _parse_iso_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(raw.strip()[:10])
    except ValueError:
        return None


def _compute_cost_and_lead_time(
    quote: ExtractedQuoteFacts,
    policy: ProcurementPolicy,
) -> tuple[CostBreakdown, int | None, list[str]]:
    """Deterministically normalize quote pricing to net landed USD and effective lead time."""
    meta = policy.rfp_metadata
    norm = policy.normalization_rules
    currency = quote.currency.upper()
    if currency not in policy.fx_rates_to_usd:
        raise ValueError(
            f"Unsupported currency {currency!r} for {quote.vendor_id}; "
            f"policy supports {sorted(policy.fx_rates_to_usd)}."
        )
    fx_rate = policy.fx_rates_to_usd[currency]
    notes: list[str] = []
    line_summary: list[str] = []

    effective_units = meta.required_quantity
    cartons_ordered: int | None = None
    base_mandatory_native = ZERO
    rebate_native = ZERO
    expedited_surcharge_native = ZERO
    exw_adder_native = ZERO
    excluded_optional_native = ZERO

    # 1. Compute base mandatory native cost by pricing structure
    if quote.pricing_structure == "master_carton" and quote.carton_pricing is not None:
        cp = quote.carton_pricing
        if cp.units_per_carton <= 0:
            raise ValueError(f"Invalid units_per_carton for {quote.vendor_id}")
        if cp.must_round_up_whole_cartons:
            cartons_ordered = math.ceil(meta.required_quantity / cp.units_per_carton)
        else:
            cartons_ordered = meta.required_quantity // cp.units_per_carton
        effective_units = cartons_ordered * cp.units_per_carton
        carton_price = _to_decimal(cp.price_per_carton_native, "price_per_carton_native")
        base_mandatory_native = _q2(Decimal(cartons_ordered) * carton_price)
        line_summary.append(
            f"{cp.sku or 'Carton'} - {cp.description}: {cartons_ordered} cartons "
            f"({effective_units} units) @ {carton_price} {currency}/carton = {base_mandatory_native} {currency}"
        )
        notes.append(
            f"Rounded {meta.required_quantity} units up to {cartons_ordered} whole cartons "
            f"({effective_units} units at {cp.units_per_carton}/carton)."
        )
        if (
            cp.volume_rebate_min_cartons is not None
            and cp.volume_rebate_percent is not None
            and cartons_ordered >= cp.volume_rebate_min_cartons
        ):
            rebate_rate = _to_fraction(cp.volume_rebate_percent, "volume_rebate_percent")
            rebate_native = _q2(base_mandatory_native * rebate_rate)
            notes.append(
                f"Applied {rebate_rate * HUNDRED:.0f}% volume rebate "
                f"(>= {cp.volume_rebate_min_cartons} cartons): -{rebate_native} {currency}."
            )
    elif quote.pricing_structure == "marginal_slabs" and quote.marginal_slabs:
        slabs = sorted(quote.marginal_slabs, key=lambda s: s.from_unit)
        remaining = meta.required_quantity
        running_total = ZERO
        for slab in slabs:
            if remaining <= 0:
                break
            slab_capacity = slab.to_unit - slab.from_unit + 1
            units_in_slab = min(remaining, slab_capacity)
            slab_price = _to_decimal(slab.unit_price_native, "unit_price_native")
            slab_subtotal = Decimal(units_in_slab) * slab_price
            running_total += slab_subtotal
            remaining -= units_in_slab
            line_summary.append(
                f"Units {slab.from_unit}-{slab.from_unit + units_in_slab - 1} "
                f"({units_in_slab} units) @ {slab_price} {currency} = {_q2(slab_subtotal)} {currency}"
            )
        if remaining > 0:
            raise ValueError(
                f"Marginal slabs for {quote.vendor_id} do not cover required quantity {meta.required_quantity}."
            )
        base_mandatory_native = _q2(running_total)
        notes.append(
            f"Marginal slab subtotal across {meta.required_quantity} units: {base_mandatory_native} {currency}."
        )
    else:
        if not quote.line_items:
            raise ValueError(f"No line items extracted for {quote.vendor_id}.")
        for item in quote.line_items:
            price = _to_decimal(item.price_native, f"line_item.{item.description}")
            if item.unit_basis == "per_unit":
                qty = meta.required_quantity if item.mandatory_for_rfp_spec else item.quantity
                subtotal = Decimal(qty) * price
            else:
                qty = item.quantity if item.quantity > 0 else 1
                subtotal = Decimal(qty) * price

            if item.mandatory_for_rfp_spec or not norm.exclude_optional_line_items:
                base_mandatory_native += subtotal
                sku_prefix = f"{item.sku} - " if item.sku else ""
                line_summary.append(
                    f"{sku_prefix}{item.description} ({item.unit_basis}, qty {qty}) "
                    f"@ {price} {currency} = {_q2(subtotal)} {currency}"
                )
            else:
                excluded_optional_native += subtotal
                notes.append(
                    f"Excluded optional line item '{item.description}' ({_q2(subtotal)} {currency}) per policy."
                )
        base_mandatory_native = _q2(base_mandatory_native)
        excluded_optional_native = _q2(excluded_optional_native)

    subtotal_after_rebate = _q2(base_mandatory_native - rebate_native)

    # 2. Effective lead time and conditional expedited freight surcharge
    effective_lead_time_days = quote.lead_time_days
    if quote.split_shipment_batches:
        effective_lead_time_days = max(b.lead_time_days for b in quote.split_shipment_batches)
        batch_desc = ", ".join(
            f"{b.units} units in {b.lead_time_days}d" for b in quote.split_shipment_batches
        )
        notes.append(
            f"Split shipment ({batch_desc}); full-quantity SLA lead time = {effective_lead_time_days} days."
        )
    elif quote.expedited_freight_option is not None:
        exp = quote.expedited_freight_option
        if exp.standard_lead_time_days > meta.max_delivery_days:
            effective_lead_time_days = exp.expedited_lead_time_days
            if effective_units > exp.min_units_for_surcharge:
                surcharge_rate = _to_fraction(exp.surcharge_percent, "surcharge_percent")
                expedited_surcharge_native = _q2(subtotal_after_rebate * surcharge_rate)
                notes.append(
                    f"Standard transit ({exp.standard_lead_time_days}d) exceeds {meta.max_delivery_days}d SLA; "
                    f"applied mandatory {surcharge_rate * HUNDRED:.0f}% expedited air freight surcharge "
                    f"({exp.expedited_lead_time_days}d delivery): +{expedited_surcharge_native} {currency}."
                )
                line_summary.append(
                    f"Mandatory Expedited Air Freight ({surcharge_rate * HUNDRED:.0f}% for {exp.expedited_lead_time_days}-day SLA) "
                    f"= {expedited_surcharge_native} {currency}"
                )

    # 3. EXW Shenzhen landed-cost adder (customs duty + international air freight)
    is_exw = quote.is_exw_shenzhen or (
        "exw" in quote.incoterm.lower() and "shenzhen" in quote.incoterm.lower()
    )
    if is_exw:
        exw_adder_native = _q2(subtotal_after_rebate * norm.exw_shenzhen_adder_pct)
        notes.append(
            f"Applied EXW Shenzhen normalization adder ({norm.exw_shenzhen_adder_pct * HUNDRED:.0f}% = "
            f"{norm.exw_shenzhen_breakdown.customs_duty_pct * HUNDRED:.0f}% customs + "
            f"{norm.exw_shenzhen_breakdown.international_air_freight_pct * HUNDRED:.0f}% air freight): "
            f"+{exw_adder_native} {currency}."
        )

    net_landed_native = _q2(
        subtotal_after_rebate + expedited_surcharge_native + exw_adder_native
    )
    net_landed_usd = _q2(net_landed_native * fx_rate)

    if currency != "USD":
        notes.append(
            f"Converted {net_landed_native} {currency} to ${net_landed_usd:,.2f} USD at FX {fx_rate}."
        )

    # 4. Indian recoverable GST ITC accounting (excluded from net landed USD, reported separately)
    india_gst_native: Decimal | None = None
    gross_cash_outlay_native: Decimal | None = None
    gross_cash_outlay_usd: Decimal | None = None
    if quote.india_gst_applicable:
        gst_rate = (
            _to_fraction(quote.india_gst_percent, "india_gst_percent")
            if quote.india_gst_percent
            else norm.india_gst_rate
        )
        india_gst_native = _q2(net_landed_native * gst_rate)
        gross_cash_outlay_native = _q2(net_landed_native + india_gst_native)
        gross_cash_outlay_usd = _q2(gross_cash_outlay_native * fx_rate)
        if norm.india_gst_recoverable_itc:
            notes.append(
                f"Excluded recoverable {gst_rate * HUNDRED:.0f}% Indian GST ITC ({india_gst_native} {currency}) "
                f"from net landed USD; gross cash outlay = {gross_cash_outlay_native} {currency} "
                f"(${gross_cash_outlay_usd:,.2f} USD)."
            )

    # 5. Optional early-payment discount (tracked separately; baseline uses standard terms)
    early_payment_net_usd: Decimal | None = None
    if quote.early_payment_discount_percent and quote.early_payment_terms:
        disc_rate = _to_fraction(
            quote.early_payment_discount_percent, "early_payment_discount_percent"
        )
        early_payment_net_usd = _q2(net_landed_usd * (Decimal("1") - disc_rate))
        notes.append(
            f"Optional {disc_rate * HUNDRED:.0f}% early-payment discount on {quote.early_payment_terms}: "
            f"${early_payment_net_usd:,.2f} USD (baseline ranked on {quote.payment_terms_standard})."
        )

    cost = CostBreakdown(
        currency=currency,
        fx_rate_to_usd=fx_rate,
        effective_units_ordered=effective_units,
        cartons_ordered=cartons_ordered,
        base_mandatory_native=base_mandatory_native,
        rebate_native=rebate_native,
        expedited_surcharge_native=expedited_surcharge_native,
        exw_adder_native=exw_adder_native,
        net_landed_native=net_landed_native,
        net_landed_usd=net_landed_usd,
        excluded_optional_native=excluded_optional_native,
        india_gst_native=india_gst_native,
        gross_cash_outlay_native=gross_cash_outlay_native,
        gross_cash_outlay_usd=gross_cash_outlay_usd,
        early_payment_net_usd=early_payment_net_usd,
        early_payment_terms=quote.early_payment_terms,
        calculation_notes=notes,
    )
    return cost, effective_lead_time_days, line_summary


def normalize_and_evaluate_bid(
    quote: ExtractedQuoteFacts,
    policy: ProcurementPolicy,
) -> EvaluatedBid:
    """Normalize a single extracted quote and run deterministic policy compliance checks."""
    meta = policy.rfp_metadata
    rules = policy.compliance_rules

    cost, effective_lead_time_days, line_summary = _compute_cost_and_lead_time(quote, policy)
    payment_terms = _normalize_payment_terms(quote.payment_terms_standard, policy)

    disqualifiers: list[str] = []
    clarifications: list[str] = []

    approved_vendor = policy.approved_vendors.get(quote.vendor_id)

    # Rule 1: Approved vendor registry (unverified verbal approvals strictly ignored)
    if rules.require_approved_vendor and approved_vendor is None:
        disqualifiers.append(
            f"Unapproved vendor ID '{quote.vendor_id}' is not in the approved vendor registry."
        )
    if quote.contains_verbal_approval_claim and rules.ignore_unverified_verbal_approvals:
        disqualifiers.append(
            "Ignored unverified verbal pre-approval / override instruction embedded in quote per procurement policy."
        ) if approved_vendor is None else None

    # Rule 2: Minimum warranty duration
    if quote.warranty_months is None:
        clarifications.append(
            f"Warranty duration is not stated; policy requires at least {meta.min_warranty_months} months."
        )
    elif quote.warranty_months < meta.min_warranty_months:
        disqualifiers.append(
            f"Warranty of {quote.warranty_months} months is below the {meta.min_warranty_months}-month minimum."
        )

    # Rule 3: Full-quantity delivery SLA
    if effective_lead_time_days is None:
        clarifications.append(
            f"Delivery lead time is not stated; policy requires <= {meta.max_delivery_days} days."
        )
    elif rules.full_quantity_must_meet_sla and effective_lead_time_days > meta.max_delivery_days:
        disqualifiers.append(
            f"Full-quantity delivery lead time of {effective_lead_time_days} days exceeds the "
            f"{meta.max_delivery_days}-day SLA."
        )

    # Rule 4: Quote validity on evaluation date -> CLARIFICATION_REQUIRED
    if rules.require_valid_quote_on_evaluation_date:
        valid_until_date = _parse_iso_date(quote.valid_until)
        if valid_until_date is None:
            clarifications.append(
                f"Quote expiration date is missing or unreadable (evaluation date: {meta.evaluation_date.isoformat()})."
            )
        elif valid_until_date < meta.evaluation_date:
            clarifications.append(
                f"Quote expired on {valid_until_date.isoformat()} (prior to evaluation date {meta.evaluation_date.isoformat()}); written quote renewal required."
            )

    # Rule 5: Explicit ingress protection certification -> CLARIFICATION_REQUIRED
    if rules.require_explicit_ingress_certification and not quote.has_explicit_ip67_certification:
        stated = quote.ingress_rating_stated or "unspecified enclosure rating"
        clarifications.append(
            f"Missing explicit {meta.required_ingress_rating} certification prior to award (quote states: '{stated}')."
        )

    # Determine compliance status (hard disqualifiers take precedence)
    if disqualifiers:
        status = "DISQUALIFIED"
        compliance_reasons = disqualifiers + clarifications
    elif clarifications:
        status = "CLARIFICATION_REQUIRED"
        compliance_reasons = clarifications
    else:
        status = "COMPLIANT"
        compliance_reasons = ["Meets all mandatory procurement policy requirements."]

    cap = rules.manager_signoff_required_above_usd
    requires_signoff = cost.net_landed_usd > cap
    cap_overage = _q2(cost.net_landed_usd - cap) if requires_signoff else ZERO

    return EvaluatedBid(
        vendor_id=quote.vendor_id,
        supplier_name=approved_vendor.name if approved_vendor else quote.supplier_name,
        source_filename=quote.source_filename,
        compliance_status=status,
        compliance_reasons=compliance_reasons,
        clarification_items=clarifications,
        verbal_approval_injection_detected=quote.contains_verbal_approval_claim,
        effective_lead_time_days=effective_lead_time_days,
        warranty_months=quote.warranty_months,
        payment_terms=payment_terms,
        track_record_tier=approved_vendor.track_record_tier if approved_vendor else None,
        vendor_prior_pos=approved_vendor.prior_pos if approved_vendor else None,
        vendor_otd_pct=approved_vendor.on_time_delivery_pct if approved_vendor else None,
        incoterm=quote.incoterm,
        valid_until=quote.valid_until,
        certifications=quote.certifications,
        cost=cost,
        requires_manager_signoff=requires_signoff,
        cap_overage_usd=cap_overage,
        score=None,
        rank=None,
        commercial_notes=quote.commercial_notes,
        line_items_summary=line_summary,
    )


def validate_scoring_weights(
    weights: ScoringWeights,
    policy: ProcurementPolicy,
) -> ScoringWeights:
    """Validate custom what-if weights (non-negative, summing to rubric total_points)."""
    for name, value in weights.as_dict().items():
        if value < ZERO:
            raise ValueError(f"Weight '{name}' cannot be negative ({value}).")
    expected_total = policy.scoring_rubric.total_points
    actual_total = weights.total()
    if actual_total != expected_total:
        raise ValueError(
            f"Scoring weights must sum to {expected_total}, but got {actual_total}."
        )
    return weights


def _delivery_base_points(days: int, policy: ProcurementPolicy) -> Decimal:
    brackets = sorted(policy.scoring_rubric.delivery_speed_brackets, key=lambda b: b.max_days)
    for bracket in brackets:
        if days <= bracket.max_days:
            return bracket.points
    return ZERO


def _warranty_base_points(months: int, policy: ProcurementPolicy) -> Decimal:
    brackets = sorted(
        policy.scoring_rubric.warranty_brackets, key=lambda b: b.min_months, reverse=True
    )
    for bracket in brackets:
        if months >= bracket.min_months:
            return bracket.points
    return ZERO


def _scale_points(
    base_points: Decimal,
    default_weight: Decimal,
    active_weight: Decimal,
) -> Decimal:
    if default_weight == ZERO:
        return ZERO
    return _q2(active_weight * (base_points / default_weight))


def score_bids(
    evaluated_bids: list[EvaluatedBid],
    policy: ProcurementPolicy,
    custom_weights: ScoringWeights | None = None,
) -> tuple[list[EvaluatedBid], list[EvaluatedBid]]:
    """Score compliant bids deterministically on the 100-point rubric.

    Returns (scored_compliant_bids_descending, non_compliant_bids_sorted).
    """
    rubric = policy.scoring_rubric
    default_weights = rubric.weights
    active_weights = (
        validate_scoring_weights(custom_weights, policy)
        if custom_weights is not None
        else default_weights
    )

    compliant = [b.model_copy(deep=True) for b in evaluated_bids if b.compliance_status == "COMPLIANT"]
    non_compliant = [
        b.model_copy(deep=True, update={"score": None, "rank": None})
        for b in evaluated_bids
        if b.compliance_status != "COMPLIANT"
    ]
    non_compliant.sort(key=lambda b: (b.compliance_status, b.source_filename, b.vendor_id))

    if not compliant:
        return [], non_compliant

    min_compliant_usd = min(b.cost.net_landed_usd for b in compliant)
    if min_compliant_usd <= ZERO:
        raise ValueError("Minimum compliant net landed USD must be positive.")

    for bid in compliant:
        cost_pts = _q2(
            active_weights.net_landed_cost * (min_compliant_usd / bid.cost.net_landed_usd)
        )
        delivery_base = _delivery_base_points(bid.effective_lead_time_days or 999, policy)
        delivery_pts = _scale_points(
            delivery_base, default_weights.delivery_speed, active_weights.delivery_speed
        )
        warranty_base = _warranty_base_points(bid.warranty_months or 0, policy)
        warranty_pts = _scale_points(
            warranty_base, default_weights.warranty_months, active_weights.warranty_months
        )
        tier_obj = (
            rubric.supplier_track_record_tiers.get(bid.track_record_tier)
            if bid.track_record_tier
            else None
        )
        track_base = tier_obj.points if tier_obj else ZERO
        track_pts = _scale_points(
            track_base,
            default_weights.supplier_track_record,
            active_weights.supplier_track_record,
        )
        payment_base = rubric.payment_terms_points.get(bid.payment_terms, ZERO)
        payment_pts = _scale_points(
            payment_base, default_weights.payment_terms, active_weights.payment_terms
        )
        total_pts = _q2(cost_pts + delivery_pts + warranty_pts + track_pts + payment_pts)
        bid.score = ScoreBreakdown(
            net_landed_cost=cost_pts,
            delivery_speed=delivery_pts,
            warranty_months=warranty_pts,
            supplier_track_record=track_pts,
            payment_terms=payment_pts,
            total_score=total_pts,
        )

    # Sort descending by total_score, tie-break by lower net_landed_usd, then vendor_id
    compliant.sort(
        key=lambda b: (
            -(b.score.total_score if b.score else ZERO),
            b.cost.net_landed_usd,
            b.vendor_id,
        )
    )
    for idx, bid in enumerate(compliant, start=1):
        bid.rank = idx

    return compliant, non_compliant


def rescore_cached_bids(
    normalized_bids: list[EvaluatedBid],
    policy: ProcurementPolicy,
    custom_weights: ScoringWeights,
) -> tuple[list[EvaluatedBid], list[EvaluatedBid]]:
    """Rescore cached normalized bids in memory with zero GCS reads."""
    return score_bids(normalized_bids, policy, custom_weights=custom_weights)


def resolve_vendor_bid(
    vendor_query: str,
    evaluated_bids: list[EvaluatedBid],
) -> EvaluatedBid | None:
    """Resolve a buyer's vendor reference by vendor ID or supplier name."""
    query = vendor_query.strip().lower()
    if not query:
        return None
    for bid in evaluated_bids:
        if bid.vendor_id.lower() == query:
            return bid
    for bid in evaluated_bids:
        if bid.supplier_name.lower() == query:
            return bid
    matches = [
        bid
        for bid in evaluated_bids
        if query in bid.supplier_name.lower()
        or query in bid.vendor_id.lower()
        or bid.supplier_name.lower().split()[0] in query
    ]
    if len(matches) == 1:
        return matches[0]
    return None


def evaluate_award_gate(
    vendor_query: str,
    evaluated_bids: list[EvaluatedBid],
    policy: ProcurementPolicy,
    manager_signoff: dict[str, str] | None = None,
) -> AwardGateDecision:
    """Enforce deterministic compliance and $50K cap / manager sign-off gating."""
    bid = resolve_vendor_bid(vendor_query, evaluated_bids)
    cap = policy.compliance_rules.manager_signoff_required_above_usd

    if bid is None:
        return AwardGateDecision(
            outcome="NOT_FOUND",
            award_authorized=False,
            pending_manager_signoff=False,
            reasons=[
                f"Could not uniquely match vendor '{vendor_query}' to any evaluated quote."
            ],
            cap_usd=cap,
        )

    if bid.compliance_status == "DISQUALIFIED":
        return AwardGateDecision(
            outcome="BLOCKED_DISQUALIFIED",
            vendor_id=bid.vendor_id,
            supplier_name=bid.supplier_name,
            award_authorized=False,
            pending_manager_signoff=False,
            reasons=bid.compliance_reasons,
            net_landed_usd=bid.cost.net_landed_usd,
            cap_usd=cap,
            cap_overage_usd=bid.cap_overage_usd,
        )

    if bid.compliance_status == "CLARIFICATION_REQUIRED":
        return AwardGateDecision(
            outcome="BLOCKED_CLARIFICATION",
            vendor_id=bid.vendor_id,
            supplier_name=bid.supplier_name,
            award_authorized=False,
            pending_manager_signoff=False,
            reasons=bid.compliance_reasons,
            clarification_items=bid.clarification_items,
            net_landed_usd=bid.cost.net_landed_usd,
            cap_usd=cap,
            cap_overage_usd=bid.cap_overage_usd,
        )

    # Compliant bid: enforce <= cap vs > cap manager sign-off
    if bid.cost.net_landed_usd <= cap:
        return AwardGateDecision(
            outcome="AUTHORIZED",
            vendor_id=bid.vendor_id,
            supplier_name=bid.supplier_name,
            award_authorized=True,
            pending_manager_signoff=False,
            reasons=[
                f"{bid.supplier_name} ({bid.vendor_id}) is COMPLIANT and net landed cost "
                f"${bid.cost.net_landed_usd:,.2f} USD is within the ${cap:,.2f} USD auto-approval cap."
            ],
            net_landed_usd=bid.cost.net_landed_usd,
            cap_usd=cap,
            cap_overage_usd=ZERO,
        )

    # Above cap: require explicit manager sign-off record
    if manager_signoff and manager_signoff.get("approved") == "true" and manager_signoff.get("approver"):
        return AwardGateDecision(
            outcome="AUTHORIZED",
            vendor_id=bid.vendor_id,
            supplier_name=bid.supplier_name,
            award_authorized=True,
            pending_manager_signoff=False,
            reasons=[
                f"{bid.supplier_name} ({bid.vendor_id}) exceeds the ${cap:,.2f} USD cap by "
                f"${bid.cap_overage_usd:,.2f} USD, and manager sign-off was recorded by "
                f"{manager_signoff['approver']}."
            ],
            net_landed_usd=bid.cost.net_landed_usd,
            cap_usd=cap,
            cap_overage_usd=bid.cap_overage_usd,
            manager_signoff_record=manager_signoff,
        )

    return AwardGateDecision(
        outcome="MANAGER_SIGNOFF_REQUIRED",
        vendor_id=bid.vendor_id,
        supplier_name=bid.supplier_name,
        award_authorized=False,
        pending_manager_signoff=True,
        reasons=[
            f"{bid.supplier_name} ({bid.vendor_id}) net landed cost of ${bid.cost.net_landed_usd:,.2f} USD "
            f"exceeds the ${cap:,.2f} USD auto-approval cap by ${bid.cap_overage_usd:,.2f} USD. "
            "Explicit manager sign-off is required before drafting a PO."
        ],
        net_landed_usd=bid.cost.net_landed_usd,
        cap_usd=cap,
        cap_overage_usd=bid.cap_overage_usd,
    )


def build_po_draft(
    bid: EvaluatedBid,
    policy: ProcurementPolicy,
    *,
    award_authorized: bool,
    manager_signoff_record: dict[str, str] | None = None,
    existing_draft: PurchaseOrderDraft | None = None,
    ship_to_contact: str | None = None,
    cost_center: str | None = None,
    delivery_instructions: str | None = None,
    apply_early_payment_discount: bool | None = None,
) -> PurchaseOrderDraft:
    """Deterministically build or revise an in-session PO draft.

    Hard Python gate: refuses to draft unless award_authorized is True, the bid
    is COMPLIANT, and any > cap requirement has recorded manager sign-off.
    """
    if not award_authorized:
        raise PermissionError(
            "PO drafting blocked: award_authorized must be True before drafting a PO."
        )
    if bid.compliance_status != "COMPLIANT":
        raise PermissionError(
            f"PO drafting blocked: vendor {bid.vendor_id} has status {bid.compliance_status}."
        )
    cap = policy.compliance_rules.manager_signoff_required_above_usd
    if bid.cost.net_landed_usd > cap:
        if not (
            manager_signoff_record
            and manager_signoff_record.get("approved") == "true"
            and manager_signoff_record.get("approver")
        ):
            raise PermissionError(
                f"PO drafting blocked: vendor {bid.vendor_id} (${bid.cost.net_landed_usd:,.2f}) "
                f"exceeds ${cap:,.2f} cap without recorded manager sign-off."
            )

    use_early_pay = (
        apply_early_payment_discount
        if apply_early_payment_discount is not None
        else (existing_draft.early_payment_applied if existing_draft else False)
    )

    if use_early_pay and bid.cost.early_payment_net_usd is not None and bid.cost.early_payment_terms:
        net_usd = bid.cost.early_payment_net_usd
        net_native = _q2(net_usd / bid.cost.fx_rate_to_usd)
        payment_terms = f"{bid.cost.early_payment_terms} (2% early-payment discount applied)"
        early_applied = True
    else:
        net_usd = bid.cost.net_landed_usd
        net_native = bid.cost.net_landed_native
        payment_terms = bid.payment_terms
        early_applied = False

    if bid.cost.net_landed_usd > cap and manager_signoff_record:
        approval_basis = (
            f"Manager sign-off approved by {manager_signoff_record['approver']} "
            f"(net landed ${bid.cost.net_landed_usd:,.2f} > ${cap:,.2f} cap)"
        )
    else:
        approval_basis = f"Buyer auto-approved within ${cap:,.2f} USD cap"

    gst_note = (
        policy.normalization_rules.gst_accounting_note
        if bid.cost.gross_cash_outlay_usd is not None
        else None
    )

    revision = (existing_draft.revision + 1) if existing_draft else 1
    return PurchaseOrderDraft(
        po_number=f"PO-DRAFT-{policy.rfp_metadata.rfp_id}-{bid.vendor_id}",
        rfp_id=policy.rfp_metadata.rfp_id,
        vendor_id=bid.vendor_id,
        supplier_name=bid.supplier_name,
        incoterm=bid.incoterm,
        effective_units=bid.cost.effective_units_ordered,
        cartons_ordered=bid.cost.cartons_ordered,
        currency=bid.cost.currency,
        fx_rate_to_usd=bid.cost.fx_rate_to_usd,
        net_landed_native=net_native,
        net_landed_usd=net_usd,
        gross_cash_outlay_native=bid.cost.gross_cash_outlay_native,
        gross_cash_outlay_usd=bid.cost.gross_cash_outlay_usd,
        gst_note=gst_note,
        payment_terms=payment_terms,
        early_payment_applied=early_applied,
        lead_time_days=bid.effective_lead_time_days or policy.rfp_metadata.max_delivery_days,
        warranty_months=bid.warranty_months or policy.rfp_metadata.min_warranty_months,
        line_items_summary=bid.line_items_summary,
        approval_basis=approval_basis,
        manager_signoff_record=manager_signoff_record,
        ship_to_location=policy.rfp_metadata.target_incoterm,
        ship_to_contact=(
            ship_to_contact
            if ship_to_contact is not None
            else (existing_draft.ship_to_contact if existing_draft else None)
        ),
        cost_center=(
            cost_center
            if cost_center is not None
            else (existing_draft.cost_center if existing_draft else None)
        ),
        delivery_instructions=(
            delivery_instructions
            if delivery_instructions is not None
            else (existing_draft.delivery_instructions if existing_draft else None)
        ),
        revision=revision,
    )


# ---------------------------------------------------------------------------
# Deterministic Markdown Renderers (numbers always locked in Python)
# ---------------------------------------------------------------------------


def format_evaluation_tables_markdown(
    scored_bids: list[EvaluatedBid],
    non_compliant_bids: list[EvaluatedBid],
    policy: ProcurementPolicy,
    active_weights: ScoringWeights | None = None,
    previous_ranks: dict[str, int] | None = None,
) -> str:
    """Render deterministic compliant rankings and non-compliant audit table."""
    weights = active_weights or policy.scoring_rubric.weights
    cap = policy.compliance_rules.manager_signoff_required_above_usd
    lines: list[str] = [
        f"### {policy.rfp_metadata.rfp_id}: {policy.rfp_metadata.title}",
        f"Policy v{policy.policy_version} | Eval Date: {policy.rfp_metadata.evaluation_date.isoformat()} | "
        f"Target: {policy.rfp_metadata.required_quantity:,} units, {policy.rfp_metadata.target_incoterm}, "
        f"<= {policy.rfp_metadata.max_delivery_days}d, {policy.rfp_metadata.required_ingress_rating}, "
        f">= {policy.rfp_metadata.min_warranty_months}m warranty | Auto-Approval Cap: ${cap:,.2f} USD",
        f"Weights: Cost {weights.net_landed_cost} | Delivery {weights.delivery_speed} | "
        f"Warranty {weights.warranty_months} | Track Record {weights.supplier_track_record} | "
        f"Payment {weights.payment_terms}",
        "",
        "#### Compliant Bids Ranked (100-Point Rubric)",
    ]

    if previous_ranks:
        lines.append(
            "| Rank | Delta | Vendor | Net Landed USD | Gross Cash USD (w/ GST) | Lead Time | Warranty | Payment | Cost | Deliv | Warr | Track | Pay | Total | Cap Gate |"
        )
        lines.append(
            "|---:|:---:|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|"
        )
    else:
        lines.append(
            "| Rank | Vendor | Net Landed USD | Gross Cash USD (w/ GST) | Lead Time | Warranty | Payment | Cost | Deliv | Warr | Track | Pay | Total | Cap Gate |"
        )
        lines.append(
            "|---:|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|"
        )

    for bid in scored_bids:
        s = bid.score
        assert s is not None
        gross_col = (
            f"${bid.cost.gross_cash_outlay_usd:,.2f}"
            if bid.cost.gross_cash_outlay_usd is not None
            else "-"
        )
        cap_col = (
            f"Sign-off req (+${bid.cap_overage_usd:,.2f})"
            if bid.requires_manager_signoff
            else "Auto-approvable (<= $50K)"
        )
        if previous_ranks:
            old = previous_ranks.get(bid.vendor_id)
            if old is None or bid.rank is None:
                delta_str = "-"
            elif old > bid.rank:
                delta_str = f"+{old - bid.rank}"
            elif old < bid.rank:
                delta_str = f"-{bid.rank - old}"
            else:
                delta_str = "0"
            lines.append(
                f"| {bid.rank} | {delta_str} | {bid.supplier_name} ({bid.vendor_id}) | "
                f"${bid.cost.net_landed_usd:,.2f} | {gross_col} | {bid.effective_lead_time_days}d | "
                f"{bid.warranty_months}m | {bid.payment_terms} | {s.net_landed_cost:.2f} | "
                f"{s.delivery_speed:.2f} | {s.warranty_months:.2f} | {s.supplier_track_record:.2f} | "
                f"{s.payment_terms:.2f} | **{s.total_score:.2f}** | {cap_col} |"
            )
        else:
            lines.append(
                f"| {bid.rank} | {bid.supplier_name} ({bid.vendor_id}) | "
                f"${bid.cost.net_landed_usd:,.2f} | {gross_col} | {bid.effective_lead_time_days}d | "
                f"{bid.warranty_months}m | {bid.payment_terms} | {s.net_landed_cost:.2f} | "
                f"{s.delivery_speed:.2f} | {s.warranty_months:.2f} | {s.supplier_track_record:.2f} | "
                f"{s.payment_terms:.2f} | **{s.total_score:.2f}** | {cap_col} |"
            )

    if non_compliant_bids:
        lines.extend(
            [
                "",
                "#### Non-Compliant Bids",
                "| Vendor | Status | Normalized Net USD | Policy Findings |",
                "|---|---|---:|---|",
            ]
        )
        for bid in non_compliant_bids:
            findings = "; ".join(bid.compliance_reasons)
            lines.append(
                f"| {bid.supplier_name} ({bid.vendor_id}) | `{bid.compliance_status}` | "
                f"${bid.cost.net_landed_usd:,.2f} | {findings} |"
            )

    return "\n".join(lines)


def format_signoff_request_markdown(
    decision: AwardGateDecision,
    bid: EvaluatedBid,
    policy: ProcurementPolicy,
) -> str:
    """Render deterministic conversational Manager Sign-Off Request packet."""
    score_str = f"{bid.score.total_score:.2f}/100 (Rank #{bid.rank})" if bid.score else "N/A"
    return "\n".join(
        [
            "### Manager Sign-Off Required (PO Held)",
            "",
            f"- **RFP:** {policy.rfp_metadata.rfp_id} ({policy.rfp_metadata.title})",
            f"- **Selected Vendor:** {bid.supplier_name} ({bid.vendor_id})",
            f"- **Rubric Score:** {score_str}",
            f"- **Net Landed Cost:** ${bid.cost.net_landed_usd:,.2f} USD ({bid.cost.net_landed_native:,.2f} {bid.cost.currency})",
            f"- **Auto-Approval Cap:** ${decision.cap_usd:,.2f} USD",
            f"- **Amount Over Cap:** ${decision.cap_overage_usd:,.2f} USD",
            f"- **Commercial Terms:** {bid.incoterm} | {bid.effective_lead_time_days}d lead time | {bid.warranty_months}m warranty | {bid.payment_terms}",
            "- **Award Authorization Status:** `award_authorized=False` (no PO drafted)",
            "",
            "To proceed with drafting the PO, reply with explicit manager approval naming the approver "
            '(for example: "Manager approved by Jane Doe, VP Procurement"). '
            "To decline or switch to an under-cap vendor (such as DeccanTech Systems, EuroSense GmbH, QuantumGrid Automation, or BharatSense Controls), reply with your rejection or new vendor choice.",
        ]
    )


def format_clarification_draft_markdown(
    decision: AwardGateDecision,
    bid: EvaluatedBid,
    policy: ProcurementPolicy,
) -> str:
    """Render deterministic in-session supplier clarification draft for incomplete bids."""
    bullet_items = "\n".join(f"{i}. {item}" for i, item in enumerate(decision.clarification_items, start=1))
    return "\n".join(
        [
            f"### Award Blocked (`CLARIFICATION_REQUIRED`): {bid.supplier_name} ({bid.vendor_id})",
            "",
            "This bid cannot be awarded or converted into a PO until the supplier resolves the open compliance items below (`award_authorized=False`).",
            "",
            "#### In-Session Supplier Clarification Request Draft",
            f"**Subject:** Clarification Required - {policy.rfp_metadata.rfp_id} ({bid.supplier_name} / {bid.vendor_id})",
            "",
            f"Hello {bid.supplier_name} Sales Team,",
            "",
            f"Thank you for your submission for {policy.rfp_metadata.rfp_id} ({policy.rfp_metadata.title}). "
            "Before we can include your bid in final award consideration, please provide written confirmation on the following mandatory items:",
            "",
            bullet_items,
            "",
            "Please reply with the updated documentation and valid quote dates at your earliest convenience.",
            "",
            "Regards,",
            "Enterprise Procurement Team",
        ]
    )


def format_po_draft_markdown(po: PurchaseOrderDraft) -> str:
    """Render deterministic in-session Purchase Order draft."""
    lines = [
        f"### In-Session Purchase Order Draft (`{po.po_number}` | Rev {po.revision})",
        "",
        f"- **Status:** `{po.status}` (in-session only; not transmitted externally)",
        f"- **RFP Reference:** {po.rfp_id}",
        f"- **Supplier:** {po.supplier_name} (`{po.vendor_id}`)",
        f"- **Approval Basis:** {po.approval_basis}",
        f"- **Incoterm / Ship-To:** {po.incoterm} ({po.ship_to_location})",
        f"- **Quantity:** {po.effective_units:,} units"
        + (f" ({po.cartons_ordered} master cartons)" if po.cartons_ordered else ""),
        f"- **Delivery Lead Time:** {po.lead_time_days} calendar days",
        f"- **Warranty:** {po.warranty_months} months",
        f"- **Payment Terms:** {po.payment_terms}",
        f"- **Net Landed Total (Native):** {po.net_landed_native:,.2f} {po.currency} (FX: {po.fx_rate_to_usd})",
        f"- **Net Landed Total (USD):** **${po.net_landed_usd:,.2f} USD**",
    ]
    if po.gross_cash_outlay_usd is not None and po.gross_cash_outlay_native is not None:
        lines.append(
            f"- **Gross Cash Outlay (incl. 18% Recoverable Indian GST ITC):** "
            f"{po.gross_cash_outlay_native:,.2f} {po.currency} (${po.gross_cash_outlay_usd:,.2f} USD)"
        )
    if po.gst_note:
        lines.append(f"- **Tax Accounting Note:** {po.gst_note}")
    if po.ship_to_contact:
        lines.append(f"- **Ship-To Contact:** {po.ship_to_contact}")
    if po.cost_center:
        lines.append(f"- **Cost Center:** {po.cost_center}")
    if po.delivery_instructions:
        lines.append(f"- **Delivery Instructions:** {po.delivery_instructions}")
    if po.line_items_summary:
        lines.append("")
        lines.append("#### Mandatory Line Items")
        for item in po.line_items_summary:
            lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Reply with any PO metadata edits you want to make in-session (for example: ship-to contact, cost center, delivery instructions, or applying a quoted early-payment discount if available).",
        ]
    )
    return "\n".join(lines)
