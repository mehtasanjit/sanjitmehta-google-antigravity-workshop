"""Deterministic unit tests for scoring_engine covering all 10 quote patterns,
compliance classification, prompt-injection defense, what-if rescoring, and award gating.

Strictly tests deterministic Python logic and ADK wiring contracts (zero LLM prose assertions).
"""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.agent import app as adk_app
from app.agent import root_agent
from app.models import (
    CartonPricing,
    DeliveryBatch,
    ExtractedBid,
    PercentageSurcharge,
    PriceSlab,
    ProcurementPolicy,
    QuoteLineItem,
    TaxDetails,
)
from app.scoring_engine import (
    assemble_po_payload,
    evaluate_all_bids,
    evaluate_award_gate,
    rescore_cached_bids,
    validate_weights,
)
from app.sub_agents import build_po_draft, evaluate_award_selection, record_manager_signoff


def _build_policy() -> ProcurementPolicy:
    """Matches gs://default-project-alpha-1-rfp-eval-and-award-data/rfp-eval-and-award/policy/procurement_policy.json."""
    return ProcurementPolicy.model_validate(
        {
            "policy_version": "2026.11",
            "rfp_metadata": {
                "rfp_id": "RFP-2026-441",
                "title": "Industrial Outdoor Pressure Sensors (0-500 PSI)",
                "evaluation_date": "2026-11-23",
                "required_quantity": 1000,
                "target_incoterm": "DDP Hyderabad",
                "max_delivery_days": 28,
                "required_ingress_rating": "IP67",
                "min_warranty_months": 24,
                "auto_approval_cap_usd": 50000.0,
            },
            "fx_rates_to_usd": {
                "USD": 1.0,
                "EUR": 1.08,
                "INR": 0.0119,
                "JPY": 0.0066,
            },
            "normalization_rules": {
                "exw_shenzhen_adder_pct": 0.18,
                "exw_shenzhen_breakdown": {
                    "customs_duty_pct": 0.12,
                    "international_air_freight_pct": 0.06,
                },
                "exclude_optional_line_items": True,
                "india_gst_rate": 0.18,
                "india_gst_recoverable_itc": True,
                "gst_accounting_note": "Exclude recoverable 18% Indian GST ITC.",
            },
            "compliance_rules": {
                "require_approved_vendor": True,
                "ignore_unverified_verbal_approvals": True,
                "require_valid_quote_on_evaluation_date": True,
                "require_explicit_ingress_certification": True,
                "full_quantity_must_meet_sla": True,
                "manager_signoff_required_above_usd": 50000.0,
                "manager_signoff_trigger": "only_when_buyer_selects_bid_above_cap",
            },
            "scoring_rubric": {
                "total_points": 100,
                "weights": {
                    "net_landed_cost": 40,
                    "delivery_speed": 20,
                    "warranty_months": 15,
                    "supplier_track_record": 15,
                    "payment_terms": 10,
                },
                "cost_formula": "weight * (min_compliant_net_landed_usd / bid_net_landed_usd)",
                "delivery_speed_brackets": [
                    {"max_days": 14, "points": 20},
                    {"max_days": 18, "points": 16},
                    {"max_days": 21, "points": 12},
                    {"max_days": 28, "points": 8},
                ],
                "warranty_brackets": [
                    {"min_months": 36, "points": 15},
                    {"min_months": 24, "points": 10},
                ],
                "supplier_track_record_tiers": {
                    "incumbent_high_otd": {"description": "Incumbent >=98% OTD", "points": 15},
                    "established_partner": {"description": "Partner >=95% OTD", "points": 12},
                    "standard_approved": {"description": "Standard <95% OTD", "points": 8},
                    "new_onboarded": {"description": "New 0 prior POs", "points": 6},
                },
                "payment_terms_points": {
                    "Net 90": 10,
                    "Net 60": 8,
                    "Net 45": 7,
                    "Net 30": 5,
                    "Advance": 2,
                },
            },
            "approved_vendors": {
                "VND-104": {
                    "name": "Apex Sensors Inc",
                    "location": "Chicago, USA",
                    "relationship_status": "incumbent",
                    "tenure_years": 7.0,
                    "prior_pos": 24,
                    "on_time_delivery_pct": 99.2,
                    "track_record_tier": "incumbent_high_otd",
                },
                "VND-209": {
                    "name": "EuroSense GmbH",
                    "location": "Munich, Germany",
                    "relationship_status": "incumbent",
                    "tenure_years": 5.0,
                    "prior_pos": 14,
                    "on_time_delivery_pct": 98.5,
                    "track_record_tier": "incumbent_high_otd",
                },
                "VND-312": {
                    "name": "BharatSense Controls Pvt Ltd",
                    "location": "Pune, India",
                    "relationship_status": "new_onboarded",
                    "tenure_years": 0.5,
                    "prior_pos": 0,
                    "on_time_delivery_pct": None,
                    "track_record_tier": "new_onboarded",
                },
                "VND-418": {
                    "name": "NipponTech Precision KK",
                    "location": "Tokyo, Japan",
                    "relationship_status": "established_partner",
                    "tenure_years": 3.5,
                    "prior_pos": 9,
                    "on_time_delivery_pct": 97.4,
                    "track_record_tier": "established_partner",
                },
                "VND-505": {
                    "name": "Vanguard Industrial Supply LLC",
                    "location": "Houston, USA",
                    "relationship_status": "established_partner",
                    "tenure_years": 2.0,
                    "prior_pos": 4,
                    "on_time_delivery_pct": 95.1,
                    "track_record_tier": "established_partner",
                },
                "VND-611": {
                    "name": "QuantumGrid Automation Corp",
                    "location": "Austin, USA",
                    "relationship_status": "established_partner",
                    "tenure_years": 3.0,
                    "prior_pos": 8,
                    "on_time_delivery_pct": 96.0,
                    "track_record_tier": "established_partner",
                },
                "VND-702": {
                    "name": "NordicSense AB",
                    "location": "Gothenburg, Sweden",
                    "relationship_status": "incumbent",
                    "tenure_years": 4.0,
                    "prior_pos": 11,
                    "on_time_delivery_pct": 98.0,
                    "track_record_tier": "incumbent_high_otd",
                },
                "VND-815": {
                    "name": "DeccanTech Systems Pvt Ltd",
                    "location": "Hyderabad, India",
                    "relationship_status": "established_partner",
                    "tenure_years": 2.0,
                    "prior_pos": 6,
                    "on_time_delivery_pct": 95.5,
                    "track_record_tier": "established_partner",
                },
                "VND-901": {
                    "name": "Pacific Industrial Controls Inc",
                    "location": "San Jose, USA",
                    "relationship_status": "standard_approved",
                    "tenure_years": 1.0,
                    "prior_pos": 2,
                    "on_time_delivery_pct": 93.0,
                    "track_record_tier": "standard_approved",
                },
            },
        }
    )


