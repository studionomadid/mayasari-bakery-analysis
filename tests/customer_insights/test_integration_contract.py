"""
M25.3.2 — Customer Insight Cross-Layer Integration Contract Tests.

Verifies that the customer insight pipeline remains structurally
consistent across:

    framework
        -> engine
        -> interpretation
        -> narrative
        -> executive report
        -> markdown export

The framework contains seven primary business insights.

The engine intentionally exposes eight evidence outputs because
``priority_group_clv_share`` is a supporting scalar metric used by
customer opportunity analysis and is not itself a framework insight.
"""

from __future__ import annotations

from pathlib import Path

from src.customer_insight_engine import (
    calculate_all_insights,
    load_customer_data,
    validate_insight_results,
)
from src.customer_insight_export import (
    render_markdown,
    validate_markdown_export,
)
from src.customer_insight_framework import (
    CUSTOMER_INSIGHT_FRAMEWORK,
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
    build_executive_report,
    validate_report,
)


EXPECTED_INSIGHT_IDS = tuple(
    definition.insight_id
    for definition in CUSTOMER_INSIGHT_FRAMEWORK
)

EXPECTED_ENGINE_SUPPORTING_METRIC = (
    "priority_group_clv_share"
)

EXPECTED_REPORT_FINDING_COUNT = 7
EXPECTED_MANAGEMENT_DECISION_COUNT = 4


def _build_pipeline():
    """
    Build the complete customer insight pipeline once.

    Returns all intermediate artifacts required for
    cross-layer validation.
    """

    # ---------------------------------------------------------
    # Layer 1 — Customer data
    # ---------------------------------------------------------

    customer = load_customer_data()

    # ---------------------------------------------------------
    # Layer 2 — Framework
    # ---------------------------------------------------------

    validate_framework()

    # ---------------------------------------------------------
    # Layer 3 — Evidence engine
    # ---------------------------------------------------------

    results = calculate_all_insights(
        customer
    )

    validate_insight_results(
        customer,
        results,
    )

    # ---------------------------------------------------------
    # Layer 4 — Interpretation
    # ---------------------------------------------------------

    interpretations = interpret_all_insights(
        results
    )

    validate_interpretations(
        interpretations
    )

    # ---------------------------------------------------------
    # Layer 5 — Business narrative
    #
    # Public API:
    #     build_business_narrative(interpretations)
    # ---------------------------------------------------------

    narrative = build_business_narrative(
        interpretations
    )

    validate_business_narrative(
        narrative
    )

    # ---------------------------------------------------------
    # Layer 6 — Executive report
    #
    # Public API:
    #     build_executive_report(
    #         narrative,
    #         interpretations,
    #     )
    # ---------------------------------------------------------

    report = build_executive_report(
        narrative,
        interpretations,
    )

    validate_report(
        report
    )

    # ---------------------------------------------------------
    # Layer 7 — Markdown export
    # ---------------------------------------------------------

    markdown = render_markdown(
        report
    )

    validate_markdown_export(
        markdown,
        report,
    )

    return (
        customer,
        results,
        interpretations,
        narrative,
        report,
        markdown,
    )


def test_framework_and_engine_primary_ids_are_aligned() -> None:
    """
    Every framework insight must have a corresponding engine
    evidence output.

    The engine may additionally expose supporting evidence metrics.
    """

    (
        _customer,
        results,
        _interpretations,
        _narrative,
        _report,
        _markdown,
    ) = _build_pipeline()

    engine_keys = set(
        results.keys()
    )

    assert set(
        EXPECTED_INSIGHT_IDS
    ).issubset(
        engine_keys
    )

    assert (
        EXPECTED_ENGINE_SUPPORTING_METRIC
        in engine_keys
    )


def test_engine_contains_no_unregistered_primary_insights() -> None:
    """
    Engine outputs beyond the framework must be explicitly classified
    as supporting evidence.

    This prevents accidental drift where a new engine metric silently
    becomes an undocumented business insight.
    """

    (
        _customer,
        results,
        _interpretations,
        _narrative,
        _report,
        _markdown,
    ) = _build_pipeline()

    framework_ids = set(
        EXPECTED_INSIGHT_IDS
    )

    extra_engine_keys = (
        set(results.keys())
        - framework_ids
    )

    assert extra_engine_keys == {
        EXPECTED_ENGINE_SUPPORTING_METRIC
    }


