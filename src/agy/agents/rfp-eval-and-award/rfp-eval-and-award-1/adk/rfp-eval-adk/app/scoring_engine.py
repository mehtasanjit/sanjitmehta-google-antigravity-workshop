"""Deterministic Python procurement normalization, compliance, scoring, and award engine.

Uses decimal.Decimal exclusively for all currency, FX, surcharge, rebate, tax,
rubric scoring, what-if rescoring, and PO total calculations. Zero LLM arithmetic.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from typing import Any

from app.models import (
    EvaluatedBid,
    EvaluationSummary,
    ExtractedBid,
    ProcurementPolicy,
    ScoreBreakdown,
)

TWO_PLACES = Decimal("0.01")
FOUR_PLACES = Decimal("0.0001")
HUNDRED = Decimal("100")

REQUIRED_RUBRIC_KEYS = (
    "net_landed_cost",
    "delivery_speed",
    "warranty_months",
    "supplier_track_record",
    "payment_terms",
)


def _d(value: int | float | str | Decimal) -> Decimal:
    """Converts numeric input to Decimal via string to avoid binary float artifacts."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _q2(value: Decimal) -> Decimal:
    """Rounds a Decimal to 2 decimal places using standard half-up rounding."""
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def _fmt2(value: Decimal) -> str:
    """Formats a Decimal to 2 decimal places."""
    return f"{_q2(value):.2f}"


def _parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def _is_exw_shenzhen(incoterm: str) -> bool:
    lowered = incoterm.lower()
    return "exw" in lowered and "shenzhen" in lowered


def _compute_full_quantity_lead_time(
    bid: ExtractedBid, required_quantity: int
) -> tuple[int, list[str]]:
    """Computes effective full-quantity delivery lead time in calendar days."""
    notes: list[str] = []
    if bid.delivery_batches:
        total_batch_units = sum(batch.units for batch in bid.delivery_batches)
        max_batch_days = max(batch.lead_time_days for batch in bid.delivery_batches)
        if total_batch_units < required_quantity:
            notes.append(
                f"Split shipment batches total {total_batch_units} units, below required "
                f"{required_quantity} units."
            )
        return max_batch_days, notes
    return bid.lead_time_days, notes


