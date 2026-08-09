from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ANALYTICS_DIR = Path("data/analytics")
FIGURES_DIR = Path("reports/figures")

CUSTOMER_DATA = (
    ANALYTICS_DIR / "customer_performance.parquet"
)

CUSTOMER_FIGURES = (
    FIGURES_DIR / "customers"
)


def load_customer_data() -> pd.DataFrame:
    """Load and validate customer performance dataset."""

    if not CUSTOMER_DATA.exists():
        raise FileNotFoundError(
            f"Customer performance dataset not found: "
            f"{CUSTOMER_DATA}"
        )

    data = pd.read_parquet(
        CUSTOMER_DATA
    )

    required_columns = {
        "customer_id",
        "revenue",
        "gross_profit",
        "transactions",
        "active_months",
        "gross_margin_pct",
        "average_transaction_value",
        "historical_clv",
        "annualized_clv",
    }

    missing_columns = (
        required_columns
        - set(data.columns)
    )

    if missing_columns:
        raise ValueError(
            "Customer performance dataset "
            "is missing columns: "
            f"{sorted(missing_columns)}"
        )

    if len(data) != 850:
        raise ValueError(
            "Expected 850 customers, "
            f"found {len(data)}."
        )

    data = data.copy()

    if data["customer_id"].duplicated().any():
        raise ValueError(
            "Customer dataset contains "
            "duplicate customer IDs."
        )

    numeric_columns = [
        "revenue",
        "gross_profit",
        "transactions",
        "active_months",
        "gross_margin_pct",
        "average_transaction_value",
        "historical_clv",
        "annualized_clv",
    ]

    if data[numeric_columns].isna().any().any():
        raise ValueError(
            "Customer dataset contains "
            "unexpected null values."
        )

    return data


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


