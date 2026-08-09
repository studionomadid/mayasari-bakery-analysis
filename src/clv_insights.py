from pathlib import Path

import pandas as pd


ANALYTICS_DIR = Path("data/analytics")
REPORTS_DIR = Path("reports/insights")

CUSTOMER_DATA = (
    ANALYTICS_DIR / "customer_performance.parquet"
)

OUTPUT = (
    REPORTS_DIR / "clv_insights.md"
)


REQUIRED_COLUMNS = {
    "customer_id",
    "revenue",
    "gross_profit",
    "transactions",
    "active_months",
    "first_purchase",
    "last_purchase",
    "gross_margin_pct",
    "average_transaction_value",
    "historical_clv",
    "annualized_clv",
    "observed_lifetime_days",
}


def load_customer_data() -> pd.DataFrame:
    """Load and validate customer CLV dataset."""

    if not CUSTOMER_DATA.exists():
        raise FileNotFoundError(
            f"Customer performance dataset not found: "
            f"{CUSTOMER_DATA}"
        )

    customer = pd.read_parquet(
        CUSTOMER_DATA
    )

    missing = (
        REQUIRED_COLUMNS
        - set(customer.columns)
    )

    if missing:
        raise ValueError(
            "Customer dataset is missing columns: "
            f"{sorted(missing)}"
        )

    if len(customer) != 850:
        raise ValueError(
            "Expected 850 customers, "
            f"found {len(customer)}."
        )

    customer = customer.copy()

    if customer["customer_id"].duplicated().any():
        raise ValueError(
            "Customer IDs must be unique."
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
        "observed_lifetime_days",
    ]

    if customer[numeric_columns].isna().any().any():
        raise ValueError(
            "Customer dataset contains "
            "unexpected numeric null values."
        )

    if customer[
        ["first_purchase", "last_purchase"]
    ].isna().any().any():
        raise ValueError(
            "Customer dataset contains "
            "unexpected purchase-date null values."
        )

    if (
        customer["historical_clv"]
        != customer["gross_profit"]
    ).all() is False:
        raise ValueError(
            "Historical CLV is expected to equal "
            "customer gross profit in this model."
        )

    if (
        customer["observed_lifetime_days"] < 0
    ).any():
        raise ValueError(
            "Observed lifetime cannot be negative."
        )

    return customer


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


def assign_clv_tiers(
    customer: pd.DataFrame,
) -> pd.DataFrame:
    """Assign deterministic CLV tiers using annualized CLV quartiles."""

    customer = customer.copy()

    customer["clv_tier"] = pd.qcut(
        customer["annualized_clv"],
        q=4,
        labels=[
            "Bronze",
            "Silver",
            "Gold",
            "Platinum",
        ],
        duplicates="drop",
    )

    customer["clv_tier"] = (
        customer["clv_tier"]
        .astype(str)
    )

    return customer


def build_tier_summary(
    customer: pd.DataFrame,
) -> pd.DataFrame:
    """Build CLV tier performance summary."""

    total_customers = len(customer)
    total_revenue = customer["revenue"].sum()
    total_gross_profit = (
        customer["gross_profit"].sum()
    )

    summary = (
        customer.groupby(
            "clv_tier",
            observed=True,
        )
        .agg(
            customers=(
                "customer_id",
                "count",
            ),
            revenue=(
                "revenue",
                "sum",
            ),
            gross_profit=(
                "gross_profit",
                "sum",
            ),
            average_historical_clv=(
                "historical_clv",
                "mean",
            ),
            average_annualized_clv=(
                "annualized_clv",
                "mean",
            ),
            average_transactions=(
                "transactions",
                "mean",
            ),
            average_margin=(
                "gross_margin_pct",
                "mean",
            ),
        )
        .reset_index()
    )

    summary["customer_share_pct"] = (
        summary["customers"]
        / total_customers
        * 100
    )

    summary["revenue_share_pct"] = (
        summary["revenue"]
        / total_revenue
        * 100
    )

    summary["gross_profit_share_pct"] = (
        summary["gross_profit"]
        / total_gross_profit
        * 100
    )

    tier_order = [
        "Bronze",
        "Silver",
        "Gold",
        "Platinum",
    ]

    summary["tier_rank"] = summary[
        "clv_tier"
    ].map(
        {
            tier: index
            for index, tier
            in enumerate(tier_order)
        }
    )

    summary = summary.sort_values(
        "tier_rank"
    ).drop(
        columns="tier_rank"
    )

    return summary