def _compute_native_pricing(
    bid: ExtractedBid, policy: ProcurementPolicy
) -> dict[str, Any]:
    """Deterministically normalizes native currency subtotal, adders, rebates, and GST."""
    required_qty = policy.rfp_metadata.required_quantity
    exclude_optional = policy.normalization_rules.exclude_optional_line_items

    adjustments: list[str] = []
    excluded_optional: list[str] = []
    quantity_billed = required_qty

    # 1. Base mandatory subtotal in native currency
    if bid.pricing_model == "carton":
        if bid.carton_pricing is None:
            raise ValueError(
                f"Bid {bid.vendor_id} ({bid.source_filename}) uses pricing_model='carton' "
                "but carton_pricing is missing."
            )
        cp = bid.carton_pricing
        if cp.units_per_carton <= 0:
            raise ValueError(f"Invalid units_per_carton={cp.units_per_carton} for {bid.vendor_id}")

        if cp.round_up_to_whole_cartons:
            cartons = ceil(required_qty / cp.units_per_carton)
        else:
            cartons = required_qty // cp.units_per_carton

        quantity_billed = cartons * cp.units_per_carton
        base_subtotal = _d(cartons) * _d(cp.price_per_carton)
        adjustments.append(
            f"Whole-carton rounding: {cartons} cartons x {cp.units_per_carton} units = "
            f"{quantity_billed} units at {_fmt2(_d(cp.price_per_carton))} {bid.currency}/carton"
        )

        # Automatic volume rebate on carton subtotal
        net_native = base_subtotal
        if (
            cp.volume_rebate_min_cartons is not None
            and cartons >= cp.volume_rebate_min_cartons
            and cp.volume_rebate_percent > 0
        ):
            rebate_rate = _d(cp.volume_rebate_percent) / HUNDRED
            rebate_amount = base_subtotal * rebate_rate
            net_native = base_subtotal - rebate_amount
            adjustments.append(
                f"Volume rebate ({cp.volume_rebate_percent:g}% for >= {cp.volume_rebate_min_cartons} "
                f"cartons): -{_fmt2(rebate_amount)} {bid.currency}"
            )

    elif bid.pricing_model == "marginal_slabs":
        if not bid.price_slabs:
            raise ValueError(
                f"Bid {bid.vendor_id} ({bid.source_filename}) uses pricing_model='marginal_slabs' "
                "but price_slabs is empty."
            )
        base_subtotal = Decimal("0")
        covered_units = 0
        for slab in sorted(bid.price_slabs, key=lambda s: s.from_unit):
            upper = min(required_qty, slab.to_unit)
            if upper < slab.from_unit:
                continue
            slab_units = upper - slab.from_unit + 1
            slab_cost = _d(slab_units) * _d(slab.unit_price)
            base_subtotal += slab_cost
            covered_units += slab_units
            adjustments.append(
                f"Marginal slab units {slab.from_unit}-{upper} ({slab_units} units x "
                f"{_fmt2(_d(slab.unit_price))} {bid.currency}) = {_fmt2(slab_cost)} {bid.currency}"
            )
        if covered_units < required_qty:
            raise ValueError(
                f"Marginal slabs for {bid.vendor_id} only cover {covered_units}/{required_qty} units."
            )
        net_native = base_subtotal

    else:  # line_items
        if not bid.line_items:
            raise ValueError(
                f"Bid {bid.vendor_id} ({bid.source_filename}) uses pricing_model='line_items' "
                "but line_items is empty."
            )
        base_subtotal = Decimal("0")
        for item in bid.line_items:
            if not item.mandatory_for_rfp_spec and exclude_optional:
                opt_total = (
                    _d(required_qty) * _d(item.price)
                    if item.unit_basis == "per_unit"
                    else _d(item.quantity) * _d(item.price)
                )
                excluded_optional.append(
                    f"{item.description} ({_fmt2(opt_total)} {bid.currency})"
                )
                continue

            if item.unit_basis == "per_unit":
                line_qty = required_qty
                line_total = _d(line_qty) * _d(item.price)
                adjustments.append(
                    f"Mandatory line '{item.description}': {line_qty} x "
                    f"{_fmt2(_d(item.price))} = {_fmt2(line_total)} {bid.currency}"
                )
            else:
                line_qty = max(item.quantity, 1)
                line_total = _d(line_qty) * _d(item.price)
                adjustments.append(
                    f"Mandatory flat line '{item.description}': {line_qty} x "
                    f"{_fmt2(_d(item.price))} = {_fmt2(line_total)} {bid.currency}"
                )
            base_subtotal += line_total
        net_native = base_subtotal

    # 2. Required percentage surcharges (e.g., expedited air freight for SLA)
    for surcharge in bid.percentage_surcharges:
        if not surcharge.required_for_sla_or_spec:
            continue
        if surcharge.percent <= 0:
            continue
        rate = _d(surcharge.percent) / HUNDRED
        surcharge_amount = net_native * rate
        net_native += surcharge_amount
        adjustments.append(
            f"Mandatory surcharge '{surcharge.description}' ({surcharge.percent:g}%): "
            f"+{_fmt2(surcharge_amount)} {bid.currency}"
        )

    # 3. EXW Shenzhen normalization adder from policy
    if _is_exw_shenzhen(bid.incoterm):
        adder_pct = _d(policy.normalization_rules.exw_shenzhen_adder_pct)
        adder_amount = net_native * adder_pct
        net_native += adder_amount
        bd = policy.normalization_rules.exw_shenzhen_breakdown
        adjustments.append(
            f"EXW Shenzhen DDP normalization (+{adder_pct * HUNDRED:.0f}%: "
            f"{_d(bd.customs_duty_pct) * HUNDRED:.0f}% customs duty + "
            f"{_d(bd.international_air_freight_pct) * HUNDRED:.0f}% air freight): "
            f"+{_fmt2(adder_amount)} {bid.currency}"
        )

    # 4. Recoverable Indian GST ITC handling (exclude from net landed comparison, report gross separately)
    recoverable_tax_name: str | None = None
    recoverable_tax_native: Decimal | None = None
    gross_cash_outlay_native: Decimal | None = None

    tax = bid.tax_details
    if tax.tax_applicable and tax.tax_percent > 0:
        tax_rate = _d(tax.tax_percent) / HUNDRED
        is_recoverable = (
            tax.recoverable_itc and policy.normalization_rules.india_gst_recoverable_itc
        )
        if is_recoverable:
            recoverable_tax_name = tax.tax_name or "Indian GST (ITC Recoverable)"
            if tax.prices_exclusive_of_tax:
                recoverable_tax_native = net_native * tax_rate
                gross_cash_outlay_native = net_native + recoverable_tax_native
            else:
                gross_cash_outlay_native = net_native
                net_native = gross_cash_outlay_native / (Decimal("1") + tax_rate)
                recoverable_tax_native = gross_cash_outlay_native - net_native
            adjustments.append(
                f"Excluded recoverable {recoverable_tax_name} ({tax.tax_percent:g}% ITC = "
                f"{_fmt2(recoverable_tax_native)} {bid.currency}) from net landed comparison; "
                f"gross cash outlay = {_fmt2(gross_cash_outlay_native)} {bid.currency}"
            )
        elif tax.prices_exclusive_of_tax:
            non_recoverable_tax = net_native * tax_rate
            net_native += non_recoverable_tax
            adjustments.append(
                f"Non-recoverable tax '{tax.tax_name}' ({tax.tax_percent:g}%): "
                f"+{_fmt2(non_recoverable_tax)} {bid.currency}"
            )

    # 5. FX conversion to USD
    if bid.currency not in policy.fx_rates_to_usd:
        raise ValueError(
            f"Currency '{bid.currency}' for {bid.vendor_id} is not defined in policy fx_rates_to_usd."
        )
    fx_rate = _d(policy.fx_rates_to_usd[bid.currency])
    net_landed_usd = net_native * fx_rate
    gross_cash_outlay_usd = (
        gross_cash_outlay_native * fx_rate if gross_cash_outlay_native is not None else None
    )
    effective_unit_usd = net_landed_usd / _d(required_qty)

    return {
        "quantity_billed": quantity_billed,
        "base_subtotal": base_subtotal,
        "net_native": net_native,
        "fx_rate": fx_rate,
        "net_landed_usd": net_landed_usd,
        "effective_unit_usd": effective_unit_usd,
        "adjustments": adjustments,
        "excluded_optional": excluded_optional,
        "recoverable_tax_name": recoverable_tax_name,
        "recoverable_tax_native": recoverable_tax_native,
        "gross_cash_outlay_native": gross_cash_outlay_native,
        "gross_cash_outlay_usd": gross_cash_outlay_usd,
    }


