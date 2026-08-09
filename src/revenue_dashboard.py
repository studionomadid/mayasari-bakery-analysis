from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.contracts.paths import (
    MONTHLY_PERFORMANCE_DATA,
    SALES_FIGURES_DIR,
)

MONTHLY_DATA = MONTHLY_PERFORMANCE_DATA
SALES_FIGURES = SALES_FIGURES_DIR


def load_monthly_data() -> pd.DataFrame:
    """Load and validate monthly performance dataset."""

    if not MONTHLY_DATA.exists():
        raise FileNotFoundError(
            f"Monthly performance dataset not found: "
            f"{MONTHLY_DATA}"
        )

    data = pd.read_parquet(MONTHLY_DATA)

    required_columns = {
        "sales_month",
        "revenue",
        "gross_profit",
        "transactions",
        "customers",
        "gross_margin_pct",
        "average_transaction_value",
        "mom_revenue_growth_pct",
        "rolling_3m_revenue",
    }

    missing_columns = (
        required_columns - set(data.columns)
    )

    if missing_columns:
        raise ValueError(
            "Monthly performance dataset is missing "
            f"columns: {sorted(missing_columns)}"
        )

    if len(data) != 12:
        raise ValueError(
            "Expected 12 monthly records, "
            f"found {len(data)}."
        )

    data = data.copy()

    data["sales_month"] = data[
        "sales_month"
    ].astype(str)

    data = data.sort_values(
        "sales_month"
    ).reset_index(drop=True)

    return data


def format_currency(value: float) -> str:
    """Format IDR values compactly."""

    if abs(value) >= 1_000_000_000:
        return (
            f"Rp {value / 1_000_000_000:.1f}B"
        )

    if abs(value) >= 1_000_000:
        return (
            f"Rp {value / 1_000_000:.1f}M"
        )

    if abs(value) >= 1_000:
        return (
            f"Rp {value / 1_000:.1f}K"
        )

    return f"Rp {value:,.0f}"