def generate_insights(
    customer: pd.DataFrame,
    tier_summary: pd.DataFrame,
) -> dict[str, object]:
    """Generate executive CLV insights."""

    total_revenue = customer["revenue"].sum()
    total_gross_profit = (
        customer["gross_profit"].sum()
    )

    average_historical_clv = (
        customer["historical_clv"].mean()
    )

    average_annualized_clv = (
        customer["annualized_clv"].mean()
    )

    median_annualized_clv = (
        customer["annualized_clv"].median()
    )

    top10 = customer.nlargest(
        10,
        "annualized_clv",
    )

    top25 = customer.nlargest(
        max(1, int(len(customer) * 0.25)),
        "annualized_clv",
    )

    top10_clv_share = (
        top10["historical_clv"].sum()
        / total_gross_profit
        * 100
    )

    top25_clv_share = (
        top25["historical_clv"].sum()
        / total_gross_profit
        * 100
    )

    highest = customer.loc[
        customer["annualized_clv"].idxmax()
    ]

    highest_historical = customer.loc[
        customer["historical_clv"].idxmax()
    ]

    highest_revenue = customer.loc[
        customer["revenue"].idxmax()
    ]

    highest_margin = customer.loc[
        customer["gross_margin_pct"].idxmax()
    ]

    return {
        "total_revenue": total_revenue,
        "total_gross_profit": total_gross_profit,
        "average_historical_clv": (
            average_historical_clv
        ),
        "average_annualized_clv": (
            average_annualized_clv
        ),
        "median_annualized_clv": (
            median_annualized_clv
        ),
        "top10_clv_share": top10_clv_share,
        "top25_clv_share": top25_clv_share,
        "highest_annualized": highest,
        "highest_historical": highest_historical,
        "highest_revenue": highest_revenue,
        "highest_margin": highest_margin,
    }