def _classify_compliance(
    bid: ExtractedBid,
    full_lead_time_days: int,
    batch_notes: list[str],
    policy: ProcurementPolicy,
) -> tuple[str, list[str], list[str], bool]:
    """Deterministically classifies COMPLIANT, CLARIFICATION_REQUIRED, or DISQUALIFIED."""
    rules = policy.compliance_rules
    meta = policy.rfp_metadata
    disqualify_reasons: list[str] = []
    clarification_items: list[str] = []

    verbal_ignored = bool(
        bid.contains_unverified_verbal_approval_claim
        and rules.ignore_unverified_verbal_approvals
    )

    # Hard Disqualification Checks
    approved = bid.vendor_id in policy.approved_vendors
    if rules.require_approved_vendor and not approved:
        reason = (
            f"Vendor ID '{bid.vendor_id}' ({bid.supplier_name}) is not in the approved vendor registry."
        )
        if verbal_ignored:
            reason += " Unverified verbal pre-approval note ignored per procurement policy."
        disqualify_reasons.append(reason)

    if rules.full_quantity_must_meet_sla and full_lead_time_days > meta.max_delivery_days:
        disqualify_reasons.append(
            f"Full-quantity delivery lead time ({full_lead_time_days} days) exceeds maximum "
            f"SLA of {meta.max_delivery_days} days."
        )
    disqualify_reasons.extend(batch_notes)

    if bid.warranty_months < meta.min_warranty_months:
        disqualify_reasons.append(
            f"Warranty ({bid.warranty_months} months) is below minimum policy requirement "
            f"of {meta.min_warranty_months} months."
        )

    # Clarification Checks (expired quote or missing explicit ingress certification)
    eval_date = _parse_iso_date(meta.evaluation_date)
    valid_until_date = _parse_iso_date(bid.valid_until)
    if rules.require_valid_quote_on_evaluation_date and eval_date is not None:
        if valid_until_date is None:
            clarification_items.append(
                f"Quote validity date is missing; must confirm validity on evaluation date {meta.evaluation_date}."
            )
        elif valid_until_date < eval_date:
            clarification_items.append(
                f"Quote expired on {bid.valid_until} (prior to evaluation date {meta.evaluation_date}); "
                "requires written validity extension."
            )

    if rules.require_explicit_ingress_certification:
        required_rating = meta.required_ingress_rating.upper()
        stated = (bid.ingress_rating_stated or "").upper()
        has_explicit_rating = bid.explicit_ingress_certified and (required_rating in stated)
        if not has_explicit_rating:
            clarification_items.append(
                f"Missing explicit {meta.required_ingress_rating} ingress certification "
                f"(stated: '{bid.ingress_rating_stated or 'unspecified'}'); requires formal "
                f"{meta.required_ingress_rating} test certificate prior to award."
            )

    if disqualify_reasons:
        all_reasons = disqualify_reasons + clarification_items
        return "DISQUALIFIED", all_reasons, clarification_items, verbal_ignored

    if clarification_items:
        return "CLARIFICATION_REQUIRED", clarification_items, clarification_items, verbal_ignored

    return "COMPLIANT", [], [], verbal_ignored


