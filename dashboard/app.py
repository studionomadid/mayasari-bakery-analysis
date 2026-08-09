from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SALES_DATA = BASE_DIR / "data/processed/sales.parquet"
EXPENSE_DATA = BASE_DIR / "data/processed/expenses.parquet"


st.set_page_config(
    page_title="Mayasari Bakery | Executive Dashboard",
    page_icon="🥐",
    layout="wide",
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load prepared sales and expense data."""

    if not SALES_DATA.exists():
        raise FileNotFoundError(
            f"Sales data not found: {SALES_DATA}"
        )

    if not EXPENSE_DATA.exists():
        raise FileNotFoundError(
            f"Expense data not found: {EXPENSE_DATA}"
        )

    sales = pd.read_parquet(SALES_DATA)
    expenses = pd.read_parquet(EXPENSE_DATA)

    return sales, expenses


# ============================================================
# KPI CALCULATION
# ============================================================

def calculate_kpis(
    sales: pd.DataFrame,
    expenses: pd.DataFrame,
) -> dict[str, float]:
    """Calculate executive dashboard KPIs."""

    gross_sales = sales["gross_sales"].sum()
    discount = sales["discount_amount"].sum()
    net_sales = sales["net_sales"].sum()

    product_cost = sales["product_cost"].sum()
    gross_profit = sales["gross_profit"].sum()

    operating_expense = expenses["amount"].sum()
    operating_profit = gross_profit - operating_expense

    transactions = sales["transaction_key"].nunique()
    units_sold = sales["quantity"].sum()

    average_transaction_value = (
        net_sales / transactions
    )

    gross_margin = (
        gross_profit / net_sales * 100
    )

    operating_margin = (
        operating_profit / net_sales * 100
    )

    return {
        "gross_sales": gross_sales,
        "discount": discount,
        "net_sales": net_sales,
        "product_cost": product_cost,
        "gross_profit": gross_profit,
        "operating_expense": operating_expense,
        "operating_profit": operating_profit,
        "transactions": transactions,
        "units_sold": units_sold,
        "average_transaction_value": (
            average_transaction_value
        ),
        "gross_margin": gross_margin,
        "operating_margin": operating_margin,
    }


# ============================================================
# FORMATTING
# ============================================================

def format_rupiah(value: float) -> str:
    """Format numeric value as Indonesian Rupiah."""

    return f"Rp {value:,.0f}"


# ============================================================
# DASHBOARD
# ============================================================

def main() -> None:
    """Render Mayasari Bakery executive dashboard."""

    st.title("Mayasari Bakery")
    st.subheader("Executive Business Dashboard")

    st.caption(
        "Sales, profitability, customer transaction, "
        "and operating performance overview."
    )

    try:
        sales, expenses = load_data()
    except FileNotFoundError as error:
        st.error(str(error))
        st.stop()

    kpis = calculate_kpis(
        sales,
        expenses,
    )

    # --------------------------------------------------------
    # KPI ROW 1 — BUSINESS SCALE
    # --------------------------------------------------------

    st.markdown("### Business Performance")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Net Sales",
            format_rupiah(kpis["net_sales"]),
        )

    with col2:
        st.metric(
            "Transactions",
            f'{kpis["transactions"]:,}',
        )

    with col3:
        st.metric(
            "Units Sold",
            f'{kpis["units_sold"]:,}',
        )

    with col4:
        st.metric(
            "Average Transaction Value",
            format_rupiah(
                kpis["average_transaction_value"]
            ),
        )

    # --------------------------------------------------------
    # KPI ROW 2 — PROFITABILITY
    # --------------------------------------------------------

    st.markdown("### Profitability")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Gross Profit",
            format_rupiah(kpis["gross_profit"]),
        )

    with col2:
        st.metric(
            "Gross Margin",
            f'{kpis["gross_margin"]:.2f}%',
        )

    with col3:
        st.metric(
            "Operating Profit",
            format_rupiah(kpis["operating_profit"]),
        )

    with col4:
        st.metric(
            "Operating Margin",
            f'{kpis["operating_margin"]:.2f}%',
        )

    # --------------------------------------------------------
    # FINANCIAL SUMMARY
    # --------------------------------------------------------

    st.markdown("### Financial Summary")

    financial_summary = pd.DataFrame(
        {
            "Metric": [
                "Gross Sales",
                "Discount",
                "Net Sales",
                "Product Cost",
                "Gross Profit",
                "Operating Expense",
                "Operating Profit",
            ],
            "Amount": [
                kpis["gross_sales"],
                kpis["discount"],
                kpis["net_sales"],
                kpis["product_cost"],
                kpis["gross_profit"],
                kpis["operating_expense"],
                kpis["operating_profit"],
            ],
        }
    )

    financial_summary["Amount"] = (
        financial_summary["Amount"]
        .map(format_rupiah)
    )

    st.dataframe(
        financial_summary,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # DATA QUALITY
    # --------------------------------------------------------

    st.markdown("### Dataset Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Sales Records",
            f"{len(sales):,}",
        )

    with col2:
        st.metric(
            "Expense Records",
            f"{len(expenses):,}",
        )

    with col3:
        st.metric(
            "Analysis Period",
            (
                f"{sales['transaction_date'].min():%b %Y}"
                " — "
                f"{sales['transaction_date'].max():%b %Y}"
            ),
        )


if __name__ == "__main__":
    main()