def _build_all_10_extracted_bids() -> list[ExtractedBid]:
    """Structured raw facts mirroring all 10 RFP-2026-441 supplier quotes."""
    return [
        # 01 Apex: mandatory IP67 kit ($4.50) + 8% expedited air freight for 14d SLA
        ExtractedBid(
            source_filename="01_apex_sensors_quote.md",
            supplier_name="Apex Sensors Inc",
            vendor_id="VND-104",
            quote_date="2026-11-14",
            valid_until="2026-12-15",
            currency="USD",
            incoterm="DDP Hyderabad",
            quantity_quoted=1000,
            pricing_model="line_items",
            line_items=[
                QuoteLineItem(
                    sku="APX-P400",
                    description="Industrial Pressure Sensor (0-500 PSI)",
                    unit_basis="per_unit",
                    quantity=1000,
                    price=44.00,
                    mandatory_for_rfp_spec=True,
                ),
                QuoteLineItem(
                    sku="APX-IP67-KIT",
                    description="Mandatory IP67 Weatherproof Enclosure Kit",
                    unit_basis="per_unit",
                    quantity=1000,
                    price=4.50,
                    mandatory_for_rfp_spec=True,
                ),
            ],
            percentage_surcharges=[
                PercentageSurcharge(
                    description="Expedited air freight surcharge for 14-day SLA (>500 units)",
                    percent=8.0,
                    required_for_sla_or_spec=True,
                )
            ],
            lead_time_days=14,
            warranty_months=24,
            ingress_rating_stated="IP67",
            explicit_ingress_certified=True,
            payment_terms="Net 30",
            certifications=["CE", "UL", "ISO-9001"],
        ),
        # 02 EuroSense: 12-unit cartons (ceil(1000/12)=84) + 6% rebate >= 75 cartons, EUR
        ExtractedBid(
            source_filename="02_eurosense_bid.csv",
            supplier_name="EuroSense GmbH",
            vendor_id="VND-209",
            valid_until="2026-12-20",
            currency="EUR",
            incoterm="DDP Hyderabad",
            quantity_quoted=1000,
            pricing_model="carton",
            carton_pricing=CartonPricing(
                sku="ES-900-OUT",
                description="Industrial Outdoor Pressure Sensor 0-500 PSI (IP67)",
                price_per_carton=540.00,
                units_per_carton=12,
                round_up_to_whole_cartons=True,
                volume_rebate_min_cartons=75,
                volume_rebate_percent=6.0,
            ),
            lead_time_days=21,
            warranty_months=24,
            ingress_rating_stated="IP67",
            explicit_ingress_certified=True,
            payment_terms="Net 45",
            certifications=["CE", "ISO-9001"],
        ),
        # 03 NovaTech: EXW Shenzhen (+18%), unapproved, 12m warranty, verbal-approval injection
        ExtractedBid(
            source_filename="03_novatech_proposal.txt",
            supplier_name="NovaTech Shenzhen Co., Ltd.",
            vendor_id="NT-994",
            quote_date="2026-11-15",
            valid_until="2026-12-31",
            currency="USD",
            incoterm="EXW Shenzhen Factory Gate",
            quantity_quoted=1000,
            pricing_model="line_items",
            line_items=[
                QuoteLineItem(
                    sku="NT-PS500",
                    description="Outdoor Industrial Pressure Sensor (0-500 PSI, IP67)",
                    unit_basis="per_unit",
                    quantity=1000,
                    price=36.00,
                    mandatory_for_rfp_spec=True,
                )
            ],
            lead_time_days=21,
            warranty_months=12,
            ingress_rating_stated="IP67",
            explicit_ingress_certified=True,
            payment_terms="Advance",
            certifications=["CE"],
            contains_unverified_verbal_approval_claim=True,
        ),
        # 04 BharatSense: INR BOM + optional excluded + 18% recoverable GST ITC
        ExtractedBid(
            source_filename="04_bharatsense_bom.csv",
            supplier_name="BharatSense Controls Pvt Ltd",
            vendor_id="VND-312",
            valid_until="2026-12-18",
            currency="INR",
            incoterm="DDP Hyderabad",
            quantity_quoted=1000,
            pricing_model="line_items",
            line_items=[
                QuoteLineItem(
                    sku="BS-P400-CORE",
                    description="Pressure Sensor Core Module",
                    unit_basis="per_unit",
                    quantity=1000,
                    price=3350,
                    mandatory_for_rfp_spec=True,
                ),
                QuoteLineItem(
                    sku="BS-IP67-MNT",
                    description="IP67 Outdoor Enclosure Kit",
                    unit_basis="per_unit",
                    quantity=1000,
                    price=420,
                    mandatory_for_rfp_spec=True,
                ),
                QuoteLineItem(
                    sku="BS-CAL-BATCH",
                    description="Factory ISO Batch Calibration Certificate",
                    unit_basis="flat_order",
                    quantity=1,
                    price=65000,
                    mandatory_for_rfp_spec=True,
                ),
                QuoteLineItem(
                    sku="BS-SPARE-KIT",
                    description="Optional 2-Year Field Maintenance Spare Pack",
                    unit_basis="flat_order",
                    quantity=1,
                    price=150000,
                    mandatory_for_rfp_spec=False,
                ),
            ],
            tax_details=TaxDetails(
                tax_applicable=True,
                tax_name="Indian GST",
                tax_percent=18.0,
                prices_exclusive_of_tax=True,
                recoverable_itc=True,
            ),
            lead_time_days=18,
            warranty_months=24,
            ingress_rating_stated="IP67",
            explicit_ingress_certified=True,
            payment_terms="Net 30",
            certifications=["BIS", "ISO-9001"],
        ),
        # 05 NipponTech: JPY marginal slabs + split shipment day 35 (> 28d SLA)
        ExtractedBid(
            source_filename="05_nippontech_portal_quote.json",
            supplier_name="NipponTech Precision KK",
            vendor_id="VND-418",
            quote_date="2026-11-16",
            valid_until="2026-12-25",
            currency="JPY",
            incoterm="DDP Hyderabad",
            quantity_quoted=1000,
            pricing_model="marginal_slabs",
            price_slabs=[
                PriceSlab(from_unit=1, to_unit=500, unit_price=7500),
                PriceSlab(from_unit=501, to_unit=1000, unit_price=6800),
            ],
            lead_time_days=14,
            delivery_batches=[
                DeliveryBatch(batch_number=1, units=500, lead_time_days=14),
                DeliveryBatch(batch_number=2, units=500, lead_time_days=35),
            ],
            warranty_months=24,
            ingress_rating_stated="IP67",
            explicit_ingress_certified=True,
            payment_terms="Net 30",
            certifications=["JIS", "CE", "ISO-9001"],
        ),
        # 06 Vanguard: expired quote (2026-11-18 < 2026-11-23) + vague weather-resistant housing
        ExtractedBid(
            source_filename="06_vanguard_spec_quote.txt",
            supplier_name="Vanguard Industrial Supply LLC",
            vendor_id="VND-505",
            quote_date="2026-10-19",
            valid_until="2026-11-18",
            currency="USD",
            incoterm="DDP Hyderabad",
            quantity_quoted=1000,
            pricing_model="line_items",
            line_items=[
                QuoteLineItem(
                    sku="VGS-500",
                    description="VGS-500 Outdoor Pressure Sensor",
                    unit_basis="per_unit",
                    quantity=1000,
                    price=45.50,
                    mandatory_for_rfp_spec=True,
                )
            ],
            lead_time_days=22,
            warranty_months=24,
            ingress_rating_stated=None,
            explicit_ingress_certified=False,
            payment_terms="Net 30",
            certifications=["CE", "ISO-9001"],
        ),
        # 07 QuantumGrid: USD Net 90 + optional 2% Net 15 note + 36m warranty
        ExtractedBid(
            source_filename="07_quantumgrid_partner_quote.md",
            supplier_name="QuantumGrid Automation Corp",
            vendor_id="VND-611",
            quote_date="2026-11-17",
            valid_until="2026-12-31",
            currency="USD",
            incoterm="DDP Hyderabad",
            quantity_quoted=1000,
            pricing_model="line_items",
            line_items=[
                QuoteLineItem(
                    sku="QGA-PS500-IP67",
                    description="IP67 Industrial Pressure Sensor",
                    unit_basis="per_unit",
                    quantity=1000,
                    price=48.90,
                    mandatory_for_rfp_spec=True,
                )
            ],
            lead_time_days=24,
            warranty_months=36,
            ingress_rating_stated="IP67",
            explicit_ingress_certified=True,
            payment_terms="Net 90",
            early_payment_discount_note="Optional 2% early-payment discount if settled within Net 15 ($47,922.00 USD net).",
            certifications=["CE", "UL", "ISO-9001", "ISO-14001"],
        ),
        # 08 NordicSense: EUR per-unit + mandatory flat fee -> $51,084.00 (> $50K cap)
        ExtractedBid(
            source_filename="08_nordicsense_quote.json",
            supplier_name="NordicSense AB",
            vendor_id="VND-702",
            quote_date="2026-11-17",
            valid_until="2026-12-28",
            currency="EUR",
            incoterm="DDP Hyderabad",
            quantity_quoted=1000,
            pricing_model="line_items",
            line_items=[
                QuoteLineItem(
                    sku="NS-PRO-500-IP67",
                    description="NS-PRO-500-IP67 Pressure Sensor Unit",
                    unit_basis="per_unit",
                    quantity=1000,
                    price=45.50,
                    mandatory_for_rfp_spec=True,
                ),
                QuoteLineItem(
                    sku="NS-CAL-PACK",
                    description="Mandatory Factory IP67 Immersion Test & Calibration Pack",
                    unit_basis="flat_order",
                    quantity=1,
                    price=1800.00,
                    mandatory_for_rfp_spec=True,
                ),
            ],
            lead_time_days=16,
            warranty_months=36,
            ingress_rating_stated="IP67",
            explicit_ingress_certified=True,
            payment_terms="Net 45",
            certifications=["CE", "ATEX", "ISO-9001", "ISO-14001"],
        ),
        # 09 DeccanTech: INR BOM + optional excluded + 18% recoverable GST ITC, 15d, Net 60
        ExtractedBid(
            source_filename="09_deccantech_quote.md",
            supplier_name="DeccanTech Systems Pvt Ltd",
            vendor_id="VND-815",
            quote_date="2026-11-18",
            valid_until="2026-12-30",
            currency="INR",
            incoterm="DDP Hyderabad",
            quantity_quoted=1000,
            pricing_model="line_items",
            line_items=[
                QuoteLineItem(
                    sku="DT-PS500-BASE",
                    description="Industrial Pressure Sensor Core",
                    unit_basis="per_unit",
                    quantity=1000,
                    price=3520,
                    mandatory_for_rfp_spec=True,
                ),
                QuoteLineItem(
                    sku="DT-IP67-SHIELD",
                    description="IP67 Sealed Outdoor Housing Kit",
                    unit_basis="per_unit",
                    quantity=1000,
                    price=430,
                    mandatory_for_rfp_spec=True,
                ),
                QuoteLineItem(
                    sku="DT-ISO-CAL",
                    description="Mandatory Factory ISO Batch Calibration Certificate",
                    unit_basis="flat_order",
                    quantity=1,
                    price=40000,
                    mandatory_for_rfp_spec=True,
                ),
                QuoteLineItem(
                    sku="DT-ONSITE-COMM",
                    description="Optional Onsite Commissioning Support Package",
                    unit_basis="flat_order",
                    quantity=1,
                    price=120000,
                    mandatory_for_rfp_spec=False,
                ),
            ],
            tax_details=TaxDetails(
                tax_applicable=True,
                tax_name="Indian GST",
                tax_percent=18.0,
                prices_exclusive_of_tax=True,
                recoverable_itc=True,
            ),
            lead_time_days=15,
            warranty_months=24,
            ingress_rating_stated="IP67",
            explicit_ingress_certified=True,
            payment_terms="Net 60",
            certifications=["BIS", "CE", "ISO-9001"],
        ),
        # 10 Pacific Industrial: 18-month warranty (< 24m minimum) -> DISQUALIFIED
        ExtractedBid(
            source_filename="10_pacific_industrial_bid.csv",
            supplier_name="Pacific Industrial Controls Inc",
            vendor_id="VND-901",
            valid_until="2026-12-22",
            currency="USD",
            incoterm="DDP Hyderabad",
            quantity_quoted=1000,
            pricing_model="line_items",
            line_items=[
                QuoteLineItem(
                    sku="PIC-500-IP67",
                    description="IP67 Industrial Outdoor Pressure Sensor",
                    unit_basis="per_unit",
                    quantity=1000,
                    price=43.80,
                    mandatory_for_rfp_spec=True,
                )
            ],
            lead_time_days=20,
            warranty_months=18,
            ingress_rating_stated="IP67",
            explicit_ingress_certified=True,
            payment_terms="Net 30",
            certifications=["CE", "ISO-9001"],
        ),
    ]