def build_report(
    customer: pd.DataFrame,
    tier_summary: pd.DataFrame,
    insights: dict[str, object],
) -> str:
    """Build management-ready CLV insights report."""

    total_customers = len(customer)

    total_revenue = insights[
        "total_revenue"
    ]

    total_gross_profit = insights[
        "total_gross_profit"
    ]

    average_historical_clv = insights[
        "average_historical_clv"
    ]

    average_annualized_clv = insights[
        "average_annualized_clv"
    ]

    median_annualized_clv = insights[
        "median_annualized_clv"
    ]

    top10_clv_share = insights[
        "top10_clv_share"
    ]

    top25_clv_share = insights[
        "top25_clv_share"
    ]

    highest_annualized = insights[
        "highest_annualized"
    ]

    highest_historical = insights[
        "highest_historical"
    ]

    highest_revenue = insights[
        "highest_revenue"
    ]

    highest_margin = insights[
        "highest_margin"
    ]

    tier_lines = []

    for _, row in tier_summary.iterrows():
        tier_lines.append(
            "| "
            f"{row['clv_tier']} | "
            f"{int(row['customers']):,} | "
            f"{row['customer_share_pct']:.1f}% | "
            f"{format_currency(row['revenue'])} | "
            f"{row['revenue_share_pct']:.1f}% | "
            f"{format_currency(row['gross_profit'])} | "
            f"{row['gross_profit_share_pct']:.1f}% | "
            f"{format_currency(row['average_annualized_clv'])} |"
        )

    tier_table = "\n".join(
        tier_lines
    )

    report = f"""# Mayasari Bakery — Customer Lifetime Value Insights

## 1. Executive Overview

The customer portfolio contains **{total_customers:,} customers**.

Customers generated total revenue of
**{format_currency(total_revenue)}**
and total gross profit of
**{format_currency(total_gross_profit)}**.

Historical CLV averages
**{format_currency(average_historical_clv)}**
per customer.

Annualized CLV averages
**{format_currency(average_annualized_clv)}**,
with a median of
**{format_currency(median_annualized_clv)}**.

In this analytical model, historical CLV represents
historical customer gross-profit contribution.

---

## 2. CLV Distribution

CLV is evaluated using annualized CLV to account for differences
in observed customer lifetime.

Customers are classified into four relative-value tiers:

- **Platinum** — top 25% annualized CLV
- **Gold** — 25–50% annualized CLV
- **Silver** — 50–75% annualized CLV
- **Bronze** — bottom 25% annualized CLV

This relative approach avoids imposing arbitrary nominal CLV thresholds
on the customer population.

---

## 3. CLV Tier Performance

| Tier | Customers | Customer Share | Revenue | Revenue Share | Gross Profit | GP Share | Avg Annualized CLV |
| ---- | --------: | -------------: | ------: | ------------: | -----------: | -------: | -----------------: |
{tier_table}

### Management Interpretation

The tier structure provides a relative ranking of customer economic value.

Platinum and Gold customers should receive greater retention attention
because they represent the highest expected annualized customer value.

Bronze customers should not automatically be treated as low-potential
customers. Their lower current annualized CLV may reflect shorter
observed lifetime or lower purchase frequency.

---

## 4. High-Value Customer Analysis

### Highest Annualized CLV

Customer **{highest_annualized['customer_id']}**
has the highest annualized CLV at
**{format_currency(highest_annualized['annualized_clv'])}**.

Historical CLV:
**{format_currency(highest_annualized['historical_clv'])}**

Revenue:
**{format_currency(highest_annualized['revenue'])}**

Transactions:
**{int(highest_annualized['transactions']):,}**

Observed lifetime:
**{int(highest_annualized['observed_lifetime_days']):,} days**

### Highest Historical CLV

Customer **{highest_historical['customer_id']}**
has the highest historical CLV at
**{format_currency(highest_historical['historical_clv'])}**.

### Highest Revenue Customer

Customer **{highest_revenue['customer_id']}**
has the highest historical revenue at
**{format_currency(highest_revenue['revenue'])}**.

These customers should be evaluated separately because revenue,
historical gross-profit contribution, and annualized CLV represent
different dimensions of customer value.

---

## 5. CLV Concentration

The top 10 customers by annualized CLV account for approximately
**{top10_clv_share:.2f}%** of total historical gross-profit contribution.

The top 25% of customers by annualized CLV account for approximately
**{top25_clv_share:.2f}%** of total historical gross-profit contribution.

This indicates the degree to which customer economic value is
concentrated within the highest-value portion of the customer base.

---

## 6. Customer Value vs Profitability

The highest customer gross-margin percentage is observed for
**{highest_margin['customer_id']}**,
at **{highest_margin['gross_margin_pct']:.2f}%**.

This reinforces that customer value should not be evaluated from revenue
alone.

A customer can have high revenue but lower margin, while another customer
may generate less revenue but produce stronger gross-profit economics.

Management should therefore combine:

- Revenue
- Gross profit
- Gross margin
- Transaction frequency
- Observed lifetime
- Annualized CLV

when evaluating strategic customer value.

---

## 7. Business Opportunities

### Opportunity 1 — Protect Platinum Customers

Create retention and relationship-management actions for the highest CLV
customers.

Potential actions include:

- Priority service
- Personalized offers
- Repeat-purchase reminders
- Product recommendations
- Early access to seasonal products

### Opportunity 2 — Develop Gold Customers

Gold customers represent an attractive upgrade pool.

Management can target these customers with strategies designed to increase:

- Purchase frequency
- Basket value
- Product breadth
- Customer lifetime

### Opportunity 3 — Identify Emerging Customers

Some Bronze and Silver customers may have relatively short observed
lifetimes.

These customers should be monitored for early signals of increasing
purchase frequency or transaction value before they become high-value
customers.

### Opportunity 4 — Protect Gross-Profit Contribution

CLV management should prioritize gross-profit contribution rather than
revenue alone.

Customer retention programs should therefore be evaluated against
incremental gross profit and not only incremental sales.

---

## 8. Key Risks

- Annualized CLV can be sensitive to short observed customer lifetimes.
- High-revenue customers are not necessarily the highest-margin customers.
- Relative CLV tiers rank customers within the current population but do not
  guarantee future customer behavior.
- Aggressive discounting may increase revenue while reducing customer
  profitability.

---

## 9. Management Priorities

### Priority 1 — Retain High-Value Customers

Prioritize Platinum customers for retention and relationship programs.

### Priority 2 — Upgrade Gold Customers

Identify practical interventions that can move Gold customers toward
Platinum-level economic contribution.

### Priority 3 — Monitor Emerging Customers

Track customers with improving transaction frequency, basket value,
and lifetime signals.

### Priority 4 — Measure Incremental Profit

Evaluate retention and customer-development programs using incremental
gross profit and CLV rather than revenue alone.

---

## 10. Executive Takeaway

Mayasari Bakery's customer portfolio contains meaningful variation
in customer economic value.

Annualized CLV provides a forward-looking relative indicator that can
help management prioritize retention and customer-development resources.

The most valuable customers should be protected, high-potential customers
should be developed, and lower-value customers should be evaluated for
future growth potential rather than treated as a homogeneous group.

The key management principle is:

**Grow customer lifetime value while protecting gross-profit economics.**

---

*Generated from Mayasari Bakery customer analytical dataset.*
"""

    return report