def create_customer_dashboard(
    customer: pd.DataFrame,
) -> Path:
    """Create customer performance dashboard."""

    CUSTOMER_FIGURES.mkdir(
        parents=True,
        exist_ok=True,
    )

    customer = customer.sort_values(
        "revenue",
        ascending=False,
    ).reset_index(drop=True)

    top10 = customer.head(10)

    # --------------------------------------------------
    # Customer concentration
    # --------------------------------------------------

    total_revenue = customer[
        "revenue"
    ].sum()

    customer["revenue_share_pct"] = (
        customer["revenue"]
        / total_revenue
        * 100
    )

    customer["cumulative_revenue_pct"] = (
        customer["revenue_share_pct"]
        .cumsum()
    )

    top10_revenue_share = (
        top10["revenue"].sum()
        / total_revenue
        * 100
    )

    top20_revenue_share = (
        customer.head(20)["revenue"].sum()
        / total_revenue
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
        "Mayasari Bakery — Customer Dashboard",
        fontsize=18,
        fontweight="bold",
    )

    # --------------------------------------------------
    # 1. Top 10 Customers by Revenue
    # --------------------------------------------------

    ax = axes[0, 0]

    top10_plot = top10.sort_values(
        "revenue"
    )

    ax.barh(
        top10_plot["customer_id"],
        top10_plot["revenue"] / 1_000_000,
    )

    ax.set_title(
        "Top 10 Customers by Revenue"
    )

    ax.set_xlabel(
        "Revenue (Rp Million)"
    )

    ax.set_ylabel(
        "Customer"
    )

    ax.grid(
        axis="x",
        alpha=0.25,
    )

    # --------------------------------------------------
    # 2. Customer Revenue Distribution
    # --------------------------------------------------

    ax = axes[0, 1]

    ax.hist(
        customer["revenue"] / 1_000_000,
        bins=20,
    )

    ax.set_title(
        "Customer Revenue Distribution"
    )

    ax.set_xlabel(
        "Customer Revenue (Rp Million)"
    )

    ax.set_ylabel(
        "Number of Customers"
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    # --------------------------------------------------
    # 3. Revenue Concentration
    # --------------------------------------------------

    ax = axes[1, 0]

    ranks = range(
        1,
        len(customer) + 1,
    )

    ax.plot(
        ranks,
        customer[
            "cumulative_revenue_pct"
        ],
        linewidth=2,
    )

    ax.axhline(
        50,
        linestyle="--",
        linewidth=1,
        label="50% Revenue",
    )

    ax.axhline(
        80,
        linestyle="--",
        linewidth=1,
        label="80% Revenue",
    )

    ax.set_title(
        "Customer Revenue Concentration"
    )

    ax.set_xlabel(
        "Customer Rank"
    )

    ax.set_ylabel(
        "Cumulative Revenue (%)"
    )

    ax.set_ylim(
        0,
        105,
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    ax.legend()

    # --------------------------------------------------
    # 4. Customer Value — Revenue vs CLV
    # --------------------------------------------------

    ax = axes[1, 1]

    ax.scatter(
        customer["revenue"] / 1_000_000,
        customer["historical_clv"] / 1_000_000,
        alpha=0.6,
    )

    ax.set_title(
        "Customer Revenue vs Historical CLV"
    )

    ax.set_xlabel(
        "Revenue (Rp Million)"
    )

    ax.set_ylabel(
        "Historical CLV (Rp Million)"
    )

    ax.grid(
        alpha=0.25,
    )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    highest_value_customer = customer.iloc[0]

    average_revenue = (
        customer["revenue"].mean()
    )

    average_clv = (
        customer["historical_clv"].mean()
    )

    average_transactions = (
        customer["transactions"].mean()
    )

    summary = (
        f"Customers: {len(customer):,}"
        f"   |   "
        f"Avg Revenue: "
        f"{format_currency(average_revenue)}"
        f"   |   "
        f"Avg CLV: "
        f"{format_currency(average_clv)}"
        f"   |   "
        f"Top 10 Revenue Share: "
        f"{top10_revenue_share:.1f}%"
        f"   |   "
        f"Top 20 Revenue Share: "
        f"{top20_revenue_share:.1f}%"
        f"   |   "
        f"Avg Transactions: "
        f"{average_transactions:.1f}"
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
        "Source: Mayasari Bakery customer analytical dataset",
        ha="center",
        fontsize=8,
    )

    figure.tight_layout(
        rect=(0, 0.06, 1, 0.94)
    )

    output = (
        CUSTOMER_FIGURES
        / "customer_dashboard.png"
    )

    figure.savefig(
        output,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(figure)

    print()
    print("=" * 80)
    print(
        "CUSTOMER DASHBOARD SUMMARY"
    )
    print("=" * 80)

    print(
        f"Customers             : "
        f"{len(customer):,}"
    )

    print(
        f"Total revenue         : "
        f"{format_currency(total_revenue)}"
    )

    print(
        f"Average customer rev. : "
        f"{format_currency(average_revenue)}"
    )

    print(
        f"Average historical CLV: "
        f"{format_currency(average_clv)}"
    )

    print(
        f"Average transactions  : "
        f"{average_transactions:.2f}"
    )

    print(
        f"Top customer          : "
        f"{highest_value_customer['customer_id']}"
    )

    print(
        f"Top customer revenue  : "
        f"{format_currency(highest_value_customer['revenue'])}"
    )

    print(
        f"Top 10 revenue share  : "
        f"{top10_revenue_share:.2f}%"
    )

    print(
        f"Top 20 revenue share  : "
        f"{top20_revenue_share:.2f}%"
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
        "M11.4 CUSTOMER DASHBOARD VALIDATION"
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
    """Generate M11.4 customer dashboard."""

    customer = load_customer_data()

    print("=" * 80)
    print(
        "MAYASARI BAKERY — M11.4 CUSTOMER DASHBOARD"
    )
    print("=" * 80)

    output = create_customer_dashboard(
        customer
    )

    if not validate_output(output):
        raise SystemExit(1)

    print()
    print("=" * 80)
    print(
        "M11.4 CUSTOMER DASHBOARD: PASS"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
