"""
M24.7 — Mayasari Bakery Executive Insight Report Export Layer.

Transforms the deterministic M24.6 ExecutiveInsightReport object
into a human-readable Markdown report.

Architecture:

    Evidence
        ->
    Interpretation
        ->
    Business Narrative
        ->
    Executive Report
        ->
    Markdown Export

Design principles:
    - deterministic
    - report-object driven
    - no metric recalculation
    - no LLM-generated content
    - no causal inference
    - reproducible output
"""

from __future__ import annotations

from pathlib import Path

from src.customer_insight_engine import (
    calculate_all_insights,
    load_customer_data,
    validate_insight_results,
)

from src.customer_insight_framework import (
    validate_framework,
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
    ExecutiveInsightReport,
    build_executive_report,
    validate_report,
)


DEFAULT_OUTPUT_PATH = Path(
    "reports/customer_insight_report.md"
)


def _escape_markdown(text: str) -> str:
    """Escape minimal Markdown-sensitive characters."""

    return (
        text
        .replace("\\", "\\\\")
        .replace("|", "\\|")
    )


def render_markdown(
    report: ExecutiveInsightReport,
) -> str:
    """Render an executive insight report as Markdown."""

    validate_report(report)

    lines: list[str] = []

    lines.extend(
        (
            f"# {_escape_markdown(report.title)}",
            "",
            f"> {_escape_markdown(report.subtitle)}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            report.executive_summary,
            "",
            "## Key Findings",
            "",
        )
    )

    for index, finding in enumerate(
        report.findings,
        start=1,
    ):
        lines.extend(
            (
                f"### {index}. {_escape_markdown(finding.title)}",
                "",
                f"**Insight ID:** `{_escape_markdown(finding.insight_id)}`  ",
                f"**Category:** {_escape_markdown(finding.category)}  ",
                f"**Priority:** **{_escape_markdown(finding.priority)}**",
                "",
                "**Evidence**",
                "",
                f"> {_escape_markdown(finding.evidence)}",
                "",
                "**Interpretation**",
                "",
                finding.interpretation,
                "",
                "**Business implication**",
                "",
                finding.implication,
                "",
                "**Recommended action**",
                "",
                finding.action,
                "",
            )
        )

    lines.extend(
        (
            "## Strategic Priorities",
            "",
        )
    )

    for item in report.strategic_priorities:
        lines.extend(
            (
                f"- {item}",
                "",
            )
        )

    lines.extend(
        (
            "## Retention Recommendations",
            "",
        )
    )

    for item in report.retention_recommendations:
        lines.extend(
            (
                f"- {item}",
                "",
            )
        )

    lines.extend(
        (
            "## Customer Development Recommendations",
            "",
        )
    )

    for item in report.development_recommendations:
        lines.extend(
            (
                f"- {item}",
                "",
            )
        )

    lines.extend(
        (
            "## Opportunity Actions",
            "",
        )
    )

    for item in report.opportunity_actions:
        lines.extend(
            (
                f"- {item}",
                "",
            )
        )

    lines.extend(
        (
            "## Management Decisions",
            "",
        )
    )

    for index, decision in enumerate(
        report.management_decisions,
        start=1,
    ):
        source_insights = ", ".join(
            f"`{_escape_markdown(source)}`"
            for source in decision.source_insights
        )

        lines.extend(
            (
                f"### {index}. "
                f"{_escape_markdown(decision.decision_id)}",
                "",
                f"**Priority:** "
                f"**{_escape_markdown(decision.priority)}**",
                "",
                f"**Decision:** {decision.decision}",
                "",
                f"**Rationale:** {decision.rationale}",
                "",
                f"**Expected focus:** {decision.expected_focus}",
                "",
                f"**Source insights:** {source_insights}",
                "",
            )
        )

    lines.extend(
        (
            "## Management Takeaways",
            "",
        )
    )

    for item in report.management_takeaways:
        lines.extend(
            (
                f"- {item}",
                "",
            )
        )

    lines.extend(
        (
            "---",
            "",
            "## Analytical Scope",
            "",
            (
                "This report describes observed customer behavior "
                "and economic relationships. It does not establish "
                "causal drivers of customer behavior."
            ),
            "",
            "## Evidence Chain",
            "",
            (
                "The report follows a deterministic analytical chain:"
            ),
            "",
            "```text",
            "Customer Data",
            "    ↓",
            "M24.3 — Deterministic Evidence",
            "    ↓",
            "M24.4 — Interpretation",
            "    ↓",
            "M24.5 — Business Narrative",
            "    ↓",
            "M24.6 — Executive Insight Report",
            "    ↓",
            "M24.7 — Markdown Export",
            "```",
            "",
        )
    )

    return "\n".join(lines).rstrip() + "\n"


def validate_markdown_export(
    markdown: str,
    report: ExecutiveInsightReport,
) -> None:
    """Validate exported Markdown against the source report."""

    if not markdown.strip():
        raise ValueError(
            "Markdown export cannot be empty."
        )

    required_sections = (
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

    for section in required_sections:
        if section not in markdown:
            raise ValueError(
                f"Missing required Markdown section: {section}"
            )

    for finding in report.findings:
        required_content = (
            finding.insight_id,
            finding.title,
            finding.category,
            finding.priority,
            finding.evidence,
            finding.interpretation,
            finding.implication,
            finding.action,
        )

        for content in required_content:
            if content not in markdown:
                raise ValueError(
                    "Report finding content missing from export: "
                    f"{content}"
                )

    for decision in report.management_decisions:
        required_content = (
            decision.decision_id,
            decision.priority,
            decision.decision,
            decision.rationale,
            decision.expected_focus,
        )

        for content in required_content:
            if content not in markdown:
                raise ValueError(
                    "Management decision content missing from export: "
                    f"{content}"
                )

        for source in decision.source_insights:
            if source not in markdown:
                raise ValueError(
                    "Management decision source insight missing: "
                    f"{source}"
                )

    if (
        "does not establish causal drivers"
        not in markdown.lower()
    ):
        raise ValueError(
            "Non-causal analytical scope is missing."
        )

    expected_evidence = (
        "44.52%",
        "24.51%",
        "18.78%",
        "43.88%",
    )

    for value in expected_evidence:
        if value not in markdown:
            raise ValueError(
                f"Expected evidence value missing from export: {value}"
            )


def export_markdown(
    report: ExecutiveInsightReport,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    """Render and write the report to Markdown."""

    markdown = render_markdown(report)

    validate_markdown_export(
        markdown,
        report,
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        markdown,
        encoding="utf-8",
    )

    return output_path


def build_report() -> ExecutiveInsightReport:
    """Build the complete executive report from source data."""

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

    return report


def main() -> None:
    """Run the complete M24.7 export pipeline."""

    report = build_report()

    output_path = export_markdown(
        report
    )

    print("=" * 110)
    print("M24.7 — CUSTOMER INSIGHT MARKDOWN EXPORT")
    print("=" * 110)

    print(f"Output: {output_path}")

    print(
        f"Size  : {output_path.stat().st_size} bytes"
    )

    print(
        "PASS — Markdown export generated successfully."
    )

    print(
        "PASS — Markdown export validation succeeded."
    )

    print("=" * 110)


if __name__ == "__main__":
    main()
