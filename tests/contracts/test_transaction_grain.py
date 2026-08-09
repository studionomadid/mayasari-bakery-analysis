"""Transaction grain contracts for analytics artifacts.

These tests explicitly distinguish:

1. Business transaction grain:
   one unique transaction_key represents one business transaction.

2. Sales-line grain:
   one unique transaction_line_key represents one sales/product line.

3. Product-transaction grain:
   one unique (product_id, transaction_key) pair represents
   one product occurrence inside a business transaction.

The three grains are intentionally different and must not be
reconciled by naive aggregation.
"""

from __future__ import annotations

import pandas as pd

from src.contracts.paths import (
    EXECUTIVE_KPIS_DATA,
    PRODUCT_PERFORMANCE_DATA,
    SALES_DATA,
)


def load_sales() -> pd.DataFrame:
    """Load the processed sales dataset."""
    return pd.read_parquet(SALES_DATA)


def load_executive() -> pd.DataFrame:
    """Load the executive KPI artifact."""
    return pd.read_parquet(EXECUTIVE_KPIS_DATA)


def load_product_performance() -> pd.DataFrame:
    """Load the product performance artifact."""
    return pd.read_parquet(PRODUCT_PERFORMANCE_DATA)


def test_business_transaction_grain() -> None:
    """Executive transactions equal unique business transactions."""
    sales = load_sales()
    executive = load_executive()

    expected = sales["transaction_key"].nunique()
    actual = int(executive.iloc[0]["transactions"])

    assert actual == expected


def test_sales_line_grain() -> None:
    """Sales rows equal unique transaction-line keys."""
    sales = load_sales()

    expected = len(sales)
    actual = sales["transaction_line_key"].nunique()

    assert actual == expected


def test_product_transaction_grain() -> None:
    """Product transaction totals equal unique product-transaction pairs."""
    sales = load_sales()
    products = load_product_performance()

    expected = (
        sales[["product_id", "transaction_key"]]
        .drop_duplicates()
        .shape[0]
    )

    actual = int(products["transactions"].sum())

    assert actual == expected


def test_product_transaction_grain_is_not_business_transaction_grain() -> None:
    """Document that product transaction totals can exceed business transactions."""
    sales = load_sales()
    products = load_product_performance()

    business_transactions = sales["transaction_key"].nunique()
    product_transactions = int(products["transactions"].sum())

    assert product_transactions >= business_transactions


def test_product_transaction_recomputation() -> None:
    """Every product transaction metric must match source-level recomputation."""
    sales = load_sales()
    products = load_product_performance()

    expected = (
        sales.groupby("product_id")["transaction_key"]
        .nunique()
        .rename("expected_transactions")
        .reset_index()
    )

    actual = products[
        [
            "product_id",
            "transactions",
        ]
    ].rename(
        columns={
            "transactions": "actual_transactions",
        }
    )

    comparison = actual.merge(
        expected,
        on="product_id",
        how="left",
        validate="one_to_one",
    )

    assert (
        comparison["actual_transactions"]
        == comparison["expected_transactions"]
    ).all()