def _score_delivery_speed(
    lead_time_days: int, policy: ProcurementPolicy, weight: Decimal
) -> Decimal:
    default_weight = _d(policy.scoring_rubric.weights["delivery_speed"])
    brackets = sorted(policy.scoring_rubric.delivery_speed_brackets, key=lambda b: b.max_days)
    raw_points = Decimal("0")
    for bracket in brackets:
        if lead_time_days <= bracket.max_days:
            raw_points = _d(bracket.points)
            break
    if default_weight == 0:
        return Decimal("0")
    return (raw_points / default_weight) * weight


def _score_warranty(
    warranty_months: int, policy: ProcurementPolicy, weight: Decimal
) -> Decimal:
    default_weight = _d(policy.scoring_rubric.weights["warranty_months"])
    brackets = sorted(
        policy.scoring_rubric.warranty_brackets, key=lambda b: b.min_months, reverse=True
    )
    raw_points = Decimal("0")
    for bracket in brackets:
        if warranty_months >= bracket.min_months:
            raw_points = _d(bracket.points)
            break
    if default_weight == 0:
        return Decimal("0")
    return (raw_points / default_weight) * weight


def _score_track_record(
    tier_key: str | None, policy: ProcurementPolicy, weight: Decimal
) -> Decimal:
    default_weight = _d(policy.scoring_rubric.weights["supplier_track_record"])
    tiers = policy.scoring_rubric.supplier_track_record_tiers
    if not tier_key or tier_key not in tiers or default_weight == 0:
        return Decimal("0")
    raw_points = _d(tiers[tier_key].points)
    return (raw_points / default_weight) * weight


def _score_payment_terms(
    payment_terms: str, policy: ProcurementPolicy, weight: Decimal
) -> Decimal:
    default_weight = _d(policy.scoring_rubric.weights["payment_terms"])
    pts_map = policy.scoring_rubric.payment_terms_points
    if payment_terms not in pts_map or default_weight == 0:
        return Decimal("0")
    raw_points = _d(pts_map[payment_terms])
    return (raw_points / default_weight) * weight


def validate_weights(
    weights: dict[str, float | int | str | Decimal], total_points: float = 100.0
) -> dict[str, Decimal]:
    """Validates rubric weights cover all 5 criteria, are non-negative, and sum to total_points."""
    missing = [k for k in REQUIRED_RUBRIC_KEYS if k not in weights]
    extra = [k for k in weights if k not in REQUIRED_RUBRIC_KEYS]
    if missing:
        raise ValueError(f"Missing required scoring weight keys: {missing}")
    if extra:
        raise ValueError(f"Unknown scoring weight keys: {extra}")

    dec_weights: dict[str, Decimal] = {}
    weight_sum = Decimal("0")
    for key in REQUIRED_RUBRIC_KEYS:
        val = _d(weights[key])
        if val < 0:
            raise ValueError(f"Weight '{key}' cannot be negative: {val}")
        dec_weights[key] = val
        weight_sum += val

    expected_total = _d(total_points)
    if weight_sum != expected_total:
        raise ValueError(
            f"Scoring weights must sum to {expected_total}, got {weight_sum}."
        )
    return dec_weights


