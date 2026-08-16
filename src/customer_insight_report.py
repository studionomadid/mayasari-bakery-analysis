"""
M24.6 — Mayasari Bakery Executive Customer Insight Report.

Transforms the deterministic M24.3 evidence, M24.4 interpretation,
and M24.5 business narrative layers into a structured executive
insight report.

Architecture:

    Evidence
        ->
    Interpretation
        ->
    Business Narrative
        ->
    Executive Report

Design principles:
    - deterministic
    - evidence traceable
    - no LLM-generated content
    - no causal inference
    - no metric recalculation
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
    InsightDefinition,
    validate_framework,
)

from src.customer_insight_interpretation import (
    InsightInterpretation,
    interpret_all_insights,
    validate_interpretations,
)

from src.customer_insight_narrative import (
    BusinessNarrative,
    build_business_narrative,
    validate_business_narrative,
)


@dataclass(frozen=True)
class ReportFinding:
    """One traceable executive report finding."""

    insight_id: str
    title: str
    category: str
    priority: str
    evidence: str
    interpretation: str
    implication: str
    action: str


@dataclass(frozen=True)
class ManagementDecision:
    """One management decision recommendation."""

    decision_id: str
    priority: str
    decision: str
    rationale: str
    expected_focus: str
    source_insights: tuple[str, ...]


@dataclass(frozen=True)
class ExecutiveInsightReport:
    """Complete structured executive customer insight report."""

    title: str
    subtitle: str
    executive_summary: str
    findings: tuple[ReportFinding, ...]
    strategic_priorities: tuple[str, ...]
    retention_recommendations: tuple[str, ...]
    development_recommendations: tuple[str, ...]
    opportunity_actions: tuple[str, ...]
    management_decisions: tuple[ManagementDecision, ...]
    management_takeaways: tuple[str, ...]


PRIORITY_ORDER: Final[tuple[str, ...]] = (
    "Critical",
    "High",
    "Medium",
    "Low",
)


def _definition_map() -> dict[str, InsightDefinition]:
    """Return framework definitions indexed by insight ID."""

    validate_framework()

    return {
        definition.insight_id: definition
        for definition in CUSTOMER_INSIGHT_FRAMEWORK
    }


def _interpretation_map(
    interpretations: tuple[InsightInterpretation, ...],
) -> dict[str, InsightInterpretation]:
    """Return interpretations indexed by insight ID."""

    validate_interpretations(
        interpretations
    )

    return {
        interpretation.insight_id: interpretation
        for interpretation in interpretations
    }


def build_report_findings(
    interpretations: tuple[InsightInterpretation, ...],
) -> tuple[ReportFinding, ...]:
    """Convert interpretations into traceable report findings."""

    definitions = _definition_map()
    interpretation_map = _interpretation_map(
        interpretations
    )

    findings: list[ReportFinding] = []

    for definition in CUSTOMER_INSIGHT_FRAMEWORK:
        interpretation = interpretation_map[
            definition.insight_id
        ]

        findings.append(
            ReportFinding(
                insight_id=definition.insight_id,
                title=definition.title,
                category=definition.category,
                priority=interpretation.priority,
                evidence=interpretation.evidence_summary,
                interpretation=interpretation.interpretation,
                implication=interpretation.business_implication,
                action=interpretation.recommended_action,
            )
        )

    return tuple(findings)


def build_management_decisions(
    interpretations: tuple[InsightInterpretation, ...],
) -> tuple[ManagementDecision, ...]:
    """Build a concise decision-oriented management layer."""

    interpretation_map = _interpretation_map(
        interpretations
    )

    concentration = interpretation_map[
        "customer_value_concentration"
    ]

    rescue = interpretation_map[
        "rescue_economics"
    ]

    risk = interpretation_map[
        "high_value_at_risk"
    ]

    opportunity = interpretation_map[
        "customer_opportunity_priority"
    ]

    return (
        ManagementDecision(
            decision_id="protect_high_value",
            priority=concentration.priority,
            decision=(
                "Protect high-value customer relationships before "
                "broad customer acquisition expansion."
            ),
            rationale=concentration.business_implication,
            expected_focus=(
                "Platinum and Gold customers, especially customers "
                "showing retention risk."
            ),
            source_insights=(
                "customer_value_concentration",
                "clv_tier_economics",
                "high_value_at_risk",
            ),
        ),
        ManagementDecision(
            decision_id="rescue_priority",
            priority=rescue.priority,
            decision=(
                "Prioritize economically meaningful Rescue customers "
                "for targeted re-engagement."
            ),
            rationale=rescue.business_implication,
            expected_focus=(
                "Rescue customers with high CLV, particularly "
                "Platinum Rescue customers."
            ),
            source_insights=(
                "rescue_economics",
                "customer_opportunity_priority",
            ),
        ),
        ManagementDecision(
            decision_id="retain_at_risk",
            priority=risk.priority,
            decision=(
                "Establish a high-value At-Risk retention queue."
            ),
            rationale=risk.business_implication,
            expected_focus=(
                "Platinum and Gold customers within the At-Risk "
                "population."
            ),
            source_insights=(
                "high_value_at_risk",
                "clv_tier_economics",
            ),
        ),
        ManagementDecision(
            decision_id="develop_customer_base",
            priority=opportunity.priority,
            decision=(
                "Use opportunity classification and customer "
                "economics to prioritize development resources."
            ),
            rationale=opportunity.business_implication,
            expected_focus=(
                "Priority 1-3 opportunity groups and customers "
                "with observable development potential."
            ),
            source_insights=(
                "customer_opportunity_priority",
                "rfm_customer_quality",
                "clv_tier_economics",
            ),
        ),
    )


def build_executive_report(
    narrative: BusinessNarrative,
    interpretations: tuple[InsightInterpretation, ...],
) -> ExecutiveInsightReport:
    """Build the complete executive insight report."""

    validate_business_narrative(
        narrative
    )

    validate_interpretations(
        interpretations
    )

    findings = build_report_findings(
        interpretations
    )

    decisions = build_management_decisions(
        interpretations
    )

    return ExecutiveInsightReport(
        title="Mayasari Bakery Customer Insight Report",
        subtitle=(
            "Evidence-backed customer economics, behavior, "
            "retention, and opportunity assessment"
        ),
        executive_summary=narrative.executive_summary,
        findings=findings,
        strategic_priorities=narrative.strategic_priorities,
        retention_recommendations=(
            narrative.retention_recommendations
        ),
        development_recommendations=(
            narrative.development_recommendations
        ),
        opportunity_actions=narrative.opportunity_actions,
        management_decisions=decisions,
        management_takeaways=narrative.management_takeaways,
    )


def validate_report(
    report: ExecutiveInsightReport,
) -> None:
    """Validate report structure and evidence traceability."""

    if not report.title.strip():
        raise ValueError(
            "Report title cannot be empty."
        )

    if not report.subtitle.strip():
        raise ValueError(
            "Report subtitle cannot be empty."
        )

    if not report.executive_summary.strip():
        raise ValueError(
            "Executive summary cannot be empty."
        )

    if len(report.findings) != 7:
        raise ValueError(
            "Executive report must contain exactly 7 findings."
        )

    expected_ids = {
        definition.insight_id
        for definition in CUSTOMER_INSIGHT_FRAMEWORK
    }

    actual_ids = {
        finding.insight_id
        for finding in report.findings
    }

    if actual_ids != expected_ids:
        raise ValueError(
            "Report findings do not cover the complete framework."
        )

    for finding in report.findings:
        if finding.priority not in PRIORITY_ORDER:
            raise ValueError(
                f"Invalid finding priority: {finding.priority}"
            )

        fields = (
            finding.insight_id,
            finding.title,
            finding.category,
            finding.evidence,
            finding.interpretation,
            finding.implication,
            finding.action,
        )

        if any(
            not field.strip()
            for field in fields
        ):
            raise ValueError(
                f"Incomplete report finding: "
                f"{finding.insight_id}"
            )

    if len(report.strategic_priorities) != 4:
        raise ValueError(
            "Expected exactly 4 strategic priorities."
        )

    if len(report.retention_recommendations) != 7:
        raise ValueError(
            "Expected exactly 7 retention recommendations."
        )

    if len(report.development_recommendations) != 8:
        raise ValueError(
            "Expected exactly 8 development recommendations."
        )

    if len(report.opportunity_actions) != 7:
        raise ValueError(
            "Expected exactly 7 opportunity actions."
        )

    if len(report.management_decisions) != 4:
        raise ValueError(
            "Expected exactly 4 management decisions."
        )

    if len(report.management_takeaways) != 6:
        raise ValueError(
            "Expected exactly 6 management takeaways."
        )

    for decision in report.management_decisions:
        if decision.priority not in PRIORITY_ORDER:
            raise ValueError(
                f"Invalid decision priority: "
                f"{decision.priority}"
            )

        if not decision.decision.strip():
            raise ValueError(
                f"Empty decision: {decision.decision_id}"
            )

        if not decision.rationale.strip():
            raise ValueError(
                f"Empty rationale: {decision.decision_id}"
            )

        if not decision.expected_focus.strip():
            raise ValueError(
                f"Empty expected focus: "
                f"{decision.decision_id}"
            )

        if not decision.source_insights:
            raise ValueError(
                f"Decision has no source insights: "
                f"{decision.decision_id}"
            )

        if any(
            source not in expected_ids
            for source in decision.source_insights
        ):
            raise ValueError(
                f"Decision contains unknown source insight: "
                f"{decision.decision_id}"
            )

    full_text = "\n".join(
        (
            report.executive_summary,
            *report.strategic_priorities,
            *report.retention_recommendations,
            *report.development_recommendations,
            *report.opportunity_actions,
            *report.management_takeaways,
        )
    )

    forbidden_terms = (
        "caused",
        "causes",
        "proves",
        "guarantees",
    )

    for term in forbidden_terms:
        if term in full_text.lower():
            raise ValueError(
                f"Forbidden causal language detected: {term}"
            )

    if (
        "does not establish causal drivers"
        not in full_text.lower()
    ):
        raise ValueError(
            "Report must explicitly preserve non-causal interpretation."
        )


def print_report(
    report: ExecutiveInsightReport,
) -> None:
    """Print the complete executive report."""

    validate_report(
        report
    )

    print("=" * 110)
    print(report.title.upper())
    print("=" * 110)

    print("\nSUBTITLE")
    print("-" * 110)
    print(report.subtitle)

    print("\nEXECUTIVE SUMMARY")
    print("-" * 110)
    print(report.executive_summary)

    print("\nKEY FINDINGS")
    print("-" * 110)

    for index, finding in enumerate(
        report.findings,
        start=1,
    ):
        print(
            f"\n[{index}] {finding.title}"
        )
        print(
            f"Insight ID : {finding.insight_id}"
        )
        print(
            f"Category   : {finding.category}"
        )
        print(
            f"Priority   : {finding.priority}"
        )
        print(
            f"Evidence   : {finding.evidence}"
        )
        print(
            f"Meaning    : {finding.interpretation}"
        )
        print(
            f"Implication: {finding.implication}"
        )
        print(
            f"Action     : {finding.action}"
        )

    print("\nSTRATEGIC PRIORITIES")
    print("-" * 110)

    for item in report.strategic_priorities:
        print(item)

    print("\nRETENTION RECOMMENDATIONS")
    print("-" * 110)

    for item in report.retention_recommendations:
        print(f"- {item}")

    print("\nCUSTOMER DEVELOPMENT RECOMMENDATIONS")
    print("-" * 110)

    for item in report.development_recommendations:
        print(f"- {item}")

    print("\nOPPORTUNITY ACTIONS")
    print("-" * 110)

    for item in report.opportunity_actions:
        print(f"- {item}")

    print("\nMANAGEMENT DECISIONS")
    print("-" * 110)

    for index, decision in enumerate(
        report.management_decisions,
        start=1,
    ):
        print(
            f"\n[{index}] {decision.decision_id}"
        )
        print(
            f"Priority       : {decision.priority}"
        )
        print(
            f"Decision       : {decision.decision}"
        )
        print(
            f"Rationale      : {decision.rationale}"
        )
        print(
            f"Expected focus : {decision.expected_focus}"
        )
        print(
            f"Source insights: "
            f"{', '.join(decision.source_insights)}"
        )

    print("\nMANAGEMENT TAKEAWAYS")
    print("-" * 110)

    for item in report.management_takeaways:
        print(f"- {item}")

    print("\n" + "=" * 110)
    print("M24.6 EXECUTIVE REPORT VALID")
    print("=" * 110)


def main() -> None:
    """Run the complete M24.6 report pipeline."""

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

    report = build_executive_report(
        narrative,
        interpretations,
    )

    validate_report(
        report
    )

    print_report(
        report
    )


if __name__ == "__main__":
    main()
