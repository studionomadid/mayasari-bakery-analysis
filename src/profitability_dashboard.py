from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.contracts.paths import (
    EXECUTIVE_KPIS_DATA,
    PROFITABILITY_FIGURES_DIR,
    PROFITABILITY_SUMMARY_DATA,
)

PROFITABILITY_DATA = (
    PROFITABILITY_SUMMARY_DATA
)

EXECUTIVE_DATA = (
    EXECUTIVE_KPIS_DATA
)

PROFITABILITY_FIGURES = (
    PROFITABILITY_FIGURES_DIR
)


def load_profitability_data() -> tuple[pd.Series, pd.Series]:
    """Load and validate profitability datasets."""

    if not PROFITABILITY_DATA.exists():
        raise FileNotFoundError(
            f"Profitability dataset not found: "
            f"{PROFITABILITY_DATA}"
        )

    if not EXECUTIVE_DATA.exists():
        raise FileNotFoundError(
            f"Executive KPI dataset not found: "
            f"{EXECUTIVE_DATA}"
        )

    profitability = pd.read_parquet(
        PROFITABILITY_DATA
    )

    executive = pd.read_parquet(
        EXECUTIVE_DATA
    )

    if len(profitability) != 1:
        raise ValueError(
            "Profitability dataset must contain "
            f"exactly one row, found {len(profitability)}."
        )

    if len(executive) != 1:
        raise ValueError(
            "Executive KPI dataset must contain "
            f"exactly one row, found {len(executive)}."
        )

    profitability_required = {
        "revenue",
        "product_cost",
        "gross_profit",
        "gross_margin_pct",
    }

    executive_required = {
        "revenue",
        "gross_profit",
        "gross_margin_pct",
        "product_cost",
        "operating_expense",
        "operating_profit",
    }

    missing_profitability = (
        profitability_required
        - set(profitability.columns)
    )

    if missing_profitability:
        raise ValueError(
            "Profitability dataset is missing columns: "
            f"{sorted(missing_profitability)}"
        )

    missing_executive = (
        executive_required
        - set(executive.columns)
    )

    if missing_executive:
        raise ValueError(
            "Executive KPI dataset is missing columns: "
            f"{sorted(missing_executive)}"
        )

    if profitability[
        list(profitability_required)
    ].isna().any().any():
        raise ValueError(
            "Profitability dataset contains "
            "unexpected null values."
        )

    if executive[
        list(executive_required)
    ].isna().any().any():
        raise ValueError(
            "Executive KPI dataset contains "
            "unexpected null values."
        )

    return (
        profitability.iloc[0],
        executive.iloc[0],
    )


def format_currency(value: float) -> str:
    """Format IDR values compactly."""

    if abs(value) >= 1_000_000_000:
        return (
            f"Rp "
            f"{value / 1_000_000_000:.1f}B"
        )

    if abs(value) >= 1_000_000:
        return (
            f"Rp "
            f"{value / 1_000_000:.1f}M"
        )

    if abs(value) >= 1_000:
        return (
            f"Rp "
            f"{value / 1_000:.1f}K"
        )

    return f"Rp {value:,.0f}"


