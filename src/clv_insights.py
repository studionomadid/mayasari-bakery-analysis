"""
Mayasari Bakery — M12.2 Customer Lifetime Value Insights.

Generates executive-level customer CLV insights from the
customer performance analytical dataset.

M12.2.1 focuses on CLV metric reconciliation:

- Historical CLV = historical gross-profit contribution.
- Annualized CLV = normalized customer value indicator.
- CLV concentration is measured using annualized CLV
  against total annualized CLV.
- Historical CLV concentration is reported separately
  against total historical CLV.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

ANALYTICS_DIR = PROJECT_ROOT / "data" / "analytics"
REPORT_DIR = PROJECT_ROOT / "reports" / "insights"

CUSTOMER_DATASET = (
    ANALYTICS_DIR / "customer_performance.parquet"
)

OUTPUT_REPORT = (
    REPORT_DIR / "clv_insights.md"
)

REQUIRED_COLUMNS = [
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
]


def format_currency(value: float | int) -> str:
    """Format a numeric value as Indonesian Rupiah."""

    return f"Rp {value:,.0f}"


def format_millions(value: float | int) -> str:
    """Format a numeric value using millions."""

    return f"Rp {value / 1_000_000:.1f}M"


def validate_customer_dataset(
    customer: pd.DataFrame,
) -> None:
    """Validate the customer analytical dataset."""

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in customer.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required customer columns: "
            f"{missing_columns}"
        )

    if customer.empty:
        raise ValueError(
            "Customer analytical dataset is empty."
        )

    if customer["customer_id"].duplicated().any():
        raise ValueError(
            "Customer dataset contains duplicate "
            "customer_id values."
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

    for column in numeric_columns:
        if customer[column].isna().any():
            raise ValueError(
                f"Column '{column}' contains null values."
            )

    if (customer["historical_clv"] < 0).any():
        raise ValueError(
            "historical_clv contains negative values."
        )

    if (customer["annualized_clv"] < 0).any():
        raise ValueError(
            "annualized_clv contains negative values."
        )

    if (
        customer["observed_lifetime_days"] < 0
    ).any():
        raise ValueError(
            "observed_lifetime_days contains negative "
            "values."
        )


def validate_clv_reconciliation(
    customer: pd.DataFrame,
) -> None:
    """
    Validate the fundamental CLV accounting relationship.

    Historical CLV is defined as historical gross-profit
    contribution in the current analytical model.
    """

    historical_clv = customer["historical_clv"]
    gross_profit = customer["gross_profit"]

    if not (
        historical_clv.to_numpy()
        == gross_profit.to_numpy()
    ).all():
        raise ValueError(
            "Historical CLV does not reconcile with "
            "customer gross profit."
        )


def assign_clv_tiers(
    customer: pd.DataFrame,
) -> pd.DataFrame:
    """
    Assign customers to relative CLV tiers.

    Tiers are based on annualized CLV:

    - Platinum: top 25%
    - Gold: 25–50%
    - Silver: 50–75%
    - Bronze: bottom 25%
    """

    result = customer.copy()

    result = result.sort_values(
        "annualized_clv",
        ascending=True,
    ).reset_index(drop=True)

    result["clv_tier"] = pd.qcut(
        result["annualized_clv"].rank(
            method="first"
        ),
        q=4,
        labels=[
            "Bronze",
            "Silver",
            "Gold",
            "Platinum",
        ],
    )

    result["clv_tier"] = (
        result["clv_tier"].astype(str)
    )

    return result


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
            observed=False,
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
            average_annualized_clv=(
                "annualized_clv",
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

    summary["clv_tier"] = pd.Categorical(
        summary["clv_tier"],
        categories=tier_order,
        ordered=True,
    )

    summary = summary.sort_values(
        "clv_tier"
    ).reset_index(drop=True)

    return summary


def calculate_clv_concentration(
    customer: pd.DataFrame,
) -> dict[str, float]:
    """
    Calculate CLV concentration metrics.

    Annualized CLV concentration:

        selected annualized CLV
        ----------------------
        total annualized CLV

    Historical CLV concentration:

        selected historical CLV
        ----------------------
        total historical CLV

    This prevents mixing annualized and historical CLV
    into a single concentration metric.
    """

    total_annualized_clv = (
        customer["annualized_clv"].sum()
    )

    total_historical_clv = (
        customer["historical_clv"].sum()
    )

    if total_annualized_clv <= 0:
        raise ValueError(
            "Total annualized CLV must be greater than zero."
        )

    if total_historical_clv <= 0:
        raise ValueError(
            "Total historical CLV must be greater than zero."
        )

    top10 = customer.nlargest(
        10,
        "annualized_clv",
    )

    top25_count = max(
        1,
        int(len(customer) * 0.25),
    )

    top25 = customer.nlargest(
        top25_count,
        "annualized_clv",
    )

    top10_annualized = (
        top10["annualized_clv"].sum()
    )

    top25_annualized = (
        top25["annualized_clv"].sum()
    )

    top10_historical = (
        top10["historical_clv"].sum()
    )

    top25_historical = (
        top25["historical_clv"].sum()
    )

    return {
        "total_annualized_clv": (
            total_annualized_clv
        ),
        "total_historical_clv": (
            total_historical_clv
        ),
        "top10_annualized_clv": (
            top10_annualized
        ),
        "top25_annualized_clv": (
            top25_annualized
        ),
        "top10_historical_clv": (
            top10_historical
        ),
        "top25_historical_clv": (
            top25_historical
        ),
        "top10_annualized_share_pct": (
            top10_annualized
            / total_annualized_clv
            * 100
        ),
        "top25_annualized_share_pct": (
            top25_annualized
            / total_annualized_clv
            * 100
        ),
        "top10_historical_share_pct": (
            top10_historical
            / total_historical_clv
            * 100
        ),
        "top25_historical_share_pct": (
            top25_historical
            / total_historical_clv
            * 100
        ),
    }


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

    concentration = calculate_clv_concentration(
        customer
    )

    highest_annualized = customer.loc[
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
        "highest_annualized": (
            highest_annualized
        ),
        "highest_historical": (
            highest_historical
        ),
        "highest_revenue": (
            highest_revenue
        ),
        "highest_margin": (
            highest_margin
        ),
        "tier_summary": tier_summary,
        **concentration,
    }


def render_report(
    customer: pd.DataFrame,
    insights: dict[str, object],
) -> str:
    """Render the complete CLV Markdown report."""

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

    top10_annualized_share_pct = insights[
        "top10_annualized_share_pct"
    ]

    top25_annualized_share_pct = insights[
        "top25_annualized_share_pct"
    ]

    top10_historical_share_pct = insights[
        "top10_historical_share_pct"
    ]

    top25_historical_share_pct = insights[
        "top25_historical_share_pct"
    ]

    tier_summary = insights[
        "tier_summary"
    ]

    tier_rows: list[str] = []

    for _, row in tier_summary.iterrows():
        tier_rows.append(
            "| "
            f"{row['clv_tier']} | "
            f"{int(row['customers']):,} | "
            f"{row['customer_share_pct']:.1f}% | "
            f"{format_millions(row['revenue'])} | "
            f"{row['revenue_share_pct']:.1f}% | "
            f"{format_millions(row['gross_profit'])} | "
            f"{row['gross_profit_share_pct']:.1f}% | "
            f"{format_currency(row['average_annualized_clv'])} |"
        )

    tier_table = "\n".join(tier_rows)

    return f"""# Mayasari Bakery — Customer Lifetime Value Insights

