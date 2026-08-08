from pathlib import Path

import pandas as pd


PROCESSED_DATA = Path("data/processed/sales.parquet")


def load_sales() -> pd.DataFrame:
    """Load prepared sales data."""
    if not PROCESSED_DATA.exists():
        raise FileNotFoundError(
            f"Processed sales data not found: {PROCESSED_DATA}"
        )

    return pd.read_parquet(PROCESSED_DATA)


def calculate_sales_metrics(
    sales: pd.DataFrame,
) -> dict[str, float]:
    """Calculate high-level sales performance metrics."""
    metrics = {
        "sales_line_records": len(sales),
        "unique_transactions": sales["transaction_key"].nunique(),
        "units_sold": sales["quantity"].sum(),
        "gross_sales": sales["gross_sales"].sum(),
        "discount": sales["discount_amount"].sum(),
        "net_sales": sales["net_sales"].sum(),
        "product_cost": sales["product_cost"].sum(),
        "gross_profit": sales["gross_profit"].sum(),
    }

    metrics["gross_margin_pct"] = (
        metrics["gross_profit"]
        / metrics["net_sales"]
        * 100
    )

    metrics["average_transaction_value"] = (
        metrics["net_sales"]
        / metrics["unique_transactions"]
    )

    return metrics


def print_metrics(
    metrics: dict[str, float],
) -> None:
    """Print sales overview metrics."""
    print("=" * 80)
    print("MAYASARI BAKERY SALES OVERVIEW")
    print("=" * 80)

    print()
    print("VOLUME")
    print("-" * 80)

    print(
        f"Sales line records       : "
        f"{metrics['sales_line_records']:,}"
    )

    print(
        f"Unique transactions      : "
        f"{metrics['unique_transactions']:,}"
    )

    print(
        f"Units sold               : "
        f"{metrics['units_sold']:,}"
    )

    print()
    print("REVENUE")
    print("-" * 80)

    print(
        f"Gross sales              : "
        f"Rp {metrics['gross_sales']:,.0f}"
    )

    print(
        f"Discount                 : "
        f"Rp {metrics['discount']:,.0f}"
    )

    print(
        f"Net sales                : "
        f"Rp {metrics['net_sales']:,.0f}"
    )

    print()
    print("PROFITABILITY")
    print("-" * 80)

    print(
        f"Product cost             : "
        f"Rp {metrics['product_cost']:,.0f}"
    )

    print(
        f"Gross profit             : "
        f"Rp {metrics['gross_profit']:,.0f}"
    )

    print(
        f"Gross margin             : "
        f"{metrics['gross_margin_pct']:.2f}%"
    )

    print()
    print("CUSTOMER TRANSACTION VALUE")
    print("-" * 80)

    print(
        f"Average transaction value: "
        f"Rp {metrics['average_transaction_value']:,.0f}"
    )

    print()
    print("=" * 80)
    print("SALES OVERVIEW COMPLETED")
    print("=" * 80)


def main() -> None:
    """Run sales overview analysis."""
    sales = load_sales()

    metrics = calculate_sales_metrics(
        sales
    )

    print_metrics(metrics)


if __name__ == "__main__":
    main()
