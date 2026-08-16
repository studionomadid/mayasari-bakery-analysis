"""
M24.5 — Mayasari Bakery Customer Insight Business Narrative Layer.

Transforms deterministic M24.3 evidence and M24.4 interpretations
into an evidence-backed business narrative.

Design principles:
    evidence
        -> interpretation
        -> business narrative
        -> recommendation

This module does not recalculate customer metrics.

No LLM-generated narrative is used here.
No causal claims are introduced.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from src.customer_insight_engine import (
    calculate_all_insights,
    load_customer_data,
    validate_insight_results,
)

from src.customer_insight_framework import (
    CUSTOMER_INSIGHT_FRAMEWORK,
    validate_framework,
)

from src.customer_insight_interpretation import (
    InsightInterpretation,
    interpret_all_insights,
    validate_interpretations,
)


@dataclass(frozen=True)
class BusinessNarrative:
    """Complete business narrative for the customer insight layer."""

    executive_summary: str
    key_findings: tuple[str, ...]
    strategic_priorities: tuple[str, ...]
    retention_recommendations: tuple[str, ...]
    development_recommendations: tuple[str, ...]
    opportunity_actions: tuple[str, ...]
    management_takeaways: tuple[str, ...]


PRIORITY_ORDER: Final[tuple[str, ...]] = (
    "Critical",
    "High",
    "Medium",
    "Low",
)


def _get_interpretation(
    interpretations: tuple[InsightInterpretation, ...],
    insight_id: str,
) -> InsightInterpretation:
    """Return one interpretation by insight ID."""

    for interpretation in interpretations:
        if interpretation.insight_id == insight_id:
            return interpretation

    raise ValueError(
        f"Interpretation not found: {insight_id}"
    )


def build_executive_summary(
    interpretations: tuple[InsightInterpretation, ...],
) -> str:
    """Build deterministic executive summary."""

    concentration = _get_interpretation(
        interpretations,
        "customer_value_concentration",
    )

    rescue = _get_interpretation(
        interpretations,
        "rescue_economics",
    )

    risk = _get_interpretation(
        interpretations,
        "high_value_at_risk",
    )

    profitability = _get_interpretation(
        interpretations,
        "customer_profitability",
    )

    return (
        "The customer analysis indicates that Mayasari Bakery's "
        "customer economics are meaningfully concentrated in "
        "higher-value customers, while a material share of customer "
        "value is associated with Rescue and At-Risk populations. "
        f"{concentration.evidence_summary} "
        f"{rescue.evidence_summary} "
        f"{risk.evidence_summary} "
        f"{profitability.evidence_summary} "
        "The resulting management priority is to protect economically "
        "valuable relationships while systematically developing "
        "customers with further economic potential."
    )


def build_key_findings(
    interpretations: tuple[InsightInterpretation, ...],
) -> tuple[str, ...]:
    """Build evidence-backed key findings."""

    concentration = _get_interpretation(
        interpretations,
        "customer_value_concentration",
    )

    tier = _get_interpretation(
        interpretations,
        "clv_tier_economics",
    )

    rfm = _get_interpretation(
        interpretations,
        "rfm_customer_quality",
    )

    opportunity = _get_interpretation(
        interpretations,
        "customer_opportunity_priority",
    )

    rescue = _get_interpretation(
        interpretations,
        "rescue_economics",
    )

    risk = _get_interpretation(
        interpretations,
        "high_value_at_risk",
    )

    profitability = _get_interpretation(
        interpretations,
        "customer_profitability",
    )

    return (
        concentration.interpretation,
        tier.interpretation,
        rfm.interpretation,
        opportunity.interpretation,
        rescue.interpretation,
        risk.interpretation,
        profitability.interpretation,
    )


def build_strategic_priorities(
    interpretations: tuple[InsightInterpretation, ...],
) -> tuple[str, ...]:
    """Build management priorities from interpretation priorities."""

    concentration = _get_interpretation(
        interpretations,
        "customer_value_concentration",
    )

    rescue = _get_interpretation(
        interpretations,
        "rescue_economics",
    )

    risk = _get_interpretation(
        interpretations,
        "high_value_at_risk",
    )

    opportunity = _get_interpretation(
        interpretations,
        "customer_opportunity_priority",
    )

    return (
        (
            f"1. Protect high-value customer economics — "
            f"{concentration.priority} priority. "
            f"{concentration.business_implication}"
        ),
        (
            f"2. Address economically meaningful Rescue customers — "
            f"{rescue.priority} priority. "
            f"{rescue.business_implication}"
        ),
        (
            f"3. Prioritize high-value retention exposure — "
            f"{risk.priority} priority. "
            f"{risk.business_implication}"
        ),
        (
            f"4. Focus customer development on economically relevant "
            f"opportunity groups — {opportunity.priority} priority. "
            f"{opportunity.business_implication}"
        ),
    )


def build_retention_recommendations(
    interpretations: tuple[InsightInterpretation, ...],
) -> tuple[str, ...]:
    """Build retention recommendations."""

    concentration = _get_interpretation(
        interpretations,
        "customer_value_concentration",
    )

    rescue = _get_interpretation(
        interpretations,
        "rescue_economics",
    )

    risk = _get_interpretation(
        interpretations,
        "high_value_at_risk",
    )

    return (
        (
            "Protect Platinum and Gold customers with differentiated "
            "retention treatment rather than a uniform customer policy."
        ),
        (
            "Prioritize economically valuable Rescue customers for "
            "targeted re-engagement, with particular attention to "
            "Platinum Rescue customers."
        ),
        (
            "Create a high-value At-Risk retention queue so Platinum "
            "and Gold customers receive earlier management attention."
        ),
        (
            "Use the observed CLV concentration as a management signal "
            "for retention planning rather than relying on customer "
            "count alone."
        ),
        (
            f"Retention planning should account for the finding that "
            f"{risk.evidence_summary.lower()}"
        ),
        (
            f"The retention program should also recognize that "
            f"{concentration.evidence_summary.lower()}"
        ),
        (
            f"Rescue intervention should remain economically selective: "
            f"{rescue.evidence_summary.lower()}"
        ),
    )


def build_development_recommendations(
    interpretations: tuple[InsightInterpretation, ...],
) -> tuple[str, ...]:
    """Build customer development recommendations."""

    tier = _get_interpretation(
        interpretations,
        "clv_tier_economics",
    )

    rfm = _get_interpretation(
        interpretations,
        "rfm_customer_quality",
    )

    opportunity = _get_interpretation(
        interpretations,
        "customer_opportunity_priority",
    )

    profitability = _get_interpretation(
        interpretations,
        "customer_profitability",
    )

    return (
        (
            "Develop lower CLV tiers using differentiated engagement "
            "strategies designed around observed customer behavior."
        ),
        (
            "Use RFM characteristics to identify customers with "
            "development potential rather than applying identical "
            "campaigns across the customer base."
        ),
        (
            "Prioritize economically meaningful opportunity groups "
            "before allocating broad customer-development resources."
        ),
        (
            "Evaluate customer-development initiatives using gross "
            "profit contribution as well as revenue."
        ),
        (
            f"Upper-tier economics should remain a benchmark for "
            f"customer development because {tier.evidence_summary.lower()}"
        ),
        (
            f"Customer development should recognize behavioral "
            f"heterogeneity: {rfm.evidence_summary.lower()}"
        ),
        (
            f"Opportunity prioritization should remain value-aware: "
            f"{opportunity.evidence_summary.lower()}"
        ),
        (
            f"Profitability should remain part of customer-development "
            f"evaluation: {profitability.evidence_summary.lower()}"
        ),
    )


def build_opportunity_actions(
    interpretations: tuple[InsightInterpretation, ...],
) -> tuple[str, ...]:
    """Build actions aligned with opportunity groups."""

    return (
        (
            "Rescue — launch targeted re-engagement for economically "
            "valuable inactive or declining customers."
        ),
        (
            "Protect — prioritize retention actions for customers "
            "already demonstrating meaningful economic value."
        ),
        (
            "Develop — identify customers with observable potential "
            "to progress into stronger CLV tiers."
        ),
        (
            "Grow — strengthen engagement and purchase development "
            "for customers showing positive commercial potential."
        ),
        (
            "Win-back — test focused reactivation strategies using "
            "historical value and observed customer behavior."
        ),
        (
            "Monitor — maintain lightweight monitoring and avoid "
            "over-investing before stronger economic signals emerge."
        ),
        (
            "Review — investigate customer-level economics and "
            "behavior before assigning intensive intervention."
        ),
    )


def build_management_takeaways(
    interpretations: tuple[InsightInterpretation, ...],
) -> tuple[str, ...]:
    """Build concise management takeaways."""

    concentration = _get_interpretation(
        interpretations,
        "customer_value_concentration",
    )

    rescue = _get_interpretation(
        interpretations,
        "rescue_economics",
    )

    risk = _get_interpretation(
        interpretations,
        "high_value_at_risk",
    )

    profitability = _get_interpretation(
        interpretations,
        "customer_profitability",
    )

    return (
        (
            "Customer count alone is insufficient for prioritization; "
            "customer economic value must remain part of management "
            "decision-making."
        ),
        (
            f"High-value concentration matters because "
            f"{concentration.evidence_summary.lower()}"
        ),
        (
            f"Rescue customers deserve targeted attention because "
            f"{rescue.evidence_summary.lower()}"
        ),
        (
            f"Retention exposure is economically relevant because "
            f"{risk.evidence_summary.lower()}"
        ),
        (
            f"Revenue should not be used as the sole economic KPI because "
            f"{profitability.evidence_summary.lower()}"
        ),
        (
            "The analysis describes observed customer behavior and "
            "economic relationships; it does not establish causal "
            "drivers of customer behavior."
        ),
    )


def build_business_narrative(
    interpretations: tuple[InsightInterpretation, ...],
) -> BusinessNarrative:
    """Build the complete business narrative."""

    validate_interpretations(
        interpretations
    )

    return BusinessNarrative(
        executive_summary=build_executive_summary(
            interpretations
        ),
        key_findings=build_key_findings(
            interpretations
        ),
        strategic_priorities=build_strategic_priorities(
            interpretations
        ),
        retention_recommendations=build_retention_recommendations(
            interpretations
        ),
        development_recommendations=build_development_recommendations(
            interpretations
        ),
        opportunity_actions=build_opportunity_actions(
            interpretations
        ),
        management_takeaways=build_management_takeaways(
            interpretations
        ),
    )


def validate_business_narrative(
    narrative: BusinessNarrative,
) -> None:
    """Validate narrative completeness."""

    scalar_fields = (
        narrative.executive_summary,
    )

    if any(
        not field.strip()
        for field in scalar_fields
    ):
        raise ValueError(
            "Business narrative contains an empty scalar field."
        )

    collection_fields = (
        narrative.key_findings,
        narrative.strategic_priorities,
        narrative.retention_recommendations,
        narrative.development_recommendations,
        narrative.opportunity_actions,
        narrative.management_takeaways,
    )

    for field in collection_fields:
        if not field:
            raise ValueError(
                "Business narrative contains an empty collection."
            )

        if any(
            not item.strip()
            for item in field
        ):
            raise ValueError(
                "Business narrative contains an empty item."
            )

    if len(narrative.key_findings) != 7:
        raise ValueError(
            "Expected exactly 7 key findings."
        )

    if len(narrative.opportunity_actions) != 7:
        raise ValueError(
            "Expected exactly 7 opportunity actions."
        )


def print_business_narrative(
    narrative: BusinessNarrative,
) -> None:
    """Print the complete business narrative."""

    validate_business_narrative(
        narrative
    )

    print("=" * 100)
    print("M24.5 — CUSTOMER BUSINESS NARRATIVE")
    print("=" * 100)

    print("\nEXECUTIVE SUMMARY")
    print("-" * 100)
    print(narrative.executive_summary)

    print("\nKEY FINDINGS")
    print("-" * 100)

    for index, finding in enumerate(
        narrative.key_findings,
        start=1,
    ):
        print(f"{index}. {finding}")

    print("\nSTRATEGIC PRIORITIES")
    print("-" * 100)

    for priority in narrative.strategic_priorities:
        print(priority)

    print("\nRETENTION RECOMMENDATIONS")
    print("-" * 100)

    for recommendation in narrative.retention_recommendations:
        print(f"- {recommendation}")

    print("\nCUSTOMER DEVELOPMENT RECOMMENDATIONS")
    print("-" * 100)

    for recommendation in narrative.development_recommendations:
        print(f"- {recommendation}")

    print("\nOPPORTUNITY ACTIONS")
    print("-" * 100)

    for action in narrative.opportunity_actions:
        print(f"- {action}")

    print("\nMANAGEMENT TAKEAWAYS")
    print("-" * 100)

    for takeaway in narrative.management_takeaways:
        print(f"- {takeaway}")

    print("\n" + "=" * 100)
    print("M24.5 BUSINESS NARRATIVE VALID")
    print("=" * 100)


def main() -> None:
    """Run the complete M24.5 narrative pipeline."""

    validate_framework()

    customer = load_customer_data()

    results = calculate_all_insights(
        customer
    )

    validate_insight_results(
        customer,
        results,
    )

    interpretations = interpret_all_insights(
        results
    )

    validate_interpretations(
        interpretations
    )

    narrative = build_business_narrative(
        interpretations
    )

    validate_business_narrative(
        narrative
    )

    print_business_narrative(
        narrative
    )


if __name__ == "__main__":
    main()