## 1. Executive Overview

The customer portfolio contains **{len(customer):,} customers**.

Customers generated total revenue of
**{format_millions(total_revenue)}**
and total gross profit of
**{format_millions(total_gross_profit)}**.

Historical CLV averages
**{format_currency(average_historical_clv)}**
per customer.

Annualized CLV averages
**{format_currency(average_annualized_clv)}**,
with a median of
**{format_currency(median_annualized_clv)}**.

In this analytical model, historical CLV represents
historical customer gross-profit contribution.

Therefore:

**Historical CLV = Customer Gross Profit**

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

Annualized CLV is used for customer ranking and concentration analysis.

Historical CLV remains the realized gross-profit contribution
generated during the observed customer lifetime.

---

## 3. CLV Tier Performance

| Tier | Customers | Customer Share | Revenue | Revenue Share | Gross Profit | GP Share | Avg Annualized CLV |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{tier_table}

### Management Interpretation

The tier structure provides a relative ranking of customer economic value.

Platinum and Gold customers should receive greater retention attention
because they represent the highest annualized customer value.

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

### Annualized CLV Concentration

The top 10 customers by annualized CLV account for
**{top10_annualized_share_pct:.2f}%**
of total annualized CLV.

The top 25% of customers by annualized CLV account for
**{top25_annualized_share_pct:.2f}%**
of total annualized CLV.

