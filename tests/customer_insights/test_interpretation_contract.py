"""
M25.2 — Customer Insight Interpretation Contract Tests.

Verifies that deterministic evidence can be transformed into
validated interpretations without introducing uncontrolled content.
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


def _build_interpretations():
    """Build validated interpretations from the production pipeline."""

    customer = load_customer_data()

    results = calculate_all_insights(customer)

    interpretations = interpret_all_insights(results)

    validate_interpretations(interpretations)

    return interpretations


def test_interpretations_are_generated() -> None:
    """Every evidence result must produce interpretation output."""

    interpretations = _build_interpretations()

    assert interpretations is not None
    assert len(interpretations) == 7


def test_interpretations_validate() -> None:
    """Interpretation output must satisfy its validation contract."""

    interpretations = _build_interpretations()

    assert validate_interpretations(interpretations) is None


def test_interpretations_are_deterministic() -> None:
    """Repeated interpretation must produce identical output."""

    first = _build_interpretations()
    second = _build_interpretations()

    assert first == second


def test_interpretations_have_content() -> None:
    """Each interpretation must contain substantive text."""

    interpretations = _build_interpretations()

    for interpretation in interpretations:
        assert interpretation.interpretation
        assert interpretation.interpretation.strip()
