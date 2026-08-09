
import pandas as pd

from src.contracts.paths import (
    ANALYTICS_DIR,
    CUSTOMERS_DATA,
    EXPENSES_DATA,
    PRODUCTS_DATA,
    SALES_DATA,
)


def load_data() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """Load and validate core datasets."""

    required_files = [
        SALES_DATA,
        CUSTOMERS_DATA,
        PRODUCTS_DATA,
        EXPENSES_DATA,
    ]

    for path in required_files:
        if not path.exists():
            raise FileNotFoundError(
                f"Required dataset not found: {path}"
            )

    sales = pd.read_parquet(SALES_DATA)
    customers = pd.read_parquet(CUSTOMERS_DATA)
    products = pd.read_parquet(PRODUCTS_DATA)
    expenses = pd.read_parquet(EXPENSES_DATA)

    required_sales = {
        "transaction_key",
        "transaction_date",
        "customer_id",
        "product_id",
        "quantity",
        "net_sales",
        "product_cost",
        "gross_profit",
    }

    missing_sales = (
        required_sales - set(sales.columns)
    )

    if missing_sales:
        raise ValueError(
            "Sales dataset missing columns: "
            f"{sorted(missing_sales)}"
        )

    required_customers = {
        "customer_id",
    }

    missing_customers = (
        required_customers - set(customers.columns)
    )

    if missing_customers:
        raise ValueError(
            "Customer dataset missing columns: "
            f"{sorted(missing_customers)}"
        )

    required_products = {
        "product_id",
    }

    missing_products = (
        required_products - set(products.columns)
    )

    if missing_products:
        raise ValueError(
            "Product dataset missing columns: "
            f"{sorted(missing_products)}"
        )

    sales["transaction_date"] = pd.to_datetime(
        sales["transaction_date"]
    )

    sales["sales_month"] = (
        sales["transaction_date"]
        .dt.to_period("M")
        .astype(str)
    )

    return (
        sales,
        customers,
        products,
        expenses,
    )


def build_executive_kpis(
    sales: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    expenses: pd.DataFrame,
) -> pd.DataFrame:
    """Build one-row executive KPI dataset."""

    revenue = sales["net_sales"].sum()
    gross_profit = sales["gross_profit"].sum()

    transactions = sales[
        "transaction_key"
    ].nunique()

    active_customers = sales[
        "customer_id"
    ].nunique()

    product_count = sales[
        "product_id"
    ].nunique()

    gross_margin = (
        gross_profit / revenue * 100
        if revenue
        else 0
    )

    average_transaction = (
        revenue / transactions
        if transactions
        else 0
    )

    total_quantity = sales[
        "quantity"
    ].sum()

    total_product_cost = sales[
        "product_cost"
    ].sum()

    total_expense = 0

    expense_numeric = expenses.select_dtypes(
        include="number"
    )

    if not expense_numeric.empty:
        expense_columns = [
            column
            for column in expense_numeric.columns
            if column.lower() not in {
                "id",
                "expense_id",
            }
        ]

        if expense_columns:
            total_expense = expenses[
                expense_columns
            ].sum().sum()

    operating_profit = (
        gross_profit - total_expense
    )

    return pd.DataFrame(
        [
            {
                "revenue": revenue,
                "gross_profit": gross_profit,
                "gross_margin_pct": gross_margin,
                "transactions": transactions,
                "active_customers": active_customers,
                "products": product_count,
                "total_quantity": total_quantity,
                "average_transaction_value": (
                    average_transaction
                ),
                "product_cost": total_product_cost,
                "operating_expense": total_expense,
                "operating_profit": operating_profit,
                "customer_master_count": len(customers),
                "product_master_count": len(products),
            }
        ]
    )


