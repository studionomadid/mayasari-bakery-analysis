"""
Sales performance analysis for Mayasari Bakery.

This module provides reusable calculations for:
- monthly sales performance
- transaction volume
- units sold
- average transaction value
- gross profit
- gross margin
- operating profit
- monthly ranking
- period-over-period changes
- performance summaries
- descriptive insights

The module is intentionally independent from file I/O and presentation.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


REQUIRED_COLUMNS = {
    "month",
    "transactions",
    "units_sold",
    "gross_sales",
    "discount",
    "net_sales",
    "product_cost",
    "gross_profit",
    "operating_expense",
    "estimated_operating_profit",
    "gross_margin_pct",
    "avg_transaction_value",
}


@dataclass(frozen=True)
class SalesPerformanceSummary:
    """High-level annual sales performance summary."""

    total_gross_sales: float
    total_discount: float
    total_net_sales: float
    total_transactions: int
    total_units_sold: int
    total_product_cost: float
    total_gross_profit: float
    total_operating_expense: float
    total_operating_profit: float
    gross_margin_pct: float
    operating_margin_pct: float
    discount_rate_pct: float
    average_transaction_value: float


def validate_monthly_kpi(
    monthly_kpi: pd.DataFrame,
) -> None:
    """Validate the monthly KPI schema."""

    missing = REQUIRED_COLUMNS - set(monthly_kpi.columns)

    if missing:
        raise ValueError(
            "Monthly KPI dataset is missing required columns: "
            + ", ".join(sorted(missing))
        )

    if monthly_kpi.empty:
        raise ValueError(
            "Monthly KPI dataset must not be empty."
        )


def prepare_monthly_kpi(
    monthly_kpi: pd.DataFrame,
) -> pd.DataFrame:
    """
    Validate and prepare monthly KPI data.

    Returns a defensive copy sorted chronologically.
    """

    validate_monthly_kpi(monthly_kpi)

    prepared = monthly_kpi.copy()

    prepared["month"] = pd.PeriodIndex(
        prepared["month"],
        freq="M",
    )

    prepared = (
        prepared
        .sort_values("month")
        .reset_index(drop=True)
    )

    return prepared


def calculate_period_changes(
    monthly_kpi: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate month-over-month percentage changes
    for key sales metrics.
    """

    prepared = prepare_monthly_kpi(
        monthly_kpi
    )

    result = prepared.copy()

    metrics = [
        "gross_sales",
        "discount",
        "net_sales",
        "transactions",
        "units_sold",
        "gross_profit",
        "estimated_operating_profit",
        "avg_transaction_value",
    ]

    for metric in metrics:
        result[f"{metric}_mom_change"] = (
            result[metric].pct_change()
            * 100
        )

    return result


def rank_months(
    monthly_kpi: pd.DataFrame,
    metric: str,
    ascending: bool = False,
) -> pd.DataFrame:
    """
    Rank months by a selected metric.

    Parameters
    ----------
    monthly_kpi:
        Monthly KPI dataframe.

    metric:
        Numeric KPI column to rank.

    ascending:
        False ranks highest values first.
    """

    prepared = prepare_monthly_kpi(
        monthly_kpi
    )

    if metric not in prepared.columns:
        raise ValueError(
            f"Unknown metric: {metric}"
        )

    return (
        prepared[
            [
                "month",
                metric,
            ]
        ]
        .sort_values(
            metric,
            ascending=ascending,
        )
        .reset_index(drop=True)
    )


def calculate_annual_summary(
    monthly_kpi: pd.DataFrame,
) -> SalesPerformanceSummary:
    """Calculate annual sales performance from monthly KPI data."""

    prepared = prepare_monthly_kpi(
        monthly_kpi
    )

    total_gross_sales = float(
        prepared["gross_sales"].sum()
    )

    total_discount = float(
        prepared["discount"].sum()
    )

    total_net_sales = float(
        prepared["net_sales"].sum()
    )

    total_transactions = int(
        prepared["transactions"].sum()
    )

    total_units_sold = int(
        prepared["units_sold"].sum()
    )

    total_product_cost = float(
        prepared["product_cost"].sum()
    )

    total_gross_profit = float(
        prepared["gross_profit"].sum()
    )

    total_operating_expense = float(
        prepared["operating_expense"].sum()
    )

    total_operating_profit = float(
        prepared["estimated_operating_profit"].sum()
    )

    if total_gross_sales <= 0:
        raise ValueError(
            "Total gross sales must be greater than zero."
        )

    if total_net_sales <= 0:
        raise ValueError(
            "Total net sales must be greater than zero."
        )

    if total_transactions <= 0:
        raise ValueError(
            "Total transactions must be greater than zero."
        )

    gross_margin_pct = (
        total_gross_profit
        / total_net_sales
        * 100
    )

    operating_margin_pct = (
        total_operating_profit
        / total_net_sales
        * 100
    )

    discount_rate_pct = (
        total_discount
        / total_gross_sales
        * 100
    )

    average_transaction_value = (
        total_net_sales
        / total_transactions
    )

    return SalesPerformanceSummary(
        total_gross_sales=total_gross_sales,
        total_discount=total_discount,
        total_net_sales=total_net_sales,
        total_transactions=total_transactions,
        total_units_sold=total_units_sold,
        total_product_cost=total_product_cost,
        total_gross_profit=total_gross_profit,
        total_operating_expense=total_operating_expense,
        total_operating_profit=total_operating_profit,
        gross_margin_pct=gross_margin_pct,
        operating_margin_pct=operating_margin_pct,
        discount_rate_pct=discount_rate_pct,
        average_transaction_value=average_transaction_value,
    )