def create_revenue_dashboard(
    monthly: pd.DataFrame,
) -> Path:
    """Create revenue performance dashboard."""

    SALES_FIGURES.mkdir(
        parents=True,
        exist_ok=True,
    )

    months = monthly["sales_month"]

    revenue = monthly["revenue"]

    rolling_revenue = (
        monthly["rolling_3m_revenue"]
    )

    mom_growth = (
        monthly["mom_revenue_growth_pct"]
    )

    transactions = monthly["transactions"]

    customers = monthly["customers"]

    peak_index = revenue.idxmax()
    lowest_index = revenue.idxmin()

    peak_month = monthly.loc[
        peak_index,
        "sales_month",
    ]

    lowest_month = monthly.loc[
        lowest_index,
        "sales_month",
    ]

    peak_revenue = monthly.loc[
        peak_index,
        "revenue",
    ]

    lowest_revenue = monthly.loc[
        lowest_index,
        "revenue",
    ]

    figure, axes = plt.subplots(
        2,
        2,
        figsize=(16, 10),
    )

    figure.suptitle(
        "Mayasari Bakery — Revenue Dashboard",
        fontsize=18,
        fontweight="bold",
    )

    # --------------------------------------------------
    # 1. Monthly Revenue Trend
    # --------------------------------------------------

    ax = axes[0, 0]

    ax.plot(
        months,
        revenue / 1_000_000,
        marker="o",
        linewidth=2,
        label="Monthly Revenue",
    )

    ax.plot(
        months,
        rolling_revenue / 1_000_000,
        linestyle="--",
        linewidth=2,
        label="3-Month Rolling Average",
    )

    ax.set_title(
        "Monthly Revenue Trend"
    )

    ax.set_ylabel(
        "Revenue (Rp Million)"
    )

    ax.set_xlabel(
        "Month"
    )

    ax.tick_params(
        axis="x",
        rotation=45,
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    ax.legend()

    # --------------------------------------------------
    # 2. MoM Revenue Growth
    # --------------------------------------------------

    ax = axes[0, 1]

    growth_values = (
        mom_growth.fillna(0)
    )

    ax.bar(
        months,
        growth_values,
    )

    ax.axhline(
        0,
        linewidth=1,
    )

    ax.set_title(
        "Month-over-Month Revenue Growth"
    )

    ax.set_ylabel(
        "Growth (%)"
    )

    ax.set_xlabel(
        "Month"
    )

    ax.tick_params(
        axis="x",
        rotation=45,
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    for index, value in enumerate(
        growth_values
    ):
        if monthly.loc[
            index,
            "mom_revenue_growth_pct",
        ] != monthly.loc[
            index,
            "mom_revenue_growth_pct",
        ]:
            continue

        ax.text(
            index,
            value,
            f"{value:.1f}%",
            ha="center",
            va=(
                "bottom"
                if value >= 0
                else "top"
            ),
            fontsize=8,
        )

    # --------------------------------------------------
    # 3. Revenue vs Transactions
    # --------------------------------------------------

    ax = axes[1, 0]

    ax.plot(
        months,
        revenue / 1_000_000,
        marker="o",
        linewidth=2,
        label="Revenue (Rp M)",
    )

    ax2 = ax.twinx()

    ax2.plot(
        months,
        transactions,
        marker="s",
        linestyle="--",
        linewidth=2,
        label="Transactions",
    )

    ax.set_title(
        "Revenue vs Transaction Volume"
    )

    ax.set_ylabel(
        "Revenue (Rp Million)"
    )

    ax2.set_ylabel(
        "Transactions"
    )

    ax.set_xlabel(
        "Month"
    )

    ax.tick_params(
        axis="x",
        rotation=45,
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    lines_1, labels_1 = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()

    ax.legend(
        lines_1 + lines_2,
        labels_1 + labels_2,
        loc="upper left",
    )

    # --------------------------------------------------
    # 4. Revenue Drivers
    # --------------------------------------------------

    ax = axes[1, 1]

    ax.plot(
        months,
        customers,
        marker="o",
        linewidth=2,
        label="Customers",
    )

    ax.set_title(
        "Monthly Active Customers"
    )

    ax.set_ylabel(
        "Customers"
    )

    ax.set_xlabel(
        "Month"
    )

    ax.tick_params(
        axis="x",
        rotation=45,
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    ax.legend()

    # --------------------------------------------------
    # Dashboard Summary
    # --------------------------------------------------

    total_revenue = revenue.sum()

    average_monthly_revenue = (
        revenue.mean()
    )

    best_growth_index = (
        mom_growth.idxmax()
    )

    best_growth_month = monthly.loc[
        best_growth_index,
        "sales_month",
    ]

    best_growth = monthly.loc[
        best_growth_index,
        "mom_revenue_growth_pct",
    ]

    summary = (
        f"Annual Revenue: "
        f"{format_currency(total_revenue)}"
        f"   |   "
        f"Avg Monthly: "
        f"{format_currency(average_monthly_revenue)}"
        f"   |   "
        f"Peak Month: {peak_month} "
        f"({format_currency(peak_revenue)})"
        f"   |   "
        f"Lowest Month: {lowest_month} "
        f"({format_currency(lowest_revenue)})"
        f"   |   "
        f"Best MoM Growth: {best_growth_month} "
        f"({best_growth:.1f}%)"
    )

    figure.text(
        0.5,
        0.015,
        summary,
        ha="center",
        fontsize=9,
    )

    figure.text(
        0.5,
        -0.005,
        "Source: Mayasari Bakery analytical datasets",
        ha="center",
        fontsize=8,
    )

    figure.tight_layout(
        rect=(0, 0.06, 1, 0.94)
    )

    output = (
        SALES_FIGURES
        / "revenue_dashboard.png"
    )

    figure.savefig(
        output,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(figure)

    return output


def validate_output(
    output: Path,
) -> bool:
    """Validate generated dashboard."""

    exists = output.exists()

    valid_size = (
        output.stat().st_size > 0
        if exists
        else False
    )

    passed = (
        exists
        and valid_size
    )

    print()
    print("=" * 80)
    print("M11.3 REVENUE DASHBOARD VALIDATION")
    print("=" * 80)

    print(
        f"Output exists : "
        f"{'PASS' if exists else 'REVIEW'}"
    )

    print(
        f"Output size   : "
        f"{output.stat().st_size:,} bytes"
        if exists
        else "Output size   : REVIEW"
    )

    print("-" * 80)

    print(
        f"Validation    : "
        f"{'PASS' if passed else 'REVIEW'}"
    )

    return passed


def main() -> None:
    """Generate M11.3 revenue dashboard."""

    monthly = load_monthly_data()

    print("=" * 80)
    print(
        "MAYASARI BAKERY — M11.3 REVENUE DASHBOARD"
    )
    print("=" * 80)

    print()
    print("REVENUE SUMMARY")
    print("-" * 80)

    total_revenue = monthly[
        "revenue"
    ].sum()

    average_monthly_revenue = monthly[
        "revenue"
    ].mean()

    peak_index = monthly[
        "revenue"
    ].idxmax()

    lowest_index = monthly[
        "revenue"
    ].idxmin()

    best_growth_index = monthly[
        "mom_revenue_growth_pct"
    ].idxmax()

    print(
        f"Annual revenue       : "
        f"{format_currency(total_revenue)}"
    )

    print(
        f"Average monthly      : "
        f"{format_currency(average_monthly_revenue)}"
    )

    print(
        f"Peak month           : "
        f"{monthly.loc[peak_index, 'sales_month']} "
        f"— "
        f"{format_currency(monthly.loc[peak_index, 'revenue'])}"
    )

    print(
        f"Lowest month         : "
        f"{monthly.loc[lowest_index, 'sales_month']} "
        f"— "
        f"{format_currency(monthly.loc[lowest_index, 'revenue'])}"
    )

    print(
        f"Best MoM growth      : "
        f"{monthly.loc[best_growth_index, 'sales_month']} "
        f"— "
        f"{monthly.loc[best_growth_index, 'mom_revenue_growth_pct']:.2f}%"
    )

    print()
    print("MONTHLY REVENUE")
    print("-" * 80)

    display = monthly[
        [
            "sales_month",
            "revenue",
            "mom_revenue_growth_pct",
            "transactions",
        ]
    ].copy()

    display["revenue"] = (
        display["revenue"]
        .map(
            lambda value:
            f"Rp {value:,.0f}"
        )
    )

    display["mom_revenue_growth_pct"] = (
        display[
            "mom_revenue_growth_pct"
        ]
        .map(
            lambda value:
            "-"
            if pd.isna(value)
            else f"{value:.2f}%"
        )
    )

    print(
        display.to_string(
            index=False
        )
    )

    output = create_revenue_dashboard(
        monthly
    )

    print()
    print(
        f"Generated figure : {output}"
    )

    if not validate_output(output):
        raise SystemExit(1)

    print()
    print("=" * 80)
    print(
        "M11.3 REVENUE DASHBOARD: PASS"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
