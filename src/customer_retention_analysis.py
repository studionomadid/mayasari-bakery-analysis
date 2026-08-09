from pathlib import Path

import pandas as pd


SALES_DATA = Path("data/processed/sales.parquet")
SNAPSHOT_DATE = pd.Timestamp("2025-12-31")


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


def build_customer_monthly_activity(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """Build unique customer-month activity records."""

    activity = (
        sales[
            [
                "customer_id",
                "sales_month",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            [
                "customer_id",
                "sales_month",
            ]
        )
        .reset_index(drop=True)
    )

    return activity


def build_customer_cohorts(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """Assign each customer to their first purchase cohort."""

    cohorts = (
        sales.groupby("customer_id")
        .agg(
            first_purchase=(
                "transaction_date",
                "min",
            ),
        )
        .reset_index()
    )

    cohorts["cohort_month"] = (
        cohorts["first_purchase"]
        .dt.to_period("M")
    )

    return cohorts[
        [
            "customer_id",
            "first_purchase",
            "cohort_month",
        ]
    ]


def build_monthly_retention(
    activity: pd.DataFrame,
    cohorts: pd.DataFrame,
) -> pd.DataFrame:
    """Build monthly active, new, returning, and retention metrics."""

    monthly = (
        activity.groupby("sales_month")
        .agg(
            active_customers=(
                "customer_id",
                "nunique",
            ),
        )
        .reset_index()
    )

    monthly_new = (
        cohorts.groupby("cohort_month")
        .agg(
            new_customers=(
                "customer_id",
                "nunique",
            ),
        )
        .reset_index()
        .rename(
            columns={
                "cohort_month": "sales_month",
            }
        )
    )

    monthly = monthly.merge(
        monthly_new,
        on="sales_month",
        how="left",
    )

    monthly["new_customers"] = (
        monthly["new_customers"]
        .fillna(0)
        .astype(int)
    )

    monthly["returning_customers"] = (
        monthly["active_customers"]
        - monthly["new_customers"]
    )

    monthly["returning_rate_pct"] = (
        monthly["returning_customers"]
        / monthly["active_customers"]
        * 100
    )

    monthly = monthly.sort_values(
        "sales_month"
    ).reset_index(drop=True)

    return monthly


def build_cohort_retention(
    activity: pd.DataFrame,
    cohorts: pd.DataFrame,
) -> pd.DataFrame:
    """Build cohort retention counts and percentages."""

    cohort_activity = activity.merge(
        cohorts[
            [
                "customer_id",
                "cohort_month",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    cohort_activity["period_number"] = (
        cohort_activity["sales_month"]
        - cohort_activity["cohort_month"]
    ).apply(
        lambda value: value.n
    )

    cohort_counts = (
        cohort_activity.groupby(
            [
                "cohort_month",
                "period_number",
            ]
        )
        .agg(
            customers=(
                "customer_id",
                "nunique",
            )
        )
        .reset_index()
    )

    cohort_sizes = (
        cohort_counts[
            cohort_counts["period_number"] == 0
        ][
            [
                "cohort_month",
                "customers",
            ]
        ]
        .rename(
            columns={
                "customers": "cohort_size",
            }
        )
    )

    cohort_counts = cohort_counts.merge(
        cohort_sizes,
        on="cohort_month",
        how="left",
    )

    cohort_counts["retention_pct"] = (
        cohort_counts["customers"]
        / cohort_counts["cohort_size"]
        * 100
    )

    return cohort_counts.sort_values(
        [
            "cohort_month",
            "period_number",
        ]
    ).reset_index(drop=True)


def build_cohort_matrix(
    cohort_retention: pd.DataFrame,
) -> pd.DataFrame:
    """Build compact cohort retention percentage matrix."""

    matrix = cohort_retention.pivot(
        index="cohort_month",
        columns="period_number",
        values="retention_pct",
    )

    matrix = matrix.sort_index()

    matrix.columns = [
        f"M{int(column)}"
        for column in matrix.columns
    ]

    return matrix


def build_retention_insights(
    monthly: pd.DataFrame,
    cohort_retention: pd.DataFrame,
) -> list[str]:
    """Generate concise retention insights."""

    total_customers = (
        cohort_retention[
            cohort_retention["period_number"] == 0
        ]["customers"]
        .sum()
    )

    latest_month = monthly.iloc[-1]

    average_active = (
        monthly["active_customers"].mean()
    )

    average_returning_rate = (
        monthly["returning_rate_pct"].mean()
    )

    m1 = cohort_retention[
        cohort_retention["period_number"] == 1
    ]

    m1_retention = (
        m1["retention_pct"].mean()
        if not m1.empty
        else 0
    )

    latest_active = int(
        latest_month["active_customers"]
    )

    insights = [
        (
            f"Customer base: "
            f"{int(total_customers):,} unique customers."
        ),
        (
            f"Average monthly active customers: "
            f"{average_active:.0f}."
        ),
        (
            f"Average returning-customer rate: "
            f"{average_returning_rate:.2f}%."
        ),
        (
            f"Average M1 cohort retention: "
            f"{m1_retention:.2f}%."
        ),
        (
            f"Latest active customers "
            f"({latest_month['sales_month']}): "
            f"{latest_active:,}."
        ),
    ]

    return insights


def validate_retention_analysis(
    sales: pd.DataFrame,
    activity: pd.DataFrame,
    cohorts: pd.DataFrame,
    monthly: pd.DataFrame,
    cohort_retention: pd.DataFrame,
) -> bool:
    """Validate customer coverage and retention calculations."""

    source_customers = (
        sales["customer_id"].nunique()
    )

    cohort_customers = (
        cohorts["customer_id"].nunique()
    )

    activity_customers = (
        activity["customer_id"].nunique()
    )

    unique_cohort_ids = (
        cohorts["customer_id"].is_unique
    )

    no_null_cohorts = (
        cohorts["cohort_month"].notna().all()
    )

    valid_periods = (
        cohort_retention["period_number"] >= 0
    ).all()

    monthly_reconciliation = (
        monthly["active_customers"].sum()
        == activity.groupby("sales_month")
        ["customer_id"]
        .nunique()
        .sum()
    )

    passed = all(
        [
            source_customers == cohort_customers,
            source_customers == activity_customers,
            unique_cohort_ids,
            no_null_cohorts,
            valid_periods,
            monthly_reconciliation,
        ]
    )

    print()
    print("=" * 80)
    print("M11 VALIDATION")
    print("=" * 80)

    print(
        f"Source customers     : "
        f"{source_customers:,}"
    )

    print(
        f"Cohort customers     : "
        f"{cohort_customers:,}"
    )

    print(
        f"Activity customers   : "
        f"{activity_customers:,}"
    )

    print(
        f"Unique cohort IDs    : "
        f"{'PASS' if unique_cohort_ids else 'REVIEW'}"
    )

    print(
        f"Cohort coverage      : "
        f"{'PASS' if no_null_cohorts else 'REVIEW'}"
    )

    print(
        f"Period validity      : "
        f"{'PASS' if valid_periods else 'REVIEW'}"
    )

    print(
        f"Monthly reconciliation: "
        f"{'PASS' if monthly_reconciliation else 'REVIEW'}"
    )

    print(
        f"Validation           : "
        f"{'PASS' if passed else 'REVIEW'}"
    )

    return passed


def print_summary(
    monthly: pd.DataFrame,
    cohort_matrix: pd.DataFrame,
    insights: list[str],
) -> None:
    """Print compact M11 output."""

    print("=" * 80)
    print("MAYASARI BAKERY — M11 CUSTOMER RETENTION")
    print("=" * 80)

    print(
        f"Period   : "
        f"{monthly['sales_month'].min()} "
        f"to "
        f"{monthly['sales_month'].max()}"
    )

    print(
        f"Customers: "
        f"{monthly['active_customers'].max():,} "
        f"max monthly active"
    )

    print()
    print("MONTHLY RETENTION")
    print("-" * 80)

    display = monthly[
        [
            "sales_month",
            "active_customers",
            "new_customers",
            "returning_customers",
            "returning_rate_pct",
        ]
    ].copy()

    display["returning_rate_pct"] = (
        display["returning_rate_pct"]
        .map(lambda value: f"{value:.1f}%")
    )

    print(
        display.to_string(index=False)
    )

    print()
    print("COHORT RETENTION")
    print("-" * 80)

    matrix_display = cohort_matrix.copy()

    for column in matrix_display.columns:
        matrix_display[column] = (
            matrix_display[column]
            .map(
                lambda value: (
                    f"{value:.1f}%"
                    if pd.notna(value)
                    else "-"
                )
            )
        )

    matrix_display.index = [
        str(index)
        for index in matrix_display.index
    ]

    print(
        matrix_display.to_string()
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
    """Run M11 customer retention analysis."""

    sales = load_sales_data()

    activity = (
        build_customer_monthly_activity(
            sales
        )
    )

    cohorts = (
        build_customer_cohorts(
            sales
        )
    )

    monthly = (
        build_monthly_retention(
            activity,
            cohorts,
        )
    )

    cohort_retention = (
        build_cohort_retention(
            activity,
            cohorts,
        )
    )

    cohort_matrix = (
        build_cohort_matrix(
            cohort_retention
        )
    )

    insights = (
        build_retention_insights(
            monthly,
            cohort_retention,
        )
    )

    print_summary(
        monthly,
        cohort_matrix,
        insights,
    )

    validation = (
        validate_retention_analysis(
            sales,
            activity,
            cohorts,
            monthly,
            cohort_retention,
        )
    )

    print()
    print("=" * 80)
    print(
        "M11 CUSTOMER RETENTION STATUS: "
        f"{'PASS' if validation else 'REVIEW'}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