def _apply_rubric_scores(
    compliant_bids: list[EvaluatedBid],
    policy: ProcurementPolicy,
    weights: dict[str, Decimal],
) -> tuple[list[EvaluatedBid], str | None]:
    """Deterministically scores and ranks COMPLIANT bids using Decimal arithmetic."""
    if not compliant_bids:
        return [], None

    exact_costs = {b.vendor_id: _d(b.net_landed_usd) for b in compliant_bids}
    min_cost = min(exact_costs.values())

    scored: list[EvaluatedBid] = []
    for bid in compliant_bids:
        bid_cost = exact_costs[bid.vendor_id]
        cost_pts = weights["net_landed_cost"] * (min_cost / bid_cost)
        delivery_pts = _score_delivery_speed(
            bid.full_quantity_lead_time_days, policy, weights["delivery_speed"]
        )
        warranty_pts = _score_warranty(
            bid.warranty_months, policy, weights["warranty_months"]
        )
        track_pts = _score_track_record(
            bid.track_record_tier, policy, weights["supplier_track_record"]
        )
        payment_pts = _score_payment_terms(
            bid.payment_terms, policy, weights["payment_terms"]
        )
        total_pts = cost_pts + delivery_pts + warranty_pts + track_pts + payment_pts

        breakdown = ScoreBreakdown(
            net_landed_cost=float(_q2(cost_pts)),
            delivery_speed=float(_q2(delivery_pts)),
            warranty_months=float(_q2(warranty_pts)),
            supplier_track_record=float(_q2(track_pts)),
            payment_terms=float(_q2(payment_pts)),
            total_score=float(_q2(total_pts)),
        )
        scored.append(bid.model_copy(update={"score_breakdown": breakdown}))

    # Deterministic tie-breaking: highest total_score, then lowest net_landed_usd, then vendor_id
    scored.sort(
        key=lambda b: (
            -_d(b.score_breakdown.total_score if b.score_breakdown else 0),
            _d(b.net_landed_usd),
            b.vendor_id,
        )
    )

    ranked = [bid.model_copy(update={"rank": idx}) for idx, bid in enumerate(scored, start=1)]
    return ranked, _fmt2(min_cost)


def evaluate_all_bids(
    extracted_bids: list[ExtractedBid],
    policy: ProcurementPolicy,
    custom_weights: dict[str, float] | None = None,
) -> EvaluationSummary:
    """Runs complete deterministic normalization, compliance, and 100-pt scoring."""
    raw_weights = custom_weights or policy.scoring_rubric.weights
    dec_weights = validate_weights(raw_weights, policy.scoring_rubric.total_points)

    cap_usd = _d(policy.compliance_rules.manager_signoff_required_above_usd)
    required_qty = policy.rfp_metadata.required_quantity

    compliant: list[EvaluatedBid] = []
    clarification: list[EvaluatedBid] = []
    disqualified: list[EvaluatedBid] = []

    for bid in extracted_bids:
        full_lead_days, batch_notes = _compute_full_quantity_lead_time(bid, required_qty)
        pricing = _compute_native_pricing(bid, policy)
        status, reasons, clar_items, verbal_ignored = _classify_compliance(
            bid, full_lead_days, batch_notes, policy
        )

        vendor_rec = policy.approved_vendors.get(bid.vendor_id)
        net_usd: Decimal = pricing["net_landed_usd"]
        over_cap = max(Decimal("0"), net_usd - cap_usd)
        needs_signoff = net_usd > cap_usd

        evaluated = EvaluatedBid(
            vendor_id=bid.vendor_id,
            supplier_name=bid.supplier_name,
            source_filename=bid.source_filename,
            currency=bid.currency,
            incoterm=bid.incoterm,
            compliance_status=status,
            compliance_reasons=reasons,
            clarification_items=clar_items,
            verbal_approval_ignored=verbal_ignored,
            native_mandatory_subtotal=_fmt2(pricing["base_subtotal"]),
            native_adjustments_summary=pricing["adjustments"],
            native_net_landed_total=_fmt2(pricing["net_native"]),
            fx_rate_to_usd=str(pricing["fx_rate"]),
            net_landed_usd=_fmt2(net_usd),
            net_landed_usd_float=float(_q2(net_usd)),
            effective_unit_cost_usd=_fmt2(pricing["effective_unit_usd"]),
            quantity_billed=pricing["quantity_billed"],
            excluded_optional_items=pricing["excluded_optional"],
            recoverable_tax_name=pricing["recoverable_tax_name"],
            recoverable_tax_native=(
                _fmt2(pricing["recoverable_tax_native"])
                if pricing["recoverable_tax_native"] is not None
                else None
            ),
            gross_cash_outlay_native=(
                _fmt2(pricing["gross_cash_outlay_native"])
                if pricing["gross_cash_outlay_native"] is not None
                else None
            ),
            gross_cash_outlay_usd=(
                _fmt2(pricing["gross_cash_outlay_usd"])
                if pricing["gross_cash_outlay_usd"] is not None
                else None
            ),
            full_quantity_lead_time_days=full_lead_days,
            warranty_months=bid.warranty_months,
            payment_terms=bid.payment_terms,
            early_payment_discount_note=bid.early_payment_discount_note,
            valid_until=bid.valid_until,
            ingress_rating_stated=bid.ingress_rating_stated,
            explicit_ingress_certified=bid.explicit_ingress_certified,
            certifications=bid.certifications,
            commercial_notes=bid.commercial_notes,
            approved_vendor=vendor_rec is not None,
            vendor_location=vendor_rec.location if vendor_rec else None,
            relationship_status=vendor_rec.relationship_status if vendor_rec else None,
            track_record_tier=vendor_rec.track_record_tier if vendor_rec else None,
            prior_pos=vendor_rec.prior_pos if vendor_rec else None,
            on_time_delivery_pct=vendor_rec.on_time_delivery_pct if vendor_rec else None,
            requires_manager_signoff=needs_signoff,
            amount_over_cap_usd=_fmt2(over_cap),
        )

        if status == "COMPLIANT":
            compliant.append(evaluated)
        elif status == "CLARIFICATION_REQUIRED":
            clarification.append(evaluated)
        else:
            disqualified.append(evaluated)

    compliant_ranked, min_cost_str = _apply_rubric_scores(compliant, policy, dec_weights)
    clarification.sort(key=lambda b: b.vendor_id)
    disqualified.sort(key=lambda b: b.vendor_id)

    all_by_id = {
        b.vendor_id: b for b in (compliant_ranked + clarification + disqualified)
    }

    return EvaluationSummary(
        rfp_id=policy.rfp_metadata.rfp_id,
        rfp_title=policy.rfp_metadata.title,
        policy_version=policy.policy_version,
        evaluation_date=policy.rfp_metadata.evaluation_date,
        required_quantity=required_qty,
        auto_approval_cap_usd=_fmt2(cap_usd),
        min_compliant_net_landed_usd=min_cost_str,
        active_weights={k: float(v) for k, v in dec_weights.items()},
        total_quotes_evaluated=len(all_by_id),
        compliant_count=len(compliant_ranked),
        clarification_required_count=len(clarification),
        disqualified_count=len(disqualified),
        compliant_ranked=compliant_ranked,
        clarification_required=clarification,
        disqualified=disqualified,
        all_bids_by_vendor_id=all_by_id,
    )


