"""
M21.2 — Generate Sales Performance Markdown Report.

Reads the validated monthly KPI dataset and generates a
reproducible Markdown report for the GitHub repository.
"""

from __future__ import annotations

import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Repository root / import path
# ---------------------------------------------------------------------------

REPOSITORY_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(REPOSITORY_ROOT),
    )


import pandas as pd  # noqa: E402

from src.sales_performance import (  # noqa: E402
    build_sales_performance_report,
)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

MONTHLY_KPI_PATH = (
    REPOSITORY_ROOT
    / "data"
    / "processed"
    / "monthly_kpi.parquet"
)

REPORT_PATH = (
    REPOSITORY_ROOT
    / "reports"
    / "sales_performance.md"
)


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def rupiah(
    value: float,
) -> str:
    """Format a numeric value as Indonesian Rupiah."""

    return f"Rp {value:,.0f}"


def percent(
    value: float,
) -> str:
    """Format a numeric percentage."""

    return f"{value:.2f}%"


def signed_percent(
    value: float,
) -> str:
    """Format a percentage with explicit sign."""

    return f"{value:+.2f}%"


def month_label(
    value,
) -> str:
    """Convert a pandas Period into a readable month label."""

    return value.strftime("%B %Y")


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

def build_markdown_report(
    report: dict,
) -> str:
    """Build the complete Markdown sales-performance report."""

    summary = report["summary"]
    monthly = report["monthly_performance"]
    growth = report["growth"]

    lines: list[str] = []

    lines.extend(
        [
            "# Mayasari Bakery — Sales Performance Analysis",
            "",
            "> Reproducible analytical report generated from "
            "`data/processed/monthly_kpi.parquet`.",
            "",
            "## Executive Summary",
            "",
            (
                "The 2025 sales dataset contains "
                f"**{summary.total_transactions:,} transactions** "
                f"and **{summary.total_units_sold:,} units sold**, "
                f"generating **{rupiah(summary.total_net_sales)} "
                "in net sales**."
            ),
            "",
            (
                f"Gross profit reached **{rupiah(summary.total_gross_profit)}** "
                f"with a **{percent(summary.gross_margin_pct)} gross margin**. "
                f"After **{rupiah(summary.total_operating_expense)}** "
                f"in operating expenses, estimated operating profit was "
                f"**{rupiah(summary.total_operating_profit)}**, "
                f"equivalent to a **{percent(summary.operating_margin_pct)} "
                "operating margin**."
            ),
            "",
            "## Annual KPI",
            "",
            "| KPI | Value |",
            "|---|---:|",
            f"| Gross sales | {rupiah(summary.total_gross_sales)} |",
            f"| Discount | {rupiah(summary.total_discount)} |",
            f"| Net sales | {rupiah(summary.total_net_sales)} |",
            f"| Transactions | {summary.total_transactions:,} |",
            f"| Units sold | {summary.total_units_sold:,} |",
            f"| Product cost | {rupiah(summary.total_product_cost)} |",
            f"| Gross profit | {rupiah(summary.total_gross_profit)} |",
            (
                f"| Gross margin | "
                f"{percent(summary.gross_margin_pct)} |"
            ),
            (
                f"| Operating expense | "
                f"{rupiah(summary.total_operating_expense)} |"
            ),
            (
                f"| Operating profit | "
                f"{rupiah(summary.total_operating_profit)} |"
            ),
            (
                f"| Operating margin | "
                f"{percent(summary.operating_margin_pct)} |"
            ),
            (
                f"| Discount rate | "
                f"{percent(summary.discount_rate_pct)} |"
            ),
            (
                f"| Average transaction value | "
                f"{rupiah(summary.average_transaction_value)} |"
            ),
            "",
            "## First-to-Last Month Movement",
            "",
            (
                "This section describes the movement between the "
                "first and last observed months. It is not a CAGR."
            ),
            "",
            "| Metric | Movement |",
            "|---|---:|",
            (
                f"| Net sales | "
                f"{signed_percent(growth['net_sales'])} |"
            ),
            (
                f"| Transactions | "
                f"{signed_percent(growth['transactions'])} |"
            ),
            (
                f"| Units sold | "
                f"{signed_percent(growth['units_sold'])} |"
            ),
            (
                f"| Gross profit | "
                f"{signed_percent(growth['gross_profit'])} |"
            ),
            (
                f"| Average transaction value | "
                f"{signed_percent(growth['avg_transaction_value'])} |"
            ),
            "",
            "## Monthly Performance",
            "",
            "| Month | Net Sales | Transactions | Units | Gross Profit | Gross Margin | Operating Profit |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )

    for _, row in monthly.iterrows():
        lines.append(
            "| "
            f"{month_label(row['month'])} | "
            f"{rupiah(row['net_sales'])} | "
            f"{int(row['transactions']):,} | "
            f"{int(row['units_sold']):,} | "
            f"{rupiah(row['gross_profit'])} | "
            f"{percent(row['gross_margin_pct'])} | "
            f"{rupiah(row['estimated_operating_profit'])} |"
        )

    lines.extend(
        [
            "",
            "## Monthly Rankings",
            "",
            "### Net Sales",
            "",
            "| Rank | Month | Net Sales |",
            "|---:|---|---:|",
        ]
    )

    for position, (_, row) in enumerate(
        report["net_sales_ranking"].head(5).iterrows(),
        start=1,
    ):
        lines.append(
            "| "
            f"{position} | "
            f"{month_label(row['month'])} | "
            f"{rupiah(row['net_sales'])} |"
        )

    lines.extend(
        [
            "",
            "### Gross Profit",
            "",
            "| Rank | Month | Gross Profit |",
            "|---:|---|---:|",
        ]
    )

    for position, (_, row) in enumerate(
        report["gross_profit_ranking"].head(5).iterrows(),
        start=1,
    ):
        lines.append(
            "| "
            f"{position} | "
            f"{month_label(row['month'])} | "
            f"{rupiah(row['gross_profit'])} |"
        )

    lines.extend(
        [
            "",
            "### Transactions",
            "",
            "| Rank | Month | Transactions |",
            "|---:|---|---:|",
        ]
    )

    for position, (_, row) in enumerate(
        report["transaction_ranking"].head(5).iterrows(),
        start=1,
    ):
        lines.append(
            "| "
            f"{position} | "
            f"{month_label(row['month'])} | "
            f"{int(row['transactions']):,} |"
        )

    lines.extend(
        [
            "",
            "### Average Transaction Value",
            "",
            "| Rank | Month | ATV |",
            "|---:|---|---:|",
        ]
    )

    for position, (_, row) in enumerate(
        report["atv_ranking"].head(5).iterrows(),
        start=1,
    ):
        lines.append(
            "| "
            f"{position} | "
            f"{month_label(row['month'])} | "
            f"{rupiah(row['avg_transaction_value'])} |"
        )

    lines.extend(
        [
            "",
            "## Descriptive Insights",
            "",
        ]
    )

    for insight in report["insights"]:
        lines.append(
            f"- {insight}"
        )

    lines.extend(
        [
            "",
            "## Analytical Interpretation",
            "",
            (
                "The observed period shows positive first-to-last "
                "movement in both sales and transaction activity. "
                "Net sales increased faster than transaction volume, "
                "while average transaction value also increased. "
                "This indicates that the final observed month generated "
                "more revenue per transaction than the first observed month."
            ),
            "",
            (
                "December 2025 was the strongest month across the "
                "primary sales metrics in this analysis, recording the "
                "highest net sales, gross profit, transaction count, "
                "and average transaction value."
            ),
            "",
            (
                "These findings are descriptive. They identify observed "
                "patterns in the dataset and do not establish causal "
                "relationships such as seasonality, promotion effects, "
                "or changes in customer behavior."
            ),
            "",
            "## Data Integrity",
            "",
            (
                "This report uses the validated monthly KPI layer from "
                "`data/processed/monthly_kpi.parquet`. Financial "
                "reconciliation was completed in M20, including "
                "transactional sales reconciliation, expense reconciliation, "
                "derived KPI formula checks, and the final financial bridge."
            ),
            "",
            "## Reproducibility",
            "",
            "Generate this report with:",
            "",
            "```bash",
            "python scripts/generate_sales_performance_report.py",
            "```",
            "",
            "Run the CLI analysis with:",
            "",
            "```bash",
            "python scripts/analyze_sales_performance.py",
            "```",
            "",
        ]
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    """Generate the Markdown report."""

    print("=" * 90)
    print(
        "M21.2 — GENERATE SALES PERFORMANCE REPORT"
    )
    print("=" * 90)

    if not MONTHLY_KPI_PATH.exists():
        print()
        print(
            "ERROR — Monthly KPI dataset not found:"
        )
        print(
            f"  {MONTHLY_KPI_PATH}"
        )
        return 1

    monthly_kpi = pd.read_parquet(
        MONTHLY_KPI_PATH
    )

    report = build_sales_performance_report(
        monthly_kpi
    )

    markdown = build_markdown_report(
        report
    )

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        markdown,
        encoding="utf-8",
    )

    print()
    print("--- OUTPUT ---")
    print(
        f"Report written to: {REPORT_PATH}"
    )

    print()
    print("--- RESULT ---")
    print(
        "PASS — sales performance report generated."
    )

    print()
    print("=" * 90)
    print("M21.2 COMPLETE")
    print("=" * 90)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
