from pathlib import Path

import pandas as pd


SALES_DATA = Path("data/processed/sales.parquet")
PRODUCT_DATA = Path("data/processed/products.parquet")


def load_sales_data() -> pd.DataFrame:
    """Load prepared sales data."""

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

    required_sales_columns = {
        "product_id",
        "gross_sales",
        "discount_amount",
        "net_sales",
        "quantity",
        "product_cost",
        "gross_profit",
    }

    required_product_columns = {
        "product_id",
        "product_name",
        "category",
    }

    missing_sales_columns = (
        required_sales_columns - set(sales.columns)
    )

    if missing_sales_columns:
        raise ValueError(
            "Sales dataset is missing required columns: "
            f"{sorted(missing_sales_columns)}"
        )

    missing_product_columns = (
        required_product_columns - set(products.columns)
    )

    if missing_product_columns:
        raise ValueError(
            "Product dataset is missing required columns: "
            f"{sorted(missing_product_columns)}"
        )

    if products["product_id"].duplicated().any():
        raise ValueError(
            "Product dataset contains duplicate product_id values."
        )

    sales = sales.merge(
        products[
            [
                "product_id",
                "product_name",
                "category",
            ]
        ],
        on="product_id",
        how="left",
        validate="many_to_one",
    )

    missing_product_names = (
        sales["product_name"].isna().sum()
    )

    if missing_product_names:
        raise ValueError(
            "Sales records contain product_id values "
            f"without product master data: "
            f"{missing_product_names} rows."
        )

    return sales


