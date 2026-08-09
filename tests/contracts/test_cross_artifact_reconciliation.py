"""Cross-artifact reconciliation contracts.

Validates that analytical artifacts reconcile with the source dataset
according to their declared data grain.
"""

from __future__ import annotations

import math

import pandas as pd

from src.contracts.paths import (
    CUSTOMER_OPPORTUNITY_DATA,
    CUSTOMER_PERFORMANCE_DATA,
    EXECUTIVE_KPIS_DATA,
    MONTHLY_PERFORMANCE_DATA,
    PRODUCT_PERFORMANCE_DATA,
    PROFITABILITY_SUMMARY_DATA,
    SALES_DATA,
)


TOLERANCE = 0.01
PERCENT_TOLERANCE = 0.0001


def check_close(
    left: float,
    right: float,
    tolerance: float = TOLERANCE,
) -> None:
    """Assert two numeric values reconcile within tolerance."""
    assert math.isclose(
        float(left),
        float(right),
        rel_tol=0.0,
        abs_tol=tolerance,
    ), f"Values do not reconcile: {left} != {right}"


def test_executive_reconciles_with_monthly() -> None:
    """Executive totals reconcile with monthly performance."""
    executive = pd.read_parquet(EXECUTIVE_KPIS_DATA)
    monthly = pd.read_parquet(MONTHLY_PERFORMANCE_DATA)

    row = executive.iloc[0]

    check_close(row["revenue"], monthly["revenue"].sum())
    check_close(row["gross_profit"], monthly["gross_profit"].sum())
    check_close(row["product_cost"], monthly["product_cost"].sum())
    check_close(row["transactions"], monthly["transactions"].sum())
    check_close(row["total_quantity"], monthly["quantity"].sum())


def test_executive_reconciles_with_customer_performance() -> None:
    """Customer-level totals reconcile with executive KPIs."""
    executive = pd.read_parquet(EXECUTIVE_KPIS_DATA)
    customers = pd.read_parquet(CUSTOMER_PERFORMANCE_DATA)

    row = executive.iloc[0]

    check_close(row["revenue"], customers["revenue"].sum())
    check_close(row["gross_profit"], customers["gross_profit"].sum())
    check_close(row["transactions"], customers["transactions"].sum())

    assert (
        customers["customer_id"].nunique()
        == int(row["active_customers"])
    )


def test_executive_reconciles_with_product_financials() -> None:
    """Product-level financial totals reconcile with executive KPIs."""
    executive = pd.read_parquet(EXECUTIVE_KPIS_DATA)
    products = pd.read_parquet(PRODUCT_PERFORMANCE_DATA)

    row = executive.iloc[0]

    check_close(row["revenue"], products["revenue"].sum())
    check_close(row["gross_profit"], products["gross_profit"].sum())
    check_close(row["product_cost"], products["product_cost"].sum())
    check_close(row["total_quantity"], products["quantity"].sum())

    assert products["product_id"].nunique() == int(row["products"])


def test_product_transaction_grain_reconciles_with_source() -> None:
    """Product transaction totals reconcile using product-transaction grain."""
    sales = pd.read_parquet(SALES_DATA)
    products = pd.read_parquet(PRODUCT_PERFORMANCE_DATA)

    expected = (
        sales[["product_id", "transaction_key"]]
        .drop_duplicates()
        .shape[0]
    )

    actual = int(products["transactions"].sum())

    assert actual == expected


def test_business_transaction_grain_reconciles_with_source() -> None:
    """Executive transactions use business transaction grain."""
    sales = pd.read_parquet(SALES_DATA)
    executive = pd.read_parquet(EXECUTIVE_KPIS_DATA)

    expected = sales["transaction_key"].nunique()
    actual = int(executive.iloc[0]["transactions"])

    assert actual == expected