def create_profitability_dashboard(
    profitability: pd.Series,
    executive: pd.Series,
) -> Path:
    """Create profitability performance dashboard."""

    PROFITABILITY_FIGURES.mkdir(
        parents=True,
        exist_ok=True,
    )

    revenue = float(
        profitability["revenue"]
    )

    product_cost = float(
        profitability["product_cost"]
    )

    gross_profit = float(
        profitability["gross_profit"]
    )

    gross_margin = float(
        profitability["gross_margin_pct"]
    )

    operating_expense = float(
        executive["operating_expense"]
    )

    operating_profit = float(
        executive["operating_profit"]
    )

    operating_margin = (
        operating_profit
        / revenue
        * 100
    )

    # --------------------------------------------------
    # Dashboard
    # --------------------------------------------------

    figure, axes = plt.subplots(
        2,
        2,
        figsize=(16, 10),
    )

    figure.suptitle(
        "Mayasari Bakery — Profitability Dashboard",
        fontsize=18,
        fontweight="bold",
    )

    # --------------------------------------------------
    # 1. Revenue → Gross Profit Structure
    # --------------------------------------------------

    ax = axes[0, 0]

    structure_labels = [
        "Product Cost",
        "Gross Profit",
    ]

    structure_values = [
        product_cost / 1_000_000,
        gross_profit / 1_000_000,
    ]

    ax.bar(
        structure_labels,
        structure_values,
    )

    ax.set_title(
        "Revenue Cost Structure"
    )

    ax.set_ylabel(
        "Amount (Rp Million)"
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    # --------------------------------------------------
    # 2. Gross Margin vs Operating Margin
    # --------------------------------------------------

    ax = axes[0, 1]

    margin_labels = [
        "Gross Margin",
        "Operating Margin",
    ]

    margin_values = [
        gross_margin,
        operating_margin,
    ]

    ax.bar(
        margin_labels,
        margin_values,
    )

    ax.set_title(
        "Profit Margin Comparison"
    )

    ax.set_ylabel(
        "Margin (%)"
    )

    ax.set_ylim(
        0,
        max(margin_values) * 1.25,
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    for index, value in enumerate(
        margin_values
    ):
        ax.text(
            index,
            value,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # --------------------------------------------------
    # 3. Gross Profit vs Operating Expense
    # --------------------------------------------------

    ax = axes[1, 0]

    profit_labels = [
        "Gross Profit",
        "Operating Expense",
        "Operating Profit",
    ]

    profit_values = [
        gross_profit / 1_000_000,
        operating_expense / 1_000_000,
        operating_profit / 1_000_000,
    ]

    ax.bar(
        profit_labels,
        profit_values,
    )

    ax.set_title(
        "Operating Profit Structure"
    )

    ax.set_ylabel(
        "Amount (Rp Million)"
    )

    ax.tick_params(
        axis="x",
        rotation=20,
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    # --------------------------------------------------
    # 4. Profitability Composition
    # --------------------------------------------------

    ax = axes[1, 1]

    composition_labels = [
        "Product Cost",
        "Operating Expense",
        "Operating Profit",
    ]

    composition_values = [
        product_cost,
        operating_expense,
        operating_profit,
    ]

    ax.barh(
        composition_labels,
        [
            value / 1_000_000
            for value in composition_values
        ],
    )

    ax.set_title(
        "Revenue Allocation"
    )

    ax.set_xlabel(
        "Amount (Rp Million)"
    )

    ax.grid(
        axis="x",
        alpha=0.25,
    )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    summary = (
        f"Revenue: "
        f"{format_currency(revenue)}"
        f"   |   "
        f"Product Cost: "
        f"{format_currency(product_cost)}"
        f"   |   "
        f"Gross Profit: "
        f"{format_currency(gross_profit)}"
        f"   |   "
        f"Gross Margin: "
        f"{gross_margin:.1f}%"
        f"   |   "
        f"Operating Expense: "
        f"{format_currency(operating_expense)}"
        f"   |   "
        f"Operating Profit: "
        f"{format_currency(operating_profit)}"
        f"   |   "
        f"Operating Margin: "
        f"{operating_margin:.1f}%"
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
        PROFITABILITY_FIGURES
        / "profitability_dashboard.png"
    )

    figure.savefig(
        output,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(figure)

    # --------------------------------------------------
    # Console summary
    # --------------------------------------------------

    print()
    print("=" * 80)
    print(
        "PROFITABILITY DASHBOARD SUMMARY"
    )
    print("=" * 80)

    print(
        f"Revenue               : "
        f"{format_currency(revenue)}"
    )

    print(
        f"Product cost          : "
        f"{format_currency(product_cost)}"
    )

    print(
        f"Gross profit          : "
        f"{format_currency(gross_profit)}"
    )

    print(
        f"Gross margin          : "
        f"{gross_margin:.2f}%"
    )

    print(
        f"Operating expense     : "
        f"{format_currency(operating_expense)}"
    )

    print(
        f"Operating profit      : "
        f"{format_currency(operating_profit)}"
    )

    print(
        f"Operating margin      : "
        f"{operating_margin:.2f}%"
    )

    print(
        f"Generated figure      : "
        f"{output}"
    )

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
    print(
        "M11.6 PROFITABILITY DASHBOARD VALIDATION"
    )
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
    """Generate M11.6 profitability dashboard."""

    profitability, executive = (
        load_profitability_data()
    )

    print("=" * 80)
    print(
        "MAYASARI BAKERY — M11.6 "
        "PROFITABILITY DASHBOARD"
    )
    print("=" * 80)

    output = create_profitability_dashboard(
        profitability,
        executive,
    )

    if not validate_output(output):
        raise SystemExit(1)

    print()
    print("=" * 80)
    print(
        "M11.6 PROFITABILITY DASHBOARD: PASS"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
