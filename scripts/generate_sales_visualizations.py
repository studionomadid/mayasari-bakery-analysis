"""
Mayasari Bakery — Sales Performance Visualization Generator.

Generates reproducible portfolio-grade sales-performance visualizations
from the validated monthly KPI dataset.

Input:
    data/processed/monthly_kpi.parquet

Outputs:
    reports/figures/sales_monthly_net_sales.png
    reports/figures/sales_monthly_transactions.png
    reports/figures/sales_monthly_units.png
    reports/figures/sales_monthly_gross_profit.png
    reports/figures/sales_monthly_atv.png
    reports/figures/sales_performance_overview.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "monthly_kpi.parquet"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "figures"


REQUIRED_COLUMNS = {
    "month",
    "net_sales",
    "transactions",
    "units_sold",
    "gross_profit",
    "avg_transaction_value",
}


def load_monthly_kpi(path: Path = INPUT_PATH) -> pd.DataFrame:
    """Load and validate the monthly KPI dataset."""

    if not path.exists():
        raise FileNotFoundError(f"Monthly KPI dataset not found: {path}")

    df = pd.read_parquet(path)

    missing_columns = REQUIRED_COLUMNS.difference(df.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    if df.empty:
        raise ValueError("Monthly KPI dataset is empty.")

    result = df.copy()

    if isinstance(result["month"].dtype, pd.PeriodDtype):
        result["month"] = result["month"].dt.to_timestamp()
    else:
        result["month"] = pd.to_datetime(result["month"])

    result = result.sort_values("month").reset_index(drop=True)

    return result


def ensure_output_directory(path: Path = OUTPUT_DIR) -> None:
    """Create the visualization output directory when necessary."""

    path.mkdir(parents=True, exist_ok=True)


def format_currency_axis(axis) -> None:
    """Format a chart axis using Indonesian Rupiah millions."""

    from matplotlib.ticker import FuncFormatter

    axis.yaxis.set_major_formatter(
        FuncFormatter(lambda value, _: f"Rp {value / 1_000_000:.0f}M")
    )


def format_integer_axis(axis) -> None:
    """Format an axis using integer values."""

    from matplotlib.ticker import FuncFormatter

    axis.yaxis.set_major_formatter(
        FuncFormatter(lambda value, _: f"{value:,.0f}")
    )


def format_currency_value(value: float) -> str:
    """Format a Rupiah value for annotations."""

    return f"Rp {value / 1_000_000:.1f}M"


def format_number_value(value: float) -> str:
    """Format a numeric value for annotations."""

    return f"{value:,.0f}"


def format_atv_value(value: float) -> str:
    """Format average transaction value for annotations."""

    return f"Rp {value:,.0f}"


def save_figure(fig, output_path: Path) -> None:
    """Save a figure using consistent portfolio-quality settings."""

    fig.tight_layout()
    fig.savefig(
        output_path,
        dpi=180,
        bbox_inches="tight",
    )
    plt.close(fig)


def plot_monthly_net_sales(df: pd.DataFrame) -> Path:
    """Generate monthly net-sales trend."""

    output_path = OUTPUT_DIR / "sales_monthly_net_sales.png"

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        df["month"],
        df["net_sales"],
        marker="o",
        linewidth=2,
    )

    ax.set_title("Mayasari Bakery — Monthly Net Sales")
    ax.set_xlabel("Month")
    ax.set_ylabel("Net Sales")

    format_currency_axis(ax)

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    best_idx = df["net_sales"].idxmax()
    best_row = df.loc[best_idx]

    ax.annotate(
        f"Peak: {format_currency_value(best_row['net_sales'])}",
        xy=(best_row["month"], best_row["net_sales"]),
        xytext=(10, 15),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->"},
    )

    save_figure(fig, output_path)

    return output_path


def plot_monthly_transactions(df: pd.DataFrame) -> Path:
    """Generate monthly transaction-volume trend."""

    output_path = OUTPUT_DIR / "sales_monthly_transactions.png"

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        df["month"],
        df["transactions"],
        marker="o",
        linewidth=2,
    )

    ax.set_title("Mayasari Bakery — Monthly Transactions")
    ax.set_xlabel("Month")
    ax.set_ylabel("Transactions")

    format_integer_axis(ax)

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    best_idx = df["transactions"].idxmax()
    best_row = df.loc[best_idx]

    ax.annotate(
        f"Peak: {format_number_value(best_row['transactions'])}",
        xy=(best_row["month"], best_row["transactions"]),
        xytext=(10, 15),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->"},
    )

    save_figure(fig, output_path)

    return output_path


def plot_monthly_units(df: pd.DataFrame) -> Path:
    """Generate monthly units-sold trend."""

    output_path = OUTPUT_DIR / "sales_monthly_units.png"

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        df["month"],
        df["units_sold"],
        marker="o",
        linewidth=2,
    )

    ax.set_title("Mayasari Bakery — Monthly Units Sold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Units Sold")

    format_integer_axis(ax)

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    best_idx = df["units_sold"].idxmax()
    best_row = df.loc[best_idx]

    ax.annotate(
        f"Peak: {format_number_value(best_row['units_sold'])}",
        xy=(best_row["month"], best_row["units_sold"]),
        xytext=(10, 15),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->"},
    )

    save_figure(fig, output_path)

    return output_path


def plot_monthly_gross_profit(df: pd.DataFrame) -> Path:
    """Generate monthly gross-profit trend."""

    output_path = OUTPUT_DIR / "sales_monthly_gross_profit.png"

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        df["month"],
        df["gross_profit"],
        marker="o",
        linewidth=2,
    )

    ax.set_title("Mayasari Bakery — Monthly Gross Profit")
    ax.set_xlabel("Month")
    ax.set_ylabel("Gross Profit")

    format_currency_axis(ax)

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    best_idx = df["gross_profit"].idxmax()
    best_row = df.loc[best_idx]

    ax.annotate(
        f"Peak: {format_currency_value(best_row['gross_profit'])}",
        xy=(best_row["month"], best_row["gross_profit"]),
        xytext=(10, 15),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->"},
    )

    save_figure(fig, output_path)

    return output_path


def plot_monthly_atv(df: pd.DataFrame) -> Path:
    """Generate monthly average transaction value trend."""

    output_path = OUTPUT_DIR / "sales_monthly_atv.png"

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        df["month"],
        df["avg_transaction_value"],
        marker="o",
        linewidth=2,
    )

    ax.set_title("Mayasari Bakery — Monthly Average Transaction Value")
    ax.set_xlabel("Month")
    ax.set_ylabel("Average Transaction Value")

    from matplotlib.ticker import FuncFormatter

    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda value, _: f"Rp {value:,.0f}")
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    best_idx = df["avg_transaction_value"].idxmax()
    best_row = df.loc[best_idx]

    ax.annotate(
        f"Peak: {format_atv_value(best_row['avg_transaction_value'])}",
        xy=(
            best_row["month"],
            best_row["avg_transaction_value"],
        ),
        xytext=(10, 15),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->"},
    )

    save_figure(fig, output_path)

    return output_path


def plot_sales_performance_overview(df: pd.DataFrame) -> Path:
    """Generate a consolidated sales-performance overview."""

    output_path = OUTPUT_DIR / "sales_performance_overview.png"

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(14, 9),
    )

    ax_net_sales = axes[0, 0]
    ax_transactions = axes[0, 1]
    ax_gross_profit = axes[1, 0]
    ax_atv = axes[1, 1]

    ax_net_sales.plot(
        df["month"],
        df["net_sales"],
        marker="o",
        linewidth=2,
    )
    ax_net_sales.set_title("Net Sales")
    ax_net_sales.set_xlabel("Month")
    ax_net_sales.set_ylabel("Net Sales")
    format_currency_axis(ax_net_sales)
    ax_net_sales.grid(axis="y", alpha=0.25)

    ax_transactions.plot(
        df["month"],
        df["transactions"],
        marker="o",
        linewidth=2,
    )
    ax_transactions.set_title("Transactions")
    ax_transactions.set_xlabel("Month")
    ax_transactions.set_ylabel("Transactions")
    format_integer_axis(ax_transactions)
    ax_transactions.grid(axis="y", alpha=0.25)

    ax_gross_profit.plot(
        df["month"],
        df["gross_profit"],
        marker="o",
        linewidth=2,
    )
    ax_gross_profit.set_title("Gross Profit")
    ax_gross_profit.set_xlabel("Month")
    ax_gross_profit.set_ylabel("Gross Profit")
    format_currency_axis(ax_gross_profit)
    ax_gross_profit.grid(axis="y", alpha=0.25)

    ax_atv.plot(
        df["month"],
        df["avg_transaction_value"],
        marker="o",
        linewidth=2,
    )
    ax_atv.set_title("Average Transaction Value")
    ax_atv.set_xlabel("Month")
    ax_atv.set_ylabel("ATV")

    from matplotlib.ticker import FuncFormatter

    ax_atv.yaxis.set_major_formatter(
        FuncFormatter(lambda value, _: f"Rp {value:,.0f}")
    )

    ax_atv.grid(axis="y", alpha=0.25)

    fig.suptitle(
        "Mayasari Bakery — Sales Performance Overview",
        fontsize=16,
        fontweight="bold",
    )

    save_figure(fig, output_path)

    return output_path


def generate_visualizations(df: pd.DataFrame) -> list[Path]:
    """Generate all sales-performance visualization artifacts."""

    ensure_output_directory()

    outputs = [
        plot_monthly_net_sales(df),
        plot_monthly_transactions(df),
        plot_monthly_units(df),
        plot_monthly_gross_profit(df),
        plot_monthly_atv(df),
        plot_sales_performance_overview(df),
    ]

    return outputs


def main() -> int:
    """Run the sales-performance visualization pipeline."""

    print("=" * 90)
    print("M22.1 — MAYASARI BAKERY SALES PERFORMANCE VISUALIZATION")
    print("=" * 90)

    print("\n--- INPUT ---")
    print(f"Monthly KPI dataset: {INPUT_PATH}")

    df = load_monthly_kpi()

    print("\n--- DATASET ---")
    print(f"Rows: {len(df):,}")
    print(
        "Period: "
        f"{df['month'].min().strftime('%Y-%m')} "
        f"to "
        f"{df['month'].max().strftime('%Y-%m')}"
    )

    print("\n--- GENERATING VISUALIZATIONS ---")

    outputs = generate_visualizations(df)

    for output in outputs:
        print(f"PASS — generated {output.relative_to(PROJECT_ROOT)}")

    print("\n--- OUTPUT COUNT ---")
    print(f"Generated: {len(outputs)} visualization artifacts")

    print("\n--- RESULT ---")
    print("PASS — sales performance visualizations generated successfully.")

    print("\n" + "=" * 90)
    print("M22.1 COMPLETE")
    print("=" * 90)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
