"""
Mayasari Bakery — Customer Performance Visualizations.

Generates reproducible customer-level analytics visualizations
from validated analytics datasets.

Source datasets:
    data/analytics/customer_performance.parquet
    data/analytics/customer_opportunity.parquet

Outputs:
    reports/figures/customer_clv_distribution.png
    reports/figures/customer_segment_performance.png
    reports/figures/customer_clv_tiers.png
    reports/figures/customer_opportunity_matrix.png
    reports/figures/customer_rfm_distribution.png
    reports/figures/customer_performance_overview.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


ROOT = Path(__file__).resolve().parents[1]

CUSTOMER_PERFORMANCE_DATA = (
    ROOT / "data" / "analytics" / "customer_performance.parquet"
)

CUSTOMER_OPPORTUNITY_DATA = (
    ROOT / "data" / "analytics" / "customer_opportunity.parquet"
)

OUTPUT_DIR = ROOT / "reports" / "figures"


REQUIRED_PERFORMANCE_COLUMNS = {
    "customer_id",
    "revenue",
    "gross_profit",
    "transactions",
    "active_months",
    "average_transaction_value",
    "historical_clv",
    "annualized_clv",
    "observed_lifetime_days",
}

REQUIRED_OPPORTUNITY_COLUMNS = {
    "customer_id",
    "revenue",
    "gross_profit",
    "transactions",
    "active_months",
    "annualized_clv",
    "clv_tier",
    "customer_name",
    "recency",
    "frequency",
    "monetary",
    "rfm_total",
    "segment",
    "opportunity",
    "opportunity_priority",
}


def format_currency_axis(axis) -> None:
    """Format currency axis values using Indonesian Rupiah millions."""

    axis.yaxis.set_major_formatter(
        FuncFormatter(lambda value, _: f"Rp {value / 1_000_000:.1f}M")
    )


def format_currency_value(value: float) -> str:
    """Format a currency value as Indonesian Rupiah millions."""

    return f"Rp {value / 1_000_000:.2f}M"


def load_customer_performance(
    path: Path = CUSTOMER_PERFORMANCE_DATA,
) -> pd.DataFrame:
    """Load and validate customer performance data."""

    if not path.exists():
        raise FileNotFoundError(
            f"Customer performance dataset not found: {path}"
        )

    df = pd.read_parquet(path)

    missing_columns = REQUIRED_PERFORMANCE_COLUMNS.difference(df.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Customer performance dataset missing required columns: {missing}"
        )

    if df.empty:
        raise ValueError("Customer performance dataset is empty.")

    result = df.copy()

    result["annualized_clv"] = pd.to_numeric(
        result["annualized_clv"],
        errors="raise",
    )

    result["historical_clv"] = pd.to_numeric(
        result["historical_clv"],
        errors="raise",
    )

    result["revenue"] = pd.to_numeric(
        result["revenue"],
        errors="raise",
    )

    result["gross_profit"] = pd.to_numeric(
        result["gross_profit"],
        errors="raise",
    )

    result["transactions"] = pd.to_numeric(
        result["transactions"],
        errors="raise",
    )

    return result


def load_customer_opportunity(
    path: Path = CUSTOMER_OPPORTUNITY_DATA,
) -> pd.DataFrame:
    """Load and validate customer opportunity data."""

    if not path.exists():
        raise FileNotFoundError(
            f"Customer opportunity dataset not found: {path}"
        )

    df = pd.read_parquet(path)

    missing_columns = REQUIRED_OPPORTUNITY_COLUMNS.difference(df.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Customer opportunity dataset missing required columns: {missing}"
        )

    if df.empty:
        raise ValueError("Customer opportunity dataset is empty.")

    result = df.copy()

    numeric_columns = [
        "revenue",
        "gross_profit",
        "transactions",
        "active_months",
        "annualized_clv",
        "recency",
        "frequency",
        "monetary",
        "rfm_total",
        "opportunity_priority",
    ]

    for column in numeric_columns:
        result[column] = pd.to_numeric(
            result[column],
            errors="raise",
        )

    return result


def ensure_output_directory(
    path: Path = OUTPUT_DIR,
) -> None:
    """Create output directory when necessary."""

    path.mkdir(parents=True, exist_ok=True)


def save_figure(
    figure,
    filename: str,
) -> None:
    """Save a figure using a consistent publication-oriented configuration."""

    output_path = OUTPUT_DIR / filename

    figure.savefig(
        output_path,
        dpi=180,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(figure)

    print(f"PASS — generated {output_path.relative_to(ROOT)}")


def plot_clv_distribution(
    customer: pd.DataFrame,
) -> None:
    """Plot annualized CLV distribution."""

    figure, axis = plt.subplots(figsize=(11, 6))

    values = customer["annualized_clv"]

    axis.hist(
        values,
        bins=30,
        edgecolor="black",
        alpha=0.8,
    )

    median = values.median()

    axis.axvline(
        median,
        linestyle="--",
        linewidth=2,
        label=f"Median: {format_currency_value(median)}",
    )

    axis.set_title(
        "Annualized Customer Lifetime Value Distribution",
        fontsize=15,
        fontweight="bold",
    )
    axis.set_xlabel("Annualized CLV")
    axis.set_ylabel("Number of Customers")
    axis.legend()

    axis.xaxis.set_major_formatter(
        FuncFormatter(lambda value, _: f"Rp {value / 1_000_000:.1f}M")
    )

    axis.grid(
        axis="y",
        alpha=0.25,
    )

    save_figure(
        figure,
        "customer_clv_distribution.png",
    )


def plot_segment_performance(
    customer: pd.DataFrame,
) -> None:
    """Plot revenue and gross profit performance by customer segment."""

    opportunity = load_customer_opportunity()

    segment = (
        opportunity.groupby("segment", as_index=False)
        .agg(
            customers=("customer_id", "nunique"),
            revenue=("revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
        .sort_values("revenue", ascending=False)
    )

    figure, axis = plt.subplots(figsize=(11, 6))

    x = range(len(segment))
    width = 0.36

    axis.bar(
        [value - width / 2 for value in x],
        segment["revenue"] / 1_000_000,
        width=width,
        label="Revenue",
    )

    axis.bar(
        [value + width / 2 for value in x],
        segment["gross_profit"] / 1_000_000,
        width=width,
        label="Gross Profit",
    )

    axis.set_xticks(list(x))
    axis.set_xticklabels(segment["segment"])

    axis.set_title(
        "Customer Segment Revenue and Gross Profit",
        fontsize=15,
        fontweight="bold",
    )
    axis.set_xlabel("Customer Segment")
    axis.set_ylabel("Value (Rp millions)")
    axis.legend()

    axis.grid(
        axis="y",
        alpha=0.25,
    )

    save_figure(
        figure,
        "customer_segment_performance.png",
    )


def plot_clv_tiers(
    customer: pd.DataFrame,
) -> None:
    """Plot customer distribution and annualized CLV by CLV tier."""

    opportunity = load_customer_opportunity()

    tier_order = [
        "Platinum",
        "Gold",
        "Silver",
        "Bronze",
    ]

    tier = (
        opportunity.groupby("clv_tier", as_index=False)
        .agg(
            customers=("customer_id", "nunique"),
            annualized_clv=("annualized_clv", "sum"),
        )
    )

    tier["tier"] = pd.Categorical(
        tier["clv_tier"],
        categories=tier_order,
        ordered=True,
    )

    tier = tier.sort_values("tier")

    figure, axis = plt.subplots(figsize=(11, 6))

    bars = axis.bar(
        tier["clv_tier"],
        tier["annualized_clv"] / 1_000_000,
    )

    axis.set_title(
        "Annualized CLV by Customer Value Tier",
        fontsize=15,
        fontweight="bold",
    )
    axis.set_xlabel("CLV Tier")
    axis.set_ylabel("Annualized CLV (Rp millions)")

    for bar, customers in zip(
        bars,
        tier["customers"],
        strict=False,
    ):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{customers:,} customers",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    axis.grid(
        axis="y",
        alpha=0.25,
    )

    save_figure(
        figure,
        "customer_clv_tiers.png",
    )


def plot_opportunity_matrix(
    customer: pd.DataFrame,
) -> None:
    """Plot customer opportunity population and CLV contribution."""

    opportunity = load_customer_opportunity()

    summary = (
        opportunity.groupby("opportunity", as_index=False)
        .agg(
            customers=("customer_id", "nunique"),
            annualized_clv=("annualized_clv", "sum"),
        )
        .sort_values(
            "annualized_clv",
            ascending=False,
        )
    )

    figure, axis = plt.subplots(figsize=(11, 6))

    bars = axis.bar(
        summary["opportunity"],
        summary["annualized_clv"] / 1_000_000,
    )

    axis.set_title(
        "Customer Opportunity by Annualized CLV",
        fontsize=15,
        fontweight="bold",
    )
    axis.set_xlabel("Opportunity")
    axis.set_ylabel("Annualized CLV (Rp millions)")

    for bar, customers in zip(
        bars,
        summary["customers"],
        strict=False,
    ):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{customers:,}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    axis.grid(
        axis="y",
        alpha=0.25,
    )

    save_figure(
        figure,
        "customer_opportunity_matrix.png",
    )


def plot_rfm_distribution(
    customer: pd.DataFrame,
) -> None:
    """Plot customer distribution by RFM total score."""

    opportunity = load_customer_opportunity()

    rfm = (
        opportunity.groupby("rfm_total", as_index=False)
        .agg(
            customers=("customer_id", "nunique"),
        )
        .sort_values("rfm_total")
    )

    figure, axis = plt.subplots(figsize=(11, 6))

    axis.bar(
        rfm["rfm_total"],
        rfm["customers"],
        width=0.8,
    )

    axis.set_title(
        "Customer Distribution by RFM Score",
        fontsize=15,
        fontweight="bold",
    )
    axis.set_xlabel("RFM Total Score")
    axis.set_ylabel("Number of Customers")

    axis.grid(
        axis="y",
        alpha=0.25,
    )

    save_figure(
        figure,
        "customer_rfm_distribution.png",
    )


def plot_customer_performance_overview(
    customer: pd.DataFrame,
) -> None:
    """Create an executive customer performance overview."""

    opportunity = load_customer_opportunity()

    total_customers = customer["customer_id"].nunique()

    total_revenue = customer["revenue"].sum()

    total_gross_profit = customer["gross_profit"].sum()

    total_annualized_clv = customer["annualized_clv"].sum()

    median_clv = customer["annualized_clv"].median()

    platinum = opportunity.loc[
        opportunity["clv_tier"] == "Platinum"
    ]

    platinum_clv_share = (
        platinum["annualized_clv"].sum()
        / opportunity["annualized_clv"].sum()
        * 100
    )

    rescue = opportunity.loc[
        opportunity["opportunity"] == "Rescue"
    ]

    rescue_clv = rescue["annualized_clv"].sum()

    figure, axes = plt.subplots(
        2,
        2,
        figsize=(13, 9),
    )

    # 1. Revenue distribution
    axes[0, 0].hist(
        customer["revenue"],
        bins=25,
        edgecolor="black",
        alpha=0.8,
    )

    axes[0, 0].set_title(
        "Customer Revenue Distribution",
        fontweight="bold",
    )
    axes[0, 0].set_xlabel("Revenue")
    axes[0, 0].set_ylabel("Customers")

    axes[0, 0].xaxis.set_major_formatter(
        FuncFormatter(
            lambda value, _: f"Rp {value / 1_000_000:.1f}M"
        )
    )

    # 2. CLV distribution
    axes[0, 1].hist(
        customer["annualized_clv"],
        bins=25,
        edgecolor="black",
        alpha=0.8,
    )

    axes[0, 1].axvline(
        median_clv,
        linestyle="--",
        linewidth=2,
        label=f"Median: {format_currency_value(median_clv)}",
    )

    axes[0, 1].set_title(
        "Annualized CLV Distribution",
        fontweight="bold",
    )
    axes[0, 1].set_xlabel("Annualized CLV")
    axes[0, 1].set_ylabel("Customers")
    axes[0, 1].legend()

    axes[0, 1].xaxis.set_major_formatter(
        FuncFormatter(
            lambda value, _: f"Rp {value / 1_000_000:.1f}M"
        )
    )

    # 3. Opportunity distribution
    opportunity_counts = (
        opportunity["opportunity"]
        .value_counts()
        .sort_values(ascending=False)
    )

    axes[1, 0].bar(
        opportunity_counts.index,
        opportunity_counts.values,
    )

    axes[1, 0].set_title(
        "Customer Opportunity Population",
        fontweight="bold",
    )
    axes[1, 0].set_xlabel("Opportunity")
    axes[1, 0].set_ylabel("Customers")

    axes[1, 0].tick_params(
        axis="x",
        rotation=20,
    )

    # 4. KPI panel
    axes[1, 1].axis("off")

    kpis = [
        ("Customers", f"{total_customers:,}"),
        ("Revenue", format_currency_value(total_revenue)),
        ("Gross Profit", format_currency_value(total_gross_profit)),
        (
            "Annualized CLV",
            format_currency_value(total_annualized_clv),
        ),
        (
            "Platinum CLV Share",
            f"{platinum_clv_share:.1f}%",
        ),
        (
            "Rescue CLV",
            format_currency_value(rescue_clv),
        ),
    ]

    axes[1, 1].text(
        0.02,
        0.96,
        "Customer Economics",
        fontsize=13,
        fontweight="bold",
        va="top",
    )

    y_position = 0.82

    for label, value in kpis:
        axes[1, 1].text(
            0.02,
            y_position,
            label,
            fontsize=10,
            fontweight="bold",
            va="top",
        )

        axes[1, 1].text(
            0.98,
            y_position,
            value,
            fontsize=10,
            ha="right",
            va="top",
        )

        y_position -= 0.13

    figure.suptitle(
        "Mayasari Bakery Customer Performance Overview",
        fontsize=17,
        fontweight="bold",
    )

    figure.tight_layout(
        rect=(0, 0, 1, 0.95),
    )

    save_figure(
        figure,
        "customer_performance_overview.png",
    )


def generate_visualizations() -> None:
    """Generate all customer performance visualizations."""

    print("=" * 90)
    print("M23.2 — MAYASARI BAKERY CUSTOMER PERFORMANCE VISUALIZATION")
    print("=" * 90)

    print("\n--- INPUT ---")
    print(
        "Customer performance dataset:",
        CUSTOMER_PERFORMANCE_DATA,
    )
    print(
        "Customer opportunity dataset:",
        CUSTOMER_OPPORTUNITY_DATA,
    )

    customer = load_customer_performance()

    opportunity = load_customer_opportunity()

    print("\n--- DATASET ---")
    print(
        f"Customers: {customer['customer_id'].nunique():,}"
    )
    print(
        f"Opportunity rows: {opportunity['customer_id'].nunique():,}"
    )
    print(
        "Annualized CLV range: "
        f"{format_currency_value(customer['annualized_clv'].min())} "
        "to "
        f"{format_currency_value(customer['annualized_clv'].max())}"
    )

    ensure_output_directory()

    print("\n--- GENERATING VISUALIZATIONS ---")

    plot_clv_distribution(customer)
    plot_segment_performance(customer)
    plot_clv_tiers(customer)
    plot_opportunity_matrix(customer)
    plot_rfm_distribution(customer)
    plot_customer_performance_overview(customer)

    print("\n--- OUTPUT COUNT ---")

    outputs = sorted(
        OUTPUT_DIR.glob("customer_*.png")
    )

    print(
        f"Generated: {len(outputs)} visualization artifacts"
    )

    if len(outputs) != 6:
        raise RuntimeError(
            "Expected exactly 6 customer visualization artifacts."
        )

    print("\n--- RESULT ---")
    print(
        "PASS — customer performance visualizations "
        "generated successfully."
    )

    print("\n" + "=" * 90)
    print("M23.2 COMPLETE")
    print("=" * 90)


if __name__ == "__main__":
    generate_visualizations()