def calculate_monthly_performance(
    monthly_kpi: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the primary monthly performance table.

    Adds:
    - operating margin
    - units per transaction
    - month-over-month changes
    """

    prepared = calculate_period_changes(
        monthly_kpi
    )

    prepared["operating_margin_pct"] = (
        prepared["estimated_operating_profit"]
        / prepared["net_sales"]
        * 100
    )

    prepared["units_per_transaction"] = (
        prepared["units_sold"]
        / prepared["transactions"]
    )

    return prepared


def identify_best_month(
    monthly_kpi: pd.DataFrame,
    metric: str = "net_sales",
) -> pd.Series:
    """Return the best-performing month for a metric."""

    prepared = prepare_monthly_kpi(
        monthly_kpi
    )

    if metric not in prepared.columns:
        raise ValueError(
            f"Unknown metric: {metric}"
        )

    return prepared.loc[
        prepared[metric].idxmax()
    ]


def identify_worst_month(
    monthly_kpi: pd.DataFrame,
    metric: str = "net_sales",
) -> pd.Series:
    """Return the worst-performing month for a metric."""

    prepared = prepare_monthly_kpi(
        monthly_kpi
    )

    if metric not in prepared.columns:
        raise ValueError(
            f"Unknown metric: {metric}"
        )

    return prepared.loc[
        prepared[metric].idxmin()
    ]


def calculate_sales_growth(
    monthly_kpi: pd.DataFrame,
) -> dict[str, float]:
    """
    Calculate first-to-last month movement.

    This is descriptive movement across the observed
    period, not a CAGR calculation.
    """

    prepared = prepare_monthly_kpi(
        monthly_kpi
    )

    first = prepared.iloc[0]
    last = prepared.iloc[-1]

    metrics = [
        "net_sales",
        "transactions",
        "units_sold",
        "gross_profit",
        "avg_transaction_value",
    ]

    growth: dict[str, float] = {}

    for metric in metrics:
        initial = float(
            first[metric]
        )

        final = float(
            last[metric]
        )

        if initial == 0:
            growth[metric] = float("nan")
        else:
            growth[metric] = (
                (final - initial)
                / initial
                * 100
            )

    return growth


def generate_insights(
    monthly_kpi: pd.DataFrame,
) -> list[str]:
    """
    Generate concise, data-grounded descriptive insights.

    These statements are descriptive rather than causal.
    """

    prepared = calculate_monthly_performance(
        monthly_kpi
    )

    insights: list[str] = []

    best_sales = identify_best_month(
        prepared,
        "net_sales",
    )

    worst_sales = identify_worst_month(
        prepared,
        "net_sales",
    )

    best_profit = identify_best_month(
        prepared,
        "gross_profit",
    )

    worst_profit = identify_worst_month(
        prepared,
        "gross_profit",
    )

    best_atv = identify_best_month(
        prepared,
        "avg_transaction_value",
    )

    worst_atv = identify_worst_month(
        prepared,
        "avg_transaction_value",
    )

    insights.append(
        "Highest net sales occurred in "
        f"{best_sales['month']} at "
        f"Rp {best_sales['net_sales']:,.0f}."
    )

    insights.append(
        "Lowest net sales occurred in "
        f"{worst_sales['month']} at "
        f"Rp {worst_sales['net_sales']:,.0f}."
    )

    insights.append(
        "Highest gross profit occurred in "
        f"{best_profit['month']} at "
        f"Rp {best_profit['gross_profit']:,.0f}."
    )

    insights.append(
        "Lowest gross profit occurred in "
        f"{worst_profit['month']} at "
        f"Rp {worst_profit['gross_profit']:,.0f}."
    )

    insights.append(
        "Highest average transaction value occurred in "
        f"{best_atv['month']} at "
        f"Rp {best_atv['avg_transaction_value']:,.2f}."
    )

    insights.append(
        "Lowest average transaction value occurred in "
        f"{worst_atv['month']} at "
        f"Rp {worst_atv['avg_transaction_value']:,.2f}."
    )

    return insights


def build_sales_performance_report(
    monthly_kpi: pd.DataFrame,
) -> dict:
    """
    Build a structured sales-performance report.

    The returned dictionary is designed for downstream
    CLI output, Markdown reports, dashboards, and notebooks.
    """

    prepared = calculate_monthly_performance(
        monthly_kpi
    )

    summary = calculate_annual_summary(
        prepared
    )

    growth = calculate_sales_growth(
        prepared
    )

    return {
        "summary": summary,
        "monthly_performance": prepared,
        "net_sales_ranking": rank_months(
            prepared,
            "net_sales",
        ),
        "gross_profit_ranking": rank_months(
            prepared,
            "gross_profit",
        ),
        "transaction_ranking": rank_months(
            prepared,
            "transactions",
        ),
        "atv_ranking": rank_months(
            prepared,
            "avg_transaction_value",
        ),
        "growth": growth,
        "insights": generate_insights(
            prepared
        ),
    }
