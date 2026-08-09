from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.contracts.paths import (
    PRODUCT_FIGURES_DIR,
    PRODUCT_PERFORMANCE_DATA,
)

PRODUCT_DATA = (
    PRODUCT_PERFORMANCE_DATA
)

PRODUCT_FIGURES = (
    PRODUCT_FIGURES_DIR
)


def load_product_data() -> pd.DataFrame:
    """Load and validate product performance dataset."""

    if not PRODUCT_DATA.exists():
        raise FileNotFoundError(
            f"Product performance dataset not found: "
            f"{PRODUCT_DATA}"
        )

    data = pd.read_parquet(
        PRODUCT_DATA
    )

    required_columns = {
        "product_id",
        "product_name",
        "category",
        "revenue",
        "gross_profit",
        "product_cost",
        "quantity",
        "transactions",
        "gross_margin_pct",
        "revenue_share_pct",
        "profit_share_pct",
        "price",
        "cost",
    }

    missing_columns = (
        required_columns
        - set(data.columns)
    )

    if missing_columns:
        raise ValueError(
            "Product performance dataset "
            "is missing columns: "
            f"{sorted(missing_columns)}"
        )

    if len(data) != 28:
        raise ValueError(
            "Expected 28 products, "
            f"found {len(data)}."
        )

    data = data.copy()

    if data["product_id"].duplicated().any():
        raise ValueError(
            "Product dataset contains "
            "duplicate product IDs."
        )

    numeric_columns = [
        "revenue",
        "gross_profit",
        "product_cost",
        "quantity",
        "transactions",
        "gross_margin_pct",
        "revenue_share_pct",
        "profit_share_pct",
        "price",
        "cost",
    ]

    if data[numeric_columns].isna().any().any():
        raise ValueError(
            "Product dataset contains "
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


def create_product_dashboard(
    product: pd.DataFrame,
) -> Path:
    """Create product performance dashboard."""

    PRODUCT_FIGURES.mkdir(
        parents=True,
        exist_ok=True,
    )

    product = product.sort_values(
        "revenue",
        ascending=False,
    ).reset_index(drop=True)

    # --------------------------------------------------
    # Product metrics
    # --------------------------------------------------

    total_revenue = product[
        "revenue"
    ].sum()

    total_profit = product[
        "gross_profit"
    ].sum()

    average_margin = (
        total_profit
        / total_revenue
        * 100
    )

    top10 = product.head(10)

    top10_revenue_share = (
        top10["revenue"].sum()
        / total_revenue
        * 100
    )

    # --------------------------------------------------
    # Category performance
    # --------------------------------------------------

    category = (
        product.groupby("category")
        .agg(
            revenue=("revenue", "sum"),
            gross_profit=(
                "gross_profit",
                "sum",
            ),
            quantity=(
                "quantity",
                "sum",
            ),
        )
        .reset_index()
    )

    category["gross_margin_pct"] = (
        category["gross_profit"]
        / category["revenue"]
        * 100
    )

    category = category.sort_values(
        "revenue",
        ascending=False,
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
        "Mayasari Bakery — Product Dashboard",
        fontsize=18,
        fontweight="bold",
    )

    # --------------------------------------------------
    # 1. Top 10 Products by Revenue
    # --------------------------------------------------

    ax = axes[0, 0]

    top10_plot = top10.sort_values(
        "revenue"
    )

    ax.barh(
        top10_plot["product_name"],
        top10_plot["revenue"] / 1_000_000,
    )

    ax.set_title(
        "Top 10 Products by Revenue"
    )

    ax.set_xlabel(
        "Revenue (Rp Million)"
    )

    ax.set_ylabel(
        "Product"
    )

    ax.grid(
        axis="x",
        alpha=0.25,
    )

    # --------------------------------------------------
    # 2. Product Gross Margin
    # --------------------------------------------------

    ax = axes[0, 1]

    margin_plot = product.sort_values(
        "gross_margin_pct"
    )

    ax.barh(
        margin_plot["product_name"],
        margin_plot["gross_margin_pct"],
    )

    ax.set_title(
        "Product Gross Margin"
    )

    ax.set_xlabel(
        "Gross Margin (%)"
    )

    ax.set_ylabel(
        "Product"
    )

    ax.grid(
        axis="x",
        alpha=0.25,
    )

    # --------------------------------------------------
    # 3. Revenue vs Gross Margin
    # --------------------------------------------------

    ax = axes[1, 0]

    ax.scatter(
        product["revenue"] / 1_000_000,
        product["gross_margin_pct"],
        alpha=0.7,
    )

    ax.set_title(
        "Revenue vs Gross Margin"
    )

    ax.set_xlabel(
        "Revenue (Rp Million)"
    )

    ax.set_ylabel(
        "Gross Margin (%)"
    )

    ax.grid(
        alpha=0.25,
    )

    # --------------------------------------------------
    # 4. Category Revenue
    # --------------------------------------------------

    ax = axes[1, 1]

    category_plot = category.sort_values(
        "revenue"
    )

    ax.barh(
        category_plot["category"],
        category_plot["revenue"] / 1_000_000,
    )

    ax.set_title(
        "Revenue by Product Category"
    )

    ax.set_xlabel(
        "Revenue (Rp Million)"
    )

    ax.set_ylabel(
        "Category"
    )

    ax.grid(
        axis="x",
        alpha=0.25,
    )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    highest_revenue_product = (
        product.iloc[0]
    )

    highest_profit_product = product.loc[
        product["gross_profit"].idxmax()
    ]

    highest_margin_product = product.loc[
        product["gross_margin_pct"].idxmax()
    ]

    lowest_margin_product = product.loc[
        product["gross_margin_pct"].idxmin()
    ]

    summary = (
        f"Products: {len(product):,}"
        f"   |   "
        f"Revenue: "
        f"{format_currency(total_revenue)}"
        f"   |   "
        f"Gross Profit: "
        f"{format_currency(total_profit)}"
        f"   |   "
        f"Overall Margin: "
        f"{average_margin:.1f}%"
        f"   |   "
        f"Top 10 Revenue Share: "
        f"{top10_revenue_share:.1f}%"
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
        "Source: Mayasari Bakery product analytical dataset",
        ha="center",
        fontsize=8,
    )

    figure.tight_layout(
        rect=(0, 0.06, 1, 0.94)
    )

    output = (
        PRODUCT_FIGURES
        / "product_dashboard.png"
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
        "PRODUCT DASHBOARD SUMMARY"
    )
    print("=" * 80)

    print(
        f"Products              : "
        f"{len(product):,}"
    )

    print(
        f"Total revenue         : "
        f"{format_currency(total_revenue)}"
    )

    print(
        f"Total gross profit    : "
        f"{format_currency(total_profit)}"
    )

    print(
        f"Overall gross margin  : "
        f"{average_margin:.2f}%"
    )

    print(
        f"Top revenue product   : "
        f"{highest_revenue_product['product_id']} "
        f"— "
        f"{highest_revenue_product['product_name']}"
    )

    print(
        f"Top product revenue   : "
        f"{format_currency(highest_revenue_product['revenue'])}"
    )

    print(
        f"Top profit product    : "
        f"{highest_profit_product['product_id']} "
        f"— "
        f"{highest_profit_product['product_name']}"
    )

    print(
        f"Top product profit    : "
        f"{format_currency(highest_profit_product['gross_profit'])}"
    )

    print(
        f"Highest margin        : "
        f"{highest_margin_product['product_id']} "
        f"— "
        f"{highest_margin_product['product_name']} "
        f"({highest_margin_product['gross_margin_pct']:.2f}%)"
    )

    print(
        f"Lowest margin         : "
        f"{lowest_margin_product['product_id']} "
        f"— "
        f"{lowest_margin_product['product_name']} "
        f"({lowest_margin_product['gross_margin_pct']:.2f}%)"
    )

    print(
        f"Top 10 revenue share  : "
        f"{top10_revenue_share:.2f}%"
    )

    print(
        f"Categories            : "
        f"{len(category):,}"
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
        "M11.5 PRODUCT DASHBOARD VALIDATION"
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
    """Generate M11.5 product dashboard."""

    product = load_product_data()

    print("=" * 80)
    print(
        "MAYASARI BAKERY — M11.5 PRODUCT DASHBOARD"
    )
    print("=" * 80)

    output = create_product_dashboard(
        product
    )

    if not validate_output(output):
        raise SystemExit(1)

    print()
    print("=" * 80)
    print(
        "M11.5 PRODUCT DASHBOARD: PASS"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