def build_product_profitability(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """Build product-level profitability analysis."""

    product_profitability = (
        sales.groupby(
            [
                "product_id",
                "product_name",
                "category",
            ],
            as_index=False,
        )
        .agg(
            gross_sales=("gross_sales", "sum"),
            discount=("discount_amount", "sum"),
            net_sales=("net_sales", "sum"),
            units_sold=("quantity", "sum"),
            product_cost=("product_cost", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
    )

    product_profitability["gross_margin_pct"] = (
        product_profitability["gross_profit"]
        / product_profitability["net_sales"]
        * 100
    )

    total_net_sales = (
        product_profitability["net_sales"].sum()
    )

    total_gross_profit = (
        product_profitability["gross_profit"].sum()
    )

    product_profitability["revenue_contribution_pct"] = (
        product_profitability["net_sales"]
        / total_net_sales
        * 100
    )

    product_profitability["profit_contribution_pct"] = (
        product_profitability["gross_profit"]
        / total_gross_profit
        * 100
    )

    product_profitability = (
        product_profitability.sort_values(
            "gross_profit",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return product_profitability


def build_product_rankings(
    product_profitability: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Build product profitability ranking views."""

    highest_profit = (
        product_profitability
        .sort_values(
            "gross_profit",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    highest_margin = (
        product_profitability
        .sort_values(
            "gross_margin_pct",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    lowest_margin = (
        product_profitability
        .sort_values(
            "gross_margin_pct",
            ascending=True,
        )
        .reset_index(drop=True)
    )

    highest_revenue = (
        product_profitability
        .sort_values(
            "net_sales",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return {
        "highest_profit": highest_profit,
        "highest_margin": highest_margin,
        "lowest_margin": lowest_margin,
        "highest_revenue": highest_revenue,
    }


def identify_product_profitability_segments(
    product_profitability: pd.DataFrame,
) -> pd.DataFrame:
    """Classify products using revenue and margin performance."""

    revenue_median = (
        product_profitability["net_sales"].median()
    )

    margin_median = (
        product_profitability["gross_margin_pct"].median()
    )

    result = product_profitability.copy()

    def classify(row: pd.Series) -> str:
        high_revenue = (
            row["net_sales"] >= revenue_median
        )

        high_margin = (
            row["gross_margin_pct"]
            >= margin_median
        )

        if high_revenue and high_margin:
            return "High Revenue / High Margin"

        if high_revenue and not high_margin:
            return "High Revenue / Low Margin"

        if not high_revenue and high_margin:
            return "Low Revenue / High Margin"

        return "Low Revenue / Low Margin"

    result["profitability_segment"] = (
        result.apply(
            classify,
            axis=1,
        )
    )

    return result


def build_product_insights(
    product_profitability: pd.DataFrame,
) -> list[str]:
    """Generate concise product profitability insights."""

    highest_profit = product_profitability.loc[
        product_profitability["gross_profit"].idxmax()
    ]

    highest_margin = product_profitability.loc[
        product_profitability["gross_margin_pct"].idxmax()
    ]

    lowest_margin = product_profitability.loc[
        product_profitability["gross_margin_pct"].idxmin()
    ]

    highest_revenue = product_profitability.loc[
        product_profitability["net_sales"].idxmax()
    ]

    total_products = len(product_profitability)

    revenue_median = (
        product_profitability["net_sales"].median()
    )

    margin_median = (
        product_profitability["gross_margin_pct"].median()
    )

    high_revenue_high_margin = (
        product_profitability[
            (
                product_profitability["net_sales"]
                >= revenue_median
            )
            & (
                product_profitability["gross_margin_pct"]
                >= margin_median
            )
        ]
    )

    high_revenue_low_margin = (
        product_profitability[
            (
                product_profitability["net_sales"]
                >= revenue_median
            )
            & (
                product_profitability["gross_margin_pct"]
                < margin_median
            )
        ]
    )

    insights = [
        (
            f"Highest gross profit was generated by "
            f"{highest_profit['product_name']} "
            f"({highest_profit['product_id']}) at "
            f"Rp {highest_profit['gross_profit']:,.0f}."
        ),
        (
            f"Highest revenue product was "
            f"{highest_revenue['product_name']} "
            f"({highest_revenue['product_id']}) at "
            f"Rp {highest_revenue['net_sales']:,.0f}."
        ),
        (
            f"Highest gross margin was achieved by "
            f"{highest_margin['product_name']} "
            f"({highest_margin['product_id']}) at "
            f"{highest_margin['gross_margin_pct']:.2f}%."
        ),
        (
            f"Lowest gross margin was recorded by "
            f"{lowest_margin['product_name']} "
            f"({lowest_margin['product_id']}) at "
            f"{lowest_margin['gross_margin_pct']:.2f}%."
        ),
        (
            f"The analysis covers "
            f"{total_products} products."
        ),
        (
            f"{len(high_revenue_high_margin)} products "
            f"fall into the high-revenue / high-margin segment."
        ),
        (
            f"{len(high_revenue_low_margin)} products "
            f"fall into the high-revenue / low-margin segment."
        ),
    ]

    return insights


def validate_product_profitability(
    product_profitability: pd.DataFrame,
    sales: pd.DataFrame,
) -> bool:
    """Validate product-level totals against source sales data."""

    expected = {
        "gross_sales": sales["gross_sales"].sum(),
        "discount": sales["discount_amount"].sum(),
        "net_sales": sales["net_sales"].sum(),
        "units_sold": sales["quantity"].sum(),
        "product_cost": sales["product_cost"].sum(),
        "gross_profit": sales["gross_profit"].sum(),
    }

    calculated = {
        "gross_sales": (
            product_profitability["gross_sales"].sum()
        ),
        "discount": (
            product_profitability["discount"].sum()
        ),
        "net_sales": (
            product_profitability["net_sales"].sum()
        ),
        "units_sold": (
            product_profitability["units_sold"].sum()
        ),
        "product_cost": (
            product_profitability["product_cost"].sum()
        ),
        "gross_profit": (
            product_profitability["gross_profit"].sum()
        ),
    }

    print()
    print("=" * 100)
    print("PRODUCT PROFITABILITY VALIDATION")
    print("=" * 100)

    all_pass = True

    for metric in expected:
        expected_value = expected[metric]
        calculated_value = calculated[metric]

        passed = expected_value == calculated_value

        if not passed:
            all_pass = False

        print(
            f"{metric:<20} "
            f"Calculated: {calculated_value:>15,.0f} | "
            f"Expected: {expected_value:>15,.0f} | "
            f"{'PASS' if passed else 'REVIEW'}"
        )

    return all_pass


def validate_product_mapping(
    sales: pd.DataFrame,
) -> bool:
    """Validate product master mapping."""

    total_rows = len(sales)

    mapped_rows = (
        sales["product_name"].notna().sum()
    )

    unique_products = (
        sales["product_id"].nunique()
    )

    unique_product_names = (
        sales["product_name"].nunique()
    )

    passed = (
        total_rows == mapped_rows
        and unique_products == unique_product_names
    )

    print()
    print("=" * 100)
    print("PRODUCT MASTER MAPPING VALIDATION")
    print("=" * 100)

    print(
        f"{'Sales Rows':<25}"
        f"{total_rows:>15,}"
    )

    print(
        f"{'Mapped Product Rows':<25}"
        f"{mapped_rows:>15,}"
    )

    print(
        f"{'Unique Product IDs':<25}"
        f"{unique_products:>15,}"
    )

    print(
        f"{'Unique Product Names':<25}"
        f"{unique_product_names:>15,}"
    )

    print(
        f"{'Mapping Status':<25}"
        f"{'PASS' if passed else 'REVIEW':>15}"
    )

    return passed


def print_product_profitability(
    product_profitability: pd.DataFrame,
) -> None:
    """Print product profitability table."""

    display = product_profitability[
        [
            "product_id",
            "product_name",
            "category",
            "net_sales",
            "units_sold",
            "product_cost",
            "gross_profit",
            "gross_margin_pct",
            "revenue_contribution_pct",
            "profit_contribution_pct",
        ]
    ].copy()

    display["net_sales"] = display["net_sales"].map(
        lambda value: f"Rp {value:,.0f}"
    )

    display["product_cost"] = display[
        "product_cost"
    ].map(
        lambda value: f"Rp {value:,.0f}"
    )

    display["gross_profit"] = display[
        "gross_profit"
    ].map(
        lambda value: f"Rp {value:,.0f}"
    )

    for column in [
        "gross_margin_pct",
        "revenue_contribution_pct",
        "profit_contribution_pct",
    ]:
        display[column] = display[column].map(
            lambda value: f"{value:.2f}%"
        )

    print()
    print("=" * 100)
    print("PRODUCT PROFITABILITY ANALYSIS")
    print("=" * 100)
    print()
    print(display.to_string(index=False))


def print_product_rankings(
    rankings: dict[str, pd.DataFrame],
) -> None:
    """Print key product profitability rankings."""

    ranking_config = [
        (
            "TOP PRODUCTS BY GROSS PROFIT",
            "highest_profit",
            [
                "product_id",
                "product_name",
                "gross_profit",
                "gross_margin_pct",
            ],
        ),
        (
            "TOP PRODUCTS BY GROSS MARGIN",
            "highest_margin",
            [
                "product_id",
                "product_name",
                "gross_margin_pct",
                "gross_profit",
            ],
        ),
        (
            "LOWEST-MARGIN PRODUCTS",
            "lowest_margin",
            [
                "product_id",
                "product_name",
                "gross_margin_pct",
                "gross_profit",
            ],
        ),
        (
            "TOP PRODUCTS BY NET SALES",
            "highest_revenue",
            [
                "product_id",
                "product_name",
                "net_sales",
                "gross_profit",
            ],
        ),
    ]

    for title, key, columns in ranking_config:
        print()
        print("=" * 100)
        print(title)
        print("=" * 100)

        display = rankings[key][columns].head(10).copy()

        for column in [
            "net_sales",
            "gross_profit",
        ]:
            if column in display.columns:
                display[column] = display[column].map(
                    lambda value: f"Rp {value:,.0f}"
                )

        if "gross_margin_pct" in display.columns:
            display["gross_margin_pct"] = (
                display["gross_margin_pct"].map(
                    lambda value: f"{value:.2f}%"
                )
            )

        print()
        print(display.to_string(index=False))


def print_profitability_segments(
    segmented: pd.DataFrame,
) -> None:
    """Print product profitability segment summary."""

    summary = (
        segmented.groupby(
            "profitability_segment"
        )
        .agg(
            products=("product_name", "count"),
            net_sales=("net_sales", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
        .reset_index()
    )

    summary["gross_margin_pct"] = (
        summary["gross_profit"]
        / summary["net_sales"]
        * 100
    )

    summary = summary.sort_values(
        "gross_profit",
        ascending=False,
    )

    print()
    print("=" * 100)
    print("PRODUCT PROFITABILITY SEGMENTS")
    print("=" * 100)

    display = summary.copy()

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

    print()
    print(display.to_string(index=False))


def print_insights(
    insights: list[str],
) -> None:
    """Print product profitability insights."""

    print()
    print("=" * 100)
    print("PRODUCT PROFITABILITY INSIGHTS")
    print("=" * 100)

    for index, insight in enumerate(
        insights,
        start=1,
    ):
        print(f"{index}. {insight}")


def main() -> None:
    """Run product profitability analysis."""

    print("=" * 100)
    print("MAYASARI BAKERY PRODUCT PROFITABILITY ANALYSIS")
    print("=" * 100)

    sales = load_sales_data()

    product_profitability = (
        build_product_profitability(
            sales
        )
    )

    rankings = build_product_rankings(
        product_profitability
    )

    segmented = (
        identify_product_profitability_segments(
            product_profitability
        )
    )

    insights = build_product_insights(
        product_profitability
    )

    print_product_profitability(
        product_profitability
    )

    print_product_rankings(
        rankings
    )

    print_profitability_segments(
        segmented
    )

    print_insights(
        insights
    )

    mapping_validation = (
        validate_product_mapping(
            sales
        )
    )

    profitability_validation = (
        validate_product_profitability(
            product_profitability,
            sales,
        )
    )

    print()
    print("=" * 100)

    if (
        mapping_validation
        and profitability_validation
    ):
        print(
            "PRODUCT PROFITABILITY ANALYSIS STATUS: PASS"
        )
    else:
        print(
            "PRODUCT PROFITABILITY ANALYSIS STATUS: REVIEW"
        )

    print("=" * 100)


if __name__ == "__main__":
    main()
