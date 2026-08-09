import pandas as pd

from src.contracts.paths import (
    EXPENSES_DATA,
    MONTHLY_KPI_DATA,
    SALES_DATA,
)

EXPENSE_DATA = EXPENSES_DATA
KPI_DATA = MONTHLY_KPI_DATA


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


def build_profitability_summary(
    sales: pd.DataFrame,
    expenses: pd.DataFrame,
) -> pd.DataFrame:
    """Build overall profitability summary."""

    gross_sales = sales["gross_sales"].sum()
    discount = sales["discount_amount"].sum()
    net_sales = sales["net_sales"].sum()
    product_cost = sales["product_cost"].sum()
    gross_profit = sales["gross_profit"].sum()
    operating_expense = expenses["amount"].sum()

    estimated_operating_profit = (
        gross_profit - operating_expense
    )

    summary = pd.DataFrame(
        [
            {
                "gross_sales": gross_sales,
                "discount": discount,
                "net_sales": net_sales,
                "product_cost": product_cost,
                "gross_profit": gross_profit,
                "operating_expense": operating_expense,
                "estimated_operating_profit": (
                    estimated_operating_profit
                ),
            }
        ]
    )

    summary["discount_rate_pct"] = (
        summary["discount"]
        / summary["gross_sales"]
        * 100
    )

    summary["product_cost_ratio_pct"] = (
        summary["product_cost"]
        / summary["net_sales"]
        * 100
    )

    summary["gross_margin_pct"] = (
        summary["gross_profit"]
        / summary["net_sales"]
        * 100
    )

    summary["operating_expense_ratio_pct"] = (
        summary["operating_expense"]
        / summary["net_sales"]
        * 100
    )

    summary["operating_margin_pct"] = (
        summary["estimated_operating_profit"]
        / summary["net_sales"]
        * 100
    )

    summary["total_cost_ratio_pct"] = (
        (
            summary["product_cost"]
            + summary["operating_expense"]
        )
        / summary["net_sales"]
        * 100
    )

    return summary


def build_monthly_profitability(
    sales: pd.DataFrame,
    expenses: pd.DataFrame,
) -> pd.DataFrame:
    """Build monthly profitability analysis."""

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

    monthly["estimated_operating_profit"] = (
        monthly["gross_profit"]
        - monthly["operating_expense"]
    )

    monthly["discount_rate_pct"] = (
        monthly["discount"]
        / monthly["gross_sales"]
        * 100
    )

    monthly["product_cost_ratio_pct"] = (
        monthly["product_cost"]
        / monthly["net_sales"]
        * 100
    )

    monthly["gross_margin_pct"] = (
        monthly["gross_profit"]
        / monthly["net_sales"]
        * 100
    )

    monthly["operating_expense_ratio_pct"] = (
        monthly["operating_expense"]
        / monthly["net_sales"]
        * 100
    )

    monthly["operating_margin_pct"] = (
        monthly["estimated_operating_profit"]
        / monthly["net_sales"]
        * 100
    )

    monthly["total_cost_ratio_pct"] = (
        (
            monthly["product_cost"]
            + monthly["operating_expense"]
        )
        / monthly["net_sales"]
        * 100
    )

    return monthly


