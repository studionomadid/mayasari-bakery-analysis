"""
M25.2 — Customer Insight Framework Contract Tests.

These tests verify that the deterministic insight framework exposes
its required analytical contract without modifying production logic.
"""

from __future__ import annotations

import pytest

from src.customer_insight_framework import (
    validate_framework,
)


def test_framework_validation_succeeds() -> None:
    """The complete insight framework must validate successfully."""

    result = validate_framework()

    assert result is None


def test_framework_validation_is_deterministic() -> None:
    """Repeated framework validation must produce the same result."""

    first = validate_framework()
    second = validate_framework()

    assert first == second


def test_framework_validation_does_not_require_customer_data() -> None:
    """Framework-level validation must remain independent of source data."""

    try:
        result = validate_framework()
    except Exception as exc:  # pragma: no cover - diagnostic guard
        pytest.fail(
            f"Framework validation unexpectedly depends on external data: "
            f"{exc}"
        )

    assert result is None
