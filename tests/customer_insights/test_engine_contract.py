"""
M25.2 — Customer Insight Engine Contract Tests.

Verifies the deterministic evidence layer and its relationship
with the customer dataset.

The engine returns a dictionary containing scalar metrics,
nested dictionaries, and pandas DataFrames. Determinism is
therefore validated structurally rather than through direct
dictionary equality.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from src.customer_insight_engine import (
    calculate_all_insights,
    load_customer_data,
    validate_insight_results,
)


EXPECTED_INSIGHT_COUNT = 8


def _assert_values_equal(
    first: Any,
    second: Any,
    path: str,
) -> None:
    """
    Recursively compare two engine result values.

    Supports:
        - scalar values
        - dictionaries
        - pandas DataFrames
        - pandas Series
    """

    if isinstance(first, pd.DataFrame):
        assert isinstance(
            second,
            pd.DataFrame,
        ), f"{path}: type mismatch"

        pd.testing.assert_frame_equal(
            first,
            second,
            check_exact=True,
            check_dtype=True,
            check_names=True,
            check_column_type=True,
        )

        return

    if isinstance(first, pd.Series):
        assert isinstance(
            second,
            pd.Series,
        ), f"{path}: type mismatch"

        pd.testing.assert_series_equal(
            first,
            second,
            check_exact=True,
            check_dtype=True,
            check_names=True,
            check_index_type=True,
        )

        return

    if isinstance(first, dict):
        assert isinstance(
            second,
            dict,
        ), f"{path}: type mismatch"

        assert list(first.keys()) == list(
            second.keys()
        ), f"{path}: dictionary keys differ"

        for key in first:
            _assert_values_equal(
                first[key],
                second[key],
                f"{path}.{key}",
            )

        return

    assert type(first) is type(second), (
        f"{path}: type mismatch — "
        f"{type(first).__name__} != "
        f"{type(second).__name__}"
    )

    assert first == second, (
        f"{path}: values differ — "
        f"{first!r} != {second!r}"
    )


def test_customer_dataset_loads() -> None:
    """The customer analytical dataset must load successfully."""

    customer = load_customer_data()

    assert customer is not None
    assert len(customer) > 0


def test_engine_produces_insight_results() -> None:
    """The evidence engine must produce a non-empty result collection."""

    customer = load_customer_data()

    results = calculate_all_insights(customer)

    assert results is not None
    assert len(results) > 0


def test_engine_results_validate() -> None:
    """Engine output must satisfy its own validation contract."""

    customer = load_customer_data()

    results = calculate_all_insights(customer)

    result = validate_insight_results(
        customer,
        results,
    )

    assert result is None


def test_engine_is_deterministic() -> None:
    """
    Repeated engine execution must produce equivalent results.

    Direct dictionary equality is intentionally avoided because
    pandas DataFrames do not produce a single boolean value when
    compared with ==.
    """

    customer = load_customer_data()

    first = calculate_all_insights(customer)
    second = calculate_all_insights(customer)

    assert list(first.keys()) == list(
        second.keys()
    )

    for key in first:
        _assert_values_equal(
            first[key],
            second[key],
            f"results[{key!r}]",
        )


def test_expected_insight_count() -> None:
    """
    M25.2 engine contract contains eight deterministic evidence outputs.

    Seven outputs correspond directly to the primary customer insights,
    while priority_group_clv_share is an additional scalar evidence
    metric used by the customer opportunity analysis.
    """

    customer = load_customer_data()

    results = calculate_all_insights(customer)

    assert len(results) == EXPECTED_INSIGHT_COUNT

    assert set(results.keys()) == {
        "customer_value_concentration",
        "clv_tier_economics",
        "rfm_customer_quality",
        "customer_opportunity_priority",
        "rescue_economics",
        "high_value_at_risk",
        "customer_profitability",
        "priority_group_clv_share",
    }


def test_engine_result_types_are_stable() -> None:
    """
    Engine result types must remain stable across executions.

    This protects downstream interpretation, narrative, and report
    layers from silent contract changes.
    """

    customer = load_customer_data()

    results = calculate_all_insights(customer)

    assert isinstance(
        results["customer_value_concentration"],
        dict,
    )

    assert isinstance(
        results["clv_tier_economics"],
        pd.DataFrame,
    )

    assert isinstance(
        results["rfm_customer_quality"],
        pd.DataFrame,
    )

    assert isinstance(
        results["customer_opportunity_priority"],
        pd.DataFrame,
    )

    assert isinstance(
        results["rescue_economics"],
        dict,
    )

    assert isinstance(
        results["high_value_at_risk"],
        dict,
    )

    assert isinstance(
        results["customer_profitability"],
        dict,
    )

    assert isinstance(
        results["priority_group_clv_share"],
        float,
    )


def test_engine_dataframe_outputs_are_non_empty() -> None:
    """
    DataFrame-based evidence outputs must contain analytical data.
    """

    customer = load_customer_data()

    results = calculate_all_insights(customer)

    dataframe_keys = (
        "clv_tier_economics",
        "rfm_customer_quality",
        "customer_opportunity_priority",
    )

    for key in dataframe_keys:
        dataframe = results[key]

        assert not dataframe.empty, (
            f"{key} must not be empty"
        )

        assert len(dataframe.columns) > 0, (
            f"{key} must contain columns"
        )


def test_engine_scalar_outputs_are_finite() -> None:
    """
    Scalar evidence values must be finite numeric values.
    """

    customer = load_customer_data()

    results = calculate_all_insights(customer)

    scalar_values = (
        results["priority_group_clv_share"],
        results["customer_value_concentration"][
            "platinum_clv_share"
        ],
        results["rescue_economics"][
            "rescue_clv_share"
        ],
        results["high_value_at_risk"][
            "at_risk_clv_share"
        ],
        results["customer_profitability"][
            "overall_gross_margin"
        ],
    )

    for value in scalar_values:
        assert isinstance(
            value,
            (int, float),
        )

        assert pd.notna(value)
        assert math.isfinite(value)