def rescore_cached_bids(
    summary: EvaluationSummary,
    policy: ProcurementPolicy,
    new_weights: dict[str, float],
) -> dict[str, Any]:
    """Rescores cached COMPLIANT bids deterministically with zero GCS reads."""
    dec_weights = validate_weights(new_weights, policy.scoring_rubric.total_points)
    previous_ranks = {
        b.vendor_id: {
            "rank": b.rank,
            "total_score": b.score_breakdown.total_score if b.score_breakdown else 0.0,
        }
        for b in summary.compliant_ranked
    }

    new_ranked, min_cost_str = _apply_rubric_scores(
        summary.compliant_ranked, policy, dec_weights
    )

    rank_changes: list[dict[str, Any]] = []
    for bid in new_ranked:
        prev = previous_ranks.get(bid.vendor_id, {})
        prev_rank = prev.get("rank")
        prev_score = prev.get("total_score", 0.0)
        new_score = bid.score_breakdown.total_score if bid.score_breakdown else 0.0
        rank_delta = (prev_rank - bid.rank) if (prev_rank and bid.rank) else 0
        score_delta = float(_q2(_d(new_score) - _d(prev_score)))
        rank_changes.append(
            {
                "vendor_id": bid.vendor_id,
                "supplier_name": bid.supplier_name,
                "previous_rank": prev_rank,
                "new_rank": bid.rank,
                "rank_delta": rank_delta,
                "previous_score": prev_score,
                "new_score": new_score,
                "score_delta": score_delta,
                "net_landed_usd": bid.net_landed_usd,
                "requires_manager_signoff": bid.requires_manager_signoff,
                "score_breakdown": bid.score_breakdown.model_dump()
                if bid.score_breakdown
                else None,
            }
        )

    return {
        "status": "success",
        "rfp_id": summary.rfp_id,
        "min_compliant_net_landed_usd": min_cost_str,
        "previous_weights": summary.active_weights,
        "new_weights": {k: float(v) for k, v in dec_weights.items()},
        "ranked_bids": [b.model_dump() for b in new_ranked],
        "rank_changes": rank_changes,
    }