def test_product_transaction_grain_is_distinct_from_business_grain() -> None:
    """Product transaction grain must not be confused with business grain."""
    sales = pd.read_parquet(SALES_DATA)
    products = pd.read_parquet(PRODUCT_PERFORMANCE_DATA)

    business_transactions = sales["transaction_key"].nunique()

    product_transactions = int(products["transactions"].sum())

    expected_product_transactions = (
        sales[["product_id", "transaction_key"]]
        .drop_duplicates()
        .shape[0]
    )

    assert product_transactions == expected_product_transactions
    assert product_transactions >= business_transactions


def test_profitability_reconciles_with_executive() -> None:
    """Profitability summary reconciles with executive KPIs."""
    executive = pd.read_parquet(EXECUTIVE_KPIS_DATA)
    profitability = pd.read_parquet(PROFITABILITY_SUMMARY_DATA)

    executive_row = executive.iloc[0]
    profitability_row = profitability.iloc[0]

    check_close(
        profitability_row["revenue"],
        executive_row["revenue"],
    )

    check_close(
        profitability_row["product_cost"],
        executive_row["product_cost"],
    )

    check_close(
        profitability_row["gross_profit"],
        executive_row["gross_profit"],
    )

    check_close(
        profitability_row["gross_margin_pct"],
        executive_row["gross_margin_pct"],
        tolerance=PERCENT_TOLERANCE,
    )


def test_customer_opportunity_preserves_customer_metrics() -> None:
    """Customer opportunity artifact preserves customer-level metrics."""
    customers = pd.read_parquet(CUSTOMER_PERFORMANCE_DATA)
    opportunity = pd.read_parquet(CUSTOMER_OPPORTUNITY_DATA)

    assert set(customers["customer_id"]) == set(
        opportunity["customer_id"]
    )

    columns = [
        "revenue",
        "gross_profit",
        "transactions",
        "active_months",
        "historical_clv",
        "annualized_clv",
    ]

    left = (
        customers[
            ["customer_id", *columns]
        ]
        .sort_values("customer_id")
        .reset_index(drop=True)
    )

    right = (
        opportunity[
            ["customer_id", *columns]
        ]
        .sort_values("customer_id")
        .reset_index(drop=True)
    )

    pd.testing.assert_frame_equal(
        left,
        right,
        check_dtype=False,
    )


def test_product_shares_reconcile() -> None:
    """Product revenue and profit shares total 100%."""
    products = pd.read_parquet(PRODUCT_PERFORMANCE_DATA)

    check_close(
        products["revenue_share_pct"].sum(),
        100.0,
    )

    check_close(
        products["profit_share_pct"].sum(),
        100.0,
    )


def test_margin_formulas_reconcile() -> None:
    """Executive, profitability, customer, and product margins are valid."""
    executive = pd.read_parquet(EXECUTIVE_KPIS_DATA)
    profitability = pd.read_parquet(PROFITABILITY_SUMMARY_DATA)
    customers = pd.read_parquet(CUSTOMER_PERFORMANCE_DATA)
    products = pd.read_parquet(PRODUCT_PERFORMANCE_DATA)

    executive_row = executive.iloc[0]
    profitability_row = profitability.iloc[0]

    expected_executive_margin = (
        executive_row["gross_profit"]
        / executive_row["revenue"]
        * 100
    )

    expected_profitability_margin = (
        profitability_row["gross_profit"]
        / profitability_row["revenue"]
        * 100
    )

    check_close(
        executive_row["gross_margin_pct"],
        expected_executive_margin,
        tolerance=PERCENT_TOLERANCE,
    )

    check_close(
        profitability_row["gross_margin_pct"],
        expected_profitability_margin,
        tolerance=PERCENT_TOLERANCE,
    )

    customer_expected = (
        customers["gross_profit"]
        / customers["revenue"]
        * 100
    )

    product_expected = (
        products["gross_profit"]
        / products["revenue"]
        * 100
    )

    assert (
        customers["gross_margin_pct"]
        .sub(customer_expected)
        .abs()
        .le(PERCENT_TOLERANCE)
    ).all()

    assert (
        products["gross_margin_pct"]
        .sub(product_expected)
        .abs()
        .le(PERCENT_TOLERANCE)
    ).all()
