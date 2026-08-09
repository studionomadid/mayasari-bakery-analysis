import pandas as pd

from src.contracts.paths import SALES_DATA


def load_data() -> pd.DataFrame:
    """Load prepared sales data."""
    if not SALES_DATA.exists():
        raise FileNotFoundError(
            f"Processed sales data not found: {SALES_DATA}"
        )

    return pd.read_parquet(SALES_DATA)


def build_monthly_trend_analysis(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """Build monthly trend and rolling performance metrics."""

    monthly = (
        sales.assign(
            month=sales["transaction_date"].dt.to_period("M")
        )
        .groupby("month", as_index=False)
        .agg(
            transactions=("transaction_key", "nunique"),
            units_sold=("quantity", "sum"),
            net_sales=("net_sales", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
    )

    monthly["average_transaction_value"] = (
        monthly["net_sales"]
        / monthly["transactions"].replace(0, pd.NA)
    )

    monthly["units_per_transaction"] = (
        monthly["units_sold"]
        / monthly["transactions"].replace(0, pd.NA)
    )

    monthly["revenue_rolling_3m"] = (
        monthly["net_sales"]
        .rolling(3, min_periods=1)
        .mean()
    )

    monthly["profit_rolling_3m"] = (
        monthly["gross_profit"]
        .rolling(3, min_periods=1)
        .mean()
    )

    monthly["transactions_rolling_3m"] = (
        monthly["transactions"]
        .rolling(3, min_periods=1)
        .mean()
    )

    monthly["units_rolling_3m"] = (
        monthly["units_sold"]
        .rolling(3, min_periods=1)
        .mean()
    )

    monthly["revenue_mom_pct"] = (
        monthly["net_sales"]
        .pct_change()
        * 100
    )

    monthly["transactions_mom_pct"] = (
        monthly["transactions"]
        .pct_change()
        * 100
    )

    monthly["atv_mom_pct"] = (
        monthly["average_transaction_value"]
        .pct_change()
        * 100
    )

    return monthly


def build_seasonality_analysis(
    monthly: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate monthly seasonal indices."""

    average_monthly_revenue = (
        monthly["net_sales"].mean()
    )

    seasonality = monthly[
        [
            "month",
            "net_sales",
            "transactions",
            "units_sold",
            "average_transaction_value",
        ]
    ].copy()

    seasonality["seasonal_index"] = (
        seasonality["net_sales"]
        / average_monthly_revenue
        * 100
    )

    seasonality["revenue_vs_average_pct"] = (
        seasonality["net_sales"]
        / average_monthly_revenue
        * 100
        - 100
    )

    seasonality["season"] = seasonality[
        "seasonal_index"
    ].apply(
        classify_season
    )

    return seasonality


def classify_season(
    seasonal_index: float,
) -> str:
    """Classify monthly demand based on seasonal index."""

    if seasonal_index >= 110:
        return "Peak"

    if seasonal_index >= 100:
        return "Above Average"

    if seasonal_index >= 90:
        return "Below Average"

    return "Low"


def build_revenue_driver_analysis(
    monthly: pd.DataFrame,
) -> pd.DataFrame:
    """Identify the primary driver of monthly revenue movement."""

    analysis = monthly[
        [
            "month",
            "net_sales",
            "transactions",
            "average_transaction_value",
            "units_sold",
            "units_per_transaction",
            "revenue_mom_pct",
            "transactions_mom_pct",
            "atv_mom_pct",
        ]
    ].copy()

    analysis["primary_revenue_driver"] = (
        analysis.apply(
            classify_revenue_driver,
            axis=1,
        )
    )

    return analysis


def classify_revenue_driver(
    row: pd.Series,
) -> str:
    """Classify revenue growth driver."""

    revenue_change = row["revenue_mom_pct"]

    if pd.isna(revenue_change):
        return "Baseline"

    transaction_change = row[
        "transactions_mom_pct"
    ]

    atv_change = row["atv_mom_pct"]

    if revenue_change > 0:
        if (
            transaction_change > 0
            and atv_change > 0
        ):
            return "Transactions + ATV"

        if transaction_change > atv_change:
            return "Transactions"

        if atv_change > transaction_change:
            return "Average Transaction Value"

        return "Mixed Positive"

    if revenue_change < 0:
        if (
            transaction_change < 0
            and atv_change < 0
        ):
            return "Transactions + ATV Decline"

        if transaction_change < atv_change:
            return "Transactions Decline"

        if atv_change < transaction_change:
            return "Average Transaction Value Decline"

        return "Mixed Negative"

    return "Stable"


def print_trend_analysis(
    monthly: pd.DataFrame,
) -> None:
    """Print monthly trend analysis."""

    print()
    print("=" * 100)
    print("MONTHLY TREND ANALYSIS")
    print("=" * 100)

    display = monthly[
        [
            "month",
            "net_sales",
            "gross_profit",
            "transactions",
            "units_sold",
            "average_transaction_value",
            "revenue_rolling_3m",
            "profit_rolling_3m",
        ]
    ].copy()

    display["month"] = display["month"].astype(str)

    currency_columns = [
        "net_sales",
        "gross_profit",
        "average_transaction_value",
        "revenue_rolling_3m",
        "profit_rolling_3m",
    ]

    for column in currency_columns:
        display[column] = display[column].map(
            lambda value: f"Rp {value:,.0f}"
        )

    print()
    print(
        display.to_string(
            index=False
        )
    )


def print_seasonality_analysis(
    seasonality: pd.DataFrame,
) -> None:
    """Print seasonal performance."""

    print()
    print("=" * 100)
    print("SEASONALITY ANALYSIS")
    print("=" * 100)

    display = seasonality[
        [
            "month",
            "net_sales",
            "seasonal_index",
            "revenue_vs_average_pct",
            "season",
        ]
    ].copy()

    display["month"] = display[
        "month"
    ].astype(str)

    display["net_sales"] = display[
        "net_sales"
    ].map(
        lambda value: f"Rp {value:,.0f}"
    )

    display["seasonal_index"] = display[
        "seasonal_index"
    ].map(
        lambda value: f"{value:.2f}"
    )

    display["revenue_vs_average_pct"] = display[
        "revenue_vs_average_pct"
    ].map(
        lambda value: f"{value:+.2f}%"
    )

    print()
    print(
        display.to_string(
            index=False
        )
    )


def print_revenue_drivers(
    drivers: pd.DataFrame,
) -> None:
    """Print monthly revenue drivers."""

    print()
    print("=" * 100)
    print("REVENUE DRIVER ANALYSIS")
    print("=" * 100)

    display = drivers[
        [
            "month",
            "revenue_mom_pct",
            "transactions_mom_pct",
            "atv_mom_pct",
            "primary_revenue_driver",
        ]
    ].copy()

    display["month"] = display[
        "month"
    ].astype(str)

    for column in [
        "revenue_mom_pct",
        "transactions_mom_pct",
        "atv_mom_pct",
    ]:
        display[column] = display[column].map(
            lambda value: (
                f"{value:+.2f}%"
                if pd.notna(value)
                else "N/A"
            )
        )

    print()
    print(
        display.to_string(
            index=False
        )
    )


def print_peak_low_periods(
    monthly: pd.DataFrame,
    seasonality: pd.DataFrame,
) -> None:
    """Print peak and low business periods."""

    print()
    print("=" * 100)
    print("PEAK & LOW PERIODS")
    print("=" * 100)

    best_revenue = monthly.loc[
        monthly["net_sales"].idxmax()
    ]

    worst_revenue = monthly.loc[
        monthly["net_sales"].idxmin()
    ]

    best_transactions = monthly.loc[
        monthly["transactions"].idxmax()
    ]

    worst_transactions = monthly.loc[
        monthly["transactions"].idxmin()
    ]

    best_atv = monthly.loc[
        monthly["average_transaction_value"].idxmax()
    ]

    worst_atv = monthly.loc[
        monthly["average_transaction_value"].idxmin()
    ]

    peak_season = seasonality.loc[
        seasonality["seasonal_index"].idxmax()
    ]

    low_season = seasonality.loc[
        seasonality["seasonal_index"].idxmin()
    ]

    print()
    print("REVENUE")
    print("-" * 100)

    print(
        f"Best  : {best_revenue['month']} | "
        f"Rp {best_revenue['net_sales']:,.0f}"
    )

    print(
        f"Worst : {worst_revenue['month']} | "
        f"Rp {worst_revenue['net_sales']:,.0f}"
    )

    print()
    print("TRANSACTIONS")
    print("-" * 100)

    print(
        f"Highest: {best_transactions['month']} | "
        f"{best_transactions['transactions']:,}"
    )

    print(
        f"Lowest : {worst_transactions['month']} | "
        f"{worst_transactions['transactions']:,}"
    )

    print()
    print("AVERAGE TRANSACTION VALUE")
    print("-" * 100)

    print(
        f"Highest: {best_atv['month']} | "
        f"Rp {best_atv['average_transaction_value']:,.0f}"
    )

    print(
        f"Lowest : {worst_atv['month']} | "
        f"Rp {worst_atv['average_transaction_value']:,.0f}"
    )

    print()
    print("SEASONAL INDEX")
    print("-" * 100)

    print(
        f"Peak : {peak_season['month']} | "
        f"{peak_season['seasonal_index']:.2f}"
    )

    print(
        f"Low  : {low_season['month']} | "
        f"{low_season['seasonal_index']:.2f}"
    )


def print_business_insights(
    monthly: pd.DataFrame,
    seasonality: pd.DataFrame,
    drivers: pd.DataFrame,
) -> None:
    """Print concise business insights."""

    print()
    print("=" * 100)
    print("BUSINESS INSIGHTS")
    print("=" * 100)

    best_month = monthly.loc[
        monthly["net_sales"].idxmax()
    ]

    worst_month = monthly.loc[
        monthly["net_sales"].idxmin()
    ]

    peak_month = seasonality.loc[
        seasonality["seasonal_index"].idxmax()
    ]

    low_month = seasonality.loc[
        seasonality["seasonal_index"].idxmin()
    ]

    growth_months = drivers[
        drivers["revenue_mom_pct"] > 0
    ]

    decline_months = drivers[
        drivers["revenue_mom_pct"] < 0
    ]

    print()
    print(
        f"1. Revenue peaked in "
        f"{best_month['month']} at "
        f"Rp {best_month['net_sales']:,.0f}."
    )

    print(
        f"2. Revenue was lowest in "
        f"{worst_month['month']} at "
        f"Rp {worst_month['net_sales']:,.0f}."
    )

    print(
        f"3. Strongest seasonal period was "
        f"{peak_month['month']} with a "
        f"{peak_month['seasonal_index']:.2f} "
        f"seasonal index."
    )

    print(
        f"4. Weakest seasonal period was "
        f"{low_month['month']} with a "
        f"{low_month['seasonal_index']:.2f} "
        f"seasonal index."
    )

    print(
        f"5. Revenue increased in "
        f"{len(growth_months)} months and "
        f"declined in "
        f"{len(decline_months)} months "
        f"on a month-over-month basis."
    )


def validate_totals(
    sales: pd.DataFrame,
    monthly: pd.DataFrame,
) -> bool:
    """Validate monthly aggregation against source sales."""

    source_metrics = {
        "transactions": sales[
            "transaction_key"
        ].nunique(),
        "units_sold": sales[
            "quantity"
        ].sum(),
        "net_sales": sales[
            "net_sales"
        ].sum(),
        "gross_profit": sales[
            "gross_profit"
        ].sum(),
    }

    monthly_metrics = {
        "transactions": monthly[
            "transactions"
        ].sum(),
        "units_sold": monthly[
            "units_sold"
        ].sum(),
        "net_sales": monthly[
            "net_sales"
        ].sum(),
        "gross_profit": monthly[
            "gross_profit"
        ].sum(),
    }

    print()
    print("=" * 100)
    print("TREND AGGREGATION VALIDATION")
    print("=" * 100)

    all_pass = True

    for metric, source_value in source_metrics.items():
        monthly_value = monthly_metrics[
            metric
        ]

        passed = source_value == monthly_value

        if not passed:
            all_pass = False

        print(
            f"{metric:<15} "
            f"Source: {source_value:>15,.0f} | "
            f"Monthly: {monthly_value:>15,.0f} | "
            f"{'PASS' if passed else 'REVIEW'}"
        )

    return all_pass


def main() -> None:
    """Run trend and seasonality analysis."""

    print("=" * 100)
    print("MAYASARI BAKERY TREND & SEASONALITY ANALYSIS")
    print("=" * 100)

    sales = load_data()

    monthly = build_monthly_trend_analysis(
        sales
    )

    seasonality = build_seasonality_analysis(
        monthly
    )

    drivers = build_revenue_driver_analysis(
        monthly
    )

    print_trend_analysis(
        monthly
    )

    print_seasonality_analysis(
        seasonality
    )

    print_revenue_drivers(
        drivers
    )

    print_peak_low_periods(
        monthly,
        seasonality,
    )

    print_business_insights(
        monthly,
        seasonality,
        drivers,
    )

    validation_pass = validate_totals(
        sales,
        monthly,
    )

    print()
    print("=" * 100)

    if validation_pass:
        print("TREND & SEASONALITY ANALYSIS STATUS: PASS")
    else:
        print("TREND & SEASONALITY ANALYSIS STATUS: REVIEW")

    print("=" * 100)


if __name__ == "__main__":
    main()
