"""
M25.2 — Executive Insight Report Contract Tests.

Verifies that the executive report is a deterministic,
validated representation of the narrative and interpretation layers.
"""

from __future__ import annotations

from src.customer_insight_engine import (
    calculate_all_insights,
    load_customer_data,
)

from src.customer_insight_interpretation import (
    interpret_all_insights,
    validate_interpretations,
)

from src.customer_insight_narrative import (
    build_business_narrative,
    validate_business_narrative,
)

from src.customer_insight_report import (
    build_executive_report,
    validate_report,
)


def _build_report():
    """Build the complete validated executive report."""

    customer = load_customer_data()

    results = calculate_all_insights(customer)

    interpretations = interpret_all_insights(results)

    validate_interpretations(interpretations)

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

    validate_report(report)

    return report


def test_report_is_generated() -> None:
    """The executive report must be generated successfully."""

    report = _build_report()

    assert report is not None


def test_report_validates() -> None:
    """The executive report must satisfy its validation contract."""

    report = _build_report()

    assert validate_report(report) is None


def test_report_is_deterministic() -> None:
    """Repeated report construction must produce identical output."""

    first = _build_report()
    second = _build_report()

    assert first == second


def test_report_contains_seven_findings() -> None:
    """M24 established seven executive findings."""

    report = _build_report()

    assert len(report.findings) == 7


def test_report_contains_four_management_decisions() -> None:
    """M24 established four management decisions."""

    report = _build_report()

    assert len(report.management_decisions) == 4


def test_report_findings_have_required_content() -> None:
    """Every finding must remain traceable."""

    report = _build_report()

    for finding in report.findings:
        assert finding.insight_id
        assert finding.title
        assert finding.category
        assert finding.priority
        assert finding.evidence
        assert finding.interpretation
        assert finding.implication
        assert finding.action


def test_report_management_decisions_are_traceable() -> None:
    """Every management decision must reference source insights."""

    report = _build_report()

    for decision in report.management_decisions:
        assert decision.decision_id
        assert decision.priority
        assert decision.decision
        assert decision.rationale
        assert decision.expected_focus
        assert decision.source_insights