def resolve_vendor_bid(
    summary: EvaluationSummary, vendor_identifier: str
) -> EvaluatedBid | None:
    """Resolves a vendor by vendor_id or case-insensitive supplier name substring."""
    query = vendor_identifier.strip()
    if not query:
        return None
    upper = query.upper()
    if upper in summary.all_bids_by_vendor_id:
        return summary.all_bids_by_vendor_id[upper]

    lower = query.lower()
    matches = [
        bid
        for bid in summary.all_bids_by_vendor_id.values()
        if lower in bid.supplier_name.lower() or lower == bid.vendor_id.lower()
    ]
    if len(matches) == 1:
        return matches[0]
    return None


def evaluate_award_gate(
    summary: EvaluationSummary,
    policy: ProcurementPolicy,
    vendor_identifier: str,
) -> dict[str, Any]:
    """Evaluates buyer vendor selection against compliance and $50K cap rules."""
    bid = resolve_vendor_bid(summary, vendor_identifier)
    if bid is None:
        return {
            "decision": "NOT_FOUND",
            "award_authorized": False,
            "message": (
                f"Could not uniquely match vendor '{vendor_identifier}'. "
                f"Available vendor IDs: {sorted(summary.all_bids_by_vendor_id.keys())}."
            ),
        }

    cap_usd = _d(policy.compliance_rules.manager_signoff_required_above_usd)
    bid_usd = _d(bid.net_landed_usd)

    if bid.compliance_status == "DISQUALIFIED":
        return {
            "decision": "BLOCKED_DISQUALIFIED",
            "award_authorized": False,
            "vendor_id": bid.vendor_id,
            "supplier_name": bid.supplier_name,
            "compliance_status": bid.compliance_status,
            "reasons": bid.compliance_reasons,
            "verbal_approval_ignored": bid.verbal_approval_ignored,
            "message": (
                f"Award blocked: {bid.supplier_name} ({bid.vendor_id}) is DISQUALIFIED. "
                "Purchase Order cannot be drafted."
            ),
        }

    if bid.compliance_status == "CLARIFICATION_REQUIRED":
        return {
            "decision": "BLOCKED_CLARIFICATION_REQUIRED",
            "award_authorized": False,
            "vendor_id": bid.vendor_id,
            "supplier_name": bid.supplier_name,
            "compliance_status": bid.compliance_status,
            "clarification_items": bid.clarification_items,
            "net_landed_usd": bid.net_landed_usd,
            "message": (
                f"Award blocked: {bid.supplier_name} ({bid.vendor_id}) requires supplier "
                "clarification before award. Draft a Supplier Clarification Request instead of a PO."
            ),
        }

    if bid_usd > cap_usd:
        over_cap = _fmt2(bid_usd - cap_usd)
        return {
            "decision": "MANAGER_SIGNOFF_REQUIRED",
            "award_authorized": False,
            "vendor_id": bid.vendor_id,
            "supplier_name": bid.supplier_name,
            "compliance_status": bid.compliance_status,
            "net_landed_usd": bid.net_landed_usd,
            "auto_approval_cap_usd": _fmt2(cap_usd),
            "amount_over_cap_usd": over_cap,
            "gross_cash_outlay_usd": bid.gross_cash_outlay_usd,
            "gross_cash_outlay_native": bid.gross_cash_outlay_native,
            "currency": bid.currency,
            "native_net_landed_total": bid.native_net_landed_total,
            "lead_time_days": bid.full_quantity_lead_time_days,
            "warranty_months": bid.warranty_months,
            "payment_terms": bid.payment_terms,
            "score_total": bid.score_breakdown.total_score if bid.score_breakdown else None,
            "rank": bid.rank,
            "message": (
                f"PO held: {bid.supplier_name} ({bid.vendor_id}) net landed total "
                f"${bid.net_landed_usd} USD exceeds auto-approval cap of ${_fmt2(cap_usd)} USD "
                f"by ${over_cap} USD. Manager sign-off is required before drafting a PO."
            ),
        }

    return {
        "decision": "AUTHORIZED_FOR_PO",
        "award_authorized": True,
        "vendor_id": bid.vendor_id,
        "supplier_name": bid.supplier_name,
        "compliance_status": bid.compliance_status,
        "net_landed_usd": bid.net_landed_usd,
        "auto_approval_cap_usd": _fmt2(cap_usd),
        "gross_cash_outlay_usd": bid.gross_cash_outlay_usd,
        "gross_cash_outlay_native": bid.gross_cash_outlay_native,
        "currency": bid.currency,
        "native_net_landed_total": bid.native_net_landed_total,
        "message": (
            f"Award authorized: {bid.supplier_name} ({bid.vendor_id}) is COMPLIANT and "
            f"${bid.net_landed_usd} USD is within the ${_fmt2(cap_usd)} USD cap. "
            "Ready for immediate PO drafting."
        ),
    }