def build_monthly_performance(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """Build monthly management performance dataset."""

    monthly = (
        sales.groupby("sales_month")
        .agg(
            revenue=("net_sales", "sum"),
            gross_profit=(
                "gross_profit",
                "sum",
            ),
            product_cost=(
                "product_cost",
                "sum",
            ),
            transactions=(
                "transaction_key",
                "nunique",
            ),
            customers=(
                "customer_id",
                "nunique",
            ),
            quantity=(
                "quantity",
                "sum",
            ),
        )
        .reset_index()
        .sort_values("sales_month")
    )

    monthly["gross_margin_pct"] = (
        monthly["gross_profit"]
        / monthly["revenue"]
        * 100
    )

    monthly["average_transaction_value"] = (
        monthly["revenue"]
        / monthly["transactions"]
    )

    monthly["mom_revenue_growth_pct"] = (
        monthly["revenue"]
        .pct_change()
        * 100
    )

    monthly["mom_profit_growth_pct"] = (
        monthly["gross_profit"]
        .pct_change()
        * 100
    )

    monthly["rolling_3m_revenue"] = (
        monthly["revenue"]
        .rolling(3)
        .mean()
    )

    monthly["rolling_3m_profit"] = (
        monthly["gross_profit"]
        .rolling(3)
        .mean()
    )

    return monthly


def build_product_performance(
    sales: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Build product-level management dataset."""

    product = (
        sales.groupby("product_id")
        .agg(
            revenue=("net_sales", "sum"),
            gross_profit=(
                "gross_profit",
                "sum",
            ),
            product_cost=(
                "product_cost",
                "sum",
            ),
            quantity=("quantity", "sum"),
            transactions=(
                "transaction_key",
                "nunique",
            ),
        )
        .reset_index()
    )

    product["gross_margin_pct"] = (
        product["gross_profit"]
        / product["revenue"]
        * 100
    )

    product["revenue_share_pct"] = (
        product["revenue"]
        / product["revenue"].sum()
        * 100
    )

    product["profit_share_pct"] = (
        product["gross_profit"]
        / product["gross_profit"].sum()
        * 100
    )

    product = product.merge(
        products,
        on="product_id",
        how="left",
        validate="many_to_one",
        suffixes=(
            "",
            "_master",
        ),
    )

    return product.sort_values(
        "revenue",
        ascending=False,
    ).reset_index(drop=True)


def build_customer_performance(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """Build customer-level management dataset."""

    customer = (
        sales.groupby("customer_id")
        .agg(
            revenue=("net_sales", "sum"),
            gross_profit=(
                "gross_profit",
                "sum",
            ),
            transactions=(
                "transaction_key",
                "nunique",
            ),
            active_months=(
                "sales_month",
                "nunique",
            ),
            first_purchase=(
                "transaction_date",
                "min",
            ),
            last_purchase=(
                "transaction_date",
                "max",
            ),
        )
        .reset_index()
    )

    customer["gross_margin_pct"] = (
        customer["gross_profit"]
        / customer["revenue"]
        * 100
    )

    customer["average_transaction_value"] = (
        customer["revenue"]
        / customer["transactions"]
    )

    customer["historical_clv"] = (
        customer["gross_profit"]
    )

    customer["annualized_clv"] = (
        customer["gross_profit"]
        / customer["active_months"]
        * 12
    )

    customer["observed_lifetime_days"] = (
        customer["last_purchase"]
        - customer["first_purchase"]
    ).dt.days

    return customer.sort_values(
        "revenue",
        ascending=False,
    ).reset_index(drop=True)


def build_profitability_summary(
    sales: pd.DataFrame,
) -> pd.DataFrame:
    """Build high-level profitability summary."""

    revenue = sales["net_sales"].sum()
    product_cost = sales["product_cost"].sum()
    gross_profit = sales["gross_profit"].sum()

    gross_margin = (
        gross_profit / revenue * 100
        if revenue
        else 0
    )

    return pd.DataFrame(
        [
            {
                "revenue": revenue,
                "product_cost": product_cost,
                "gross_profit": gross_profit,
                "gross_margin_pct": gross_margin,
            }
        ]
    )


def validate_bi_layer(
    sales: pd.DataFrame,
    executive: pd.DataFrame,
    monthly: pd.DataFrame,
    product: pd.DataFrame,
    customer: pd.DataFrame,
    profitability: pd.DataFrame,
) -> bool:
    """Validate BI datasets against source sales."""

    source_revenue = sales[
        "net_sales"
    ].sum()

    source_profit = sales[
        "gross_profit"
    ].sum()

    revenue_ok = (
        executive.loc[0, "revenue"]
        == source_revenue
    )

    profit_ok = (
        executive.loc[0, "gross_profit"]
        == source_profit
    )

    monthly_revenue_ok = (
        monthly["revenue"].sum()
        == source_revenue
    )

    monthly_profit_ok = (
        monthly["gross_profit"].sum()
        == source_profit
    )

    product_revenue_ok = (
        product["revenue"].sum()
        == source_revenue
    )

    product_profit_ok = (
        product["gross_profit"].sum()
        == source_profit
    )

    customer_revenue_ok = (
        customer["revenue"].sum()
        == source_revenue
    )

    customer_profit_ok = (
        customer["gross_profit"].sum()
        == source_profit
    )

    profitability_ok = (
        profitability.loc[0, "revenue"]
        == source_revenue
        and
        profitability.loc[0, "gross_profit"]
        == source_profit
    )

    checks = {
        "Executive revenue": revenue_ok,
        "Executive profit": profit_ok,
        "Monthly revenue": monthly_revenue_ok,
        "Monthly profit": monthly_profit_ok,
        "Product revenue": product_revenue_ok,
        "Product profit": product_profit_ok,
        "Customer revenue": customer_revenue_ok,
        "Customer profit": customer_profit_ok,
        "Profitability": profitability_ok,
    }

    passed = all(checks.values())

    print()
    print("=" * 80)
    print("M13 BI LAYER VALIDATION")
    print("=" * 80)

    for name, result in checks.items():
        print(
            f"{name:<25}: "
            f"{'PASS' if result else 'REVIEW'}"
        )

    print("-" * 80)
    print(
        f"Validation              : "
        f"{'PASS' if passed else 'REVIEW'}"
    )

    return passed


def save_datasets(
    executive: pd.DataFrame,
    monthly: pd.DataFrame,
    product: pd.DataFrame,
    customer: pd.DataFrame,
    profitability: pd.DataFrame,
) -> None:
    """Save BI analytical datasets."""

    ANALYTICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    executive.to_parquet(
        ANALYTICS_DIR
        / "executive_kpis.parquet",
        index=False,
    )

    monthly.to_parquet(
        ANALYTICS_DIR
        / "monthly_performance.parquet",
        index=False,
    )

    product.to_parquet(
        ANALYTICS_DIR
        / "product_performance.parquet",
        index=False,
    )

    customer.to_parquet(
        ANALYTICS_DIR
        / "customer_performance.parquet",
        index=False,
    )

    profitability.to_parquet(
        ANALYTICS_DIR
        / "profitability_summary.parquet",
        index=False,
    )


def print_summary(
    executive: pd.DataFrame,
    monthly: pd.DataFrame,
    product: pd.DataFrame,
    customer: pd.DataFrame,
) -> None:
    """Print concise M13 BI summary."""

    kpi = executive.iloc[0]

    print()
    print("=" * 80)
    print("MAYASARI BAKERY — M13 BUSINESS INTELLIGENCE")
    print("=" * 80)

    print(
        f"Revenue          : "
        f"Rp {kpi['revenue']:,.0f}"
    )

    print(
        f"Gross profit     : "
        f"Rp {kpi['gross_profit']:,.0f}"
    )

    print(
        f"Gross margin     : "
        f"{kpi['gross_margin_pct']:.2f}%"
    )

    print(
        f"Transactions      : "
        f"{int(kpi['transactions']):,}"
    )

    print(
        f"Customers         : "
        f"{int(kpi['active_customers']):,}"
    )

    print(
        f"Products          : "
        f"{int(kpi['products']):,}"
    )

    print()
    print("ANALYTICAL DATASETS")
    print("-" * 80)

    print(
        f"Executive KPIs        : "
        f"{len(executive):,} rows"
    )

    print(
        f"Monthly performance   : "
        f"{len(monthly):,} rows"
    )

    print(
        f"Product performance   : "
        f"{len(product):,} rows"
    )

    print(
        f"Customer performance  : "
        f"{len(customer):,} rows"
    )

    print()
    print("TOP 3 PRODUCTS BY REVENUE")
    print("-" * 80)

    top_products = product[
        [
            "product_id",
            "revenue",
            "gross_profit",
            "gross_margin_pct",
        ]
    ].head(3).copy()

    top_products["revenue"] = (
        top_products["revenue"]
        .map(lambda value: f"Rp {value:,.0f}")
    )

    top_products["gross_profit"] = (
        top_products["gross_profit"]
        .map(lambda value: f"Rp {value:,.0f}")
    )

    top_products["gross_margin_pct"] = (
        top_products["gross_margin_pct"]
        .map(lambda value: f"{value:.1f}%")
    )

    print(
        top_products.to_string(
            index=False
        )
    )

    print()
    print("TOP 3 CUSTOMERS BY REVENUE")
    print("-" * 80)

    top_customers = customer[
        [
            "customer_id",
            "revenue",
            "gross_profit",
            "transactions",
        ]
    ].head(3).copy()

    top_customers["revenue"] = (
        top_customers["revenue"]
        .map(lambda value: f"Rp {value:,.0f}")
    )

    top_customers["gross_profit"] = (
        top_customers["gross_profit"]
        .map(lambda value: f"Rp {value:,.0f}")
    )

    print(
        top_customers.to_string(
            index=False
        )
    )


def main() -> None:
    """Run M13 Business Intelligence layer."""

    (
        sales,
        customers,
        products,
        expenses,
    ) = load_data()

    executive = build_executive_kpis(
        sales,
        customers,
        products,
        expenses,
    )

    monthly = build_monthly_performance(
        sales
    )

    product = build_product_performance(
        sales,
        products,
    )

    customer = build_customer_performance(
        sales
    )

    profitability = (
        build_profitability_summary(
            sales
        )
    )

    save_datasets(
        executive,
        monthly,
        product,
        customer,
        profitability,
    )

    print_summary(
        executive,
        monthly,
        product,
        customer,
    )

    validation = validate_bi_layer(
        sales,
        executive,
        monthly,
        product,
        customer,
        profitability,
    )

    print()
    print("=" * 80)
    print(
        "M13 BUSINESS INTELLIGENCE STATUS: "
        f"{'PASS' if validation else 'REVIEW'}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
