from pathlib import Path

import pandas as pd


SALES_DATA = Path("data/processed/sales.parquet")
EXPENSE_DATA = Path("data/processed/expenses.parquet")
KPI_DATA = Path("data/processed/monthly_kpi.parquet")


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load prepared sales and expense data."""

    if not SALES_DATA.exists():
        raise FileNotFoundError(
            f"Processed sales data not found: {SALES_DATA}"
        )

    if not EXPENSE_DATA.exists():
        raise FileNotFoundError(
            f"Processed expense data not found: {EXPENSE_DATA}"
        )

    sales = pd.read_parquet(SALES_DATA)
    expenses = pd.read_parquet(EXPENSE_DATA)

    return sales, expenses


def build_executive_kpis(
    sales: pd.DataFrame,
    expenses: pd.DataFrame,
) -> pd.DataFrame:
    """Build executive-level business KPIs."""

    gross_sales = sales["gross_sales"].sum()
    discount = sales["discount_amount"].sum()
    net_sales = sales["net_sales"].sum()
    product_cost = sales["product_cost"].sum()
    gross_profit = sales["gross_profit"].sum()

    transactions = sales["transaction_key"].nunique()
    units_sold = sales["quantity"].sum()

    operating_expense = expenses["amount"].sum()

    operating_profit = (
        gross_profit - operating_expense
    )

    total_cost = (
        product_cost + operating_expense
    )

    kpis = pd.DataFrame(
        [
            {
                "gross_sales": gross_sales,
                "discount": discount,
                "net_sales": net_sales,
                "transactions": transactions,
                "units_sold": units_sold,
                "product_cost": product_cost,
                "gross_profit": gross_profit,
                "operating_expense": operating_expense,
                "operating_profit": operating_profit,
                "total_cost": total_cost,
            }
        ]
    )

    kpis["discount_rate_pct"] = (
        kpis["discount"]
        / kpis["gross_sales"]
        * 100
    )

    kpis["revenue_retained_pct"] = (
        kpis["net_sales"]
        / kpis["gross_sales"]
        * 100
    )

    kpis["average_transaction_value"] = (
        kpis["net_sales"]
        / kpis["transactions"]
    )

    kpis["units_per_transaction"] = (
        kpis["units_sold"]
        / kpis["transactions"]
    )

    kpis["product_cost_ratio_pct"] = (
        kpis["product_cost"]
        / kpis["net_sales"]
        * 100
    )

    kpis["gross_margin_pct"] = (
        kpis["gross_profit"]
        / kpis["net_sales"]
        * 100
    )

    kpis["operating_expense_ratio_pct"] = (
        kpis["operating_expense"]
        / kpis["net_sales"]
        * 100
    )

    kpis["operating_margin_pct"] = (
        kpis["operating_profit"]
        / kpis["net_sales"]
        * 100
    )

    kpis["total_cost_ratio_pct"] = (
        kpis["total_cost"]
        / kpis["net_sales"]
        * 100
    )

    return kpis


def build_monthly_kpi_snapshot(
    sales: pd.DataFrame,
    expenses: pd.DataFrame,
) -> pd.DataFrame:
    """Build monthly executive KPI snapshot."""

    monthly_sales = (
        sales.assign(
            month=sales["transaction_date"].dt.to_period("M")
        )
        .groupby("month", as_index=False)
        .agg(
            gross_sales=("gross_sales", "sum"),
            discount=("discount_amount", "sum"),
            net_sales=("net_sales", "sum"),
            product_cost=("product_cost", "sum"),
            gross_profit=("gross_profit", "sum"),
            transactions=("transaction_key", "nunique"),
            units_sold=("quantity", "sum"),
        )
    )

    monthly_expenses = (
        expenses.assign(
            month=expenses["expense_date"].dt.to_period("M")
        )
        .groupby("month", as_index=False)
        .agg(
            operating_expense=("amount", "sum"),
        )
    )

    monthly = monthly_sales.merge(
        monthly_expenses,
        on="month",
        how="left",
        validate="one_to_one",
    )

    monthly["operating_expense"] = (
        monthly["operating_expense"].fillna(0)
    )

    monthly["operating_profit"] = (
        monthly["gross_profit"]
        - monthly["operating_expense"]
    )

    monthly["average_transaction_value"] = (
        monthly["net_sales"]
        / monthly["transactions"]
    )

    monthly["units_per_transaction"] = (
        monthly["units_sold"]
        / monthly["transactions"]
    )

    monthly["gross_margin_pct"] = (
        monthly["gross_profit"]
        / monthly["net_sales"]
        * 100
    )

    monthly["operating_margin_pct"] = (
        monthly["operating_profit"]
        / monthly["net_sales"]
        * 100
    )

    return monthly


def build_executive_insights(
    monthly: pd.DataFrame,
) -> list[str]:
    """Generate concise executive-level business insights."""

    best_revenue = monthly.loc[
        monthly["net_sales"].idxmax()
    ]

    worst_revenue = monthly.loc[
        monthly["net_sales"].idxmin()
    ]

    best_profit = monthly.loc[
        monthly["operating_profit"].idxmax()
    ]

    best_margin = monthly.loc[
        monthly["operating_margin_pct"].idxmax()
    ]

    best_atv = monthly.loc[
        monthly["average_transaction_value"].idxmax()
    ]

    strongest_volume = monthly.loc[
        monthly["transactions"].idxmax()
    ]

    average_monthly_revenue = (
        monthly["net_sales"].mean()
    )

    peak_vs_average_pct = (
        (
            best_revenue["net_sales"]
            / average_monthly_revenue
        )
        - 1
    ) * 100

    growth_months = (
        monthly["net_sales"]
        .pct_change()
        .gt(0)
        .sum()
    )

    decline_months = (
        monthly["net_sales"]
        .pct_change()
        .lt(0)
        .sum()
    )

    insights = [
        (
            f"Revenue peaked in "
            f"{best_revenue['month']} at "
            f"Rp {best_revenue['net_sales']:,.0f}."
        ),
        (
            f"Revenue was lowest in "
            f"{worst_revenue['month']} at "
            f"Rp {worst_revenue['net_sales']:,.0f}."
        ),
        (
            f"Operating profit peaked in "
            f"{best_profit['month']} at "
            f"Rp {best_profit['operating_profit']:,.0f}."
        ),
        (
            f"Best operating margin occurred in "
            f"{best_margin['month']} at "
            f"{best_margin['operating_margin_pct']:.2f}%."
        ),
        (
            f"Highest average transaction value occurred "
            f"in {best_atv['month']} at "
            f"Rp {best_atv['average_transaction_value']:,.0f}."
        ),
        (
            f"Highest transaction volume occurred in "
            f"{strongest_volume['month']} with "
            f"{strongest_volume['transactions']:,} transactions."
        ),
        (
            f"Peak revenue was "
            f"{peak_vs_average_pct:+.2f}% above "
            f"the average monthly revenue."
        ),
        (
            f"Revenue increased in {growth_months} months "
            f"and declined in {decline_months} months."
        ),
    ]

    return insights


def print_executive_kpis(
    kpis: pd.DataFrame,
) -> None:
    """Print executive KPI dashboard."""

    row = kpis.iloc[0]

    print()
    print("=" * 100)
    print("EXECUTIVE KPI DASHBOARD")
    print("=" * 100)

    currency_metrics = [
        ("Gross Sales", row["gross_sales"]),
        ("Discount", row["discount"]),
        ("Net Sales", row["net_sales"]),
        ("Product Cost", row["product_cost"]),
        ("Gross Profit", row["gross_profit"]),
        ("Operating Expense", row["operating_expense"]),
        ("Operating Profit", row["operating_profit"]),
        ("Total Cost", row["total_cost"]),
        (
            "Average Transaction Value",
            row["average_transaction_value"],
        ),
    ]

    for label, value in currency_metrics:
        print(
            f"{label:<32} "
            f"Rp {value:>15,.0f}"
        )

    integer_metrics = [
        ("Transactions", row["transactions"]),
        ("Units Sold", row["units_sold"]),
    ]

    print()

    for label, value in integer_metrics:
        print(
            f"{label:<32} "
            f"{value:>15,.0f}"
        )

    print()

    print(
        f"{'Units / Transaction':<32} "
        f"{row['units_per_transaction']:.2f}"
    )

    percentage_metrics = [
        ("Discount Rate", row["discount_rate_pct"]),
        (
            "Revenue Retained",
            row["revenue_retained_pct"],
        ),
        (
            "Product Cost Ratio",
            row["product_cost_ratio_pct"],
        ),
        ("Gross Margin", row["gross_margin_pct"]),
        (
            "Operating Expense Ratio",
            row["operating_expense_ratio_pct"],
        ),
        (
            "Operating Margin",
            row["operating_margin_pct"],
        ),
        (
            "Total Cost Ratio",
            row["total_cost_ratio_pct"],
        ),
    ]

    print()

    for label, value in percentage_metrics:
        print(
            f"{label:<32} "
            f"{value:>14.2f}%"
        )


def print_monthly_snapshot(
    monthly: pd.DataFrame,
) -> None:
    """Print monthly executive KPI snapshot."""

    print()
    print("=" * 100)
    print("MONTHLY EXECUTIVE KPI SNAPSHOT")
    print("=" * 100)

    display = monthly[
        [
            "month",
            "net_sales",
            "transactions",
            "units_sold",
            "average_transaction_value",
            "gross_margin_pct",
            "operating_profit",
            "operating_margin_pct",
        ]
    ].copy()

    display["month"] = display["month"].astype(str)

    for column in [
        "net_sales",
        "average_transaction_value",
        "operating_profit",
    ]:
        display[column] = display[column].map(
            lambda value: f"Rp {value:,.0f}"
        )

    for column in [
        "gross_margin_pct",
        "operating_margin_pct",
    ]:
        display[column] = display[column].map(
            lambda value: f"{value:.2f}%"
        )

    print()
    print(
        display.to_string(
            index=False
        )
    )


def print_executive_insights(
    insights: list[str],
) -> None:
    """Print executive business insights."""

    print()
    print("=" * 100)
    print("EXECUTIVE BUSINESS INSIGHTS")
    print("=" * 100)

    for index, insight in enumerate(
        insights,
        start=1,
    ):
        print(
            f"{index}. {insight}"
        )


def validate_against_kpi(
    kpis: pd.DataFrame,
) -> bool:
    """Validate executive KPIs against monthly KPI dataset."""

    if not KPI_DATA.exists():
        raise FileNotFoundError(
            f"Monthly KPI data not found: {KPI_DATA}"
        )

    kpi = pd.read_parquet(KPI_DATA)

    row = kpis.iloc[0]

    analysis_values = {
        "gross_sales": row["gross_sales"],
        "discount": row["discount"],
        "net_sales": row["net_sales"],
        "product_cost": row["product_cost"],
        "gross_profit": row["gross_profit"],
    }

    kpi_values = {
        metric: kpi[metric].sum()
        for metric in analysis_values
    }

    print()
    print("=" * 100)
    print("EXECUTIVE KPI RECONCILIATION")
    print("=" * 100)

    all_pass = True

    for metric in analysis_values:
        analysis_value = analysis_values[metric]
        kpi_value = kpi_values[metric]

        passed = analysis_value == kpi_value

        if not passed:
            all_pass = False

        print(
            f"{metric:<20} "
            f"Analysis: {analysis_value:>15,.0f} | "
            f"KPI: {kpi_value:>15,.0f} | "
            f"{'PASS' if passed else 'REVIEW'}"
        )

    return all_pass


def validate_monthly_snapshot(
    monthly: pd.DataFrame,
) -> bool:
    """Validate monthly snapshot totals against source data."""

    source_metrics = {
        "gross_sales": monthly["gross_sales"].sum(),
        "discount": monthly["discount"].sum(),
        "net_sales": monthly["net_sales"].sum(),
        "product_cost": monthly["product_cost"].sum(),
        "gross_profit": monthly["gross_profit"].sum(),
        "transactions": monthly["transactions"].sum(),
        "units_sold": monthly["units_sold"].sum(),
    }

    print()
    print("=" * 100)
    print("MONTHLY SNAPSHOT VALIDATION")
    print("=" * 100)

    expected_values = {
        "gross_sales": 790_613_000,
        "discount": 28_808_075,
        "net_sales": 761_804_925,
        "product_cost": 427_522_700,
        "gross_profit": 334_282_225,
        "transactions": 13_000,
        "units_sold": 38_602,
    }

    all_pass = True

    for metric in source_metrics:
        calculated_value = source_metrics[metric]
        expected_value = expected_values[metric]

        passed = calculated_value == expected_value

        if not passed:
            all_pass = False

        print(
            f"{metric:<20} "
            f"Calculated: {calculated_value:>15,.0f} | "
            f"Expected: {expected_value:>15,.0f} | "
            f"{'PASS' if passed else 'REVIEW'}"
        )

    return all_pass


def main() -> None:
    """Run executive KPI analysis."""

    print("=" * 100)
    print("MAYASARI BAKERY EXECUTIVE KPI ANALYSIS")
    print("=" * 100)

    sales, expenses = load_data()

    kpis = build_executive_kpis(
        sales,
        expenses,
    )

    monthly = build_monthly_kpi_snapshot(
        sales,
        expenses,
    )

    insights = build_executive_insights(
        monthly
    )

    print_executive_kpis(
        kpis
    )

    print_monthly_snapshot(
        monthly
    )

    print_executive_insights(
        insights
    )

    kpi_validation = validate_against_kpi(
        kpis
    )

    snapshot_validation = (
        validate_monthly_snapshot(
            monthly
        )
    )

    print()
    print("=" * 100)

    if (
        kpi_validation
        and snapshot_validation
    ):
        print(
            "EXECUTIVE KPI ANALYSIS STATUS: PASS"
        )
    else:
        print(
            "EXECUTIVE KPI ANALYSIS STATUS: REVIEW"
        )

    print("=" * 100)


if __name__ == "__main__":
    main()
