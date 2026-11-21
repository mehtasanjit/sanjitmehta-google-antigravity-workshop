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

"""Deterministic unit tests for scoring_engine (all 10 quote patterns, compliance, injections, what-if, award/PO gates)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.models import (
    CartonPricing,
    ExpeditedFreightRule,
    ExtractedQuoteFacts,
    MarginalPriceSlab,
    ProcurementPolicy,
    QuotedLineItem,
    ScoringWeights,
    ShipmentBatch,
)
from app.scoring_engine import (
    build_po_draft,
    evaluate_award_gate,
    normalize_and_evaluate_bid,
    rescore_cached_bids,
    score_bids,
)


@pytest.fixture
def policy() -> ProcurementPolicy:
    """Exact procurement_policy.json structure (v2026.11) for deterministic math tests."""
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
                "gst_accounting_note": "Exclude recoverable 18% Indian GST Input Tax Credit from net landed USD comparison; report gross cash outlay separately.",
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
                    "incumbent_high_otd": {
                        "description": "Approved incumbent with >= 98.0% historical OTD and >= 10 prior POs",
                        "points": 15,
                    },
                    "established_partner": {
                        "description": "Approved partner with >= 95.0% historical OTD and >= 3 prior POs",
                        "points": 12,
                    },
                    "standard_approved": {
                        "description": "Approved vendor with prior PO history below 95.0% OTD",
                        "points": 8,
                    },
                    "new_onboarded": {
                        "description": "Newly onboarded approved vendor with 0 prior POs",
                        "points": 6,
                    },
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


@pytest.fixture
def all_ten_quotes() -> list[ExtractedQuoteFacts]:
    """Structured factual representations covering all 10 GCS quote patterns."""
    return [
        # 01 Apex Sensors: IP54 base + mandatory IP67 kit + mandatory 8% expedited air freight
        ExtractedQuoteFacts(
            source_filename="01_apex_sensors_quote.md",
            vendor_id="VND-104",
            supplier_name="Apex Sensors Inc",
            quote_date="2026-11-14",
            valid_until="2026-12-15",
            currency="USD",
            incoterm="DDP Hyderabad",
            is_exw_shenzhen=False,
            quantity_quoted=1000,
            pricing_structure="line_items",
            line_items=[
                QuotedLineItem(
                    sku="APX-P400",
                    description="Industrial Pressure Sensor (0-500 PSI)",
                    unit_basis="per_unit",
                    quantity=1000,
                    price_native="44.00",
                    mandatory_for_rfp_spec=True,
                ),
                QuotedLineItem(
                    sku="APX-IP67-KIT",
                    description="Mandatory IP67 Weatherproof Enclosure Kit",
                    unit_basis="per_unit",
                    quantity=1000,
                    price_native="4.50",
                    mandatory_for_rfp_spec=True,
                ),
            ],
            expedited_freight_option=ExpeditedFreightRule(
                standard_lead_time_days=49,
                expedited_lead_time_days=14,
                min_units_for_surcharge=500,
                surcharge_percent="8",
                applies_to_hardware_total=True,
            ),
            lead_time_days=14,
            warranty_months=24,
            ingress_rating_stated="IP67 with mandatory IP67 Weatherproof Enclosure Kit",
            has_explicit_ip67_certification=True,
            payment_terms_standard="Net 30",
            certifications=["CE", "UL", "ISO-9001"],
        ),
        # 02 EuroSense: EUR master carton of 12 (84 cartons = 1,008 units) + 6% rebate
        ExtractedQuoteFacts(
            source_filename="02_eurosense_bid.csv",
            vendor_id="VND-209",
            supplier_name="EuroSense GmbH",
            valid_until="2026-12-20",
            currency="EUR",
            incoterm="DDP Hyderabad",
            is_exw_shenzhen=False,
            quantity_quoted=1000,
            pricing_structure="master_carton",
            carton_pricing=CartonPricing(
                sku="ES-900-OUT",
                description="Industrial Outdoor Pressure Sensor 0-500 PSI (IP67)",
                price_per_carton_native="540.00",
                units_per_carton=12,
                must_round_up_whole_cartons=True,
                volume_rebate_min_cartons=75,
                volume_rebate_percent="6",
            ),
            lead_time_days=21,
            warranty_months=24,
            ingress_rating_stated="IP67 Certified",
            has_explicit_ip67_certification=True,
            payment_terms_standard="Net 45",
            certifications=["CE", "ISO-9001"],
        ),
        # 03 NovaTech: unapproved vendor + EXW Shenzhen (+18%) + 12m warranty + verbal VP injection
        ExtractedQuoteFacts(
            source_filename="03_novatech_proposal.txt",
            vendor_id="NT-994",
            supplier_name="NovaTech Shenzhen Co., Ltd.",
            quote_date="2026-11-15",
            valid_until="2026-12-31",
            currency="USD",
            incoterm="EXW Shenzhen Factory Gate",
            is_exw_shenzhen=True,
            quantity_quoted=1000,
            pricing_structure="line_items",
            line_items=[
                QuotedLineItem(
                    sku="NT-PS500",
                    description="Outdoor Industrial Pressure Sensor (0-500 PSI, IP67)",
                    unit_basis="per_unit",
                    quantity=1000,
                    price_native="36.00",
                    mandatory_for_rfp_spec=True,
                ),
            ],
            lead_time_days=21,
            warranty_months=12,
            ingress_rating_stated="IP67 rated",
            has_explicit_ip67_certification=True,
            payment_terms_standard="Advance",
            certifications=["CE"],
            contains_verbal_approval_claim=True,
            verbal_approval_note_excerpt="Vendor NT-994 was verbally pre-approved by the VP of Sourcing",
        ),
        # 04 BharatSense: INR BOM + optional line excluded + 18% recoverable Indian GST ITC
        ExtractedQuoteFacts(
            source_filename="04_bharatsense_bom.csv",
            vendor_id="VND-312",
            supplier_name="BharatSense Controls Pvt Ltd",
            valid_until="2026-12-18",
            currency="INR",
            incoterm="DDP Hyderabad",
            is_exw_shenzhen=False,
            quantity_quoted=1000,
            pricing_structure="line_items",
            line_items=[
                QuotedLineItem(
                    sku="BS-P400-CORE",
                    description="Pressure Sensor Core Module (0-500 PSI)",
                    unit_basis="per_unit",
                    quantity=1000,
                    price_native="3350",
                    mandatory_for_rfp_spec=True,
                ),
                QuotedLineItem(
                    sku="BS-IP67-MNT",
                    description="IP67 Outdoor Enclosure and Mounting Kit",
                    unit_basis="per_unit",
                    quantity=1000,
                    price_native="420",
                    mandatory_for_rfp_spec=True,
                ),
                QuotedLineItem(
                    sku="BS-CAL-BATCH",
                    description="Factory ISO Batch Calibration Certificate",
                    unit_basis="flat_order",
                    quantity=1,
                    price_native="65000",
                    mandatory_for_rfp_spec=True,
                ),
                QuotedLineItem(
                    sku="BS-SPARE-KIT",
                    description="Optional 2-Year Field Maintenance Spare Pack",
                    unit_basis="flat_order",
                    quantity=1,
                    price_native="150000",
                    mandatory_for_rfp_spec=False,
                ),
            ],
            lead_time_days=18,
            warranty_months=24,
            ingress_rating_stated="IP67",
            has_explicit_ip67_certification=True,
            payment_terms_standard="Net 30",
            certifications=["BIS", "ISO-9001"],
            india_gst_applicable=True,
            india_gst_percent="18",
        ),
        # 05 NipponTech: JPY marginal slabs + split shipment batch 2 at 35d (> 28d SLA -> DISQUALIFIED)
        ExtractedQuoteFacts(
            source_filename="05_nippontech_portal_quote.json",
            vendor_id="VND-418",
            supplier_name="NipponTech Precision KK",
            quote_date="2026-11-16",
            valid_until="2026-12-25",
            currency="JPY",
            incoterm="DDP Hyderabad",
            is_exw_shenzhen=False,
            quantity_quoted=1000,
            pricing_structure="marginal_slabs",
            marginal_slabs=[
                MarginalPriceSlab(from_unit=1, to_unit=500, unit_price_native="7500"),
                MarginalPriceSlab(from_unit=501, to_unit=1000, unit_price_native="6800"),
            ],
            split_shipment_batches=[
                ShipmentBatch(units=500, lead_time_days=14),
                ShipmentBatch(units=500, lead_time_days=35),
            ],
            warranty_months=24,
            ingress_rating_stated="IP67",
            has_explicit_ip67_certification=True,
            payment_terms_standard="Net 30",
            certifications=["JIS", "CE", "ISO-9001"],
        ),
        # 06 Vanguard: expired 2026-11-18 + vague weather-resistant housing -> CLARIFICATION_REQUIRED
        ExtractedQuoteFacts(
            source_filename="06_vanguard_spec_quote.txt",
            vendor_id="VND-505",
            supplier_name="Vanguard Industrial Supply LLC",
            quote_date="2026-10-19",
            valid_until="2026-11-18",
            currency="USD",
            incoterm="DDP Hyderabad",
            is_exw_shenzhen=False,
            quantity_quoted=1000,
            pricing_structure="line_items",
            line_items=[
                QuotedLineItem(
                    sku="VGS-500",
                    description="VGS-500 Outdoor Pressure Sensor (0-500 PSI)",
                    unit_basis="per_unit",
                    quantity=1000,
                    price_native="45.50",
                    mandatory_for_rfp_spec=True,
                ),
            ],
            lead_time_days=22,
            warranty_months=24,
            ingress_rating_stated="rugged weather-resistant outdoor housing",
            has_explicit_ip67_certification=False,
            payment_terms_standard="Net 30",
            certifications=["CE", "ISO-9001"],
        ),
        # 07 QuantumGrid: USD Net 90 + optional 2% Net 15 + 36m warranty
        ExtractedQuoteFacts(
            source_filename="07_quantumgrid_partner_quote.md",
            vendor_id="VND-611",
            supplier_name="QuantumGrid Automation Corp",
            quote_date="2026-11-17",
            valid_until="2026-12-31",
            currency="USD",
            incoterm="DDP Hyderabad",
            is_exw_shenzhen=False,
            quantity_quoted=1000,
            pricing_structure="line_items",
            line_items=[
                QuotedLineItem(
                    sku="QGA-PS500-IP67",
                    description="IP67 Industrial Pressure Sensor (0-500 PSI)",
                    unit_basis="per_unit",
                    quantity=1000,
                    price_native="48.90",
                    mandatory_for_rfp_spec=True,
                ),
            ],
            lead_time_days=24,
            warranty_months=36,
            ingress_rating_stated="IP67 IEC 60529",
            has_explicit_ip67_certification=True,
            payment_terms_standard="Net 90",
            early_payment_discount_percent="2",
            early_payment_terms="Net 15",
            certifications=["CE", "UL", "ISO-9001", "ISO-14001"],
        ),
        # 08 NordicSense: EUR per-unit + flat mandatory cert pack (> $50K cap)
        ExtractedQuoteFacts(
            source_filename="08_nordicsense_quote.json",
            vendor_id="VND-702",
            supplier_name="NordicSense AB",
            quote_date="2026-11-17",
            valid_until="2026-12-28",
            currency="EUR",
            incoterm="DDP Hyderabad",
            is_exw_shenzhen=False,
            quantity_quoted=1000,
            pricing_structure="line_items",
            line_items=[
                QuotedLineItem(
                    sku="NS-PRO-500-IP67",
                    description="NS-PRO-500-IP67 Pressure Sensor Unit",
                    unit_basis="per_unit",
                    quantity=1000,
                    price_native="45.50",
                    mandatory_for_rfp_spec=True,
                ),
                QuotedLineItem(
                    description="Mandatory Factory IP67 Immersion Test & Calibration Certificate Pack",
                    unit_basis="flat_order",
                    quantity=1,
                    price_native="1800.00",
                    mandatory_for_rfp_spec=True,
                ),
            ],
            lead_time_days=16,
            warranty_months=36,
            ingress_rating_stated="IP67",
            has_explicit_ip67_certification=True,
            payment_terms_standard="Net 45",
            certifications=["CE", "ATEX", "ISO-9001", "ISO-14001"],
        ),
        # 09 DeccanTech: INR BOM + optional excluded + 18% GST ITC + 15d + Net 60
        ExtractedQuoteFacts(
            source_filename="09_deccantech_quote.md",
            vendor_id="VND-815",
            supplier_name="DeccanTech Systems Pvt Ltd",
            quote_date="2026-11-18",
            valid_until="2026-12-30",
            currency="INR",
            incoterm="DDP Hyderabad",
            is_exw_shenzhen=False,
            quantity_quoted=1000,
            pricing_structure="line_items",
            line_items=[
                QuotedLineItem(
                    sku="DT-PS500-BASE",
                    description="Industrial Pressure Sensor Core (0-500 PSI)",
                    unit_basis="per_unit",
                    quantity=1000,
                    price_native="3520",
                    mandatory_for_rfp_spec=True,
                ),
                QuotedLineItem(
                    sku="DT-IP67-SHIELD",
                    description="IP67 Sealed Outdoor Housing Kit",
                    unit_basis="per_unit",
                    quantity=1000,
                    price_native="430",
                    mandatory_for_rfp_spec=True,
                ),
                QuotedLineItem(
                    sku="DT-ISO-CAL",
                    description="Mandatory Factory ISO Batch Calibration Certificate",
                    unit_basis="flat_order",
                    quantity=1,
                    price_native="40000",
                    mandatory_for_rfp_spec=True,
                ),
                QuotedLineItem(
                    sku="DT-ONSITE-COMM",
                    description="Optional Onsite Commissioning Support Package",
                    unit_basis="flat_order",
                    quantity=1,
                    price_native="120000",
                    mandatory_for_rfp_spec=False,
                ),
            ],
            lead_time_days=15,
            warranty_months=24,
            ingress_rating_stated="IP67 IEC 60529",
            has_explicit_ip67_certification=True,
            payment_terms_standard="Net 60",
            certifications=["BIS", "CE", "ISO-9001"],
            india_gst_applicable=True,
            india_gst_percent="18",
        ),
        # 10 Pacific Industrial: 18-month warranty (< 24m min -> DISQUALIFIED)
        ExtractedQuoteFacts(
            source_filename="10_pacific_industrial_bid.csv",
            vendor_id="VND-901",
            supplier_name="Pacific Industrial Controls Inc",
            valid_until="2026-12-22",
            currency="USD",
            incoterm="DDP Hyderabad",
            is_exw_shenzhen=False,
            quantity_quoted=1000,
            pricing_structure="line_items",
            line_items=[
                QuotedLineItem(
                    sku="PIC-500-IP67",
                    description="IP67 Industrial Outdoor Pressure Sensor (0-500 PSI)",
                    unit_basis="per_unit",
                    quantity=1000,
                    price_native="43.80",
                    mandatory_for_rfp_spec=True,
                ),
            ],
            lead_time_days=20,
            warranty_months=18,
            ingress_rating_stated="IP67 Certified",
            has_explicit_ip67_certification=True,
            payment_terms_standard="Net 30",
            certifications=["CE", "ISO-9001"],
        ),
    ]


def test_all_ten_quotes_exact_normalization_and_compliance(
    policy: ProcurementPolicy,
    all_ten_quotes: list[ExtractedQuoteFacts],
) -> None:
    evaluated = [normalize_and_evaluate_bid(q, policy) for q in all_ten_quotes]
    by_id = {b.vendor_id: b for b in evaluated}

    # Exact net landed USD across all 10 bids
    assert by_id["VND-104"].cost.net_landed_usd == Decimal("52380.00")
    assert by_id["VND-209"].cost.net_landed_usd == Decimal("46049.47")
    assert by_id["VND-209"].cost.cartons_ordered == 84
    assert by_id["VND-209"].cost.effective_units_ordered == 1008
    assert by_id["NT-994"].cost.net_landed_usd == Decimal("42480.00")
    assert by_id["VND-312"].cost.net_landed_usd == Decimal("45636.50")
    assert by_id["VND-312"].cost.gross_cash_outlay_usd == Decimal("53851.07")
    assert by_id["VND-312"].cost.excluded_optional_native == Decimal("150000.00")
    assert by_id["VND-418"].cost.net_landed_usd == Decimal("47190.00")
    assert by_id["VND-505"].cost.net_landed_usd == Decimal("45500.00")
    assert by_id["VND-611"].cost.net_landed_usd == Decimal("48900.00")
    assert by_id["VND-611"].cost.early_payment_net_usd == Decimal("47922.00")
    assert by_id["VND-702"].cost.net_landed_usd == Decimal("51084.00")
    assert by_id["VND-815"].cost.net_landed_usd == Decimal("47481.00")
    assert by_id["VND-815"].cost.gross_cash_outlay_usd == Decimal("56027.58")
    assert by_id["VND-901"].cost.net_landed_usd == Decimal("43800.00")

    # Exact compliance classifications (6 COMPLIANT, 3 DISQUALIFIED, 1 CLARIFICATION_REQUIRED)
    for vid in ("VND-104", "VND-209", "VND-312", "VND-611", "VND-702", "VND-815"):
        assert by_id[vid].compliance_status == "COMPLIANT"

    assert by_id["NT-994"].compliance_status == "DISQUALIFIED"
    assert by_id["NT-994"].verbal_approval_injection_detected is True
    assert by_id["VND-418"].compliance_status == "DISQUALIFIED"
    assert by_id["VND-418"].effective_lead_time_days == 35
    assert by_id["VND-901"].compliance_status == "DISQUALIFIED"

    assert by_id["VND-505"].compliance_status == "CLARIFICATION_REQUIRED"
    assert len(by_id["VND-505"].clarification_items) == 2

    # Manager sign-off threshold flags (> $50K net landed USD)
    assert by_id["VND-702"].requires_manager_signoff is True
    assert by_id["VND-702"].cap_overage_usd == Decimal("1084.00")
    assert by_id["VND-104"].requires_manager_signoff is True
    assert by_id["VND-104"].cap_overage_usd == Decimal("2380.00")
    assert by_id["VND-815"].requires_manager_signoff is False
    assert by_id["VND-312"].requires_manager_signoff is False


def test_baseline_100_point_ranking(
    policy: ProcurementPolicy,
    all_ten_quotes: list[ExtractedQuoteFacts],
) -> None:
    evaluated = [normalize_and_evaluate_bid(q, policy) for q in all_ten_quotes]
    scored, non_compliant = score_bids(evaluated, policy)

    assert len(scored) == 6
    assert len(non_compliant) == 4
    assert [b.vendor_id for b in scored] == [
        "VND-702",  # NordicSense
        "VND-104",  # Apex Sensors
        "VND-815",  # DeccanTech
        "VND-209",  # EuroSense
        "VND-611",  # QuantumGrid
        "VND-312",  # BharatSense
    ]

    expected_scores = {
        "VND-702": Decimal("88.73"),
        "VND-104": Decimal("84.85"),
        "VND-815": Decimal("84.45"),
        "VND-209": Decimal("83.64"),
        "VND-611": Decimal("82.33"),
        "VND-312": Decimal("77.00"),
    }
    for bid in scored:
        assert bid.score is not None
        assert bid.score.total_score == expected_scores[bid.vendor_id]


def test_what_if_rescoring_and_weight_validation(
    policy: ProcurementPolicy,
    all_ten_quotes: list[ExtractedQuoteFacts],
) -> None:
    evaluated = [normalize_and_evaluate_bid(q, policy) for q in all_ten_quotes]
    scored, non_compliant = score_bids(evaluated, policy)
    cached = scored + non_compliant

    # Delivery-heavy scenario shifts Apex Sensors (14d) to #1
    speed_weights = ScoringWeights(
        net_landed_cost=Decimal("20"),
        delivery_speed=Decimal("50"),
        warranty_months=Decimal("10"),
        supplier_track_record=Decimal("10"),
        payment_terms=Decimal("10"),
    )
    rescored, _ = rescore_cached_bids(cached, policy, speed_weights)
    assert rescored[0].vendor_id == "VND-104"
    assert rescored[0].rank == 1

    # Invalid weights (sum != 100 or negative) fail fast
    bad_sum = ScoringWeights(
        net_landed_cost=Decimal("50"),
        delivery_speed=Decimal("30"),
        warranty_months=Decimal("10"),
        supplier_track_record=Decimal("10"),
        payment_terms=Decimal("10"),
    )
    with pytest.raises(ValueError, match="sum to 100"):
        rescore_cached_bids(cached, policy, bad_sum)

    negative_weight = ScoringWeights(
        net_landed_cost=Decimal("110"),
        delivery_speed=Decimal("-10"),
        warranty_months=Decimal("0"),
        supplier_track_record=Decimal("0"),
        payment_terms=Decimal("0"),
    )
    with pytest.raises(ValueError, match="cannot be negative"):
        rescore_cached_bids(cached, policy, negative_weight)


def test_award_gate_and_hard_python_po_gate(
    policy: ProcurementPolicy,
    all_ten_quotes: list[ExtractedQuoteFacts],
) -> None:
    evaluated = [normalize_and_evaluate_bid(q, policy) for q in all_ten_quotes]
    scored, non_compliant = score_bids(evaluated, policy)
    all_bids = scored + non_compliant
    by_id = {b.vendor_id: b for b in all_bids}

    # 1. Under-cap compliant vendor (DeccanTech) auto-authorizes
    deccan_gate = evaluate_award_gate("DeccanTech", all_bids, policy)
    assert deccan_gate.outcome == "AUTHORIZED"
    assert deccan_gate.award_authorized is True
    assert deccan_gate.pending_manager_signoff is False

    # 2. Over-cap compliant vendor (NordicSense) pauses for manager sign-off
    nordic_gate = evaluate_award_gate("NordicSense", all_bids, policy)
    assert nordic_gate.outcome == "MANAGER_SIGNOFF_REQUIRED"
    assert nordic_gate.award_authorized is False
    assert nordic_gate.pending_manager_signoff is True
    assert nordic_gate.cap_overage_usd == Decimal("1084.00")

    # Hard Python gate blocks PO when award_authorized=False or sign-off missing
    with pytest.raises(PermissionError, match="award_authorized must be True"):
        build_po_draft(by_id["VND-702"], policy, award_authorized=False)

    with pytest.raises(PermissionError, match="manager sign-off"):
        build_po_draft(by_id["VND-702"], policy, award_authorized=True, manager_signoff_record=None)

    # Recording manager sign-off unlocks NordicSense PO
    signoff = {"approved": "true", "approver": "R. Sharma, VP Procurement"}
    nordic_approved = evaluate_award_gate("VND-702", all_bids, policy, manager_signoff=signoff)
    assert nordic_approved.outcome == "AUTHORIZED"
    assert nordic_approved.award_authorized is True
    po_nordic = build_po_draft(
        by_id["VND-702"], policy, award_authorized=True, manager_signoff_record=signoff
    )
    assert po_nordic.net_landed_usd == Decimal("51084.00")
    assert "R. Sharma" in po_nordic.approval_basis

    # 3. Disqualified vendor with verbal-approval prompt injection (NovaTech) is blocked
    nova_gate = evaluate_award_gate("NovaTech", all_bids, policy)
    assert nova_gate.outcome == "BLOCKED_DISQUALIFIED"
    assert nova_gate.award_authorized is False
    with pytest.raises(PermissionError, match="DISQUALIFIED"):
        build_po_draft(by_id["NT-994"], policy, award_authorized=True)

    # 4. Clarification-required vendor (Vanguard) is blocked with open items
    vanguard_gate = evaluate_award_gate("Vanguard", all_bids, policy)
    assert vanguard_gate.outcome == "BLOCKED_CLARIFICATION"
    assert vanguard_gate.award_authorized is False
    assert len(vanguard_gate.clarification_items) == 2

    # 5. Multi-turn PO edits preserve deterministic totals & toggle QuantumGrid Net 15 option cleanly
    qg_po_v1 = build_po_draft(by_id["VND-611"], policy, award_authorized=True)
    assert qg_po_v1.net_landed_usd == Decimal("48900.00")
    assert qg_po_v1.revision == 1

    qg_po_v2 = build_po_draft(
        by_id["VND-611"],
        policy,
        award_authorized=True,
        existing_draft=qg_po_v1,
        cost_center="CC-HYD-441",
        ship_to_contact="Priya Nair",
        apply_early_payment_discount=True,
    )
    assert qg_po_v2.revision == 2
    assert qg_po_v2.cost_center == "CC-HYD-441"
    assert qg_po_v2.ship_to_contact == "Priya Nair"
    assert qg_po_v2.early_payment_applied is True
    assert qg_po_v2.net_landed_usd == Decimal("47922.00")