def test_all_10_quotes_normalization_compliance_and_ranking() -> None:
    """Verifies exact Decimal totals, GST separation, compliance, and ranking across all 10 quotes."""
    policy = _build_policy()
    summary = evaluate_all_bids(_build_all_10_extracted_bids(), policy)

    assert summary.total_quotes_evaluated == 10
    assert summary.compliant_count == 6
    assert summary.clarification_required_count == 1
    assert summary.disqualified_count == 3
    assert summary.min_compliant_net_landed_usd == "45636.50"

    # Exact net landed USD verification for all 10 bids
    by_id = summary.all_bids_by_vendor_id
    assert by_id["VND-104"].net_landed_usd == "52380.00"
    assert by_id["VND-209"].net_landed_usd == "46049.47"
    assert by_id["VND-209"].quantity_billed == 1008
    assert by_id["NT-994"].net_landed_usd == "42480.00"
    assert by_id["VND-312"].net_landed_usd == "45636.50"
    assert by_id["VND-312"].gross_cash_outlay_native == "4525300.00"
    assert by_id["VND-312"].gross_cash_outlay_usd == "53851.07"
    assert len(by_id["VND-312"].excluded_optional_items) == 1
    assert by_id["VND-418"].net_landed_usd == "47190.00"
    assert by_id["VND-505"].net_landed_usd == "45500.00"
    assert by_id["VND-611"].net_landed_usd == "48900.00"
    assert by_id["VND-702"].net_landed_usd == "51084.00"
    assert by_id["VND-815"].net_landed_usd == "47481.00"
    assert by_id["VND-815"].gross_cash_outlay_native == "4708200.00"
    assert by_id["VND-815"].gross_cash_outlay_usd == "56027.58"
    assert len(by_id["VND-815"].excluded_optional_items) == 1
    assert by_id["VND-901"].net_landed_usd == "43800.00"

    # Exact default ranking order & scores
    ranked_ids = [b.vendor_id for b in summary.compliant_ranked]
    assert ranked_ids == ["VND-702", "VND-104", "VND-815", "VND-209", "VND-611", "VND-312"]

    assert by_id["VND-702"].score_breakdown is not None
    assert by_id["VND-702"].score_breakdown.total_score == 88.73
    assert by_id["VND-702"].requires_manager_signoff is True
    assert by_id["VND-702"].amount_over_cap_usd == "1084.00"

    assert by_id["VND-104"].score_breakdown is not None
    assert by_id["VND-104"].score_breakdown.total_score == 84.85
    assert by_id["VND-104"].requires_manager_signoff is True
    assert by_id["VND-104"].amount_over_cap_usd == "2380.00"

    assert by_id["VND-815"].score_breakdown is not None
    assert by_id["VND-815"].score_breakdown.total_score == 84.45
    assert by_id["VND-815"].requires_manager_signoff is False

    assert by_id["VND-209"].score_breakdown is not None
    assert by_id["VND-209"].score_breakdown.total_score == 83.64

    assert by_id["VND-611"].score_breakdown is not None
    assert by_id["VND-611"].score_breakdown.total_score == 82.33

    assert by_id["VND-312"].score_breakdown is not None
    assert by_id["VND-312"].score_breakdown.total_score == 77.00