This is the primary CLV concentration metric because both the
numerator and denominator use the same annualized CLV measure.

### Historical CLV Concentration

The same customers selected by annualized CLV ranking contribute:

- Top 10 annualized-CLV customers:
  **{top10_historical_share_pct:.2f}%**
  of total historical CLV.

- Top 25% annualized-CLV customers:
  **{top25_historical_share_pct:.2f}%**
  of total historical CLV.

Historical CLV concentration provides a realized profitability view,
while annualized CLV concentration provides a normalized customer-value view.

### Metric Reconciliation

The underlying CLV totals reconcile as follows:

| Metric | Total |
| --- | ---: |
| Total annualized CLV | {format_currency(insights['total_annualized_clv'])} |
| Total historical CLV | {format_currency(insights['total_historical_clv'])} |
| Total customer gross profit | {format_currency(total_gross_profit)} |

Historical CLV and customer gross profit are equal in the current
analytical model.

Annualized CLV is intentionally **not** treated as historical gross profit.
It is a normalized value indicator derived from customer economics.

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
- Historical CLV
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
- Annualized CLV should not be interpreted as realized historical profit.

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

Annualized CLV provides a normalized relative indicator that can
help management prioritize retention and customer-development resources.

The most valuable customers should be protected, high-potential customers
should be developed, and lower-value customers should be evaluated for
future growth potential rather than treated as a homogeneous group.

The key management principle is:

**Grow customer lifetime value while protecting gross-profit economics.**

---

*Generated from Mayasari Bakery customer analytical dataset.*
"""


def generate_report(
    customer_path: Path = CUSTOMER_DATASET,
    output_path: Path = OUTPUT_REPORT,
) -> dict[str, object]:
    """Load data, calculate insights, and write the report."""

    customer = pd.read_parquet(
        customer_path
    )

    validate_customer_dataset(customer)

    validate_clv_reconciliation(customer)

    customer = assign_clv_tiers(customer)

    tier_summary = build_tier_summary(
        customer
    )

    insights = generate_insights(
        customer,
        tier_summary,
    )

    report = render_report(
        customer,
        insights,
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        report,
        encoding="utf-8",
    )

    return insights


def print_summary(
    insights: dict[str, object],
) -> None:
    """Print a concise terminal summary."""

    highest_annualized = insights[
        "highest_annualized"
    ]

    highest_historical = insights[
        "highest_historical"
    ]

    highest_revenue = insights[
        "highest_revenue"
    ]

    print("=" * 80)
    print("MAYASARI BAKERY — M12.2 CLV INSIGHTS")
    print("=" * 80)
    print()

    print(
        "Customers             : "
        f"{len(pd.read_parquet(CUSTOMER_DATASET)):,}"
    )

    print(
        "Average historical CLV: "
        f"{format_currency(insights['average_historical_clv'])}"
    )

    print(
        "Average annualized CLV: "
        f"{format_currency(insights['average_annualized_clv'])}"
    )

    print(
        "Median annualized CLV : "
        f"{format_currency(insights['median_annualized_clv'])}"
    )

    print(
        "Top 10 CLV share      : "
        f"{insights['top10_annualized_share_pct']:.2f}%"
    )

    print(
        "Top 25% CLV share     : "
        f"{insights['top25_annualized_share_pct']:.2f}%"
    )

    print(
        "Highest annualized CLV: "
        f"{highest_annualized['customer_id']}"
    )

    print(
        "Highest historical CLV: "
        f"{highest_historical['customer_id']}"
    )

    print(
        "Highest revenue       : "
        f"{highest_revenue['customer_id']}"
    )

    print()

    print(
        "Generated report      : "
        f"{OUTPUT_REPORT.relative_to(PROJECT_ROOT)}"
    )


def main() -> None:
    """CLI entry point."""

    insights = generate_report()

    print_summary(insights)


if __name__ == "__main__":
    main()
