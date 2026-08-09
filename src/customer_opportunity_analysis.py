"""
Mayasari Bakery — M12.2.3 Customer Opportunity Analysis.

Combines customer-level RFM segmentation with CLV metrics
to identify customer-value management opportunities.

The module produces a customer-level analytical bridge
between behavioral segmentation and economic customer value.
"""

from __future__ import annotations

import pandas as pd

from src.contracts.paths import (
    ANALYTICS_DIR,
    CUSTOMER_PERFORMANCE_DATA,
    CUSTOMERS_DATA,
    PROJECT_ROOT,
    SALES_DATA,
)

CUSTOMER_DATASET = CUSTOMER_PERFORMANCE_DATA

SALES_DATASET = SALES_DATA

CUSTOMER_MASTER_DATASET = CUSTOMERS_DATA

OUTPUT_DATASET = (
    ANALYTICS_DIR / "customer_opportunity.parquet"
)

SNAPSHOT_DATE = pd.Timestamp("2025-12-31")


REQUIRED_CLV_COLUMNS = [
    "customer_id",
    "revenue",
    "gross_profit",
    "transactions",
    "active_months",
    "gross_margin_pct",
    "average_transaction_value",
    "historical_clv",
    "annualized_clv",
    "observed_lifetime_days",
]


def load_clv_data() -> pd.DataFrame:
    """Load and validate the customer CLV dataset."""

    if not CUSTOMER_DATASET.exists():
        raise FileNotFoundError(
            f"Customer CLV dataset not found: "
            f"{CUSTOMER_DATASET}"
        )

    customer = pd.read_parquet(
        CUSTOMER_DATASET
    )

    missing = [
        column
        for column in REQUIRED_CLV_COLUMNS
        if column not in customer.columns
    ]

    if missing:
        raise ValueError(
            "Customer CLV dataset is missing columns: "
            f"{missing}"
        )

    if customer.empty:
        raise ValueError(
            "Customer CLV dataset is empty."
        )

    if customer["customer_id"].duplicated().any():
        raise ValueError(
            "Customer CLV dataset contains duplicate "
            "customer_id values."
        )

    if customer["customer_id"].isna().any():
        raise ValueError(
            "Customer CLV dataset contains null customer IDs."
        )

    return customer


