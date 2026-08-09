import pandas as pd

from src.contracts.paths import CUSTOMERS_DATA, SALES_DATA

CUSTOMER_DATA = CUSTOMERS_DATA


SNAPSHOT_DATE = pd.Timestamp("2025-12-31")


def load_customer_data() -> pd.DataFrame:
    """Load sales and customer master data."""

    if not SALES_DATA.exists():
        raise FileNotFoundError(
            f"Sales data not found: {SALES_DATA}"
        )

    if not CUSTOMER_DATA.exists():
        raise FileNotFoundError(
            f"Customer data not found: {CUSTOMER_DATA}"
        )

    sales = pd.read_parquet(SALES_DATA)
    customers = pd.read_parquet(CUSTOMER_DATA)

    required_sales = {
        "transaction_key",
        "transaction_date",
        "customer_id",
        "net_sales",
    }

    required_customers = {
        "customer_id",
        "customer_name",
        "customer_segment",
    }

    missing_sales = required_sales - set(sales.columns)
    missing_customers = required_customers - set(customers.columns)

    if missing_sales:
        raise ValueError(
            "Sales dataset is missing columns: "
            f"{sorted(missing_sales)}"
        )

    if missing_customers:
        raise ValueError(
            "Customer dataset is missing columns: "
            f"{sorted(missing_customers)}"
        )

    if customers["customer_id"].duplicated().any():
        raise ValueError(
            "Customer dataset contains duplicate customer_id values."
        )

    sales["transaction_date"] = pd.to_datetime(
        sales["transaction_date"]
    )

    sales = sales.merge(
        customers[
            [
                "customer_id",
                "customer_name",
                "customer_segment",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    if sales["customer_name"].isna().any():
        raise ValueError(
            "Some sales records have no customer master mapping."
        )

    return sales


def build_rfm(sales: pd.DataFrame) -> pd.DataFrame:
    """Build customer-level RFM metrics."""

    rfm = (
        sales.groupby(
            [
                "customer_id",
                "customer_name",
                "customer_segment",
            ],
            as_index=False,
        )
        .agg(
            last_transaction=("transaction_date", "max"),
            frequency=("transaction_key", "nunique"),
            monetary=("net_sales", "sum"),
        )
    )

    rfm["recency"] = (
        SNAPSHOT_DATE - rfm["last_transaction"]
    ).dt.days

    return rfm[
        [
            "customer_id",
            "customer_name",
            "customer_segment",
            "last_transaction",
            "recency",
            "frequency",
            "monetary",
        ]
    ]


def score_rfm(rfm: pd.DataFrame) -> pd.DataFrame:
    """Calculate 1-5 RFM scores."""

    result = rfm.copy()

    result["r_score"] = pd.qcut(
        result["recency"].rank(method="first"),
        5,
        labels=[5, 4, 3, 2, 1],
    ).astype(int)

    result["f_score"] = pd.qcut(
        result["frequency"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5],
    ).astype(int)

    result["m_score"] = pd.qcut(
        result["monetary"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5],
    ).astype(int)

    result["rfm_score"] = (
        result["r_score"].astype(str)
        + result["f_score"].astype(str)
        + result["m_score"].astype(str)
    )

    result["rfm_total"] = (
        result["r_score"]
        + result["f_score"]
        + result["m_score"]
    )

    return result


def assign_segments(rfm: pd.DataFrame) -> pd.DataFrame:
    """Assign business-oriented RFM customer segments."""

    result = rfm.copy()

    result["segment"] = "Others"

    result.loc[
        (
            (result["r_score"] >= 4)
            & (result["f_score"] >= 4)
            & (result["m_score"] >= 4)
        ),
        "segment",
    ] = "Champions"

    result.loc[
        (
            (result["r_score"] >= 3)
            & (result["f_score"] >= 4)
            & (result["m_score"] >= 3)
        ),
        "segment",
    ] = "Loyal Customers"

    result.loc[
        (
            (result["r_score"] >= 4)
            & (result["f_score"] >= 2)
            & (result["m_score"] >= 2)
        ),
        "segment",
    ] = "Potential Loyalists"

    result.loc[
        (
            (result["r_score"] >= 3)
            & (result["f_score"] <= 2)
            & (result["m_score"] >= 3)
        ),
        "segment",
    ] = "Promising"

    result.loc[
        (
            (result["r_score"] <= 2)
            & (result["f_score"] >= 3)
            & (result["m_score"] >= 3)
        ),
        "segment",
    ] = "At Risk"

    result.loc[
        (
            (result["r_score"] <= 2)
            & (result["f_score"] <= 2)
            & (result["m_score"] >= 3)
        ),
        "segment",
    ] = "Need Attention"

    result.loc[
        (
            (result["r_score"] == 1)
            & (result["f_score"] <= 2)
            & (result["m_score"] <= 2)
        ),
        "segment",
    ] = "Lost Customers"

    return result


def build_segment_summary(
    segmented: pd.DataFrame,
) -> pd.DataFrame:
    """Build concise segment-level summary."""

    summary = (
        segmented.groupby("segment")
        .agg(
            customers=("customer_id", "count"),
            revenue=("monetary", "sum"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
            avg_recency=("recency", "mean"),
        )
        .reset_index()
    )

    total_revenue = summary["revenue"].sum()

    summary["revenue_pct"] = (
        summary["revenue"]
        / total_revenue
        * 100
    )

    summary = summary.sort_values(
        "revenue",
        ascending=False,
    ).reset_index(drop=True)

    return summary


def build_insights(
    segmented: pd.DataFrame,
    summary: pd.DataFrame,
) -> list[str]:
    """Generate concise segmentation insights."""

    largest = summary.loc[
        summary["customers"].idxmax()
    ]

    highest_revenue = summary.loc[
        summary["revenue"].idxmax()
    ]

    champions = summary[
        summary["segment"] == "Champions"
    ]

    at_risk = summary[
        summary["segment"] == "At Risk"
    ]

    insights = [
        (
            f"Largest customer segment: "
            f"{largest['segment']} "
            f"({int(largest['customers']):,} customers)."
        ),
        (
            f"Highest revenue segment: "
            f"{highest_revenue['segment']} "
            f"(Rp {highest_revenue['revenue']:,.0f})."
        ),
    ]

    if not champions.empty:
        row = champions.iloc[0]
        insights.append(
            f"Champions contribute Rp "
            f"{row['revenue']:,.0f} "
            f"({row['revenue_pct']:.2f}% of revenue)."
        )

    if not at_risk.empty:
        row = at_risk.iloc[0]
        insights.append(
            f"At Risk customers: "
            f"{int(row['customers']):,} "
            f"customers worth Rp "
            f"{row['revenue']:,.0f}."
        )

    return insights


def validate_segmentation(
    rfm: pd.DataFrame,
    sales: pd.DataFrame,
) -> bool:
    """Validate RFM customer coverage."""

    expected_customers = sales["customer_id"].nunique()
    actual_customers = rfm["customer_id"].nunique()

    unique_ids = rfm["customer_id"].is_unique
    no_null_segments = rfm["segment"].notna().all()

    passed = (
        expected_customers == actual_customers
        and unique_ids
        and no_null_segments
    )

    print()
    print("=" * 80)
    print("M10 VALIDATION")
    print("=" * 80)
    print(
        f"Customers source : {expected_customers:,}"
    )
    print(
        f"Customers RFM    : {actual_customers:,}"
    )
    print(
        f"Unique customer  : "
        f"{'PASS' if unique_ids else 'REVIEW'}"
    )
    print(
        f"Segment coverage : "
        f"{'PASS' if no_null_segments else 'REVIEW'}"
    )
    print(
        f"Validation       : "
        f"{'PASS' if passed else 'REVIEW'}"
    )

    return passed


def print_summary(
    segmented: pd.DataFrame,
    summary: pd.DataFrame,
) -> None:
    """Print compact M10 output."""

    print()
    print("=" * 80)
    print("MAYASARI BAKERY — M10 CUSTOMER SEGMENTATION")
    print("=" * 80)

    print(
        f"Customers : {len(segmented):,}"
    )
    print(
        f"Snapshot  : {SNAPSHOT_DATE.date()}"
    )

    print()
    print("SEGMENT SUMMARY")
    print("-" * 80)

    display = summary[
        [
            "segment",
            "customers",
            "revenue",
            "revenue_pct",
            "avg_frequency",
            "avg_recency",
        ]
    ].copy()

    display["revenue"] = display["revenue"].map(
        lambda value: f"Rp {value:,.0f}"
    )

    display["revenue_pct"] = display[
        "revenue_pct"
    ].map(
        lambda value: f"{value:.2f}%"
    )

    display["avg_frequency"] = display[
        "avg_frequency"
    ].map(
        lambda value: f"{value:.1f}"
    )

    display["avg_recency"] = display[
        "avg_recency"
    ].map(
        lambda value: f"{value:.0f}d"
    )

    print(display.to_string(index=False))

    print()
    print("TOP 5 CUSTOMERS")
    print("-" * 80)

    top = (
        segmented
        .sort_values(
            "monetary",
            ascending=False,
        )
        .head(5)
        [
            [
                "customer_id",
                "customer_name",
                "segment",
                "frequency",
                "monetary",
                "recency",
            ]
        ]
        .copy()
    )

    top["monetary"] = top["monetary"].map(
        lambda value: f"Rp {value:,.0f}"
    )

    top["recency"] = top["recency"].map(
        lambda value: f"{value}d"
    )

    print(top.to_string(index=False))


def print_insights(
    insights: list[str],
) -> None:
    """Print concise business insights."""

    print()
    print("KEY INSIGHTS")
    print("-" * 80)

    for index, insight in enumerate(
        insights,
        start=1,
    ):
        print(f"{index}. {insight}")


def main() -> None:
    """Run M10 customer segmentation."""

    sales = load_customer_data()

    rfm = build_rfm(sales)
    rfm = score_rfm(rfm)
    segmented = assign_segments(rfm)

    summary = build_segment_summary(
        segmented
    )

    insights = build_insights(
        segmented,
        summary,
    )

    print_summary(
        segmented,
        summary,
    )

    print_insights(insights)

    validation = validate_segmentation(
        segmented,
        sales,
    )

    print()
    print("=" * 80)
    print(
        "M10 CUSTOMER SEGMENTATION STATUS: "
        f"{'PASS' if validation else 'REVIEW'}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