def main() -> None:
    """Generate M12.2 CLV insights report."""

    customer = load_customer_data()

    customer = assign_clv_tiers(
        customer
    )

    tier_summary = build_tier_summary(
        customer
    )

    insights = generate_insights(
        customer,
        tier_summary,
    )

    report = build_report(
        customer,
        tier_summary,
        insights,
    )

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        report,
        encoding="utf-8",
    )

    print("=" * 80)
    print(
        "MAYASARI BAKERY — "
        "M12.2 CLV INSIGHTS"
    )
    print("=" * 80)

    print()
    print(
        f"Customers             : "
        f"{len(customer):,}"
    )

    print(
        f"Average historical CLV: "
        f"{format_currency(insights['average_historical_clv'])}"
    )

    print(
        f"Average annualized CLV: "
        f"{format_currency(insights['average_annualized_clv'])}"
    )

    print(
        f"Median annualized CLV : "
        f"{format_currency(insights['median_annualized_clv'])}"
    )

    print(
        f"Top 10 CLV share      : "
        f"{insights['top10_clv_share']:.2f}%"
    )

    print(
        f"Top 25% CLV share     : "
        f"{insights['top25_clv_share']:.2f}%"
    )

    print(
        f"Highest annualized CLV: "
        f"{insights['highest_annualized']['customer_id']}"
    )

    print(
        f"Highest historical CLV: "
        f"{insights['highest_historical']['customer_id']}"
    )

    print(
        f"Highest revenue       : "
        f"{insights['highest_revenue']['customer_id']}"
    )

    print()
    print(
        f"Generated report      : "
        f"{OUTPUT}"
    )

    print()
    print("=" * 80)
    print("M12.2 CLV INSIGHTS: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()
