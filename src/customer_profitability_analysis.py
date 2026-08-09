from pathlib import Path

import pandas as pd


SALES_DATA = Path("data/processed/sales.parquet")
CUSTOMER_DATA = Path("data/processed/customers.parquet")


def load_customer_sales_data() -> pd.DataFrame:
    """Load sales data and enrich it with customer master data."""

    if not SALES_DATA.exists():
        raise FileNotFoundError(
            f"Processed sales data not found: {SALES_DATA}"
        )

    if not CUSTOMER_DATA.exists():
        raise FileNotFoundError(
            f"Processed customer data not found: {CUSTOMER_DATA}"
        )

    sales = pd.read_parquet(SALES_DATA)
    customers = pd.read_parquet(CUSTOMER_DATA)

    required_sales_columns = {
        "transaction_key",
        "customer_id",
        "quantity",
        "gross_sales",
        "discount_amount",
        "net_sales",
        "product_cost",
        "gross_profit",
    }

    required_customer_columns = {
        "customer_id",
        "customer_name",
        "customer_segment",
    }

    missing_sales_columns = (
        required_sales_columns - set(sales.columns)
    )

    if missing_sales_columns:
        raise ValueError(
            "Sales dataset is missing required columns: "
            f"{sorted(missing_sales_columns)}"
        )

    missing_customer_columns = (
        required_customer_columns - set(customers.columns)
    )

    if missing_customer_columns:
        raise ValueError(
            "Customer dataset is missing required columns: "
            f"{sorted(missing_customer_columns)}"
        )

    if customers["customer_id"].duplicated().any():
        raise ValueError(
            "Customer dataset contains duplicate customer_id values."
        )

    sales = sales.merge(
        customers[
            [
                "customer_id",
                "customer_name",
                "customer_segment",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    missing_customer_names = (
        sales["customer_name"].isna().sum()
    )

    if missing_customer_names:
        raise ValueError(
            "Sales records contain customer_id values "
            "without customer master data: "
            f"{missing_customer_names} rows."
        )

    return sales


def build_customer_profitability(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """Build customer-level profitability analysis."""

    customer_profitability = (
        sales.groupby(
            [
                "customer_id",
                "customer_name",
                "customer_segment",
            ],
            as_index=False,
        )
        .agg(
            transactions=("transaction_key", "nunique"),
            gross_sales=("gross_sales", "sum"),
            discount=("discount_amount", "sum"),
            net_sales=("net_sales", "sum"),
            units_sold=("quantity", "sum"),
            product_cost=("product_cost", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
    )

    customer_profitability["average_transaction_value"] = (
        customer_profitability["net_sales"]
        / customer_profitability["transactions"]
    )

    customer_profitability["gross_margin_pct"] = (
        customer_profitability["gross_profit"]
        / customer_profitability["net_sales"]
        * 100
    )

    total_net_sales = (
        customer_profitability["net_sales"].sum()
    )

    total_gross_profit = (
        customer_profitability["gross_profit"].sum()
    )

    customer_profitability["revenue_contribution_pct"] = (
        customer_profitability["net_sales"]
        / total_net_sales
        * 100
    )

    customer_profitability["profit_contribution_pct"] = (
        customer_profitability["gross_profit"]
        / total_gross_profit
        * 100
    )

    customer_profitability = (
        customer_profitability.sort_values(
            "gross_profit",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return customer_profitability


def build_customer_rankings(
    customer_profitability: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Build customer profitability ranking views."""

    highest_revenue = (
        customer_profitability
        .sort_values(
            "net_sales",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    highest_profit = (
        customer_profitability
        .sort_values(
            "gross_profit",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    highest_margin = (
        customer_profitability
        .sort_values(
            "gross_margin_pct",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    lowest_margin = (
        customer_profitability
        .sort_values(
            "gross_margin_pct",
            ascending=True,
        )
        .reset_index(drop=True)
    )

    highest_transaction_value = (
        customer_profitability
        .sort_values(
            "average_transaction_value",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return {
        "highest_revenue": highest_revenue,
        "highest_profit": highest_profit,
        "highest_margin": highest_margin,
        "lowest_margin": lowest_margin,
        "highest_transaction_value": (
            highest_transaction_value
        ),
    }


def identify_customer_profitability_tiers(
    customer_profitability: pd.DataFrame,
) -> pd.DataFrame:
    """
    Classify customers using revenue and gross margin medians.

    Tier logic:
        High Value / High Margin
        High Value / Low Margin
        Low Value / High Margin
        Low Value / Low Margin
    """

    revenue_median = (
        customer_profitability["net_sales"].median()
    )

    margin_median = (
        customer_profitability["gross_margin_pct"].median()
    )

    result = customer_profitability.copy()

    high_value = (
        result["net_sales"] >= revenue_median
    )

    high_margin = (
        result["gross_margin_pct"] >= margin_median
    )

    result["profitability_tier"] = "Low Value / Low Margin"

    result.loc[
        high_value & high_margin,
        "profitability_tier",
    ] = "High Value / High Margin"

    result.loc[
        high_value & ~high_margin,
        "profitability_tier",
    ] = "High Value / Low Margin"

    result.loc[
        ~high_value & high_margin,
        "profitability_tier",
    ] = "Low Value / High Margin"

    return result


def build_customer_insights(
    customer_profitability: pd.DataFrame,
) -> list[str]:
    """Generate concise customer profitability insights."""

    highest_revenue = customer_profitability.loc[
        customer_profitability["net_sales"].idxmax()
    ]

    highest_profit = customer_profitability.loc[
        customer_profitability["gross_profit"].idxmax()
    ]

    highest_margin = customer_profitability.loc[
        customer_profitability["gross_margin_pct"].idxmax()
    ]

    lowest_margin = customer_profitability.loc[
        customer_profitability["gross_margin_pct"].idxmin()
    ]

    highest_atv = customer_profitability.loc[
        customer_profitability[
            "average_transaction_value"
        ].idxmax()
    ]

    total_customers = len(customer_profitability)

    revenue_median = (
        customer_profitability["net_sales"].median()
    )

    margin_median = (
        customer_profitability["gross_margin_pct"].median()
    )

    high_value_high_margin = customer_profitability[
        (
            customer_profitability["net_sales"]
            >= revenue_median
        )
        & (
            customer_profitability["gross_margin_pct"]
            >= margin_median
        )
    ]

    high_value_low_margin = customer_profitability[
        (
            customer_profitability["net_sales"]
            >= revenue_median
        )
        & (
            customer_profitability["gross_margin_pct"]
            < margin_median
        )
    ]

    low_value_high_margin = customer_profitability[
        (
            customer_profitability["net_sales"]
            < revenue_median
        )
        & (
            customer_profitability["gross_margin_pct"]
            >= margin_median
        )
    ]

    low_value_low_margin = customer_profitability[
        (
            customer_profitability["net_sales"]
            < revenue_median
        )
        & (
            customer_profitability["gross_margin_pct"]
            < margin_median
        )
    ]

    insights = [
        (
            f"Highest revenue customer was "
            f"{highest_revenue['customer_name']} "
            f"({highest_revenue['customer_id']}) "
            f"at Rp "
            f"{highest_revenue['net_sales']:,.0f}."
        ),
        (
            f"Highest gross profit customer was "
            f"{highest_profit['customer_name']} "
            f"({highest_profit['customer_id']}) "
            f"at Rp "
            f"{highest_profit['gross_profit']:,.0f}."
        ),
        (
            f"Highest gross margin was achieved by "
            f"{highest_margin['customer_name']} "
            f"({highest_margin['customer_id']}) "
            f"at "
            f"{highest_margin['gross_margin_pct']:.2f}%."
        ),
        (
            f"Lowest gross margin was recorded by "
            f"{lowest_margin['customer_name']} "
            f"({lowest_margin['customer_id']}) "
            f"at "
            f"{lowest_margin['gross_margin_pct']:.2f}%."
        ),
        (
            f"Highest average transaction value was "
            f"generated by "
            f"{highest_atv['customer_name']} "
            f"({highest_atv['customer_id']}) "
            f"at Rp "
            f"{highest_atv['average_transaction_value']:,.0f}."
        ),
        (
            f"The analysis covers "
            f"{total_customers:,} active customers."
        ),
        (
            f"{len(high_value_high_margin):,} customers "
            f"fall into the high-value / high-margin tier."
        ),
        (
            f"{len(high_value_low_margin):,} customers "
            f"fall into the high-value / low-margin tier."
        ),
        (
            f"{len(low_value_high_margin):,} customers "
            f"fall into the low-value / high-margin tier."
        ),
        (
            f"{len(low_value_low_margin):,} customers "
            f"fall into the low-value / low-margin tier."
        ),
    ]

    return insights


def validate_customer_mapping(
    sales: pd.DataFrame,
) -> bool:
    """Validate customer master mapping."""

    total_rows = len(sales)

    mapped_rows = (
        sales["customer_name"].notna().sum()
    )

    unique_customer_ids = (
        sales["customer_id"].nunique()
    )

    unique_customer_names = (
        sales["customer_name"].nunique()
    )

    passed = (
        total_rows == mapped_rows
        and unique_customer_ids == unique_customer_names
    )

    print()
    print("=" * 100)
    print("CUSTOMER MASTER MAPPING VALIDATION")
    print("=" * 100)

    print(
        f"{'Sales Rows':<30}"
        f"{total_rows:>15,}"
    )

    print(
        f"{'Mapped Customer Rows':<30}"
        f"{mapped_rows:>15,}"
    )

    print(
        f"{'Unique Customer IDs':<30}"
        f"{unique_customer_ids:>15,}"
    )

    print(
        f"{'Unique Customer Names':<30}"
        f"{unique_customer_names:>15,}"
    )

    print(
        f"{'Mapping Status':<30}"
        f"{'PASS' if passed else 'REVIEW':>15}"
    )

    return passed


def validate_customer_profitability(
    customer_profitability: pd.DataFrame,
    sales: pd.DataFrame,
) -> bool:
    """Validate customer-level totals against source sales data."""

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
            customer_profitability["gross_sales"].sum()
        ),
        "discount": (
            customer_profitability["discount"].sum()
        ),
        "net_sales": (
            customer_profitability["net_sales"].sum()
        ),
        "units_sold": (
            customer_profitability["units_sold"].sum()
        ),
        "product_cost": (
            customer_profitability["product_cost"].sum()
        ),
        "gross_profit": (
            customer_profitability["gross_profit"].sum()
        ),
    }

    print()
    print("=" * 100)
    print("CUSTOMER PROFITABILITY VALIDATION")
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


def print_customer_profitability(
    customer_profitability: pd.DataFrame,
) -> None:
    """Print customer profitability table."""

    display = customer_profitability[
        [
            "customer_id",
            "customer_name",
            "customer_segment",
            "transactions",
            "units_sold",
            "net_sales",
            "product_cost",
            "gross_profit",
            "gross_margin_pct",
            "average_transaction_value",
            "revenue_contribution_pct",
            "profit_contribution_pct",
        ]
    ].copy()

    for column in [
        "net_sales",
        "product_cost",
        "gross_profit",
        "average_transaction_value",
    ]:
        display[column] = display[column].map(
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
    print("CUSTOMER PROFITABILITY ANALYSIS")
    print("=" * 100)
    print()
    print(display.to_string(index=False))


def print_customer_rankings(
    rankings: dict[str, pd.DataFrame],
) -> None:
    """Print key customer profitability rankings."""

    ranking_config = [
        (
            "TOP CUSTOMERS BY NET SALES",
            "highest_revenue",
            [
                "customer_id",
                "customer_name",
                "customer_segment",
                "net_sales",
                "gross_profit",
                "gross_margin_pct",
            ],
        ),
        (
            "TOP CUSTOMERS BY GROSS PROFIT",
            "highest_profit",
            [
                "customer_id",
                "customer_name",
                "customer_segment",
                "gross_profit",
                "net_sales",
                "gross_margin_pct",
            ],
        ),
        (
            "TOP CUSTOMERS BY GROSS MARGIN",
            "highest_margin",
            [
                "customer_id",
                "customer_name",
                "customer_segment",
                "gross_margin_pct",
                "gross_profit",
                "net_sales",
            ],
        ),
        (
            "LOWEST-MARGIN CUSTOMERS",
            "lowest_margin",
            [
                "customer_id",
                "customer_name",
                "customer_segment",
                "gross_margin_pct",
                "gross_profit",
                "net_sales",
            ],
        ),
        (
            "TOP CUSTOMERS BY AVERAGE TRANSACTION VALUE",
            "highest_transaction_value",
            [
                "customer_id",
                "customer_name",
                "customer_segment",
                "average_transaction_value",
                "transactions",
                "net_sales",
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
            "average_transaction_value",
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


def print_profitability_tiers(
    tiered: pd.DataFrame,
) -> None:
    """Print customer profitability tier summary."""

    summary = (
        tiered.groupby(
            "profitability_tier"
        )
        .agg(
            customers=("customer_id", "count"),
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

    summary["revenue_contribution_pct"] = (
        summary["net_sales"]
        / tiered["net_sales"].sum()
        * 100
    )

    summary["profit_contribution_pct"] = (
        summary["gross_profit"]
        / tiered["gross_profit"].sum()
        * 100
    )

    summary = summary.sort_values(
        "gross_profit",
        ascending=False,
    )

    print()
    print("=" * 100)
    print("CUSTOMER PROFITABILITY TIERS")
    print("=" * 100)

    display = summary.copy()

    for column in [
        "net_sales",
        "gross_profit",
    ]:
        display[column] = display[column].map(
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
    print(display.to_string(index=False))


def print_insights(
    insights: list[str],
) -> None:
    """Print customer profitability insights."""

    print()
    print("=" * 100)
    print("CUSTOMER PROFITABILITY INSIGHTS")
    print("=" * 100)

    for index, insight in enumerate(
        insights,
        start=1,
    ):
        print(f"{index}. {insight}")


def main() -> None:
    """Run customer profitability analysis."""

    print("=" * 100)
    print("MAYASARI BAKERY CUSTOMER PROFITABILITY ANALYSIS")
    print("=" * 100)

    sales = load_customer_sales_data()

    customer_profitability = (
        build_customer_profitability(
            sales
        )
    )

    rankings = build_customer_rankings(
        customer_profitability
    )

    tiered = (
        identify_customer_profitability_tiers(
            customer_profitability
        )
    )

    insights = build_customer_insights(
        customer_profitability
    )

    print_customer_profitability(
        customer_profitability
    )

    print_customer_rankings(
        rankings
    )

    print_profitability_tiers(
        tiered
    )

    print_insights(
        insights
    )

    mapping_validation = (
        validate_customer_mapping(
            sales
        )
    )

    profitability_validation = (
        validate_customer_profitability(
            customer_profitability,
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
            "CUSTOMER PROFITABILITY ANALYSIS STATUS: PASS"
        )
    else:
        print(
            "CUSTOMER PROFITABILITY ANALYSIS STATUS: REVIEW"
        )

    print("=" * 100)


if __name__ == "__main__":
    main()