def test_interpretation_ids_match_framework_ids() -> None:
    """
    Interpretation coverage must exactly match the seven framework
    insights.
    """

    (
        _customer,
        _results,
        interpretations,
        _narrative,
        _report,
        _markdown,
    ) = _build_pipeline()

    interpretation_ids = tuple(
        interpretation.insight_id
        for interpretation in interpretations
    )

    assert (
        interpretation_ids
        == EXPECTED_INSIGHT_IDS
    )


def test_report_finding_ids_match_framework_ids() -> None:
    """
    Every primary framework insight must appear exactly once as an
    executive report finding.
    """

    (
        _customer,
        _results,
        _interpretations,
        _narrative,
        report,
        _markdown,
    ) = _build_pipeline()

    finding_ids = tuple(
        finding.insight_id
        for finding in report.findings
    )

    assert (
        finding_ids
        == EXPECTED_INSIGHT_IDS
    )

    assert (
        len(finding_ids)
        == EXPECTED_REPORT_FINDING_COUNT
    )

    assert (
        len(finding_ids)
        == len(set(finding_ids))
    )


def test_report_management_decisions_have_valid_sources() -> None:
    """
    Every management decision must reference only known framework
    insight IDs.
    """

    (
        _customer,
        _results,
        _interpretations,
        _narrative,
        report,
        _markdown,
    ) = _build_pipeline()

    framework_ids = set(
        EXPECTED_INSIGHT_IDS
    )

    assert (
        len(report.management_decisions)
        == EXPECTED_MANAGEMENT_DECISION_COUNT
    )

    for decision in report.management_decisions:
        assert decision.decision_id
        assert decision.priority
        assert decision.decision
        assert decision.rationale
        assert decision.expected_focus
        assert decision.source_insights

        assert set(
            decision.source_insights
        ).issubset(
            framework_ids
        )


def test_narrative_is_supported_by_framework_insights() -> None:
    """
    Narrative output must contain the expected seven key findings and
    seven opportunity actions established by the report architecture.
    """

    (
        _customer,
        _results,
        _interpretations,
        narrative,
        _report,
        _markdown,
    ) = _build_pipeline()

    assert (
        len(narrative.key_findings)
        == EXPECTED_REPORT_FINDING_COUNT
    )

    assert (
        len(narrative.opportunity_actions)
        == EXPECTED_REPORT_FINDING_COUNT
    )

    for item in (
        narrative.key_findings
        + narrative.opportunity_actions
    ):
        assert item
        assert isinstance(
            item,
            str,
        )


def test_markdown_contains_all_report_findings() -> None:
    """
    The final Markdown artifact must preserve every report finding.
    """

    (
        _customer,
        _results,
        _interpretations,
        _narrative,
        report,
        markdown,
    ) = _build_pipeline()

    for finding in report.findings:
        assert (
            finding.insight_id
            in markdown
        )

        assert (
            finding.title
            in markdown
        )

        assert (
            finding.evidence
            in markdown
        )


def test_markdown_contains_all_management_decisions() -> None:
    """
    The final Markdown artifact must preserve every public field
    exposed by ManagementDecision and rendered by render_markdown().
    """

    (
        _customer,
        _results,
        _interpretations,
        _narrative,
        report,
        markdown,
    ) = _build_pipeline()

    for decision in (
        report.management_decisions
    ):
        # ManagementDecision public identity.
        assert (
            decision.decision_id
            in markdown
        )

        # Priority is rendered as:
        # **Priority:** **<priority>**
        assert (
            decision.priority
            in markdown
        )

        # Main management recommendation.
        assert (
            decision.decision
            in markdown
        )

        # Supporting rationale.
        assert (
            decision.rationale
            in markdown
        )

        # Expected business focus.
        assert (
            decision.expected_focus
            in markdown
        )

        # Every framework insight reference must survive
        # the Markdown export.
        for source in (
            decision.source_insights
        ):
            assert (
                source
                in markdown
            )


def test_complete_pipeline_is_valid() -> None:
    """
    Single integration gate for the entire deterministic pipeline.

    If this test passes, every layer from framework through Markdown
    export has been constructed and validated successfully.
    """

    (
        customer,
        results,
        interpretations,
        narrative,
        report,
        markdown,
    ) = _build_pipeline()

    assert len(customer) > 0
    assert results
    assert interpretations
    assert narrative
    assert report
    assert markdown.strip()

    assert set(
        EXPECTED_INSIGHT_IDS
    ).issubset(
        results.keys()
    )


def test_committed_markdown_artifact_exists() -> None:
    """
    The repository must contain the generated Markdown report artifact.
    """

    report_path = Path(
        "reports/customer_insight_report.md"
    )

    assert report_path.exists()
    assert report_path.is_file()
    assert (
        report_path.stat().st_size > 0
    )