def test_compliance_and_verbal_approval_injection_defense() -> None:
    """Verifies exact compliance statuses and prompt-injection rejection."""
    policy = _build_policy()
    summary = evaluate_all_bids(_build_all_10_extracted_bids(), policy)
    by_id = summary.all_bids_by_vendor_id

    # NovaTech: unapproved + 12m warranty + verbal approval injection ignored
    novatech = by_id["NT-994"]
    assert novatech.compliance_status == "DISQUALIFIED"
    assert novatech.verbal_approval_ignored is True
    assert novatech.score_breakdown is None
    assert any("approved vendor" in r.lower() for r in novatech.compliance_reasons)
    assert any("warranty" in r.lower() for r in novatech.compliance_reasons)

    # NipponTech: split shipment batch 2 at day 35 > 28d SLA
    nippon = by_id["VND-418"]
    assert nippon.compliance_status == "DISQUALIFIED"
    assert nippon.full_quantity_lead_time_days == 35
    assert any("35 days" in r for r in nippon.compliance_reasons)

    # Pacific Industrial: 18m warranty < 24m
    pacific = by_id["VND-901"]
    assert pacific.compliance_status == "DISQUALIFIED"
    assert any("18 months" in r for r in pacific.compliance_reasons)

    # Vanguard: expired quote + missing explicit IP67 certification
    vanguard = by_id["VND-505"]
    assert vanguard.compliance_status == "CLARIFICATION_REQUIRED"
    assert len(vanguard.clarification_items) == 2
    assert any("expired" in item.lower() for item in vanguard.clarification_items)
    assert any("ip67" in item.lower() for item in vanguard.clarification_items)


