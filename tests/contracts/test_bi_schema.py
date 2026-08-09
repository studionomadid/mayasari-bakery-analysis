"""BI artifact schema contracts.

These tests protect the public schema of the analytical Parquet artifacts.
Dashboard and insight layers depend on these columns and their data types.
"""

from __future__ import annotations

import pandas as pd

from src.contracts.paths import (
    CUSTOMER_PERFORMANCE_DATA,
    EXECUTIVE_KPIS_DATA,
    MONTHLY_PERFORMANCE_DATA,
    PRODUCT_PERFORMANCE_DATA,
    PROFITABILITY_SUMMARY_DATA,
)

EXPECTED_SCHEMAS = {
    "executive_kpis": {
        "path": EXECUTIVE_KPIS_DATA,
        "columns": {
            "revenue": "int64",
            "gross_profit": "int64",
            "gross_margin_pct": "float64",
            "transactions": "int64",
            "active_customers": "int64",
            "products": "int64",
            "total_quantity": "int64",
            "average_transaction_value": "float64",
            "product_cost": "int64",
            "operating_expense": "int64",
            "operating_profit": "int64",
            "customer_master_count": "int64",
            "product_master_count": "int64",
        },
    },
    "monthly_performance": {
        "path": MONTHLY_PERFORMANCE_DATA,
        "columns": {
            "sales_month": "str",
            "revenue": "int64",
            "gross_profit": "int64",
            "product_cost": "int64",
            "transactions": "int64",
            "customers": "int64",
            "quantity": "int64",
            "gross_margin_pct": "float64",
            "average_transaction_value": "float64",
            "mom_revenue_growth_pct": "float64",
            "mom_profit_growth_pct": "float64",
            "rolling_3m_revenue": "float64",
            "rolling_3m_profit": "float64",
        },
    },
    "product_performance": {
        "path": PRODUCT_PERFORMANCE_DATA,
        "columns": {
            "product_id": "str",
            "revenue": "int64",
            "gross_profit": "int64",
            "product_cost": "int64",
            "quantity": "int64",
            "transactions": "int64",
            "gross_margin_pct": "float64",
            "revenue_share_pct": "float64",
            "profit_share_pct": "float64",
            "product_name": "str",
            "category": "str",
            "price": "int64",
            "cost": "int64",
        },
    },
    "customer_performance": {
        "path": CUSTOMER_PERFORMANCE_DATA,
        "columns": {
            "customer_id": "str",
            "revenue": "int64",
            "gross_profit": "int64",
            "transactions": "int64",
            "active_months": "int64",
            "first_purchase": "datetime64[us]",
            "last_purchase": "datetime64[us]",
            "gross_margin_pct": "float64",
            "average_transaction_value": "float64",
            "historical_clv": "int64",
            "annualized_clv": "float64",
            "observed_lifetime_days": "int64",
        },
    },
    "profitability_summary": {
        "path": PROFITABILITY_SUMMARY_DATA,
        "columns": {
            "revenue": "int64",
            "product_cost": "int64",
            "gross_profit": "int64",
            "gross_margin_pct": "float64",
        },
    },
}


def test_bi_artifacts_exist() -> None:
    """Every BI artifact required by downstream consumers must exist."""

    for artifact in EXPECTED_SCHEMAS.values():
        assert artifact["path"].exists(), (
            f"Missing BI artifact: {artifact['path']}"
        )


def test_bi_artifact_schemas() -> None:
    """Every BI artifact must preserve its expected public schema."""

    for name, artifact in EXPECTED_SCHEMAS.items():
        path = artifact["path"]
        expected_columns = artifact["columns"]

        dataframe = pd.read_parquet(path)

        assert list(dataframe.columns) == list(
            expected_columns.keys()
        ), f"Schema columns changed for {name}"

        actual_dtypes = {
            column: str(dtype)
            for column, dtype in dataframe.dtypes.items()
        }

        assert actual_dtypes == expected_columns, (
            f"Schema dtypes changed for {name}: "
            f"{actual_dtypes}"
        )


def test_singleton_bi_artifacts_have_one_row() -> None:
    """Executive and profitability summaries must remain singleton datasets."""

    singleton_artifacts = (
        "executive_kpis",
        "profitability_summary",
    )

    for name in singleton_artifacts:
        dataframe = pd.read_parquet(
            EXPECTED_SCHEMAS[name]["path"]
        )

        assert len(dataframe) == 1, (
            f"{name} must contain exactly one row."
        )


def test_customer_and_product_grain_are_unique() -> None:
    """Customer and product BI artifacts must preserve entity-level grain."""

    customer = pd.read_parquet(
        CUSTOMER_PERFORMANCE_DATA
    )

    product = pd.read_parquet(
        PRODUCT_PERFORMANCE_DATA
    )

    assert customer["customer_id"].is_unique
    assert product["product_id"].is_unique
