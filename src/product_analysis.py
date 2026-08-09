import pandas as pd

from src.contracts.paths import PRODUCTS_DATA, SALES_DATA

PRODUCT_DATA = PRODUCTS_DATA


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load prepared sales and product data."""
    if not SALES_DATA.exists():
        raise FileNotFoundError(
            f"Processed sales data not found: {SALES_DATA}"
        )

    if not PRODUCT_DATA.exists():
        raise FileNotFoundError(
            f"Processed product data not found: {PRODUCT_DATA}"
        )

    sales = pd.read_parquet(SALES_DATA)
    products = pd.read_parquet(PRODUCT_DATA)

    return sales, products


def build_product_analysis(
    sales: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Build product-level sales and profitability analysis."""

    product_sales = (
        sales.groupby("product_id", as_index=False)
        .agg(
            units_sold=("quantity", "sum"),
            sales_lines=("transaction_line_key", "nunique"),
            transactions=("transaction_key", "nunique"),
            gross_sales=("gross_sales", "sum"),
            discount=("discount_amount", "sum"),
            net_sales=("net_sales", "sum"),
            product_cost=("product_cost", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
    )

    analysis = products.merge(
        product_sales,
        on="product_id",
        how="left",
        validate="one_to_one",
    )

    numeric_columns = [
        "units_sold",
        "sales_lines",
        "transactions",
        "gross_sales",
        "discount",
        "net_sales",
        "product_cost",
        "gross_profit",
    ]

    analysis[numeric_columns] = (
        analysis[numeric_columns]
        .fillna(0)
    )

    analysis["gross_margin_pct"] = (
        analysis["gross_profit"]
        / analysis["net_sales"]
        .replace(0, pd.NA)
        * 100
    )

    analysis["revenue_share_pct"] = (
        analysis["net_sales"]
        / analysis["net_sales"].sum()
        * 100
    )

    analysis["profit_share_pct"] = (
        analysis["gross_profit"]
        / analysis["gross_profit"].sum()
        * 100
    )

    analysis["avg_selling_price"] = (
        analysis["net_sales"]
        / analysis["units_sold"]
        .replace(0, pd.NA)
    )

    analysis["profit_per_unit"] = (
        analysis["gross_profit"]
        / analysis["units_sold"]
        .replace(0, pd.NA)
    )

    analysis = analysis.sort_values(
        "net_sales",
        ascending=False,
    ).reset_index(drop=True)

    analysis["revenue_rank"] = (
        analysis["net_sales"]
        .rank(
            method="min",
            ascending=False,
        )
        .astype(int)
    )

    analysis["profit_rank"] = (
        analysis["gross_profit"]
        .rank(
            method="min",
            ascending=False,
        )
        .astype(int)
    )

    return analysis


def build_category_analysis(
    product_analysis: pd.DataFrame,
) -> pd.DataFrame:
    """Build category-level sales and profitability analysis."""

    category = (
        product_analysis.groupby(
            "category",
            as_index=False,
        )
        .agg(
            products=("product_id", "nunique"),
            units_sold=("units_sold", "sum"),
            sales_lines=("sales_lines", "sum"),
            transactions=("transactions", "sum"),
            gross_sales=("gross_sales", "sum"),
            discount=("discount", "sum"),
            net_sales=("net_sales", "sum"),
            product_cost=("product_cost", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
    )

    category["gross_margin_pct"] = (
        category["gross_profit"]
        / category["net_sales"]
        .replace(0, pd.NA)
        * 100
    )

    category["revenue_share_pct"] = (
        category["net_sales"]
        / category["net_sales"].sum()
        * 100
    )

    category["profit_share_pct"] = (
        category["gross_profit"]
        / category["gross_profit"].sum()
        * 100
    )

    category["avg_transaction_value"] = (
        category["net_sales"]
        / category["transactions"]
        .replace(0, pd.NA)
    )

    category = category.sort_values(
        "net_sales",
        ascending=False,
    ).reset_index(drop=True)

    category["revenue_rank"] = (
        category["net_sales"]
        .rank(
            method="min",
            ascending=False,
        )
        .astype(int)
    )

    category["profit_rank"] = (
        category["gross_profit"]
        .rank(
            method="min",
            ascending=False,
        )
        .astype(int)
    )

    return category


def print_product_analysis(
    product_analysis: pd.DataFrame,
) -> None:
    """Print product-level analysis."""

    print()
    print("=" * 80)
    print("PRODUCT PERFORMANCE")
    print("=" * 80)

    columns = [
        "product_id",
        "product_name",
        "category",
        "units_sold",
        "net_sales",
        "gross_profit",
        "gross_margin_pct",
        "revenue_rank",
    ]

    display = product_analysis[columns].copy()

    display["net_sales"] = display["net_sales"].map(
        lambda value: f"Rp {value:,.0f}"
    )

    display["gross_profit"] = display["gross_profit"].map(
        lambda value: f"Rp {value:,.0f}"
    )

    display["gross_margin_pct"] = display[
        "gross_margin_pct"
    ].map(
        lambda value: (
            f"{value:.2f}%"
            if pd.notna(value)
            else "N/A"
        )
    )

    print()
    print("TOP 10 PRODUCTS BY NET SALES")
    print("-" * 80)

    print(
        display.head(10).to_string(
            index=False
        )
    )

    print()
    print("BOTTOM 10 PRODUCTS BY NET SALES")
    print("-" * 80)

    print(
        display.tail(10).to_string(
            index=False
        )
    )


def print_category_analysis(
    category_analysis: pd.DataFrame,
) -> None:
    """Print category-level analysis."""

    print()
    print("=" * 80)
    print("CATEGORY PERFORMANCE")
    print("=" * 80)

    display = category_analysis[
        [
            "category",
            "products",
            "units_sold",
            "net_sales",
            "gross_profit",
            "gross_margin_pct",
            "revenue_share_pct",
            "profit_share_pct",
        ]
    ].copy()

    display["net_sales"] = display["net_sales"].map(
        lambda value: f"Rp {value:,.0f}"
    )

    display["gross_profit"] = display[
        "gross_profit"
    ].map(
        lambda value: f"Rp {value:,.0f}"
    )

    display["gross_margin_pct"] = display[
        "gross_margin_pct"
    ].map(
        lambda value: f"{value:.2f}%"
    )

    display["revenue_share_pct"] = display[
        "revenue_share_pct"
    ].map(
        lambda value: f"{value:.2f}%"
    )

    display["profit_share_pct"] = display[
        "profit_share_pct"
    ].map(
        lambda value: f"{value:.2f}%"
    )

    print()
    print(
        display.to_string(
            index=False
        )
    )


def print_margin_opportunities(
    product_analysis: pd.DataFrame,
) -> None:
    """Print products with high revenue but comparatively low margins."""

    print()
    print("=" * 80)
    print("MARGIN OPPORTUNITIES")
    print("=" * 80)

    margin_threshold = (
        product_analysis["gross_margin_pct"]
        .median()
    )

    revenue_threshold = (
        product_analysis["net_sales"]
        .median()
    )

    opportunities = product_analysis[
        (
            product_analysis["net_sales"]
            >= revenue_threshold
        )
        & (
            product_analysis["gross_margin_pct"]
            < margin_threshold
        )
    ].copy()

    opportunities = opportunities.sort_values(
        "net_sales",
        ascending=False,
    )

    print()
    print(
        f"Revenue threshold : "
        f"Rp {revenue_threshold:,.0f}"
    )

    print(
        f"Margin threshold  : "
        f"{margin_threshold:.2f}%"
    )

    print()

    if opportunities.empty:
        print(
            "No products meet the high-revenue / "
            "low-margin criteria."
        )
        return

    display = opportunities[
        [
            "product_id",
            "product_name",
            "category",
            "net_sales",
            "gross_profit",
            "gross_margin_pct",
        ]
    ].copy()

    display["net_sales"] = display["net_sales"].map(
        lambda value: f"Rp {value:,.0f}"
    )

    display["gross_profit"] = display[
        "gross_profit"
    ].map(
        lambda value: f"Rp {value:,.0f}"
    )

    display["gross_margin_pct"] = display[
        "gross_margin_pct"
    ].map(
        lambda value: f"{value:.2f}%"
    )

    print(
        display.to_string(
            index=False
        )
    )


def validate_totals(
    sales: pd.DataFrame,
    product_analysis: pd.DataFrame,
) -> bool:
    """Validate product aggregation against source sales totals."""

    source_metrics = {
        "units_sold": sales["quantity"].sum(),
        "gross_sales": sales["gross_sales"].sum(),
        "discount": sales["discount_amount"].sum(),
        "net_sales": sales["net_sales"].sum(),
        "product_cost": sales["product_cost"].sum(),
        "gross_profit": sales["gross_profit"].sum(),
    }

    aggregated_metrics = {
        "units_sold": product_analysis["units_sold"].sum(),
        "gross_sales": product_analysis["gross_sales"].sum(),
        "discount": product_analysis["discount"].sum(),
        "net_sales": product_analysis["net_sales"].sum(),
        "product_cost": product_analysis["product_cost"].sum(),
        "gross_profit": product_analysis["gross_profit"].sum(),
    }

    print()
    print("=" * 80)
    print("PRODUCT AGGREGATION VALIDATION")
    print("=" * 80)

    all_pass = True

    for metric, source_value in source_metrics.items():
        aggregated_value = aggregated_metrics[metric]

        passed = source_value == aggregated_value

        if not passed:
            all_pass = False

        print(
            f"{metric:<15} "
            f"Source: {source_value:>15,.0f} | "
            f"Products: {aggregated_value:>15,.0f} | "
            f"{'PASS' if passed else 'REVIEW'}"
        )

    return all_pass


def main() -> None:
    """Run product and category analysis."""

    sales, products = load_data()

    product_analysis = build_product_analysis(
        sales,
        products,
    )

    category_analysis = build_category_analysis(
        product_analysis
    )

    print_product_analysis(
        product_analysis
    )

    print_category_analysis(
        category_analysis
    )

    print_margin_opportunities(
        product_analysis
    )

    validation_pass = validate_totals(
        sales,
        product_analysis,
    )

    print()
    print("=" * 80)

    if validation_pass:
        print("PRODUCT ANALYSIS STATUS: PASS")
    else:
        print("PRODUCT ANALYSIS STATUS: REVIEW")

    print("=" * 80)


if __name__ == "__main__":
    main()