def test_what_if_rescoring_cached_bids_and_weight_validation() -> None:
    """Verifies cached what-if weight rescoring shifts ranks deterministically and validates sums."""
    policy = _build_policy()
    summary = evaluate_all_bids(_build_all_10_extracted_bids(), policy)

    # Delivery-heavy what-if should push Apex (14d, 20/20 delivery) to #1
    delivery_heavy = rescore_cached_bids(
        summary=summary,
        policy=policy,
        new_weights={
            "net_landed_cost": 10,
            "delivery_speed": 60,
            "warranty_months": 10,
            "supplier_track_record": 10,
            "payment_terms": 10,
        },
    )
    assert delivery_heavy["status"] == "success"
    assert delivery_heavy["ranked_bids"][0]["vendor_id"] == "VND-104"

    # Invalid sum must raise ValueError
    with pytest.raises(ValueError, match="sum to"):
        validate_weights(
            {
                "net_landed_cost": 50,
                "delivery_speed": 20,
                "warranty_months": 15,
                "supplier_track_record": 15,
                "payment_terms": 10,
            }
        )


def test_award_gate_and_python_po_authorization_enforcement() -> None:
    """Verifies <= $50K auto-authorization, > $50K manager sign-off pause, blocked bids, and Python PO gate."""
    policy = _build_policy()
    summary = evaluate_all_bids(_build_all_10_extracted_bids(), policy)

    # 1. PO denied when award_authorized is False (Turn-1 / premature PO protection)
    ctx = SimpleNamespace(
        state={
            "policy": policy.model_dump(),
            "evaluation_summary": summary.model_dump(),
            "award_authorized": False,
            "selected_vendor_id": "VND-815",
        }
    )
    blocked_po = build_po_draft("", "", "", "", "", tool_context=ctx)  # type: ignore[arg-type]
    assert blocked_po["status"] == "BLOCKED"

    # 2. Selecting DISQUALIFIED vendor (NovaTech) stays unauthorized
    disq = evaluate_award_selection("NT-994", tool_context=ctx)  # type: ignore[arg-type]
    assert disq["decision"] == "BLOCKED_DISQUALIFIED"
    assert ctx.state["award_authorized"] is False

    # 3. Selecting CLARIFICATION_REQUIRED vendor (Vanguard) stays unauthorized
    clar = evaluate_award_selection("Vanguard", tool_context=ctx)  # type: ignore[arg-type]
    assert clar["decision"] == "BLOCKED_CLARIFICATION_REQUIRED"
    assert len(clar["clarification_items"]) == 2
    assert ctx.state["award_authorized"] is False

    # 4. Selecting > $50K compliant vendor (NordicSense $51,084) holds PO until manager approval
    held = evaluate_award_selection("NordicSense AB", tool_context=ctx)  # type: ignore[arg-type]
    assert held["decision"] == "MANAGER_SIGNOFF_REQUIRED"
    assert held["amount_over_cap_usd"] == "1084.00"
    assert ctx.state["award_authorized"] is False
    assert ctx.state["pending_signoff"]["vendor_id"] == "VND-702"

    # PO still blocked while awaiting manager sign-off
    still_blocked = build_po_draft("", "", "", "", "", tool_context=ctx)  # type: ignore[arg-type]
    assert still_blocked["status"] == "BLOCKED"

    # Manager approves -> award_authorized flips to True -> PO draft succeeds with exact Decimal total
    approved = record_manager_signoff(
        approver_name="Sarah Chen",
        approval_rationale="Highest overall score with 36-month warranty and incumbent OTD.",
        approved=True,
        tool_context=ctx,  # type: ignore[arg-type]
    )
    assert approved["status"] == "APPROVED_FOR_PO"
    assert ctx.state["award_authorized"] is True

    po = build_po_draft(
        ship_to_location="Hyderabad Plant Dock B",
        ship_to_contact="Priya Rao",
        cost_center="CC-4410",
        billing_instructions="",
        special_delivery_notes="Include IEC 60529 cert in carton 1.",
        tool_context=ctx,  # type: ignore[arg-type]
    )
    assert po["status"] == "DRAFT_READY"
    assert po["vendor_id"] == "VND-702"
    assert po["net_landed_usd"] == "51084.00"
    assert po["manager_signoff"]["approver_name"] == "Sarah Chen"
    assert po["buyer_metadata"]["cost_center"] == "CC-4410"

    # 5. Selecting <= $50K compliant vendor (DeccanTech $47,481) authorizes immediately
    auto = evaluate_award_selection("VND-815", tool_context=ctx)  # type: ignore[arg-type]
    assert auto["decision"] == "AUTHORIZED_FOR_PO"
    assert ctx.state["award_authorized"] is True
    po_auto = assemble_po_payload(
        summary=summary,
        policy=policy,
        vendor_id="VND-815",
        award_authorized=True,
    )
    assert po_auto["status"] == "DRAFT_READY"
    assert po_auto["net_landed_usd"] == "47481.00"
    assert po_auto["gross_cash_outlay_usd"] == "56027.58"
    assert Decimal(po_auto["net_landed_usd"]) <= Decimal("50000.00")


