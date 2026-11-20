"""Pure deterministic Python engine for landed-cost math, compliance gates, 100-pt scoring, and PO gates."""

from __future__ import annotations

import datetime
import math
from decimal import ROUND_HALF_UP, Decimal

from app.models import (
    ComplianceCheckDetail,
    ComplianceStatus,
    CostBreakdown,
    EvaluatedBid,
    EvaluationReport,
    ManagerSignOffRequest,
    PostSelectionDecision,
    ProcurementPolicy,
    PurchaseOrderDraft,
    ScoreBreakdown,
    ScoringWeights,
    SupplierBidIntake,
    SupplierClarificationDraft,
)

TWO_PLACES = Decimal("0.01")
ONE_PLACE = Decimal("0.1")


def _d(value: float | int | str | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _round2(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def _round1(value: Decimal) -> Decimal:
    return value.quantize(ONE_PLACE, rounding=ROUND_HALF_UP)


def _pct_to_rate(pct: float | None) -> Decimal:
    """Convert percentage points (e.g., 8.0 -> 0.08) or fraction (0.08 -> 0.08) into a Decimal rate."""
    if pct is None or pct <= 0:
        return Decimal("0")
    dec = _d(pct)
    if dec < Decimal("1"):
        return dec
    return dec / Decimal("100")


def compute_landed_cost(
    intake: SupplierBidIntake,
    policy: ProcurementPolicy,
) -> CostBreakdown:
    """Normalize a supplier bid into exact net landed USD and gross cash outlay USD."""
    req_qty = policy.rfp_metadata.required_quantity
    if req_qty <= 0:
        raise ValueError(f"required_quantity must be positive, got {req_qty}")

    if intake.currency not in policy.fx_rates_to_usd:
        raise ValueError(f"Unsupported currency {intake.currency!r} not in policy fx_rates_to_usd.")

    has_carton_basis = any(item.basis == "per_carton" for item in intake.mandatory_line_items)
    if (
        intake.pricing_structure == "carton_moq" or has_carton_basis
    ) and intake.units_per_carton:
        if intake.units_per_carton <= 0:
            raise ValueError(f"Invalid units_per_carton: {intake.units_per_carton}")
        cartons_ordered: int | None = math.ceil(req_qty / intake.units_per_carton)
        units_ordered = cartons_ordered * intake.units_per_carton
        spare_units = units_ordered - req_qty
    elif intake.units_per_carton and intake.units_per_carton > 0 and has_carton_basis:
        cartons_ordered = math.ceil(req_qty / intake.units_per_carton)
        units_ordered = cartons_ordered * intake.units_per_carton
        spare_units = units_ordered - req_qty
    else:
        cartons_ordered = None
        units_ordered = req_qty
        spare_units = 0

    if not intake.mandatory_line_items:
        raise ValueError(f"Proposal {intake.source_file} has no mandatory_line_items.")

    base_subtotal = Decimal("0")
    for item in intake.mandatory_line_items:
        price = _d(item.price_in_source_currency)
        if item.basis == "per_unit":
            base_subtotal += _d(req_qty) * price
        elif item.basis == "per_carton":
            if cartons_ordered is None:
                raise ValueError(
                    f"per_carton item in {intake.source_file} requires positive units_per_carton."
                )
            base_subtotal += _d(cartons_ordered) * price
        elif item.basis == "flat_order":
            qty = item.quantity if (item.quantity is not None and item.quantity > 0) else 1
            base_subtotal += _d(qty) * price
        elif item.basis == "slab":
            if item.from_unit is None or item.to_unit is None:
                raise ValueError(
                    f"Slab item in {intake.source_file} requires from_unit and to_unit bounds."
                )
            if item.to_unit < item.from_unit or item.from_unit < 1:
                raise ValueError(
                    f"Invalid slab bounds [{item.from_unit}, {item.to_unit}] in {intake.source_file}."
                )
            units_in_slab = max(0, min(req_qty, item.to_unit) - item.from_unit + 1)
            base_subtotal += _d(units_in_slab) * price
        else:
            raise ValueError(f"Unsupported line item basis: {item.basis!r}")

    # Optional line items are excluded when policy.normalization_rules.exclude_optional_line_items is True.
    if not policy.normalization_rules.exclude_optional_line_items:
        for opt in intake.optional_line_items:
            opt_price = _d(opt.price_in_source_currency)
            if opt.basis == "per_unit":
                base_subtotal += _d(req_qty) * opt_price
            elif opt.basis == "per_carton" and cartons_ordered is not None:
                base_subtotal += _d(cartons_ordered) * opt_price
            else:
                base_subtotal += _d(max(1, opt.quantity)) * opt_price

    # Automatic volume rebate when carton count meets threshold
    rebate_rate = _pct_to_rate(intake.volume_rebate_pct)
    rebate_eligible = rebate_rate > Decimal("0") and (
        intake.volume_rebate_min_cartons is None
        or (
            cartons_ordered is not None
            and cartons_ordered >= intake.volume_rebate_min_cartons
        )
    )
    volume_rebate_source = base_subtotal * rebate_rate if rebate_eligible else Decimal("0")
    after_rebate = base_subtotal - volume_rebate_source

    # Mandatory expedited freight / percentage surcharge
    surcharge_rate = _pct_to_rate(intake.surcharge_pct)
    surcharge_source = after_rebate * surcharge_rate
    after_surcharge = after_rebate + surcharge_source

    # EXW Shenzhen +18% adder (12% customs duty + 6% international air freight)
    is_exw = "exw" in intake.incoterm.strip().lower()
    exw_rate = (
        _d(policy.normalization_rules.exw_shenzhen_adder_pct) if is_exw else Decimal("0")
    )
    exw_adder_source = after_surcharge * exw_rate
    net_landed_source_exact = after_surcharge + exw_adder_source

    # GST / VAT handling: exclude recoverable Indian GST ITC from net landed USD comparison
    gst_rate = _pct_to_rate(intake.gst_or_vat_pct)
    fx_rate = _d(policy.fx_rates_to_usd[intake.currency])

    if gst_rate > Decimal("0"):
        if intake.tax_recoverable_itc and policy.normalization_rules.india_gst_recoverable_itc:
            net_landed_usd_dec = _round2(net_landed_source_exact * fx_rate)
            recoverable_gst_usd_dec = _round2(net_landed_usd_dec * gst_rate)
            gross_cash_outlay_usd_dec = _round2(net_landed_usd_dec + recoverable_gst_usd_dec)
        else:
            net_landed_source_exact = net_landed_source_exact * (Decimal("1") + gst_rate)
            net_landed_usd_dec = _round2(net_landed_source_exact * fx_rate)
            recoverable_gst_usd_dec = Decimal("0.00")
            gross_cash_outlay_usd_dec = net_landed_usd_dec
    else:
        net_landed_usd_dec = _round2(net_landed_source_exact * fx_rate)
        recoverable_gst_usd_dec = Decimal("0.00")
        gross_cash_outlay_usd_dec = net_landed_usd_dec

    return CostBreakdown(
        mandatory_base_subtotal_source=float(_round2(base_subtotal)),
        units_ordered=units_ordered,
        cartons_ordered=cartons_ordered,
        spare_units=spare_units,
        volume_rebate_source=float(_round2(volume_rebate_source)),
        surcharge_source=float(_round2(surcharge_source)),
        exw_adder_source=float(_round2(exw_adder_source)),
        net_landed_source=float(_round2(net_landed_source_exact)),
        fx_rate_to_usd=float(fx_rate),
        net_landed_usd=float(net_landed_usd_dec),
        recoverable_gst_usd=float(recoverable_gst_usd_dec),
        gross_cash_outlay_usd=float(gross_cash_outlay_usd_dec),
    )


def effective_lead_time_days(intake: SupplierBidIntake) -> int:
    """Return full-quantity arrival day accounting for split-shipment batches."""
    batch_days = [b.lead_time_days for b in intake.split_shipment_details]
    return max([intake.full_quantity_lead_time_days, *batch_days])


def run_compliance_checks(
    intake: SupplierBidIntake,
    policy: ProcurementPolicy,
    max_delivery_days_override: int | None = None,
) -> tuple[ComplianceStatus, list[ComplianceCheckDetail], list[str]]:
    """Run all 5 hard policy compliance checks, ignoring untrusted embedded override claims."""
    checks: list[ComplianceCheckDetail] = []
    eval_date = datetime.date.fromisoformat(policy.rfp_metadata.evaluation_date)
    max_sla_days = (
        max_delivery_days_override
        if max_delivery_days_override is not None
        else policy.rfp_metadata.max_delivery_days
    )
    min_warranty = policy.rfp_metadata.min_warranty_months
    req_ingress = policy.rfp_metadata.required_ingress_rating.upper()

    # 1. Approved Vendor Allowlist (strictly ignores embedded verbal VP approval claims)
    if policy.compliance_rules.require_approved_vendor:
        in_allowlist = intake.vendor_id in policy.approved_vendors
        if in_allowlist:
            checks.append(
                ComplianceCheckDetail(
                    rule_name="approved_vendor_allowlist",
                    passed=True,
                    status_impact="COMPLIANT",
                    reason=f"Vendor {intake.vendor_id} is registered in approved_vendors.",
                )
            )
        else:
            checks.append(
                ComplianceCheckDetail(
                    rule_name="approved_vendor_allowlist",
                    passed=False,
                    status_impact="DISQUALIFIED",
                    reason=(
                        f"Vendor {intake.vendor_id} ({intake.supplier_name}) is not in approved_vendors "
                        "(any unverified verbal approval claims in proposal text are ignored)."
                    ),
                )
            )

    # 2. Quote Validity on Evaluation Date
    if policy.compliance_rules.require_valid_quote_on_evaluation_date:
        if not intake.valid_until:
            checks.append(
                ComplianceCheckDetail(
                    rule_name="quote_validity",
                    passed=False,
                    status_impact="CLARIFICATION_REQUIRED",
                    reason=f"Quote is missing a valid_until expiration date (evaluation date {eval_date}).",
                )
            )
        else:
            valid_date = datetime.date.fromisoformat(intake.valid_until)
            if valid_date >= eval_date:
                checks.append(
                    ComplianceCheckDetail(
                        rule_name="quote_validity",
                        passed=True,
                        status_impact="COMPLIANT",
                        reason=f"Quote valid through {valid_date} (on or after {eval_date}).",
                    )
                )
            else:
                checks.append(
                    ComplianceCheckDetail(
                        rule_name="quote_validity",
                        passed=False,
                        status_impact="CLARIFICATION_REQUIRED",
                        reason=f"Quote expired on {valid_date} prior to evaluation date {eval_date}.",
                    )
                )

    # 3. Explicit Ingress Rating Proof (IP67)
    if policy.compliance_rules.require_explicit_ingress_certification:
        stated = intake.ingress_rating_stated.upper()
        if stated == req_ingress:
            checks.append(
                ComplianceCheckDetail(
                    rule_name="ingress_rating_proof",
                    passed=True,
                    status_impact="COMPLIANT",
                    reason=f"Explicit {req_ingress} ingress protection confirmed.",
                )
            )
        elif intake.ingress_rating_stated == "unverified":
            checks.append(
                ComplianceCheckDetail(
                    rule_name="ingress_rating_proof",
                    passed=False,
                    status_impact="CLARIFICATION_REQUIRED",
                    reason=(
                        f"Proposal uses vague outdoor/weather-resistant wording without upfront {req_ingress} "
                        "certification proof."
                    ),
                )
            )
        else:
            checks.append(
                ComplianceCheckDetail(
                    rule_name="ingress_rating_proof",
                    passed=False,
                    status_impact="DISQUALIFIED",
                    reason=(
                        f"Quoted ingress rating {intake.ingress_rating_stated} does not meet mandatory "
                        f"{req_ingress} requirement."
                    ),
                )
            )

    # 4. Full-Quantity Delivery SLA
    lead_days = effective_lead_time_days(intake)
    if policy.compliance_rules.full_quantity_must_meet_sla:
        if lead_days <= max_sla_days:
            checks.append(
                ComplianceCheckDetail(
                    rule_name="full_quantity_delivery_sla",
                    passed=True,
                    status_impact="COMPLIANT",
                    reason=f"Full 1,000-unit delivery in {lead_days} days meets <= {max_sla_days}-day SLA.",
                )
            )
        else:
            split_note = " (split shipment final batch)" if intake.split_shipment_details else ""
            checks.append(
                ComplianceCheckDetail(
                    rule_name="full_quantity_delivery_sla",
                    passed=False,
                    status_impact="DISQUALIFIED",
                    reason=(
                        f"Full-quantity delivery arrives on day {lead_days}{split_note}, exceeding the "
                        f"{max_sla_days}-day maximum SLA."
                    ),
                )
            )

    # 5. Minimum Warranty
    if intake.warranty_months >= min_warranty:
        checks.append(
            ComplianceCheckDetail(
                rule_name="minimum_warranty",
                passed=True,
                status_impact="COMPLIANT",
                reason=f"{intake.warranty_months}-month warranty meets >= {min_warranty}-month minimum.",
            )
        )
    else:
        checks.append(
            ComplianceCheckDetail(
                rule_name="minimum_warranty",
                passed=False,
                status_impact="DISQUALIFIED",
                reason=(
                    f"{intake.warranty_months}-month warranty is below the mandatory "
                    f"{min_warranty}-month minimum."
                ),
            )
        )

    failed = [c for c in checks if not c.passed]
    filter_reasons = [c.reason for c in failed]
    if any(c.status_impact == "DISQUALIFIED" for c in failed):
        status: ComplianceStatus = "DISQUALIFIED"
    elif any(c.status_impact == "CLARIFICATION_REQUIRED" for c in failed):
        status = "CLARIFICATION_REQUIRED"
    else:
        status = "COMPLIANT"

    return status, checks, filter_reasons


def resolve_scoring_weights(
    default_weights: ScoringWeights,
    weight_overrides: dict[str, float] | None = None,
) -> ScoringWeights:
    """Resolve runtime weight overrides.

    - Partial overrides (e.g., {'net_landed_cost': 60}) proportionally scale the remaining
      default weights so all 5 weights sum to 100.0.
    - Explicit 5-weight overrides are validated to sum to 100.0 (or scaled from 1.0 if given as fractions).
    """
    if not weight_overrides:
        return default_weights

    base = default_weights.model_dump()
    clean_overrides: dict[str, float] = {}
    for key, val in weight_overrides.items():
        if val is None:
            continue
        if key not in base:
            raise ValueError(f"Unknown weight criterion {key!r}. Valid keys: {list(base.keys())}")
        if val < 0:
            raise ValueError(f"Weight for {key!r} must be non-negative, got {val}.")
        clean_overrides[key] = float(val)

    if not clean_overrides:
        return default_weights

    # Normalize fractional inputs (e.g. 0.60 instead of 60) if all supplied values are <= 1.0
    if all(v <= 1.0 for v in clean_overrides.values()) and sum(clean_overrides.values()) <= 1.0001:
        if len(clean_overrides) == len(base) and abs(sum(clean_overrides.values()) - 1.0) <= 1e-4:
            clean_overrides = {k: v * 100.0 for k, v in clean_overrides.items()}
        elif len(clean_overrides) < len(base) and any(0 < v < 1.0 for v in clean_overrides.values()):
            clean_overrides = {k: v * 100.0 for k, v in clean_overrides.items()}

    override_sum = sum(clean_overrides.values())
    if len(clean_overrides) == len(base):
        if abs(override_sum - 100.0) > 0.05:
            raise ValueError(
                f"Explicit 5-criterion weight overrides must sum to 100.0, got {override_sum:.2f}."
            )
        scale = 100.0 / override_sum
        return ScoringWeights(**{k: round(v * scale, 4) for k, v in clean_overrides.items()})

    if override_sum > 100.0001:
        raise ValueError(
            f"Partial weight overrides sum to {override_sum:.2f}, exceeding 100.0 total points."
        )

    remaining_budget = max(0.0, 100.0 - override_sum)
    remaining_keys = [k for k in base if k not in clean_overrides]
    remaining_default_sum = sum(base[k] for k in remaining_keys)

    resolved: dict[str, float] = dict(clean_overrides)
    if remaining_default_sum > 0:
        for k in remaining_keys:
            resolved[k] = round(base[k] * (remaining_budget / remaining_default_sum), 4)
    else:
        even_share = round(remaining_budget / len(remaining_keys), 4)
        for k in remaining_keys:
            resolved[k] = even_share

    return ScoringWeights(**resolved)


def _lookup_delivery_points(lead_days: int, policy: ProcurementPolicy) -> Decimal:
    brackets = sorted(policy.scoring_rubric.delivery_speed_brackets, key=lambda b: b.max_days)
    for bracket in brackets:
        if lead_days <= bracket.max_days:
            return _d(bracket.points)
    return _d(brackets[-1].points) if brackets else Decimal("0")


def _lookup_warranty_points(warranty_months: int, policy: ProcurementPolicy) -> Decimal:
    brackets = sorted(policy.scoring_rubric.warranty_brackets, key=lambda b: b.min_months, reverse=True)
    for bracket in brackets:
        if warranty_months >= bracket.min_months:
            return _d(bracket.points)
    return Decimal("0")


def _scale_bracket_points(
    raw_points: Decimal,
    active_weight: float,
    default_weight: float,
) -> Decimal:
    if default_weight <= 0:
        return Decimal("0")
    return _round2(raw_points * (_d(active_weight) / _d(default_weight)))


def _build_pros_and_cons(
    bid: EvaluatedBid,
    min_net_usd: float,
    min_lead_days: int,
    cap_usd: float,
    rank_among_under_cap: int | None,
) -> tuple[list[str], list[str]]:
    pros: list[str] = []
    cons: list[str] = []

    if bid.rank == 1:
        pros.append(f"#1 overall rubric score ({bid.score_breakdown.total_score:.1f}/100)")
    if rank_among_under_cap == 1:
        pros.append(f"#1 auto-approvable score under ${cap_usd:,.0f} cap")
    if abs(bid.cost_breakdown.net_landed_usd - min_net_usd) < 0.01:
        pros.append(f"Lowest net landed cost (${bid.cost_breakdown.net_landed_usd:,.2f} USD)")
    if bid.full_quantity_lead_time_days == min_lead_days:
        pros.append(f"Fastest delivery ({bid.full_quantity_lead_time_days} days)")
    elif bid.full_quantity_lead_time_days <= 16:
        pros.append(f"Fast {bid.full_quantity_lead_time_days}-day delivery")

    if bid.warranty_months >= 36:
        pros.append(f"Extended {bid.warranty_months}-month warranty")

    if bid.vendor_profile:
        vp = bid.vendor_profile
        if vp.track_record_tier == "incumbent_high_otd":
            otd_str = f"{vp.on_time_delivery_pct:.1f}% OTD" if vp.on_time_delivery_pct is not None else "high OTD"
            pros.append(f"{vp.tenure_years:g}-year incumbent ({otd_str}, {vp.prior_pos} prior POs)")
        elif vp.track_record_tier == "established_partner":
            pros.append(f"Established partner ({vp.location}, {vp.prior_pos} prior POs)")
        elif vp.track_record_tier == "new_onboarded":
            cons.append("Newly onboarded supplier with 0 prior POs")

    if bid.payment_terms in ("Net 90", "Net 60"):
        note = f" ({bid.early_payment_discount_note})" if bid.early_payment_discount_note else ""
        pros.append(f"Favorable {bid.payment_terms} payment terms{note}")
    elif bid.payment_terms == "Net 30":
        cons.append("Shorter Net 30 payment window")

    if "ISO-14001" in bid.certifications or "ATEX" in bid.certifications:
        extra = [c for c in bid.certifications if c in ("ATEX", "ISO-14001")]
        pros.append(f"Additional certifications ({', '.join(extra)})")

    if bid.requires_manager_signoff_if_selected:
        cons.append(
            f"Exceeds ${cap_usd:,.0f} auto-approval cap by ${bid.overage_above_cap_usd:,.2f} "
            "(requires manager sign-off if selected)"
        )
    if bid.cost_breakdown.spare_units > 0 and bid.cost_breakdown.cartons_ordered:
        pros.append(
            f"{bid.cost_breakdown.cartons_ordered} master cartons include "
            f"{bid.cost_breakdown.spare_units} spare units"
        )
    if bid.cost_breakdown.recoverable_gst_usd > 0:
        cons.append(
            f"Higher upfront gross cash outlay (${bid.cost_breakdown.gross_cash_outlay_usd:,.2f} USD "
            f"including recoverable GST ITC)"
        )
    if bid.full_quantity_lead_time_days >= 21:
        cons.append(f"Longer {bid.full_quantity_lead_time_days}-day lead time")

    return pros, cons


def evaluate_bids(
    intakes: list[SupplierBidIntake],
    policy: ProcurementPolicy,
    weight_overrides: dict[str, float] | None = None,
    max_delivery_days_override: int | None = None,
    auto_approval_cap_override: float | None = None,
) -> EvaluationReport:
    """Run full deterministic cost normalization, compliance filtering, and 100-pt rubric scoring."""
    if not intakes:
        raise ValueError("Cannot evaluate an empty list of supplier bid intakes.")

    default_weights = policy.scoring_rubric.weights
    active_weights = resolve_scoring_weights(default_weights, weight_overrides)
    effective_max_days = (
        max_delivery_days_override
        if max_delivery_days_override is not None
        else policy.rfp_metadata.max_delivery_days
    )
    cap_usd = (
        auto_approval_cap_override
        if auto_approval_cap_override is not None
        else policy.rfp_metadata.auto_approval_cap_usd
    )

    preliminary: list[EvaluatedBid] = []
    for intake in intakes:
        cost = compute_landed_cost(intake, policy)
        status, checks, reasons = run_compliance_checks(
            intake,
            policy,
            max_delivery_days_override=effective_max_days,
        )
        lead_days = effective_lead_time_days(intake)
        overage = float(
            max(Decimal("0.00"), _round2(_d(cost.net_landed_usd) - _d(cap_usd)))
        )
        needs_signoff = status == "COMPLIANT" and cost.net_landed_usd > cap_usd

        preliminary.append(
            EvaluatedBid(
                source_file=intake.source_file,
                supplier_name=intake.supplier_name,
                vendor_id=intake.vendor_id,
                status=status,
                requires_manager_signoff_if_selected=needs_signoff,
                overage_above_cap_usd=overage if status == "COMPLIANT" else 0.0,
                currency=intake.currency,
                incoterm=intake.incoterm,
                full_quantity_lead_time_days=lead_days,
                warranty_months=intake.warranty_months,
                payment_terms=intake.payment_terms,
                early_payment_discount_note=intake.early_payment_discount_note,
                certifications=list(intake.certifications),
                vendor_profile=policy.approved_vendors.get(intake.vendor_id),
                cost_breakdown=cost,
                compliance_checks=checks,
                filter_reasons=reasons,
                audit_flags=intake.unusual_claims_or_notes,
            )
        )

    compliant = [b for b in preliminary if b.status == "COMPLIANT"]
    filtered = [b for b in preliminary if b.status != "COMPLIANT"]
    filtered.sort(
        key=lambda b: (0 if b.status == "CLARIFICATION_REQUIRED" else 1, b.source_file)
    )

    min_compliant_usd: float | None = None
    if compliant:
        min_dec = min(_d(b.cost_breakdown.net_landed_usd) for b in compliant)
        min_compliant_usd = float(min_dec)
        min_lead = min(b.full_quantity_lead_time_days for b in compliant)

        for bid in compliant:
            bid_usd = _d(bid.cost_breakdown.net_landed_usd)
            cost_pts = _round2(_d(active_weights.net_landed_cost) * (min_dec / bid_usd))

            raw_deliv = _lookup_delivery_points(bid.full_quantity_lead_time_days, policy)
            deliv_pts = _scale_bracket_points(
                raw_deliv, active_weights.delivery_speed, default_weights.delivery_speed
            )

            raw_warr = _lookup_warranty_points(bid.warranty_months, policy)
            warr_pts = _scale_bracket_points(
                raw_warr, active_weights.warranty_months, default_weights.warranty_months
            )

            tier_key = bid.vendor_profile.track_record_tier if bid.vendor_profile else ""
            if tier_key not in policy.scoring_rubric.supplier_track_record_tiers:
                raise ValueError(
                    f"Missing track_record_tier {tier_key!r} for compliant vendor {bid.vendor_id}."
                )
            raw_track = _d(policy.scoring_rubric.supplier_track_record_tiers[tier_key].points)
            track_pts = _scale_bracket_points(
                raw_track,
                active_weights.supplier_track_record,
                default_weights.supplier_track_record,
            )

            if bid.payment_terms not in policy.scoring_rubric.payment_terms_points:
                raise ValueError(f"Unsupported payment_terms {bid.payment_terms!r} on {bid.vendor_id}.")
            raw_pay = _d(policy.scoring_rubric.payment_terms_points[bid.payment_terms])
            pay_pts = _scale_bracket_points(
                raw_pay, active_weights.payment_terms, default_weights.payment_terms
            )

            total_pts = _round1(cost_pts + deliv_pts + warr_pts + track_pts + pay_pts)
            bid.score_breakdown = ScoreBreakdown(
                net_landed_cost_points=float(cost_pts),
                delivery_speed_points=float(deliv_pts),
                warranty_points=float(warr_pts),
                supplier_track_record_points=float(track_pts),
                payment_terms_points=float(pay_pts),
                total_score=float(total_pts),
            )

        compliant.sort(
            key=lambda b: (
                -(b.score_breakdown.total_score if b.score_breakdown else 0.0),
                b.cost_breakdown.net_landed_usd,
                b.full_quantity_lead_time_days,
                b.vendor_id,
            )
        )

        under_cap_counter = 0
        for idx, bid in enumerate(compliant, start=1):
            bid.rank = idx
            under_cap_rank: int | None = None
            if not bid.requires_manager_signoff_if_selected:
                under_cap_counter += 1
                under_cap_rank = under_cap_counter
            pros, cons = _build_pros_and_cons(
                bid=bid,
                min_net_usd=min_compliant_usd,
                min_lead_days=min_lead,
                cap_usd=cap_usd,
                rank_among_under_cap=under_cap_rank,
            )
            bid.pros = pros
            bid.cons = cons

    return EvaluationReport(
        rfp_id=policy.rfp_metadata.rfp_id,
        evaluation_date=policy.rfp_metadata.evaluation_date,
        required_quantity=policy.rfp_metadata.required_quantity,
        max_delivery_days=effective_max_days,
        auto_approval_cap_usd=cap_usd,
        active_weights=active_weights,
        min_compliant_net_landed_usd=min_compliant_usd,
        compliant_finalists=compliant,
        filtered_bids=filtered,
        po_drafted=False,
        manager_signoff_triggered=False,
    )


# ---------------------------------------------------------------------------
# Post-Selection Routing, PO Drafting, Sign-Off, and Clarification Helpers
# ---------------------------------------------------------------------------


def find_bid_and_intake(
    report: EvaluationReport,
    intakes: list[SupplierBidIntake],
    vendor_query: str,
) -> tuple[EvaluatedBid, SupplierBidIntake]:
    """Match a supplier by exact vendor_id or unambiguous supplier_name / source_file substring."""
    q = vendor_query.strip().lower()
    if not q:
        raise ValueError("vendor_query must be non-empty.")

    all_bids = [*report.compliant_finalists, *report.filtered_bids]
    intake_by_file = {i.source_file: i for i in intakes}

    for bid in all_bids:
        if bid.vendor_id.lower() == q or bid.source_file.lower() == q:
            return bid, intake_by_file[bid.source_file]

    matches = [
        bid
        for bid in all_bids
        if q in bid.supplier_name.lower()
        or q in bid.vendor_id.lower()
        or q in bid.source_file.lower()
    ]
    if len(matches) == 1:
        matched = matches[0]
        return matched, intake_by_file[matched.source_file]
    if len(matches) > 1:
        names = ", ".join(f"{m.supplier_name} ({m.vendor_id})" for m in matches)
        raise ValueError(f"Ambiguous vendor query {vendor_query!r}; matched: {names}")

    valid = ", ".join(f"{b.supplier_name} ({b.vendor_id})" for b in all_bids)
    raise ValueError(f"Unknown supplier {vendor_query!r}. Available bids: {valid}")


def build_clarification_draft(
    rfp_id: str,
    bid: EvaluatedBid,
) -> SupplierClarificationDraft:
    """Build a structured Supplier Clarification Request for CLARIFICATION_REQUIRED bids."""
    confirmations: list[str] = []
    for check in bid.compliance_checks:
        if not check.passed and check.rule_name == "quote_validity":
            confirmations.append(
                "Provide an updated signed quotation extending validity on or past the evaluation date "
                "while holding quoted DDP Hyderabad pricing."
            )
        elif not check.passed and check.rule_name == "ingress_rating_proof":
            confirmations.append(
                "Submit a formal IEC 60529 IP67 laboratory test certificate confirming IP67 outdoor "
                "ingress protection prior to award consideration."
            )
    if not confirmations:
        confirmations.append("Provide written documentation resolving all open compliance items.")

    return SupplierClarificationDraft(
        rfp_id=rfp_id,
        supplier_name=bid.supplier_name,
        vendor_id=bid.vendor_id,
        source_file=bid.source_file,
        issues_identified=list(bid.filter_reasons),
        requested_confirmations=confirmations,
    )


def _build_po_draft(
    report: EvaluationReport,
    bid: EvaluatedBid,
    intake: SupplierBidIntake,
    approval_basis: str,
) -> PurchaseOrderDraft:
    line_summaries: list[str] = []
    for item in intake.mandatory_line_items:
        sku_prefix = f"[{item.sku}] " if item.sku else ""
        if item.basis == "per_unit":
            line_summaries.append(
                f"{sku_prefix}{item.description}: {report.required_quantity} units @ "
                f"{item.price_in_source_currency:,.2f} {intake.currency}/unit"
            )
        elif item.basis == "per_carton":
            line_summaries.append(
                f"{sku_prefix}{item.description}: {bid.cost_breakdown.cartons_ordered} cartons "
                f"({bid.cost_breakdown.units_ordered} units) @ "
                f"{item.price_in_source_currency:,.2f} {intake.currency}/carton"
            )
        elif item.basis == "flat_order":
            qty = item.quantity if (item.quantity is not None and item.quantity > 0) else 1
            line_summaries.append(
                f"{sku_prefix}{item.description}: {qty} flat order @ "
                f"{item.price_in_source_currency:,.2f} {intake.currency}"
            )
        elif item.basis == "slab":
            line_summaries.append(
                f"{sku_prefix}{item.description}: units {item.from_unit}-{item.to_unit} @ "
                f"{item.price_in_source_currency:,.2f} {intake.currency}/unit"
            )

    score_val = bid.score_breakdown.total_score if bid.score_breakdown else 0.0
    return PurchaseOrderDraft(
        po_reference=f"PO-{report.rfp_id}-{bid.vendor_id}",
        rfp_id=report.rfp_id,
        evaluation_date=report.evaluation_date,
        supplier_name=bid.supplier_name,
        vendor_id=bid.vendor_id,
        incoterm=bid.incoterm,
        units_ordered=bid.cost_breakdown.units_ordered,
        cartons_ordered=bid.cost_breakdown.cartons_ordered,
        spare_units=bid.cost_breakdown.spare_units,
        lead_time_days=bid.full_quantity_lead_time_days,
        warranty_months=bid.warranty_months,
        payment_terms=bid.payment_terms,
        early_payment_discount_note=bid.early_payment_discount_note,
        source_currency=bid.currency,
        net_landed_source=bid.cost_breakdown.net_landed_source,
        net_landed_usd=bid.cost_breakdown.net_landed_usd,
        recoverable_gst_usd=bid.cost_breakdown.recoverable_gst_usd,
        gross_cash_outlay_usd=bid.cost_breakdown.gross_cash_outlay_usd,
        rubric_score=score_val,
        approval_basis=approval_basis,
        line_items_summary=line_summaries,
    )


def evaluate_post_selection(
    report: EvaluationReport,
    intakes: list[SupplierBidIntake],
    vendor_query: str,
    buyer_justification: str | None = None,
) -> PostSelectionDecision:
    """Enforce deterministic post-selection policy gates on an explicit buyer choice."""
    bid, intake = find_bid_and_intake(report, intakes, vendor_query)

    # Branch 3: Disqualified or Clarification-Required -> Hard policy block (never draft PO)
    if bid.status != "COMPLIANT":
        clarification = (
            build_clarification_draft(report.rfp_id, bid)
            if bid.status == "CLARIFICATION_REQUIRED"
            else None
        )
        compliant_names = ", ".join(
            f"{c.supplier_name} ({c.vendor_id})" for c in report.compliant_finalists
        )
        return PostSelectionDecision(
            outcome="POLICY_BLOCKED",
            rfp_id=report.rfp_id,
            vendor_id=bid.vendor_id,
            supplier_name=bid.supplier_name,
            compliance_status=bid.status,
            po_drafted=False,
            clarification_draft=clarification,
            blocked_reasons=list(bid.filter_reasons),
            summary_message=(
                f"PO drafting blocked for {bid.supplier_name} ({bid.vendor_id}): status is {bid.status}. "
                f"Procurement policy cannot be overridden by verbal claims or user prompts. "
                f"Select a compliant finalist ({compliant_names})."
            ),
        )

    cap = report.auto_approval_cap_usd
    net_usd = bid.cost_breakdown.net_landed_usd
    score_val = bid.score_breakdown.total_score if bid.score_breakdown else 0.0
    rank_val = bid.rank or 1

    # Branch 1: Compliant and <= $50,000 net landed USD -> Direct PO draft
    if net_usd <= cap:
        basis = (
            f"Auto-approved: compliant finalist at ${net_usd:,.2f} net landed USD "
            f"(within ${cap:,.2f} auto-approval cap)."
        )
        po = _build_po_draft(report, bid, intake, approval_basis=basis)
        return PostSelectionDecision(
            outcome="DIRECT_PO_APPROVED",
            rfp_id=report.rfp_id,
            vendor_id=bid.vendor_id,
            supplier_name=bid.supplier_name,
            compliance_status="COMPLIANT",
            po_drafted=True,
            po_draft=po,
            summary_message=(
                f"Award Decision and PO Summary ({po.po_reference}) drafted directly for "
                f"{bid.supplier_name} ({bid.vendor_id}) at ${net_usd:,.2f} net landed USD "
                f"(<= ${cap:,.2f} cap; no manager sign-off required)."
            ),
        )

    # Branch 2: Compliant and > $50,000 net landed USD -> Hold PO & trigger Manager Sign-Off
    overage = float(_round2(_d(net_usd) - _d(cap)))
    default_rationale = "; ".join(bid.pros) if bid.pros else f"Ranked #{rank_val} ({score_val:.1f}/100)"
    rationale = (
        f"{buyer_justification.strip()} ({default_rationale})"
        if buyer_justification and buyer_justification.strip()
        else default_rationale
    )
    signoff = ManagerSignOffRequest(
        rfp_id=report.rfp_id,
        supplier_name=bid.supplier_name,
        vendor_id=bid.vendor_id,
        net_landed_usd=net_usd,
        gross_cash_outlay_usd=bid.cost_breakdown.gross_cash_outlay_usd,
        auto_approval_cap_usd=cap,
        overage_usd=overage,
        rubric_score=score_val,
        rank=rank_val,
        lead_time_days=bid.full_quantity_lead_time_days,
        warranty_months=bid.warranty_months,
        payment_terms=bid.payment_terms,
        business_justification=rationale,
    )
    return PostSelectionDecision(
        outcome="MANAGER_SIGNOFF_REQUIRED",
        rfp_id=report.rfp_id,
        vendor_id=bid.vendor_id,
        supplier_name=bid.supplier_name,
        compliance_status="COMPLIANT",
        po_drafted=False,
        signoff_request=signoff,
        summary_message=(
            f"PO drafting held for {bid.supplier_name} ({bid.vendor_id}): net landed cost "
            f"${net_usd:,.2f} exceeds the ${cap:,.2f} auto-approval cap by ${overage:,.2f}. "
            "Manager Sign-Off Exception Request generated; explicit manager approval is required before drafting PO."
        ),
    )


def resolve_manager_signoff(
    report: EvaluationReport,
    intakes: list[SupplierBidIntake],
    vendor_query: str,
    approved: bool,
    approver_note: str | None = None,
) -> PostSelectionDecision:
    """Complete or reject a pending >$50K manager sign-off gate."""
    bid, intake = find_bid_and_intake(report, intakes, vendor_query)
    if bid.status != "COMPLIANT":
        return evaluate_post_selection(report, intakes, vendor_query)

    cap = report.auto_approval_cap_usd
    net_usd = bid.cost_breakdown.net_landed_usd
    overage = float(max(Decimal("0.00"), _round2(_d(net_usd) - _d(cap))))

    if not approved:
        under_cap_options = ", ".join(
            f"{c.supplier_name} ({c.vendor_id}, ${c.cost_breakdown.net_landed_usd:,.2f})"
            for c in report.compliant_finalists
            if c.cost_breakdown.net_landed_usd <= cap
        )
        return PostSelectionDecision(
            outcome="MANAGER_SIGNOFF_REJECTED",
            rfp_id=report.rfp_id,
            vendor_id=bid.vendor_id,
            supplier_name=bid.supplier_name,
            compliance_status="COMPLIANT",
            po_drafted=False,
            summary_message=(
                f"Manager sign-off declined for {bid.supplier_name} ({bid.vendor_id}). "
                f"No PO was drafted. Please select another compliant finalist "
                f"(auto-approvable <= ${cap:,.2f} options: {under_cap_options})."
            ),
        )

    note_suffix = f" Note: {approver_note.strip()}" if approver_note and approver_note.strip() else ""
    basis = (
        f"Manager sign-off approved for ${overage:,.2f} overage above ${cap:,.2f} cap.{note_suffix}"
    )
    po = _build_po_draft(report, bid, intake, approval_basis=basis)
    return PostSelectionDecision(
        outcome="MANAGER_SIGNOFF_APPROVED_PO_DRAFTED",
        rfp_id=report.rfp_id,
        vendor_id=bid.vendor_id,
        supplier_name=bid.supplier_name,
        compliance_status="COMPLIANT",
        po_drafted=True,
        po_draft=po,
        summary_message=(
            f"Manager sign-off recorded for {bid.supplier_name} ({bid.vendor_id}). "
            f"Award Decision and PO Summary ({po.po_reference}) drafted at ${net_usd:,.2f} net landed USD."
        ),
    )
