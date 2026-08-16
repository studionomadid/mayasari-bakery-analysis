"""
M25.2 — Markdown Export Contract Tests.

Verifies deterministic rendering and preservation of the
M24 executive report contract in Markdown.
"""

from __future__ import annotations

from pathlib import Path

from src.customer_insight_export import (
    build_report,
    export_markdown,
    render_markdown,
    validate_markdown_export,
)


EXPECTED_EVIDENCE = (
    "44.52%",
    "24.51%",
    "18.78%",
    "43.88%",
)


REQUIRED_SECTIONS = (
    "# Mayasari Bakery Customer Insight Report",
    "## Executive Summary",
    "## Key Findings",
    "## Strategic Priorities",
    "## Retention Recommendations",
    "## Customer Development Recommendations",
    "## Opportunity Actions",
    "## Management Decisions",
    "## Management Takeaways",
    "## Analytical Scope",
    "## Evidence Chain",
)


def test_markdown_render_is_non_empty() -> None:
    """Markdown rendering must produce substantive output."""

    report = build_report()

    markdown = render_markdown(report)

    assert markdown.strip()


def test_markdown_export_validates() -> None:
    """Rendered Markdown must satisfy the export contract."""

    report = build_report()

    markdown = render_markdown(report)

    assert validate_markdown_export(
        markdown,
        report,
    ) is None


def test_markdown_render_is_deterministic() -> None:
    """Repeated Markdown rendering must produce identical output."""

    report = build_report()

    first = render_markdown(report)
    second = render_markdown(report)

    assert first == second


def test_required_sections_are_present() -> None:
    """All executive report sections must remain present."""

    report = build_report()

    markdown = render_markdown(report)

    for section in REQUIRED_SECTIONS:
        assert section in markdown


def test_expected_evidence_is_preserved() -> None:
    """Critical M24 evidence values must survive Markdown rendering."""

    report = build_report()

    markdown = render_markdown(report)

    for value in EXPECTED_EVIDENCE:
        assert value in markdown


def test_non_causal_scope_is_preserved() -> None:
    """The report must retain its explicit non-causal scope."""

    report = build_report()

    markdown = render_markdown(report)

    assert (
        "does not establish causal drivers"
        in markdown.lower()
    )


def test_all_findings_are_traceable() -> None:
    """Every report finding must be represented in Markdown."""

    report = build_report()

    markdown = render_markdown(report)

    for finding in report.findings:
        assert finding.insight_id in markdown
        assert finding.title in markdown
        assert finding.evidence in markdown
        assert finding.interpretation in markdown
        assert finding.implication in markdown
        assert finding.action in markdown


def test_all_management_decisions_are_traceable() -> None:
    """Every management decision must be represented in Markdown."""

    report = build_report()

    markdown = render_markdown(report)

    for decision in report.management_decisions:
        assert decision.decision_id in markdown
        assert decision.decision in markdown
        assert decision.rationale in markdown
        assert decision.expected_focus in markdown

        for source in decision.source_insights:
            assert source in markdown


def test_export_matches_committed_report() -> None:
    """Generated Markdown must match the repository artifact."""

    report = build_report()

    markdown = render_markdown(report)

    output_path = Path(
        "reports/customer_insight_report.md"
    )

    assert output_path.exists()

    committed_report = output_path.read_text(
        encoding="utf-8"
    )

    assert committed_report == markdown


def test_export_function_writes_deterministic_artifact(
    tmp_path: Path,
) -> None:
    """export_markdown must write the same deterministic representation."""

    report = build_report()

    output_path = tmp_path / "customer_insight_report.md"

    result = export_markdown(
        report,
        output_path,
    )

    assert result == output_path
    assert output_path.exists()

    exported = output_path.read_text(
        encoding="utf-8"
    )

    assert exported == render_markdown(report)
