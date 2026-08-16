"""
M21.1 — Sales Performance Analysis CLI.

Executable entry point for the Mayasari Bakery
sales-performance analysis.

Business logic lives in src.sales_performance.
"""

from __future__ import annotations

import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Repository root / import path
# ---------------------------------------------------------------------------

REPOSITORY_ROOT = Path(
    __file__
).resolve().parents[1]

if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(REPOSITORY_ROOT),
    )


# ---------------------------------------------------------------------------
# Application imports
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_rupiah(
    value: float,
) -> str:
    """Format a numeric value as Indonesian Rupiah."""

    return f"Rp {value:,.0f}"


def print_ranking(
    title: str,
    ranking,
    metric: str,
    limit: int = 3,
) -> None:
    """Print a compact ranking table."""

    print()
    print(f"--- {title} ---")

    for position, (_, row) in enumerate(
        ranking.head(limit).iterrows(),
        start=1,
    ):
        print(
            f"{position}. "
            f"{row['month']} — "
            f"{row[metric]:,.2f}"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    """Run the sales-performance analysis."""

    print("=" * 90)
    print(
        "M21.1 — MAYASARI BAKERY "
        "SALES PERFORMANCE ANALYSIS"
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

    print()
    print("--- INPUT ---")
    print(
        f"Monthly KPI dataset: "
        f"{MONTHLY_KPI_PATH}"
    )

    try:
        import pandas as pd

        monthly_kpi = pd.read_parquet(
            MONTHLY_KPI_PATH
        )

        report = build_sales_performance_report(
            monthly_kpi
        )

    except Exception as exc:
        print()
        print(
            "ERROR — Sales performance analysis failed:"
        )
        print(
            f"  {type(exc).__name__}: {exc}"
        )
        return 1

    summary = report["summary"]

    print()
    print("--- SALES PERFORMANCE SUMMARY ---")

    print(
        f"Gross sales       : "
        f"{format_rupiah(summary.total_gross_sales)}"
    )

    print(
        f"Discount          : "
        f"{format_rupiah(summary.total_discount)}"
    )

    print(
        f"Net sales         : "
        f"{format_rupiah(summary.total_net_sales)}"
    )

    print(
        f"Transactions      : "
        f"{summary.total_transactions:,}"
    )

    print(
        f"Units sold        : "
        f"{summary.total_units_sold:,}"
    )

    print(
        f"Product cost      : "
        f"{format_rupiah(summary.total_product_cost)}"
    )

    print(
        f"Gross profit      : "
        f"{format_rupiah(summary.total_gross_profit)}"
    )

    print(
        f"Operating expense : "
        f"{format_rupiah(summary.total_operating_expense)}"
    )

    print(
        f"Operating profit  : "
        f"{format_rupiah(summary.total_operating_profit)}"
    )

    print(
        f"Gross margin      : "
        f"{summary.gross_margin_pct:.2f}%"
    )

    print(
        f"Operating margin  : "
        f"{summary.operating_margin_pct:.2f}%"
    )

    print(
        f"Discount rate     : "
        f"{summary.discount_rate_pct:.2f}%"
    )

    print(
        f"Average transaction value: "
        f"{format_rupiah(summary.average_transaction_value)}"
    )

    # -----------------------------------------------------------------------
    # Growth
    # -----------------------------------------------------------------------

    growth = report["growth"]

    print()
    print("--- FIRST-TO-LAST MONTH MOVEMENT ---")

    print(
        f"Net sales          : "
        f"{growth['net_sales']:+.2f}%"
    )

    print(
        f"Transactions       : "
        f"{growth['transactions']:+.2f}%"
    )

    print(
        f"Units sold         : "
        f"{growth['units_sold']:+.2f}%"
    )

    print(
        f"Gross profit       : "
        f"{growth['gross_profit']:+.2f}%"
    )

    print(
        f"Average transaction: "
        f"{growth['avg_transaction_value']:+.2f}%"
    )

    # -----------------------------------------------------------------------
    # Rankings
    # -----------------------------------------------------------------------

    print_ranking(
        "TOP 3 MONTHS — NET SALES",
        report["net_sales_ranking"],
        "net_sales",
    )

    print_ranking(
        "TOP 3 MONTHS — GROSS PROFIT",
        report["gross_profit_ranking"],
        "gross_profit",
    )

    print_ranking(
        "TOP 3 MONTHS — TRANSACTIONS",
        report["transaction_ranking"],
        "transactions",
    )

    print_ranking(
        "TOP 3 MONTHS — AVERAGE TRANSACTION VALUE",
        report["atv_ranking"],
        "avg_transaction_value",
    )

    # -----------------------------------------------------------------------
    # Descriptive insights
    # -----------------------------------------------------------------------

    print()
    print("--- DESCRIPTIVE INSIGHTS ---")

    for insight in report["insights"]:
        print(
            f"- {insight}"
        )

    print()
    print("--- RESULT ---")
    print(
        "PASS — sales performance analysis completed."
    )

    print()
    print("=" * 90)
    print("M21.1 COMPLETE")
    print("=" * 90)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