def test_agent_architecture_wiring_contracts() -> None:
    """Verifies ADK 2.0 wiring: Workflow as NodeTool in root tools, modes on sub-agents, App name='app'."""
    assert adk_app.name == "app"
    assert root_agent.name == "rfp_eval_adk"
    assert root_agent.mode == "chat"

    # Root tools contain NodeTool(rfp_evaluation_workflow) plus ADK auto-generated task delegation tools
    node_tools = [t for t in root_agent.tools if type(t).__name__ == "NodeTool"]
    assert len(node_tools) == 1
    assert node_tools[0].name == "rfp_evaluation_workflow"
    assert getattr(node_tools[0].node, "input_schema", None) is not None

    # Root has zero direct math, GCS, or PO FunctionTools
    tool_names = {getattr(t, "name", "") for t in root_agent.tools}
    assert "build_po_draft" not in tool_names
    assert "rescore_what_if" not in tool_names
    assert "evaluate_award_selection" not in tool_names

    sub_by_name = {a.name: a for a in root_agent.sub_agents}
    assert set(sub_by_name.keys()) == {
        "what_if_analyst_agent",
        "policy_signoff_agent",
        "po_drafter_agent",
    }
    assert sub_by_name["what_if_analyst_agent"].mode == "task"
    assert sub_by_name["policy_signoff_agent"].mode == "task"
    assert sub_by_name["po_drafter_agent"].mode == "chat"

    gate_check = evaluate_award_gate(
        summary=evaluate_all_bids(_build_all_10_extracted_bids(), _build_policy()),
        policy=_build_policy(),
        vendor_identifier="UNKNOWN-999",
    )
    assert gate_check["decision"] == "NOT_FOUND"
