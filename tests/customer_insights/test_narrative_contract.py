"""
M25.2 — Customer Insight Narrative Contract Tests.

Verifies the deterministic transformation from interpretation
objects into business narrative.
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


def _build_narrative():
    """Build the validated business narrative pipeline."""

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

    return narrative


def test_business_narrative_is_generated() -> None:
    """The narrative layer must produce a non-empty object."""

    narrative = _build_narrative()

    assert narrative is not None


def test_business_narrative_validates() -> None:
    """Narrative output must satisfy its validation contract."""

    narrative = _build_narrative()

    assert validate_business_narrative(
        narrative
    ) is None


def test_business_narrative_is_deterministic() -> None:
    """Repeated narrative generation must remain identical."""

    first = _build_narrative()
    second = _build_narrative()

    assert first == second


def test_business_narrative_contains_strategic_content() -> None:
    """The narrative must expose strategic business content."""

    narrative = _build_narrative()

    assert narrative.strategic_priorities
    assert narrative.retention_recommendations
    assert narrative.development_recommendations
    assert narrative.opportunity_actions
