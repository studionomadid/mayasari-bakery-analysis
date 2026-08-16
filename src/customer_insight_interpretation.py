"""
M24.4 — Mayasari Bakery Customer Insight Interpretation Layer.

Transforms deterministic evidence produced by the M24.3 customer
insight evidence engine into business interpretations.

This module intentionally separates:
    evidence
    interpretation
    business implication
    recommended action

No LLM-generated interpretation is used here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from src.customer_insight_framework import (
    CUSTOMER_INSIGHT_FRAMEWORK,
    InsightDefinition,
    validate_framework,
)
from src.customer_insight_engine import (
    calculate_all_insights,
    load_customer_data,
    validate_insight_results,
)


@dataclass(frozen=True)
class InsightInterpretation:
    """Business interpretation of one customer insight."""

    insight_id: str
    title: str
    category: str
    priority: str
    evidence_summary: str
    interpretation: str
    business_implication: str
    recommended_action: str


PRIORITY_ORDER: Final[tuple[str, ...]] = (
    "Critical",
    "High",
    "Medium",
    "Low",
)


def _priority_from_percentage(
    percentage: float,
    *,
    critical_threshold: float,
    high_threshold: float,
    medium_threshold: float,
) -> str:
    """Convert a percentage metric into deterministic priority."""

    if percentage >= critical_threshold:
        return "Critical"

    if percentage >= high_threshold:
        return "High"

    if percentage >= medium_threshold:
        return "Medium"

    return "Low"


def interpret_customer_value_concentration(
    evidence: dict[str, float],
    definition: InsightDefinition,
) -> InsightInterpretation:
    """Interpret annualized CLV concentration."""

    platinum_share = evidence["platinum_clv_share"]
    top_25_share = evidence["top_25_clv_share"]

    priority = _priority_from_percentage(
        platinum_share,
        critical_threshold=50.0,
        high_threshold=35.0,
        medium_threshold=20.0,
    )

    if platinum_share >= 35:
        interpretation = (
            "Customer economic value is materially concentrated "
            "within the Platinum tier."
        )
    elif platinum_share >= 20:
        interpretation = (
            "Customer economic value shows meaningful concentration "
            "within the Platinum tier."
        )
    else:
        interpretation = (
            "Customer economic value is relatively distributed "
            "across the customer base."
        )

    implication = (
        f"Platinum customers contribute {platinum_share:.2f}% of "
        f"annualized CLV, while the top 25 customers contribute "
        f"{top_25_share:.2f}%. Retention performance among the "
        "highest-value customers therefore has disproportionate "
        "economic importance."
    )

    evidence_summary = (
        f"Platinum CLV share: {platinum_share:.2f}%; "
        f"top 25 CLV share: {top_25_share:.2f}%."
    )

    return InsightInterpretation(
        insight_id=definition.insight_id,
        title=definition.title,
        category=definition.category,
        priority=priority,
        evidence_summary=evidence_summary,
        interpretation=interpretation,
        business_implication=implication,
        recommended_action=definition.recommended_action,
    )


def interpret_clv_tier_economics(
    evidence,
    definition: InsightDefinition,
) -> InsightInterpretation:
    """Interpret CLV tier economics."""

    platinum = evidence.loc[
        evidence["clv_tier"].astype(str) == "Platinum"
    ]

    gold = evidence.loc[
        evidence["clv_tier"].astype(str) == "Gold"
    ]

    platinum_share = (
        float(platinum["clv_share"].iloc[0])
        if not platinum.empty
        else 0.0
    )

    gold_share = (
        float(gold["clv_share"].iloc[0])
        if not gold.empty
        else 0.0
    )

    priority = _priority_from_percentage(
        platinum_share,
        critical_threshold=50.0,
        high_threshold=35.0,
        medium_threshold=20.0,
    )

    interpretation = (
        f"Platinum customers contribute {platinum_share:.2f}% "
        f"of annualized CLV, compared with {gold_share:.2f}% "
        "from Gold customers."
    )

    implication = (
        "The upper CLV tiers represent the economically strongest "
        "customer population and should receive differentiated "
        "retention and development treatment."
    )

    evidence_summary = (
        f"Platinum CLV share: {platinum_share:.2f}%; "
        f"Gold CLV share: {gold_share:.2f}%."
    )

    return InsightInterpretation(
        insight_id=definition.insight_id,
        title=definition.title,
        category=definition.category,
        priority=priority,
        evidence_summary=evidence_summary,
        interpretation=interpretation,
        business_implication=implication,
        recommended_action=definition.recommended_action,
    )


def interpret_rfm_customer_quality(
    evidence,
    definition: InsightDefinition,
) -> InsightInterpretation:
    """Interpret RFM segment distribution."""

    largest = evidence.iloc[0]

    segment = str(largest["segment"])
    customer_share = float(largest["customer_share"])
    average_rfm = float(largest["average_rfm"])

    priority = _priority_from_percentage(
        customer_share,
        critical_threshold=50.0,
        high_threshold=35.0,
        medium_threshold=20.0,
    )

    interpretation = (
        f"The largest observed RFM segment is '{segment}', "
        f"representing {customer_share:.2f}% of customers with "
        f"an average RFM score of {average_rfm:.2f}."
    )

    implication = (
        "Customer behavior is heterogeneous, so engagement "
        "strategies should be differentiated by observed RFM "
        "characteristics rather than treating the entire customer "
        "base uniformly."
    )

    evidence_summary = (
        f"Largest segment: {segment}; "
        f"customer share: {customer_share:.2f}%; "
        f"average RFM: {average_rfm:.2f}."
    )

    return InsightInterpretation(
        insight_id=definition.insight_id,
        title=definition.title,
        category=definition.category,
        priority=priority,
        evidence_summary=evidence_summary,
        interpretation=interpretation,
        business_implication=implication,
        recommended_action=definition.recommended_action,
    )


def interpret_customer_opportunity_priority(
    evidence,
    definition: InsightDefinition,
) -> InsightInterpretation:
    """Interpret customer opportunity distribution."""

    priority_groups = {
        "Rescue",
        "Protect",
        "Develop",
    }

    priority_rows = evidence.loc[
        evidence["opportunity"].astype(str).isin(
            priority_groups
        )
    ]

    priority_clv = float(
        priority_rows["clv_share"].sum()
    )

    priority_customers = int(
        priority_rows["customer_count"].sum()
    )

    priority = _priority_from_percentage(
        priority_clv,
        critical_threshold=50.0,
        high_threshold=35.0,
        medium_threshold=20.0,
    )

    interpretation = (
        f"Priority 1-3 opportunity groups contain "
        f"{priority_customers:,} customers and account for "
        f"{priority_clv:.2f}% of annualized CLV."
    )

    implication = (
        "The economically relevant intervention population should "
        "be prioritized according to both customer value and the "
        "existing behavioral opportunity classification."
    )

    evidence_summary = (
        f"Priority 1-3 customers: {priority_customers:,}; "
        f"priority-group CLV share: {priority_clv:.2f}%."
    )

    return InsightInterpretation(
        insight_id=definition.insight_id,
        title=definition.title,
        category=definition.category,
        priority=priority,
        evidence_summary=evidence_summary,
        interpretation=interpretation,
        business_implication=implication,
        recommended_action=definition.recommended_action,
    )


def interpret_rescue_economics(
    evidence: dict[str, float],
    definition: InsightDefinition,
) -> InsightInterpretation:
    """Interpret Rescue customer economics."""

    rescue_share = evidence["rescue_clv_share"]
    platinum_count = int(
        evidence["rescue_platinum_count"]
    )

    priority = _priority_from_percentage(
        rescue_share,
        critical_threshold=25.0,
        high_threshold=15.0,
        medium_threshold=8.0,
    )

    interpretation = (
        f"Rescue customers account for {rescue_share:.2f}% "
        "of annualized CLV, indicating that the Rescue group "
        "contains economically meaningful customers."
    )

    implication = (
        f"The Rescue population includes {platinum_count} Platinum "
        "customers, so customer re-engagement should not be treated "
        "as a low-value blanket campaign."
    )

    evidence_summary = (
        f"Rescue CLV share: {rescue_share:.2f}%; "
        f"Rescue Platinum customers: {platinum_count:,}."
    )

    return InsightInterpretation(
        insight_id=definition.insight_id,
        title=definition.title,
        category=definition.category,
        priority=priority,
        evidence_summary=evidence_summary,
        interpretation=interpretation,
        business_implication=implication,
        recommended_action=definition.recommended_action,
    )


def interpret_high_value_at_risk(
    evidence: dict[str, float],
    definition: InsightDefinition,
) -> InsightInterpretation:
    """Interpret high-value retention risk."""

    at_risk_share = evidence["at_risk_clv_share"]
    platinum_count = int(
        evidence["at_risk_platinum_count"]
    )
    gold_count = int(
        evidence["at_risk_gold_count"]
    )

    priority = _priority_from_percentage(
        at_risk_share,
        critical_threshold=25.0,
        high_threshold=15.0,
        medium_threshold=8.0,
    )

    interpretation = (
        f"At-Risk customers account for {at_risk_share:.2f}% "
        "of annualized CLV, indicating meaningful economic exposure "
        "within the observed customer base."
    )

    implication = (
        f"The At-Risk population contains {platinum_count} Platinum "
        f"and {gold_count} Gold customers. Retention attention should "
        "therefore be concentrated on economically valuable members "
        "of this group."
    )

    evidence_summary = (
        f"At-Risk CLV share: {at_risk_share:.2f}%; "
        f"Platinum: {platinum_count:,}; "
        f"Gold: {gold_count:,}."
    )

    return InsightInterpretation(
        insight_id=definition.insight_id,
        title=definition.title,
        category=definition.category,
        priority=priority,
        evidence_summary=evidence_summary,
        interpretation=interpretation,
        business_implication=implication,
        recommended_action=definition.recommended_action,
    )


def interpret_customer_profitability(
    evidence: dict[str, float],
    definition: InsightDefinition,
) -> InsightInterpretation:
    """Interpret customer gross-profit economics."""

    gross_margin = evidence["overall_gross_margin"]
    top_customer_profit_share = evidence[
        "top_customer_profit_share"
    ]

    priority = _priority_from_percentage(
        top_customer_profit_share,
        critical_threshold=50.0,
        high_threshold=35.0,
        medium_threshold=20.0,
    )

    interpretation = (
        f"The customer base generates a {gross_margin:.2f}% "
        "overall gross margin, while the top 10 customers account "
        f"for {top_customer_profit_share:.2f}% of gross profit."
    )

    implication = (
        "Customer value should be assessed using gross-profit "
        "contribution rather than revenue alone, because revenue "
        "concentration does not necessarily represent profitability "
        "concentration."
    )

    evidence_summary = (
        f"Gross margin: {gross_margin:.2f}%; "
        f"top 10 gross-profit share: "
        f"{top_customer_profit_share:.2f}%."
    )

    return InsightInterpretation(
        insight_id=definition.insight_id,
        title=definition.title,
        category=definition.category,
        priority=priority,
        evidence_summary=evidence_summary,
        interpretation=interpretation,
        business_implication=implication,
        recommended_action=definition.recommended_action,
    )


def interpret_all_insights(
    results: dict[str, object],
) -> tuple[InsightInterpretation, ...]:
    """Interpret all seven framework insights."""

    validate_framework()

    definitions = {
        definition.insight_id: definition
        for definition in CUSTOMER_INSIGHT_FRAMEWORK
    }

    interpretations = (
        interpret_customer_value_concentration(
            results["customer_value_concentration"],
            definitions["customer_value_concentration"],
        ),
        interpret_clv_tier_economics(
            results["clv_tier_economics"],
            definitions["clv_tier_economics"],
        ),
        interpret_rfm_customer_quality(
            results["rfm_customer_quality"],
            definitions["rfm_customer_quality"],
        ),
        interpret_customer_opportunity_priority(
            results["customer_opportunity_priority"],
            definitions["customer_opportunity_priority"],
        ),
        interpret_rescue_economics(
            results["rescue_economics"],
            definitions["rescue_economics"],
        ),
        interpret_high_value_at_risk(
            results["high_value_at_risk"],
            definitions["high_value_at_risk"],
        ),
        interpret_customer_profitability(
            results["customer_profitability"],
            definitions["customer_profitability"],
        ),
    )

    if len(interpretations) != len(
        CUSTOMER_INSIGHT_FRAMEWORK
    ):
        raise ValueError(
            "Interpretation result count does not match framework."
        )

    return interpretations


def validate_interpretations(
    interpretations: tuple[InsightInterpretation, ...],
) -> None:
    """Validate interpretation structure and framework coverage."""

    validate_framework()

    expected_ids = {
        definition.insight_id
        for definition in CUSTOMER_INSIGHT_FRAMEWORK
    }

    actual_ids = {
        interpretation.insight_id
        for interpretation in interpretations
    }

    if actual_ids != expected_ids:
        raise ValueError(
            "Interpretation IDs do not match the insight framework."
        )

    if len(interpretations) != len(expected_ids):
        raise ValueError(
            "Interpretation count does not match framework."
        )

    for interpretation in interpretations:
        if interpretation.priority not in PRIORITY_ORDER:
            raise ValueError(
                f"Unexpected priority: {interpretation.priority}"
            )

        fields = (
            interpretation.title,
            interpretation.category,
            interpretation.evidence_summary,
            interpretation.interpretation,
            interpretation.business_implication,
            interpretation.recommended_action,
        )

        if any(not field.strip() for field in fields):
            raise ValueError(
                f"Incomplete interpretation: "
                f"{interpretation.insight_id}"
            )


def print_interpretations(
    interpretations: tuple[InsightInterpretation, ...],
) -> None:
    """Print the complete interpretation layer."""

    validate_interpretations(
        interpretations
    )

    print("=" * 100)
    print("M24.4 — CUSTOMER INSIGHT INTERPRETATION")
    print("=" * 100)

    for index, interpretation in enumerate(
        interpretations,
        start=1,
    ):
        print(
            f"\n[{index}] {interpretation.insight_id}"
        )
        print(
            f"Title                : "
            f"{interpretation.title}"
        )
        print(
            f"Category             : "
            f"{interpretation.category}"
        )
        print(
            f"Priority             : "
            f"{interpretation.priority}"
        )
        print(
            f"Evidence             : "
            f"{interpretation.evidence_summary}"
        )
        print(
            f"Interpretation       : "
            f"{interpretation.interpretation}"
        )
        print(
            f"Business implication : "
            f"{interpretation.business_implication}"
        )
        print(
            f"Recommended action   : "
            f"{interpretation.recommended_action}"
        )

    print("\n" + "=" * 100)
    print("M24.4 INTERPRETATION LAYER VALID")
    print("=" * 100)


def main() -> None:
    """Run the complete M24.4 interpretation pipeline."""

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

    print_interpretations(
        interpretations
    )


if __name__ == "__main__":
    main()