def load_rfm_data() -> pd.DataFrame:
    """Build the customer-level RFM dataset."""

    if not SALES_DATASET.exists():
        raise FileNotFoundError(
            f"Sales dataset not found: "
            f"{SALES_DATASET}"
        )

    if not CUSTOMER_MASTER_DATASET.exists():
        raise FileNotFoundError(
            f"Customer master dataset not found: "
            f"{CUSTOMER_MASTER_DATASET}"
        )

    sales = pd.read_parquet(
        SALES_DATASET
    )

    customers = pd.read_parquet(
        CUSTOMER_MASTER_DATASET
    )

    required_sales = {
        "transaction_key",
        "transaction_date",
        "customer_id",
        "net_sales",
    }

    required_customers = {
        "customer_id",
        "customer_name",
    }

    missing_sales = (
        required_sales
        - set(sales.columns)
    )

    missing_customers = (
        required_customers
        - set(customers.columns)
    )

    if missing_sales:
        raise ValueError(
            "Sales dataset is missing columns: "
            f"{sorted(missing_sales)}"
        )

    if missing_customers:
        raise ValueError(
            "Customer master dataset is missing columns: "
            f"{sorted(missing_customers)}"
        )

    if customers["customer_id"].duplicated().any():
        raise ValueError(
            "Customer master contains duplicate "
            "customer_id values."
        )

    sales["transaction_date"] = pd.to_datetime(
        sales["transaction_date"]
    )

    sales = sales.merge(
        customers[
            [
                "customer_id",
                "customer_name",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    if sales["customer_name"].isna().any():
        raise ValueError(
            "Some sales records have no customer "
            "master mapping."
        )

    rfm = (
        sales.groupby(
            [
                "customer_id",
                "customer_name",
            ],
            as_index=False,
        )
        .agg(
            last_transaction=(
                "transaction_date",
                "max",
            ),
            frequency=(
                "transaction_key",
                "nunique",
            ),
            monetary=(
                "net_sales",
                "sum",
            ),
        )
    )

    rfm["recency"] = (
        SNAPSHOT_DATE
        - rfm["last_transaction"]
    ).dt.days

    rfm["r_score"] = pd.qcut(
        rfm["recency"].rank(
            method="first"
        ),
        5,
        labels=[5, 4, 3, 2, 1],
    ).astype(int)

    rfm["f_score"] = pd.qcut(
        rfm["frequency"].rank(
            method="first"
        ),
        5,
        labels=[1, 2, 3, 4, 5],
    ).astype(int)

    rfm["m_score"] = pd.qcut(
        rfm["monetary"].rank(
            method="first"
        ),
        5,
        labels=[1, 2, 3, 4, 5],
    ).astype(int)

    rfm["rfm_score"] = (
        rfm["r_score"].astype(str)
        + rfm["f_score"].astype(str)
        + rfm["m_score"].astype(str)
    )

    rfm["rfm_total"] = (
        rfm["r_score"]
        + rfm["f_score"]
        + rfm["m_score"]
    )

    rfm["segment"] = "Others"

    rfm.loc[
        (
            (rfm["r_score"] >= 4)
            & (rfm["f_score"] >= 4)
            & (rfm["m_score"] >= 4)
        ),
        "segment",
    ] = "Champions"

    rfm.loc[
        (
            (rfm["r_score"] >= 3)
            & (rfm["f_score"] >= 4)
            & (rfm["m_score"] >= 3)
        ),
        "segment",
    ] = "Loyal Customers"

    rfm.loc[
        (
            (rfm["r_score"] >= 4)
            & (rfm["f_score"] >= 2)
            & (rfm["m_score"] >= 2)
        ),
        "segment",
    ] = "Potential Loyalists"

    rfm.loc[
        (
            (rfm["r_score"] >= 3)
            & (rfm["f_score"] <= 2)
            & (rfm["m_score"] >= 3)
        ),
        "segment",
    ] = "Promising"

    rfm.loc[
        (
            (rfm["r_score"] <= 2)
            & (rfm["f_score"] >= 3)
            & (rfm["m_score"] >= 3)
        ),
        "segment",
    ] = "At Risk"

    rfm.loc[
        (
            (rfm["r_score"] <= 2)
            & (rfm["f_score"] <= 2)
            & (rfm["m_score"] >= 3)
        ),
        "segment",
    ] = "Need Attention"

    rfm.loc[
        (
            (rfm["r_score"] == 1)
            & (rfm["f_score"] <= 2)
            & (rfm["m_score"] <= 2)
        ),
        "segment",
    ] = "Lost Customers"

    return rfm[
        [
            "customer_id",
            "customer_name",
            "last_transaction",
            "recency",
            "frequency",
            "monetary",
            "r_score",
            "f_score",
            "m_score",
            "rfm_score",
            "rfm_total",
            "segment",
        ]
    ]


def classify_opportunity(
    clv_tier: str,
    rfm_segment: str,
) -> tuple[str, str]:
    """Classify customer-value management opportunity."""

    high_value = clv_tier in {
        "Platinum",
        "Gold",
    }

    mid_value = clv_tier in {
        "Gold",
        "Silver",
    }

    low_value = clv_tier in {
        "Silver",
        "Bronze",
    }

    if high_value and rfm_segment in {
        "Champions",
        "Loyal Customers",
    }:
        return (
            "Protect",
            "High CLV with healthy customer engagement.",
        )

    if high_value and rfm_segment in {
        "At Risk",
        "Need Attention",
    }:
        return (
            "Rescue",
            "High CLV combined with declining engagement.",
        )

    if mid_value and rfm_segment in {
        "Potential Loyalists",
        "Promising",
    }:
        return (
            "Develop",
            "Customer shows behavioral potential for higher value.",
        )

    if low_value and rfm_segment in {
        "Potential Loyalists",
        "Promising",
    }:
        return (
            "Grow",
            "Emerging behavior provides room for value development.",
        )

    if low_value and rfm_segment in {
        "Need Attention",
        "Others",
    }:
        return (
            "Monitor",
            "Lower current value requires selective engagement.",
        )

    if low_value and rfm_segment == "Lost Customers":
        return (
            "Win-back",
            "Low current value combined with severe inactivity.",
        )

    return (
        "Review",
        "Customer requires individual evaluation.",
    )


def build_opportunity_dataset(
    clv: pd.DataFrame,
    rfm: pd.DataFrame,
) -> pd.DataFrame:
    """Merge CLV and RFM into the opportunity dataset."""

    if clv["customer_id"].nunique() != len(clv):
        raise ValueError(
            "CLV customer IDs are not unique."
        )

    if rfm["customer_id"].nunique() != len(rfm):
        raise ValueError(
            "RFM customer IDs are not unique."
        )

    result = clv.merge(
        rfm,
        on="customer_id",
        how="inner",
        validate="one_to_one",
    )

    if len(result) != len(clv):
        raise ValueError(
            "CLV/RFM merge did not preserve all customers."
        )

    result[
        [
            "opportunity",
            "priority_rationale",
        ]
    ] = result.apply(
        lambda row: pd.Series(
            classify_opportunity(
                row["clv_tier"],
                row["segment"],
            )
        ),
        axis=1,
    )

    result["opportunity_priority"] = (
        result["opportunity"]
        .map(
            {
                "Rescue": 1,
                "Protect": 2,
                "Develop": 3,
                "Grow": 4,
                "Win-back": 5,
                "Monitor": 6,
                "Review": 7,
            }
        )
    )

    result = result.sort_values(
        [
            "opportunity_priority",
            "annualized_clv",
        ],
        ascending=[
            True,
            False,
        ],
    ).reset_index(drop=True)

    return result


def validate_opportunity_dataset(
    result: pd.DataFrame,
) -> bool:
    """Validate the final opportunity dataset."""

    required_columns = {
        "customer_id",
        "customer_name",
        "annualized_clv",
        "historical_clv",
        "clv_tier",
        "segment",
        "opportunity",
        "opportunity_priority",
        "priority_rationale",
    }

    missing = (
        required_columns
        - set(result.columns)
    )

    if missing:
        raise ValueError(
            "Opportunity dataset is missing columns: "
            f"{sorted(missing)}"
        )

    unique_ids = (
        result["customer_id"].is_unique
    )

    no_null_opportunities = (
        result["opportunity"].notna().all()
    )

    valid_opportunities = result[
        "opportunity"
    ].isin(
        {
            "Protect",
            "Rescue",
            "Develop",
            "Grow",
            "Win-back",
            "Monitor",
            "Review",
        }
    ).all()

    passed = (
        unique_ids
        and no_null_opportunities
        and valid_opportunities
    )

    print()
    print("=" * 80)
    print("M12.2.3-C VALIDATION")
    print("=" * 80)

    print(
        f"Customers              : "
        f"{len(result):,}"
    )

    print(
        f"Unique customer IDs    : "
        f"{'PASS' if unique_ids else 'REVIEW'}"
    )

    print(
        f"Opportunity coverage   : "
        f"{'PASS' if no_null_opportunities else 'REVIEW'}"
    )

    print(
        f"Valid classifications  : "
        f"{'PASS' if valid_opportunities else 'REVIEW'}"
    )

    print(
        f"Validation             : "
        f"{'PASS' if passed else 'REVIEW'}"
    )

    return passed


def print_summary(
    result: pd.DataFrame,
) -> None:
    """Print opportunity summary."""

    summary = (
        result.groupby(
            "opportunity"
        )
        .agg(
            customers=(
                "customer_id",
                "count",
            ),
            revenue=(
                "revenue",
                "sum",
            ),
            gross_profit=(
                "gross_profit",
                "sum",
            ),
            annualized_clv=(
                "annualized_clv",
                "sum",
            ),
        )
        .reset_index()
    )

    summary = summary.sort_values(
        "annualized_clv",
        ascending=False,
    )

    print()
    print("=" * 80)
    print(
        "MAYASARI BAKERY — "
        "M12.2.3 CUSTOMER OPPORTUNITY"
    )
    print("=" * 80)

    print()
    print("OPPORTUNITY SUMMARY")
    print("-" * 80)

    display = summary.copy()

    display["revenue"] = display[
        "revenue"
    ].map(
        lambda value: (
            f"Rp {value:,.0f}"
        )
    )

    display["gross_profit"] = display[
        "gross_profit"
    ].map(
        lambda value: (
            f"Rp {value:,.0f}"
        )
    )

    display["annualized_clv"] = display[
        "annualized_clv"
    ].map(
        lambda value: (
            f"Rp {value:,.0f}"
        )
    )

    print(
        display.to_string(
            index=False
        )
    )


def generate_opportunity_dataset() -> pd.DataFrame:
    """Generate, validate, and persist opportunity dataset."""

    clv = load_clv_data()

    clv = clv.copy()

    clv["clv_tier"] = pd.qcut(
        clv["annualized_clv"].rank(
            method="first"
        ),
        q=4,
        labels=[
            "Bronze",
            "Silver",
            "Gold",
            "Platinum",
        ],
    ).astype(str)

    rfm = load_rfm_data()

    result = build_opportunity_dataset(
        clv,
        rfm,
    )

    validation = validate_opportunity_dataset(
        result
    )

    if not validation:
        raise ValueError(
            "M12.2.3 opportunity validation failed."
        )

    OUTPUT_DATASET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_parquet(
        OUTPUT_DATASET,
        index=False,
    )

    print_summary(result)

    print()
    print(
        "Generated dataset      : "
        f"{OUTPUT_DATASET.relative_to(PROJECT_ROOT)}"
    )

    return result


def main() -> None:
    """Run M12.2.3 customer opportunity analysis."""

    generate_opportunity_dataset()


if __name__ == "__main__":
    main()