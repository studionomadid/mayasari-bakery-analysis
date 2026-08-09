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

M12.2.2 extends the CLV insight layer with:

- CLV distribution statistics.
- Annualized CLV contribution by tier.
- Customer value-driver analysis.
- Correlation-based association analysis.
- Management-oriented CLV interpretation.
"""

from __future__ import annotations

from math import ceil
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

    total_annualized_clv = (
        customer["annualized_clv"].sum()
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
            annualized_clv=(
                "annualized_clv",
                "sum",
            ),
            average_annualized_clv=(
                "annualized_clv",
                "mean",
            ),
            average_transactions=(
                "transactions",
                "mean",
            ),
            average_lifetime_days=(
                "observed_lifetime_days",
                "mean",
            ),
            average_margin_pct=(
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

    summary["annualized_clv_share_pct"] = (
        summary["annualized_clv"]
        / total_annualized_clv
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

    summary = (
        summary
        .sort_values("clv_tier")
        .reset_index(drop=True)
    )

    return summary


def calculate_clv_distribution(
    customer: pd.DataFrame,
) -> dict[str, float]:
    """Calculate annualized CLV distribution statistics."""

    clv = customer["annualized_clv"]

    return {
        "min_annualized_clv": float(clv.min()),
        "q1_annualized_clv": float(clv.quantile(0.25)),
        "median_annualized_clv": float(clv.median()),
        "q3_annualized_clv": float(clv.quantile(0.75)),
        "max_annualized_clv": float(clv.max()),
        "mean_annualized_clv": float(clv.mean()),
    }


def calculate_clv_concentration(
    customer: pd.DataFrame,
) -> dict[str, float]:
    """
    Calculate CLV concentration metrics.

    Annualized CLV concentration:

        selected annualized CLV
        -----------------------
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

    top10_count = min(
        10,
        len(customer),
    )

    top10 = customer.nlargest(
        top10_count,
        "annualized_clv",
    )

    top25_count = max(
        1,
        ceil(len(customer) * 0.25),
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


def calculate_value_driver_analysis(
    customer: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate associations between annualized CLV
    and selected customer economic drivers.

    Correlation indicates statistical association only.
    It must not be interpreted as causation.
    """

    driver_columns = [
        "revenue",
        "transactions",
        "active_months",
        "observed_lifetime_days",
        "gross_margin_pct",
        "average_transaction_value",
        "historical_clv",
    ]

    rows: list[dict[str, float | str]] = []

    for column in driver_columns:
        correlation = customer[
            "annualized_clv"
        ].corr(customer[column])

        if pd.isna(correlation):
            correlation = 0.0

        rows.append(
            {
                "driver": column,
                "correlation": float(correlation),
                "absolute_correlation": abs(
                    float(correlation)
                ),
            }
        )

    result = pd.DataFrame(rows)

    result["relationship"] = result[
        "correlation"
    ].apply(
        classify_correlation
    )

    return (
        result
        .sort_values(
            "absolute_correlation",
            ascending=False,
        )
        .reset_index(drop=True)
    )


def classify_correlation(
    correlation: float,
) -> str:
    """Classify the strength of a correlation."""

    absolute_value = abs(correlation)

    if absolute_value >= 0.70:
        strength = "Strong"
    elif absolute_value >= 0.40:
        strength = "Moderate"
    elif absolute_value >= 0.20:
        strength = "Weak"
    else:
        strength = "Very weak"

    direction = (
        "positive"
        if correlation >= 0
        else "negative"
    )

    return f"{strength} {direction}"


def generate_management_insights(
    customer: pd.DataFrame,
    tier_summary: pd.DataFrame,
    driver_analysis: pd.DataFrame,
) -> dict[str, str]:
    """Generate concise management-oriented CLV insights."""

    platinum = tier_summary.loc[
        tier_summary["clv_tier"] == "Platinum"
    ]

    gold = tier_summary.loc[
        tier_summary["clv_tier"] == "Gold"
    ]

    if platinum.empty:
        platinum_clv_share = 0.0
    else:
        platinum_clv_share = float(
            platinum[
                "annualized_clv_share_pct"
            ].iloc[0]
        )

    if gold.empty:
        gold_clv_share = 0.0
    else:
        gold_clv_share = float(
            gold[
                "annualized_clv_share_pct"
            ].iloc[0]
        )

    top_driver = driver_analysis.iloc[0]

    top_driver_name = str(
        top_driver["driver"]
    )

    top_driver_correlation = float(
        top_driver["correlation"]
    )

    if top_driver_correlation >= 0:
        driver_direction = "positively"
    else:
        driver_direction = "negatively"

    return {
        "protection_priority": (
            "Platinum customers should receive "
            "priority retention attention because "
            f"they contribute {platinum_clv_share:.1f}% "
            "of total annualized CLV."
        ),
        "development_priority": (
            "Gold customers represent a potential "
            "upgrade pool because they occupy the "
            "second-highest relative CLV tier and "
            f"contribute {gold_clv_share:.1f}% "
            "of total annualized CLV."
        ),
        "driver_priority": (
            f"{top_driver_name} shows the strongest "
            f"observed association with annualized CLV "
            f"({top_driver_correlation:.2f}), "
            f"with a {driver_direction} relationship."
        ),
        "interpretation_note": (
            "Correlation identifies association rather "
            "than causation. Customer-level actions should "
            "therefore be validated through behavioral and "
            "commercial analysis."
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

    distribution = calculate_clv_distribution(
        customer
    )

    driver_analysis = (
        calculate_value_driver_analysis(
            customer
        )
    )

    management_insights = (
        generate_management_insights(
            customer,
            tier_summary,
            driver_analysis,
        )
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
        "driver_analysis": driver_analysis,
        "management_insights": (
            management_insights
        ),
        **distribution,
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

    tier_summary = insights[
        "tier_summary"
    ]

    driver_analysis = insights[
        "driver_analysis"
    ]

    management_insights = insights[
        "management_insights"
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

    tier_rows: list[str] = []

    for _, row in tier_summary.iterrows():
        tier_rows.append(
            f"| {row['clv_tier']} "
            f"| {int(row['customers']):,} "
            f"| {row['customer_share_pct']:.1f}% "
            f"| {format_currency(row['revenue'])} "
            f"| {row['revenue_share_pct']:.1f}% "
            f"| {format_currency(row['gross_profit'])} "
            f"| {row['gross_profit_share_pct']:.1f}% "
            f"| {format_currency(row['annualized_clv'])} "
            f"| {row['annualized_clv_share_pct']:.1f}% "
            f"| {format_currency(row['average_annualized_clv'])} "
            f"| {row['average_transactions']:.2f} "
            f"| {row['average_lifetime_days']:.1f} "
            f"| {row['average_margin_pct']:.2f}% |"
        )

    tier_table = "\n".join(tier_rows)

    driver_rows: list[str] = []

    for _, row in driver_analysis.iterrows():
        driver_rows.append(
            f"| {row['driver']} "
            f"| {row['correlation']:.3f} "
            f"| {row['relationship']} |"
        )

    driver_table = "\n".join(driver_rows)

    return f"""# Mayasari Bakery — Customer Lifetime Value Insights

## 1. Executive Overview

The customer portfolio contains **{len(customer):,} customers**.

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

Therefore:

**Historical CLV = Customer Gross Profit**

---

## 2. Annualized CLV Distribution

Annualized CLV distribution:

| Statistic | Value |
| --------- | ----: |
| Minimum | {format_currency(insights['min_annualized_clv'])} |
| Q1 | {format_currency(insights['q1_annualized_clv'])} |
| Median | {format_currency(insights['median_annualized_clv'])} |
| Q3 | {format_currency(insights['q3_annualized_clv'])} |
| Maximum | {format_currency(insights['max_annualized_clv'])} |

The distribution shows the spread of normalized customer value
across the observed customer population.

The gap between median and maximum CLV should be monitored because
a large difference may indicate a concentrated high-value customer
population.

---

## 3. CLV Tier Performance

CLV tiers are based on relative annualized CLV:

- **Platinum** — top 25%
- **Gold** — 25–50%
- **Silver** — 50–75%
- **Bronze** — bottom 25%

| Tier | Customers | Customer Share | Revenue | Revenue Share | Gross Profit | GP Share | Annualized CLV | CLV Share | Avg Annualized CLV | Avg Transactions | Avg Lifetime (Days) | Avg Margin |
| ---- | --------: | -------------: | ------: | ------------: | -----------: | -------: | --------------: | --------: | -----------------: | ---------------: | ------------------: | ---------: |
{tier_table}

The annualized CLV share column shows how normalized customer value
is distributed across the four relative-value tiers.

Platinum and Gold customers should receive greater retention and
development attention because they represent the highest-value
segments of the current customer portfolio.

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

### Highest Gross-Margin Customer

Customer **{highest_margin['customer_id']}**
has the highest gross-margin percentage at
**{highest_margin['gross_margin_pct']:.2f}%**.

These customers should be evaluated separately because revenue,
historical gross-profit contribution, margin, and annualized CLV
represent different dimensions of customer economics.

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
while annualized CLV concentration provides a normalized customer-value
view.

---

## 6. Customer Value Drivers

Annualized CLV is compared with selected customer economic and
behavioral variables.

The correlation values below indicate **association**, not causation.

| Driver | Correlation with Annualized CLV | Relationship |
| ------ | ------------------------------: | ------------ |
{driver_table}

The strongest observed association is:

**{management_insights['driver_priority']}**

This relationship should be investigated further through behavioral
analysis before being translated into a causal business conclusion.

---

## 7. Metric Reconciliation

The underlying CLV totals reconcile as follows:

| Metric | Total |
| ------ | ----: |
| Total annualized CLV | {format_currency(insights['total_annualized_clv'])} |
| Total historical CLV | {format_currency(insights['total_historical_clv'])} |
| Total customer gross profit | {format_currency(total_gross_profit)} |

Historical CLV and customer gross profit are equal in the current
analytical model.

Annualized CLV is intentionally **not** treated as historical gross profit.

It is a normalized customer-value indicator derived from customer
economics.

---

## 8. Management Priorities

### Priority 1 — Protect Platinum Customers

{management_insights['protection_priority']}

Potential actions include:

- Priority service
- Personalized offers
- Repeat-purchase reminders
- Product recommendations
- Early access to seasonal products

### Priority 2 — Develop Gold Customers

{management_insights['development_priority']}

Potential development levers include:

- Increasing purchase frequency
- Increasing basket value
- Expanding product breadth
- Encouraging repeat purchases
- Improving customer lifetime

### Priority 3 — Investigate Value Drivers

{management_insights['driver_priority']}

{management_insights['interpretation_note']}

---

## 9. Customer Value vs Profitability

Customer value should not be evaluated from revenue alone.

A customer can generate high revenue but lower margin, while another
customer may generate less revenue but stronger gross-profit economics.

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

## 10. Business Opportunities

### Opportunity 1 — Protect High-Value Customers

Create retention and relationship-management actions for Platinum
customers and other customers with unusually high annualized CLV.

### Opportunity 2 — Develop Gold Customers

Gold customers represent an attractive upgrade pool.

Focus on increasing purchase frequency, basket value, product breadth,
and customer lifetime.

### Opportunity 3 — Monitor Emerging Customers

Some Bronze and Silver customers may have relatively short observed
lifetimes.

These customers should be monitored for early signals of increasing
purchase frequency or transaction value.

### Opportunity 4 — Validate CLV Drivers

The strongest statistical associations with annualized CLV should
be investigated through customer behavior analysis.

Correlation should be treated as a prioritization tool for further
analysis, not as evidence of causality.

---

## 11. Analytical Limitations

Several limitations should be considered:

- Historical CLV represents realized gross-profit contribution,
  not future customer lifetime value.
- Annualized CLV is a normalized indicator rather than realized profit.
- Annualized CLV can be sensitive to short observed customer lifetimes.
- Relative CLV tiers rank customers within the current population but do not
  establish absolute economic thresholds.
- Correlation analysis identifies association rather than causation.
- Customer behavior may change after the observation period.
- Gross margin is based on the current analytical gross-profit definition.

Annualized CLV should therefore be interpreted as a comparative
customer-value indicator rather than a forecast of future realized profit.

---

## 12. Conclusion

The customer portfolio demonstrates meaningful variation in economic value.

Platinum customers represent the highest relative annualized customer
value and should receive priority retention attention.

Gold customers represent an important development opportunity because
they already demonstrate relatively strong annualized customer value.

The distribution and concentration metrics provide visibility into
whether customer value is broadly distributed or concentrated among
a smaller group of customers.

The value-driver analysis provides a structured starting point for
understanding which customer behaviors and economic characteristics
are most strongly associated with annualized CLV.

The combination of CLV, revenue, gross profit, transaction frequency,
customer lifetime, average transaction value, and margin provides a more
complete framework for customer-value management than revenue alone.
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
    print(
        "MAYASARI BAKERY — M12.2 CLV INSIGHTS"
    )
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
