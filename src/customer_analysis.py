
import pandas as pd

from src.contracts.paths import CUSTOMERS_DATA, SALES_DATA

CUSTOMER_DATA = CUSTOMERS_DATA




def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load prepared sales and customer data."""
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

    return sales, customers


def build_customer_analysis(
    sales: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Build customer-level sales and profitability analysis."""

    customer_sales = (
        sales.groupby("customer_id", as_index=False)
        .agg(
            sales_lines=("transaction_line_key", "nunique"),
            transactions=("transaction_key", "nunique"),
            units_sold=("quantity", "sum"),
            gross_sales=("gross_sales", "sum"),
            discount=("discount_amount", "sum"),
            net_sales=("net_sales", "sum"),
            product_cost=("product_cost", "sum"),
            gross_profit=("gross_profit", "sum"),
            first_purchase_date=("transaction_date", "min"),
            last_purchase_date=("transaction_date", "max"),
        )
    )

    analysis = customers.merge(
        customer_sales,
        on="customer_id",
        how="left",
        validate="one_to_one",
    )

    numeric_columns = [
        "sales_lines",
        "transactions",
        "units_sold",
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

    analysis["average_transaction_value"] = (
        analysis["net_sales"]
        / analysis["transactions"]
        .replace(0, pd.NA)
    )

    analysis["units_per_transaction"] = (
        analysis["units_sold"]
        / analysis["transactions"]
        .replace(0, pd.NA)
    )

    analysis["purchase_frequency"] = analysis[
        "transactions"
    ]

    analysis["customer_value_rank"] = (
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

    analysis = analysis.sort_values(
        "net_sales",
        ascending=False,
    ).reset_index(drop=True)

    return analysis


def build_segment_analysis(
    customer_analysis: pd.DataFrame,
) -> pd.DataFrame:
    """Build customer segment performance analysis."""

    segment = (
        customer_analysis.groupby(
            "customer_segment",
            as_index=False,
        )
        .agg(
            customers=("customer_id", "nunique"),
            transactions=("transactions", "sum"),
            units_sold=("units_sold", "sum"),
            gross_sales=("gross_sales", "sum"),
            discount=("discount", "sum"),
            net_sales=("net_sales", "sum"),
            product_cost=("product_cost", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
    )

    segment["gross_margin_pct"] = (
        segment["gross_profit"]
        / segment["net_sales"]
        .replace(0, pd.NA)
        * 100
    )

    segment["revenue_share_pct"] = (
        segment["net_sales"]
        / segment["net_sales"].sum()
        * 100
    )

    segment["profit_share_pct"] = (
        segment["gross_profit"]
        / segment["gross_profit"].sum()
        * 100
    )

    segment["revenue_per_customer"] = (
        segment["net_sales"]
        / segment["customers"]
        .replace(0, pd.NA)
    )

    segment["transactions_per_customer"] = (
        segment["transactions"]
        / segment["customers"]
        .replace(0, pd.NA)
    )

    segment["average_transaction_value"] = (
        segment["net_sales"]
        / segment["transactions"]
        .replace(0, pd.NA)
    )

    segment = segment.sort_values(
        "net_sales",
        ascending=False,
    ).reset_index(drop=True)

    segment["revenue_rank"] = (
        segment["net_sales"]
        .rank(
            method="min",
            ascending=False,
        )
        .astype(int)
    )

    segment["profit_rank"] = (
        segment["gross_profit"]
        .rank(
            method="min",
            ascending=False,
        )
        .astype(int)
    )

    return segment


def print_customer_analysis(
    customer_analysis: pd.DataFrame,
) -> None:
    """Print top and bottom customers."""

    print()
    print("=" * 80)
    print("CUSTOMER PERFORMANCE")
    print("=" * 80)

    columns = [
        "customer_id",
        "customer_name",
        "customer_segment",
        "transactions",
        "units_sold",
        "net_sales",
        "gross_profit",
        "gross_margin_pct",
        "customer_value_rank",
    ]

    display = customer_analysis[
        columns
    ].copy()

    display["net_sales"] = display[
        "net_sales"
    ].map(
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
        lambda value: (
            f"{value:.2f}%"
            if pd.notna(value)
            else "N/A"
        )
    )

    print()
    print("TOP 10 CUSTOMERS BY NET SALES")
    print("-" * 80)

    print(
        display.head(10).to_string(
            index=False
        )
    )

    print()
    print("BOTTOM 10 CUSTOMERS BY NET SALES")
    print("-" * 80)

    print(
        display.tail(10).to_string(
            index=False
        )
    )


def print_segment_analysis(
    segment_analysis: pd.DataFrame,
) -> None:
    """Print customer segment performance."""

    print()
    print("=" * 80)
    print("CUSTOMER SEGMENT PERFORMANCE")
    print("=" * 80)

    display = segment_analysis[
        [
            "customer_segment",
            "customers",
            "transactions",
            "units_sold",
            "net_sales",
            "gross_profit",
            "gross_margin_pct",
            "revenue_share_pct",
            "profit_share_pct",
            "revenue_per_customer",
            "transactions_per_customer",
            "average_transaction_value",
        ]
    ].copy()

    display["net_sales"] = display[
        "net_sales"
    ].map(
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

    display["revenue_per_customer"] = display[
        "revenue_per_customer"
    ].map(
        lambda value: f"Rp {value:,.0f}"
    )

    display["transactions_per_customer"] = (
        display["transactions_per_customer"].map(
            lambda value: f"{value:.2f}"
        )
    )

    display["average_transaction_value"] = (
        display["average_transaction_value"].map(
            lambda value: f"Rp {value:,.0f}"
        )
    )

    print()
    print(
        display.to_string(
            index=False
        )
    )


def print_customer_concentration(
    customer_analysis: pd.DataFrame,
) -> None:
    """Analyze revenue concentration among top customers."""

    print()
    print("=" * 80)
    print("CUSTOMER REVENUE CONCENTRATION")
    print("=" * 80)

    total_revenue = (
        customer_analysis["net_sales"].sum()
    )

    print()

    for top_n in [5, 10, 20, 50]:
        top_revenue = (
            customer_analysis
            .head(top_n)["net_sales"]
            .sum()
        )

        share = (
            top_revenue
            / total_revenue
            * 100
        )

        print(
            f"Top {top_n:<2} customers: "
            f"Rp {top_revenue:,.0f} "
            f"({share:.2f}% of total revenue)"
        )


def validate_totals(
    sales: pd.DataFrame,
    customer_analysis: pd.DataFrame,
) -> bool:
    """Validate customer aggregation against source sales totals."""

    source_metrics = {
        "units_sold": sales["quantity"].sum(),
        "gross_sales": sales["gross_sales"].sum(),
        "discount": sales["discount_amount"].sum(),
        "net_sales": sales["net_sales"].sum(),
        "product_cost": sales["product_cost"].sum(),
        "gross_profit": sales["gross_profit"].sum(),
    }

    aggregated_metrics = {
        "units_sold": customer_analysis[
            "units_sold"
        ].sum(),
        "gross_sales": customer_analysis[
            "gross_sales"
        ].sum(),
        "discount": customer_analysis[
            "discount"
        ].sum(),
        "net_sales": customer_analysis[
            "net_sales"
        ].sum(),
        "product_cost": customer_analysis[
            "product_cost"
        ].sum(),
        "gross_profit": customer_analysis[
            "gross_profit"
        ].sum(),
    }

    print()
    print("=" * 80)
    print("CUSTOMER AGGREGATION VALIDATION")
    print("=" * 80)

    all_pass = True

    for metric, source_value in source_metrics.items():
        aggregated_value = aggregated_metrics[
            metric
        ]

        passed = (
            source_value == aggregated_value
        )

        if not passed:
            all_pass = False

        print(
            f"{metric:<15} "
            f"Source: {source_value:>15,.0f} | "
            f"Customers: {aggregated_value:>15,.0f} | "
            f"{'PASS' if passed else 'REVIEW'}"
        )

    return all_pass


def main() -> None:
    """Run customer analysis."""

    sales, customers = load_data()

    customer_analysis = build_customer_analysis(
        sales,
        customers,
    )

    segment_analysis = build_segment_analysis(
        customer_analysis
    )

    print_customer_analysis(
        customer_analysis
    )

    print_segment_analysis(
        segment_analysis
    )

    print_customer_concentration(
        customer_analysis
    )

    validation_pass = validate_totals(
        sales,
        customer_analysis,
    )

    print()
    print("=" * 80)

    if validation_pass:
        print("CUSTOMER ANALYSIS STATUS: PASS")
    else:
        print("CUSTOMER ANALYSIS STATUS: REVIEW")

    print("=" * 80)


if __name__ == "__main__":
    main()
