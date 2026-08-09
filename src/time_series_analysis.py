import pandas as pd

from src.contracts.paths import (
    EXPENSES_DATA,
    MONTHLY_KPI_DATA,
    SALES_DATA,
)

EXPENSE_DATA = EXPENSES_DATA


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


def build_monthly_sales_analysis(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """Build monthly sales performance analysis."""

    monthly = (
        sales.assign(
            month=sales["transaction_date"].dt.to_period("M")
        )
        .groupby("month", as_index=False)
        .agg(
            transactions=("transaction_key", "nunique"),
            sales_lines=("transaction_line_key", "nunique"),
            units_sold=("quantity", "sum"),
            gross_sales=("gross_sales", "sum"),
            discount=("discount_amount", "sum"),
            net_sales=("net_sales", "sum"),
            product_cost=("product_cost", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
    )

    monthly["gross_margin_pct"] = (
        monthly["gross_profit"]
        / monthly["net_sales"].replace(0, pd.NA)
        * 100
    )

    monthly["average_transaction_value"] = (
        monthly["net_sales"]
        / monthly["transactions"].replace(0, pd.NA)
    )

    monthly["units_per_transaction"] = (
        monthly["units_sold"]
        / monthly["transactions"].replace(0, pd.NA)
    )

    monthly["revenue_mom_pct"] = (
        monthly["net_sales"]
        .pct_change()
        * 100
    )

    monthly["profit_mom_pct"] = (
        monthly["gross_profit"]
        .pct_change()
        * 100
    )

    monthly["transactions_mom_pct"] = (
        monthly["transactions"]
        .pct_change()
        * 100
    )

    monthly["units_mom_pct"] = (
        monthly["units_sold"]
        .pct_change()
        * 100
    )

    return monthly


def build_monthly_expense_analysis(
    expenses: pd.DataFrame,
) -> pd.DataFrame:
    """Build monthly operating expense analysis."""

    monthly = (
        expenses.assign(
            month=expenses["expense_date"].dt.to_period("M")
        )
        .groupby("month", as_index=False)
        .agg(
            expense_records=("expense_id", "nunique"),
            operating_expense=("amount", "sum"),
        )
    )

    return monthly


def combine_monthly_analysis(
    monthly_sales: pd.DataFrame,
    monthly_expenses: pd.DataFrame,
) -> pd.DataFrame:
    """Combine monthly sales and expense performance."""

    monthly = monthly_sales.merge(
        monthly_expenses,
        on="month",
        how="left",
        validate="one_to_one",
    )

    monthly["operating_expense"] = (
        monthly["operating_expense"]
        .fillna(0)
    )

    monthly["estimated_operating_profit"] = (
        monthly["gross_profit"]
        - monthly["operating_expense"]
    )

    monthly["operating_margin_pct"] = (
        monthly["estimated_operating_profit"]
        / monthly["net_sales"].replace(0, pd.NA)
        * 100
    )

    monthly["expense_ratio_pct"] = (
        monthly["operating_expense"]
        / monthly["net_sales"].replace(0, pd.NA)
        * 100
    )

    monthly["profit_mom_pct"] = (
        monthly["estimated_operating_profit"]
        .pct_change()
        * 100
    )

    monthly["expense_mom_pct"] = (
        monthly["operating_expense"]
        .pct_change()
        * 100
    )

    return monthly


def print_monthly_performance(
    monthly: pd.DataFrame,
) -> None:
    """Print monthly performance table."""

    print()
    print("=" * 100)
    print("MONTHLY PERFORMANCE")
    print("=" * 100)

    display = monthly[
        [
            "month",
            "transactions",
            "units_sold",
            "net_sales",
            "gross_profit",
            "gross_margin_pct",
            "operating_expense",
            "estimated_operating_profit",
            "operating_margin_pct",
        ]
    ].copy()

    display["month"] = display["month"].astype(str)

    for column in [
        "net_sales",
        "gross_profit",
        "operating_expense",
        "estimated_operating_profit",
    ]:
        display[column] = display[column].map(
            lambda value: f"Rp {value:,.0f}"
        )

    for column in [
        "gross_margin_pct",
        "operating_margin_pct",
    ]:
        display[column] = display[column].map(
            lambda value: (
                f"{value:.2f}%"
                if pd.notna(value)
                else "N/A"
            )
        )

    print(
        display.to_string(index=False)
    )


def print_growth_analysis(
    monthly: pd.DataFrame,
) -> None:
    """Print monthly growth analysis."""

    print()
    print("=" * 100)
    print("MONTH-OVER-MONTH GROWTH")
    print("=" * 100)

    display = monthly[
        [
            "month",
            "revenue_mom_pct",
            "profit_mom_pct",
            "transactions_mom_pct",
            "units_mom_pct",
            "expense_mom_pct",
        ]
    ].copy()

    display["month"] = display["month"].astype(str)

    for column in [
        "revenue_mom_pct",
        "profit_mom_pct",
        "transactions_mom_pct",
        "units_mom_pct",
        "expense_mom_pct",
    ]:
        display[column] = display[column].map(
            lambda value: (
                f"{value:+.2f}%"
                if pd.notna(value)
                else "N/A"
            )
        )

    print(
        display.to_string(index=False)
    )


def print_best_worst_months(
    monthly: pd.DataFrame,
) -> None:
    """Print best and worst months by key business metrics."""

    print()
    print("=" * 100)
    print("BEST & WORST MONTHS")
    print("=" * 100)

    revenue_best = monthly.loc[
        monthly["net_sales"].idxmax()
    ]

    revenue_worst = monthly.loc[
        monthly["net_sales"].idxmin()
    ]

    profit_best = monthly.loc[
        monthly["estimated_operating_profit"].idxmax()
    ]

    profit_worst = monthly.loc[
        monthly["estimated_operating_profit"].idxmin()
    ]

    margin_best = monthly.loc[
        monthly["operating_margin_pct"].idxmax()
    ]

    margin_worst = monthly.loc[
        monthly["operating_margin_pct"].idxmin()
    ]

    print()
    print("NET SALES")
    print("-" * 100)

    print(
        f"Best  : {revenue_best['month']} | "
        f"Rp {revenue_best['net_sales']:,.0f}"
    )

    print(
        f"Worst : {revenue_worst['month']} | "
        f"Rp {revenue_worst['net_sales']:,.0f}"
    )

    print()
    print("ESTIMATED OPERATING PROFIT")
    print("-" * 100)

    print(
        f"Best  : {profit_best['month']} | "
        f"Rp {profit_best['estimated_operating_profit']:,.0f}"
    )

    print(
        f"Worst : {profit_worst['month']} | "
        f"Rp {profit_worst['estimated_operating_profit']:,.0f}"
    )

    print()
    print("OPERATING MARGIN")
    print("-" * 100)

    print(
        f"Best  : {margin_best['month']} | "
        f"{margin_best['operating_margin_pct']:.2f}%"
    )

    print(
        f"Worst : {margin_worst['month']} | "
        f"{margin_worst['operating_margin_pct']:.2f}%"
    )


def validate_against_kpi(
    monthly: pd.DataFrame,
) -> bool:
    """Validate monthly sales totals against source KPI totals."""

    kpi_path = MONTHLY_KPI_DATA

    if not kpi_path.exists():
        raise FileNotFoundError(
            f"Monthly KPI data not found: {kpi_path}"
        )

    kpi = pd.read_parquet(kpi_path)

    monthly_sales = monthly[
        [
            "transactions",
            "units_sold",
            "gross_sales",
            "discount",
            "net_sales",
            "product_cost",
            "gross_profit",
        ]
    ].sum()

    kpi_totals = kpi[
        [
            "transactions",
            "units_sold",
            "gross_sales",
            "discount",
            "net_sales",
            "product_cost",
            "gross_profit",
        ]
    ].sum()

    print()
    print("=" * 100)
    print("MONTHLY KPI VALIDATION")
    print("=" * 100)

    all_pass = True

    for metric in monthly_sales.index:
        source_value = monthly_sales[metric]
        kpi_value = kpi_totals[metric]

        passed = source_value == kpi_value

        if not passed:
            all_pass = False

        print(
            f"{metric:<15} "
            f"Monthly: {source_value:>15,.0f} | "
            f"KPI: {kpi_value:>15,.0f} | "
            f"{'PASS' if passed else 'REVIEW'}"
        )

    return all_pass


def main() -> None:
    """Run time-series and monthly performance analysis."""

    print("=" * 100)
    print("MAYASARI BAKERY TIME SERIES ANALYSIS")
    print("=" * 100)

    sales, expenses = load_data()

    monthly_sales = build_monthly_sales_analysis(
        sales
    )

    monthly_expenses = build_monthly_expense_analysis(
        expenses
    )

    monthly = combine_monthly_analysis(
        monthly_sales,
        monthly_expenses,
    )

    print_monthly_performance(
        monthly
    )

    print_growth_analysis(
        monthly
    )

    print_best_worst_months(
        monthly
    )

    validation_pass = validate_against_kpi(
        monthly
    )

    print()
    print("=" * 100)

    if validation_pass:
        print("TIME SERIES ANALYSIS STATUS: PASS")
    else:
        print("TIME SERIES ANALYSIS STATUS: REVIEW")

    print("=" * 100)


if __name__ == "__main__":
    main()