def build_discount_analysis(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """Analyze discount impact."""

    gross_sales = sales["gross_sales"].sum()
    discount = sales["discount_amount"].sum()
    net_sales = sales["net_sales"].sum()

    discount_analysis = pd.DataFrame(
        [
            {
                "gross_sales": gross_sales,
                "discount": discount,
                "net_sales": net_sales,
                "discount_rate_pct": (
                    discount / gross_sales * 100
                ),
                "revenue_retained_pct": (
                    net_sales / gross_sales * 100
                ),
            }
        ]
    )

    return discount_analysis


def print_profitability_summary(
    summary: pd.DataFrame,
) -> None:
    """Print overall profitability KPIs."""

    print()
    print("=" * 100)
    print("PROFITABILITY SUMMARY")
    print("=" * 100)

    row = summary.iloc[0]

    currency_metrics = [
        ("Gross Sales", row["gross_sales"]),
        ("Discount", row["discount"]),
        ("Net Sales", row["net_sales"]),
        ("Product Cost", row["product_cost"]),
        ("Gross Profit", row["gross_profit"]),
        (
            "Operating Expense",
            row["operating_expense"],
        ),
        (
            "Estimated Operating Profit",
            row["estimated_operating_profit"],
        ),
    ]

    for label, value in currency_metrics:
        print(f"{label:<30} Rp {value:>15,.0f}")

    print()
    print(
        f"{'Discount Rate':<30} "
        f"{row['discount_rate_pct']:.2f}%"
    )

    print(
        f"{'Product Cost Ratio':<30} "
        f"{row['product_cost_ratio_pct']:.2f}%"
    )

    print(
        f"{'Gross Margin':<30} "
        f"{row['gross_margin_pct']:.2f}%"
    )

    print(
        f"{'Operating Expense Ratio':<30} "
        f"{row['operating_expense_ratio_pct']:.2f}%"
    )

    print(
        f"{'Operating Margin':<30} "
        f"{row['operating_margin_pct']:.2f}%"
    )

    print(
        f"{'Total Cost Ratio':<30} "
        f"{row['total_cost_ratio_pct']:.2f}%"
    )


def print_monthly_profitability(
    monthly: pd.DataFrame,
) -> None:
    """Print monthly profitability."""

    print()
    print("=" * 100)
    print("MONTHLY PROFITABILITY")
    print("=" * 100)

    display = monthly[
        [
            "month",
            "net_sales",
            "product_cost",
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
        "product_cost",
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
            lambda value: f"{value:.2f}%"
        )

    print(display.to_string(index=False))


def print_discount_analysis(
    discount: pd.DataFrame,
) -> None:
    """Print discount impact."""

    print()
    print("=" * 100)
    print("DISCOUNT IMPACT")
    print("=" * 100)

    row = discount.iloc[0]

    print(
        f"{'Gross Sales':<30} "
        f"Rp {row['gross_sales']:>15,.0f}"
    )

    print(
        f"{'Discount':<30} "
        f"Rp {row['discount']:>15,.0f}"
    )

    print(
        f"{'Net Sales':<30} "
        f"Rp {row['net_sales']:>15,.0f}"
    )

    print(
        f"{'Discount Rate':<30} "
        f"{row['discount_rate_pct']:.2f}%"
    )

    print(
        f"{'Revenue Retained':<30} "
        f"{row['revenue_retained_pct']:.2f}%"
    )


def print_profitability_extremes(
    monthly: pd.DataFrame,
) -> None:
    """Print best and worst profitability periods."""

    print()
    print("=" * 100)
    print("PROFITABILITY EXTREMES")
    print("=" * 100)

    best_profit = monthly.loc[
        monthly["estimated_operating_profit"].idxmax()
    ]

    worst_profit = monthly.loc[
        monthly["estimated_operating_profit"].idxmin()
    ]

    best_margin = monthly.loc[
        monthly["operating_margin_pct"].idxmax()
    ]

    worst_margin = monthly.loc[
        monthly["operating_margin_pct"].idxmin()
    ]

    best_gross_margin = monthly.loc[
        monthly["gross_margin_pct"].idxmax()
    ]

    worst_gross_margin = monthly.loc[
        monthly["gross_margin_pct"].idxmin()
    ]

    print()
    print("ESTIMATED OPERATING PROFIT")
    print("-" * 100)

    print(
        f"Best  : {best_profit['month']} | "
        f"Rp {best_profit['estimated_operating_profit']:,.0f}"
    )

    print(
        f"Worst : {worst_profit['month']} | "
        f"Rp {worst_profit['estimated_operating_profit']:,.0f}"
    )

    print()
    print("OPERATING MARGIN")

    print(
        f"Best  : {best_margin['month']} | "
        f"{best_margin['operating_margin_pct']:.2f}%"
    )

    print(
        f"Worst : {worst_margin['month']} | "
        f"{worst_margin['operating_margin_pct']:.2f}%"
    )

    print()
    print("GROSS MARGIN")

    print(
        f"Best  : {best_gross_margin['month']} | "
        f"{best_gross_margin['gross_margin_pct']:.2f}%"
    )

    print(
        f"Worst : {worst_gross_margin['month']} | "
        f"{worst_gross_margin['gross_margin_pct']:.2f}%"
    )


def validate_against_source(
    sales: pd.DataFrame,
    expenses: pd.DataFrame,
    summary: pd.DataFrame,
) -> bool:
    """Validate profitability calculations against source data."""

    source_values = {
        "gross_sales": sales["gross_sales"].sum(),
        "discount": sales["discount_amount"].sum(),
        "net_sales": sales["net_sales"].sum(),
        "product_cost": sales["product_cost"].sum(),
        "gross_profit": sales["gross_profit"].sum(),
        "operating_expense": expenses["amount"].sum(),
    }

    calculated_values = {
        metric: summary.iloc[0][metric]
        for metric in source_values
    }

    print()
    print("=" * 100)
    print("PROFITABILITY VALIDATION")
    print("=" * 100)

    all_pass = True

    for metric, source_value in source_values.items():
        calculated_value = calculated_values[metric]

        passed = source_value == calculated_value

        if not passed:
            all_pass = False

        print(
            f"{metric:<20} "
            f"Source: {source_value:>15,.0f} | "
            f"Analysis: {calculated_value:>15,.0f} | "
            f"{'PASS' if passed else 'REVIEW'}"
        )

    return all_pass


def validate_against_kpi(
    summary: pd.DataFrame,
) -> bool:
    """Validate profitability totals against monthly KPI data."""

    if not KPI_DATA.exists():
        raise FileNotFoundError(
            f"Monthly KPI data not found: {KPI_DATA}"
        )

    kpi = pd.read_parquet(KPI_DATA)

    row = summary.iloc[0]

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
    print("KPI RECONCILIATION")
    print("=" * 100)

    all_pass = True

    for metric, analysis_value in analysis_values.items():
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


def main() -> None:
    """Run profitability and cost analysis."""

    print("=" * 100)
    print("MAYASARI BAKERY PROFITABILITY & COST ANALYSIS")
    print("=" * 100)

    sales, expenses = load_data()

    summary = build_profitability_summary(
        sales,
        expenses,
    )

    monthly = build_monthly_profitability(
        sales,
        expenses,
    )

    discount = build_discount_analysis(
        sales
    )

    print_profitability_summary(
        summary
    )

    print_monthly_profitability(
        monthly
    )

    print_discount_analysis(
        discount
    )

    print_profitability_extremes(
        monthly
    )

    source_validation = validate_against_source(
        sales,
        expenses,
        summary,
    )

    kpi_validation = validate_against_kpi(
        summary
    )

    print()
    print("=" * 100)

    if source_validation and kpi_validation:
        print(
            "PROFITABILITY ANALYSIS STATUS: PASS"
        )
    else:
        print(
            "PROFITABILITY ANALYSIS STATUS: REVIEW"
        )

    print("=" * 100)


if __name__ == "__main__":
    main()