def assemble_po_payload(
    summary: EvaluationSummary,
    policy: ProcurementPolicy,
    vendor_id: str,
    award_authorized: bool,
    manager_signoff: dict[str, Any] | None = None,
    buyer_edits: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Builds a deterministic in-session Purchase Order payload only when award_authorized is True."""
    if award_authorized is not True:
        return {
            "status": "BLOCKED",
            "error": (
                "Purchase Order generation denied: state['award_authorized'] is not True. "
                "The buyer must select a compliant supplier and complete any required "
                "manager sign-off (> $50,000 USD) through policy_signoff_agent first."
            ),
        }

    bid = summary.all_bids_by_vendor_id.get(vendor_id)
    if bid is None:
        return {
            "status": "BLOCKED",
            "error": f"Selected vendor '{vendor_id}' not found in evaluated bids.",
        }

    if bid.compliance_status != "COMPLIANT":
        return {
            "status": "BLOCKED",
            "error": (
                f"Purchase Order generation denied: vendor '{vendor_id}' has status "
                f"'{bid.compliance_status}', not COMPLIANT."
            ),
        }

    cap_usd = _d(policy.compliance_rules.manager_signoff_required_above_usd)
    bid_usd = _d(bid.net_landed_usd)
    if bid_usd > cap_usd and not (manager_signoff and manager_signoff.get("approved") is True):
        return {
            "status": "BLOCKED",
            "error": (
                f"Purchase Order generation denied: ${bid.net_landed_usd} USD exceeds "
                f"${_fmt2(cap_usd)} USD cap and manager sign-off has not been recorded."
            ),
        }

    edits = buyer_edits or {}
    return {
        "status": "DRAFT_READY",
        "po_mode": "IN_SESSION_DRAFT_ONLY",
        "po_reference": f"PO-DRAFT-{policy.rfp_metadata.rfp_id}-{bid.vendor_id}",
        "rfp_id": policy.rfp_metadata.rfp_id,
        "rfp_title": policy.rfp_metadata.title,
        "policy_version": policy.policy_version,
        "supplier_name": bid.supplier_name,
        "vendor_id": bid.vendor_id,
        "vendor_location": bid.vendor_location,
        "incoterm": bid.incoterm,
        "required_quantity": policy.rfp_metadata.required_quantity,
        "quantity_billed": bid.quantity_billed,
        "currency": bid.currency,
        "native_mandatory_subtotal": bid.native_mandatory_subtotal,
        "native_net_landed_total": bid.native_net_landed_total,
        "fx_rate_to_usd": bid.fx_rate_to_usd,
        "net_landed_usd": bid.net_landed_usd,
        "effective_unit_cost_usd": bid.effective_unit_cost_usd,
        "pricing_breakdown": bid.native_adjustments_summary,
        "excluded_optional_items": bid.excluded_optional_items,
        "recoverable_tax_name": bid.recoverable_tax_name,
        "recoverable_tax_native": bid.recoverable_tax_native,
        "gross_cash_outlay_native": bid.gross_cash_outlay_native,
        "gross_cash_outlay_usd": bid.gross_cash_outlay_usd,
        "delivery_sla_days": bid.full_quantity_lead_time_days,
        "warranty_months": bid.warranty_months,
        "payment_terms": bid.payment_terms,
        "early_payment_discount_note": bid.early_payment_discount_note,
        "certifications": bid.certifications,
        "requires_manager_signoff": bid.requires_manager_signoff,
        "manager_signoff": manager_signoff,
        "buyer_metadata": {
            "ship_to_location": edits.get("ship_to_location", "Hyderabad Plant Receiving Dock"),
            "ship_to_contact": edits.get("ship_to_contact", "Procurement Receiving Team"),
            "cost_center": edits.get("cost_center", "TBD-BUYER-COST-CENTER"),
            "billing_instructions": edits.get(
                "billing_instructions",
                "Reference PO draft number and RFP-2026-441 on all invoices and shipping docs.",
            ),
            "special_delivery_notes": edits.get("special_delivery_notes", "None"),
        },
    }
