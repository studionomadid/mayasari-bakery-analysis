from pathlib import Path

import pandas as pd


SALES_DATA = Path("data/processed/sales.parquet")
MONTHS_IN_YEAR = 12


def load_sales_data() -> pd.DataFrame:
    """Load and validate prepared sales data."""

    if not SALES_DATA.exists():
        raise FileNotFoundError(
            f"Sales data not found: {SALES_DATA}"
        )

    sales = pd.read_parquet(SALES_DATA)

    required_columns = {
        "transaction_key",
        "transaction_date",
        "customer_id",
        "net_sales",
        "gross_profit",
    }

    missing_columns = (
        required_columns - set(sales.columns)
    )

    if missing_columns:
        raise ValueError(
            "Sales dataset is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    sales["transaction_date"] = pd.to_datetime(
        sales["transaction_date"]
    )

    if sales["transaction_date"].isna().any():
        raise ValueError(
            "Sales dataset contains invalid transaction dates."
        )

    if sales["customer_id"].isna().any():
        raise ValueError(
            "Sales dataset contains null customer_id values."
        )

    sales["sales_month"] = (
        sales["transaction_date"]
        .dt.to_period("M")
    )

    return sales


def build_customer_value(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """Build customer-level CLV metrics."""

    customer_value = (
        sales.groupby("customer_id")
        .agg(
            transactions=(
                "transaction_key",
                "nunique",
            ),
            net_sales=(
                "net_sales",
                "sum",
            ),
            gross_profit=(
                "gross_profit",
                "sum",
            ),
            active_months=(
                "sales_month",
                "nunique",
            ),
            first_purchase=(
                "transaction_date",
                "min",
            ),
            last_purchase=(
                "transaction_date",
                "max",
            ),
        )
        .reset_index()
    )

    customer_value["average_transaction_value"] = (
        customer_value["net_sales"]
        / customer_value["transactions"]
    )

    customer_value["gross_margin_pct"] = (
        customer_value["gross_profit"]
        / customer_value["net_sales"]
        * 100
    )

    customer_value["historical_clv"] = (
        customer_value["gross_profit"]
    )

    customer_value["annualized_clv"] = (
        customer_value["gross_profit"]
        / customer_value["active_months"]
        * MONTHS_IN_YEAR
    )

    customer_value["observed_lifetime_days"] = (
        customer_value["last_purchase"]
        - customer_value["first_purchase"]
    ).dt.days

    return customer_value


def assign_clv_tiers(
    customer_value: pd.DataFrame,
) -> pd.DataFrame:
    """Assign customer value tiers using CLV quartiles."""

    result = customer_value.copy()

    q1 = result["historical_clv"].quantile(0.25)
    q2 = result["historical_clv"].quantile(0.50)
    q3 = result["historical_clv"].quantile(0.75)

    result["clv_tier"] = "Low Value"

    result.loc[
        result["historical_clv"] > q1,
        "clv_tier",
    ] = "Medium Value"

    result.loc[
        result["historical_clv"] > q2,
        "clv_tier",
    ] = "High Value"

    result.loc[
        result["historical_clv"] > q3,
        "clv_tier",
    ] = "Top Value"

    return result


def build_tier_summary(
    customer_value: pd.DataFrame,
) -> pd.DataFrame:
    """Build concise CLV tier summary."""

    summary = (
        customer_value.groupby("clv_tier")
        .agg(
            customers=(
                "customer_id",
                "count",
            ),
            gross_profit=(
                "historical_clv",
                "sum",
            ),
            annualized_clv=(
                "annualized_clv",
                "sum",
            ),
            avg_clv=(
                "historical_clv",
                "mean",
            ),
        )
        .reset_index()
    )

    total_profit = summary["gross_profit"].sum()

    summary["profit_contribution_pct"] = (
        summary["gross_profit"]
        / total_profit
        * 100
    )

    tier_order = [
        "Top Value",
        "High Value",
        "Medium Value",
        "Low Value",
    ]

    summary["clv_tier"] = pd.Categorical(
        summary["clv_tier"],
        categories=tier_order,
        ordered=True,
    )

    return (
        summary
        .sort_values("clv_tier")
        .reset_index(drop=True)
    )


def build_insights(
    customer_value: pd.DataFrame,
    tier_summary: pd.DataFrame,
) -> list[str]:
    """Generate concise CLV business insights."""

    highest = customer_value.loc[
        customer_value["historical_clv"].idxmax()
    ]

    highest_annualized = customer_value.loc[
        customer_value["annualized_clv"].idxmax()
    ]

    top_value = tier_summary[
        tier_summary["clv_tier"] == "Top Value"
    ]

    insights = [
        (
            f"Highest historical CLV: "
            f"{highest['customer_id']} "
            f"(Rp {highest['historical_clv']:,.0f})."
        ),
        (
            f"Highest annualized CLV run-rate: "
            f"{highest_annualized['customer_id']} "
            f"(Rp "
            f"{highest_annualized['annualized_clv']:,.0f})."
        ),
    ]

    if not top_value.empty:
        row = top_value.iloc[0]

        insights.append(
            f"Top Value customers: "
            f"{int(row['customers']):,} "
            f"customers generating "
            f"Rp {row['gross_profit']:,.0f} "
            f"({row['profit_contribution_pct']:.2f}% "
            f"of total gross profit)."
        )

    return insights


def validate_clv(
    sales: pd.DataFrame,
    customer_value: pd.DataFrame,
) -> bool:
    """Validate customer CLV aggregation."""

    source_customers = (
        sales["customer_id"].nunique()
    )

    calculated_customers = (
        customer_value["customer_id"].nunique()
    )

    source_profit = sales["gross_profit"].sum()

    calculated_profit = (
        customer_value["historical_clv"].sum()
    )

    unique_customer_ids = (
        customer_value["customer_id"].is_unique
    )

    no_null_clv = (
        customer_value["historical_clv"]
        .notna()
        .all()
    )

    profit_reconciles = (
        source_profit == calculated_profit
    )

    passed = all(
        [
            source_customers == calculated_customers,
            unique_customer_ids,
            no_null_clv,
            profit_reconciles,
        ]
    )

    print()
    print("=" * 80)
    print("M12 VALIDATION")
    print("=" * 80)

    print(
        f"Source customers      : "
        f"{source_customers:,}"
    )

    print(
        f"Calculated customers  : "
        f"{calculated_customers:,}"
    )

    print(
        f"Unique customer IDs   : "
        f"{'PASS' if unique_customer_ids else 'REVIEW'}"
    )

    print(
        f"CLV null check        : "
        f"{'PASS' if no_null_clv else 'REVIEW'}"
    )

    print(
        f"Profit reconciliation : "
        f"{'PASS' if profit_reconciles else 'REVIEW'}"
    )

    print(
        f"Validation            : "
        f"{'PASS' if passed else 'REVIEW'}"
    )

    return passed


def print_summary(
    customer_value: pd.DataFrame,
    tier_summary: pd.DataFrame,
    insights: list[str],
) -> None:
    """Print compact M12 output."""

    print("=" * 80)
    print("MAYASARI BAKERY — M12 CUSTOMER LIFETIME VALUE")
    print("=" * 80)

    print(
        f"Customers : "
        f"{len(customer_value):,}"
    )

    print(
        "CLV basis : Historical gross profit"
    )

    print(
        "Run-rate  : Gross profit per active month × 12"
    )

    print()
    print("CLV TIER SUMMARY")
    print("-" * 80)

    display = tier_summary[
        [
            "clv_tier",
            "customers",
            "gross_profit",
            "profit_contribution_pct",
            "avg_clv",
        ]
    ].copy()

    display["gross_profit"] = (
        display["gross_profit"]
        .map(lambda value: f"Rp {value:,.0f}")
    )

    display["profit_contribution_pct"] = (
        display["profit_contribution_pct"]
        .map(lambda value: f"{value:.1f}%")
    )

    display["avg_clv"] = (
        display["avg_clv"]
        .map(lambda value: f"Rp {value:,.0f}")
    )

    print(
        display.to_string(index=False)
    )

    print()
    print("TOP 5 CUSTOMERS BY HISTORICAL CLV")
    print("-" * 80)

    top = (
        customer_value
        .sort_values(
            "historical_clv",
            ascending=False,
        )
        .head(5)
        [
            [
                "customer_id",
                "transactions",
                "net_sales",
                "historical_clv",
                "annualized_clv",
                "gross_margin_pct",
            ]
        ]
        .copy()
    )

    for column in [
        "net_sales",
        "historical_clv",
        "annualized_clv",
    ]:
        top[column] = top[column].map(
            lambda value: f"Rp {value:,.0f}"
        )

    top["gross_margin_pct"] = (
        top["gross_margin_pct"]
        .map(lambda value: f"{value:.1f}%")
    )

    print(
        top.to_string(index=False)
    )

    print()
    print("KEY INSIGHTS")
    print("-" * 80)

    for index, insight in enumerate(
        insights,
        start=1,
    ):
        print(
            f"{index}. {insight}"
        )


def main() -> None:
    """Run M12 customer lifetime value analysis."""

    sales = load_sales_data()

    customer_value = build_customer_value(
        sales
    )

    customer_value = assign_clv_tiers(
        customer_value
    )

    tier_summary = build_tier_summary(
        customer_value
    )

    insights = build_insights(
        customer_value,
        tier_summary,
    )

    print_summary(
        customer_value,
        tier_summary,
        insights,
    )

    validation = validate_clv(
        sales,
        customer_value,
    )

    print()
    print("=" * 80)
    print(
        "M12 CUSTOMER LIFETIME VALUE STATUS: "
        f"{'PASS' if validation else 'REVIEW'}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
