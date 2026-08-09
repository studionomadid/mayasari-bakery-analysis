"""
Mayasari Bakery — M12.2.4 Customer Opportunity Insights.

Generates management-oriented insights from the
customer-level opportunity dataset.

The module summarizes customer opportunity groups
using economic value, CLV, RFM behavior, and priority.
"""

from __future__ import annotations

import pandas as pd

from src.contracts.paths import (
    CUSTOMER_OPPORTUNITY_DATA,
    CUSTOMER_OPPORTUNITY_REPORT,
)

INPUT_DATASET = (
    CUSTOMER_OPPORTUNITY_DATA
)

OUTPUT_REPORT = (
    CUSTOMER_OPPORTUNITY_REPORT
)


REQUIRED_COLUMNS = [
    "customer_id",
    "revenue",
    "gross_profit",
    "transactions",
    "active_months",
    "gross_margin_pct",
    "average_transaction_value",
    "historical_clv",
    "annualized_clv",
    "observed_lifetime_days",
    "clv_tier",
    "customer_name",
    "recency",
    "frequency",
    "monetary",
    "rfm_score",
    "rfm_total",
    "segment",
    "opportunity",
    "priority_rationale",
    "opportunity_priority",
]


OPPORTUNITY_ORDER = [
    "Protect",
    "Rescue",
    "Review",
    "Develop",
    "Grow",
    "Monitor",
    "Win-back",
]


def format_currency(value: float) -> str:
    """Format a numeric value as Indonesian Rupiah."""

    return f"Rp {value:,.0f}"


def format_pct(value: float) -> str:
    """Format a percentage value."""

    return f"{value:.2f}%"


def load_opportunity_data() -> pd.DataFrame:
    """Load and validate the opportunity dataset."""

    if not INPUT_DATASET.exists():
        raise FileNotFoundError(
            f"Opportunity dataset not found: {INPUT_DATASET}"
        )

    customer = pd.read_parquet(INPUT_DATASET)

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in customer.columns
    ]

    if missing:
        raise ValueError(
            "Opportunity dataset is missing required columns: "
            f"{missing}"
        )

    if customer.empty:
        raise ValueError(
            "Opportunity dataset is empty."
        )

    if customer["customer_id"].duplicated().any():
        raise ValueError(
            "Opportunity dataset contains duplicate customer IDs."
        )

    if customer["customer_id"].isna().any():
        raise ValueError(
            "Opportunity dataset contains null customer IDs."
        )

    if customer["opportunity"].isna().any():
        raise ValueError(
            "Opportunity dataset contains null opportunities."
        )

    if customer["opportunity_priority"].isna().any():
        raise ValueError(
            "Opportunity dataset contains null priority values."
        )

    return customer


def validate_opportunity_data(
    customer: pd.DataFrame,
) -> None:
    """Validate opportunity coverage and financial reconciliation."""

    expected_opportunities = set(OPPORTUNITY_ORDER)
    actual_opportunities = set(
        customer["opportunity"].unique()
    )

    unexpected = actual_opportunities - expected_opportunities

    if unexpected:
        raise ValueError(
            "Unexpected opportunity classifications: "
            f"{sorted(unexpected)}"
        )

    if len(customer) != customer["customer_id"].nunique():
        raise ValueError(
            "Customer opportunity dataset is not one row per customer."
        )

    if (
        customer["revenue"].sum()
        != customer["monetary"].sum()
    ):
        raise ValueError(
            "Revenue does not reconcile with RFM monetary value."
        )

    if (
        customer["historical_clv"].sum()
        != customer["gross_profit"].sum()
    ):
        raise ValueError(
            "Historical CLV does not reconcile with gross profit."
        )


def build_opportunity_summary(
    customer: pd.DataFrame,
) -> pd.DataFrame:
    """Build opportunity-level economic and behavioral summary."""

    total_customers = len(customer)
    total_revenue = customer["revenue"].sum()
    total_gross_profit = customer["gross_profit"].sum()
    total_annualized_clv = customer["annualized_clv"].sum()

    summary = (
        customer.groupby("opportunity", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            revenue=("revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
            annualized_clv=("annualized_clv", "sum"),
            avg_annualized_clv=("annualized_clv", "mean"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
            avg_margin=("gross_margin_pct", "mean"),
            avg_priority=("opportunity_priority", "mean"),
        )
    )

    summary["customer_share"] = (
        summary["customers"]
        / total_customers
        * 100
    )

    summary["revenue_share"] = (
        summary["revenue"]
        / total_revenue
        * 100
    )

    summary["gross_profit_share"] = (
        summary["gross_profit"]
        / total_gross_profit
        * 100
    )

    summary["clv_share"] = (
        summary["annualized_clv"]
        / total_annualized_clv
        * 100
    )

    summary["opportunity"] = pd.Categorical(
        summary["opportunity"],
        categories=OPPORTUNITY_ORDER,
        ordered=True,
    )

    summary = (
        summary.sort_values("opportunity")
        .reset_index(drop=True)
    )

    return summary


def build_priority_summary(
    customer: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize opportunity groups by management priority."""

    summary = (
        customer.groupby(
            "opportunity_priority",
            as_index=False,
        )
        .agg(
            customers=("customer_id", "count"),
            revenue=("revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
            annualized_clv=("annualized_clv", "sum"),
        )
        .sort_values(
            "opportunity_priority",
            ascending=True,
        )
        .reset_index(drop=True)
    )

    total_customers = len(customer)
    total_revenue = customer["revenue"].sum()
    total_clv = customer["annualized_clv"].sum()

    summary["customer_share"] = (
        summary["customers"]
        / total_customers
        * 100
    )

    summary["revenue_share"] = (
        summary["revenue"]
        / total_revenue
        * 100
    )

    summary["clv_share"] = (
        summary["annualized_clv"]
        / total_clv
        * 100
    )

    return summary


def build_cross_tab(
    customer: pd.DataFrame,
) -> pd.DataFrame:
    """Build CLV tier by opportunity distribution."""

    cross_tab = pd.crosstab(
        customer["clv_tier"],
        customer["opportunity"],
    )

    for opportunity in OPPORTUNITY_ORDER:
        if opportunity not in cross_tab.columns:
            cross_tab[opportunity] = 0

    cross_tab = cross_tab[
        OPPORTUNITY_ORDER
    ]

    tier_order = [
        "Bronze",
        "Silver",
        "Gold",
        "Platinum",
    ]

    cross_tab = cross_tab.reindex(
        tier_order,
        fill_value=0,
    )

    return cross_tab


def build_segment_summary(
    customer: pd.DataFrame,
) -> pd.DataFrame:
    """Build RFM segment by opportunity summary."""

    summary = (
        customer.groupby(
            ["segment", "opportunity"],
            as_index=False,
        )
        .agg(
            customers=("customer_id", "count"),
            revenue=("revenue", "sum"),
            annualized_clv=("annualized_clv", "sum"),
        )
        .sort_values(
            ["opportunity", "annualized_clv"],
            ascending=[True, False],
        )
        .reset_index(drop=True)
    )

    return summary


def identify_priority_groups(
    summary: pd.DataFrame,
) -> list[str]:
    """Identify management priority opportunity groups."""

    ranked = summary.sort_values(
        "annualized_clv",
        ascending=False,
    )

    groups: list[str] = []

    for opportunity in [
        "Rescue",
        "Review",
        "Protect",
        "Develop",
        "Grow",
    ]:
        if opportunity in set(ranked["opportunity"]):
            groups.append(opportunity)

    return groups


def build_management_insights(
    customer: pd.DataFrame,
    summary: pd.DataFrame,
) -> list[str]:
    """Generate concise management-oriented insights."""

    insights: list[str] = []

    highest_clv = summary.loc[
        summary["annualized_clv"].idxmax()
    ]

    highest_revenue = summary.loc[
        summary["revenue"].idxmax()
    ]

    largest = summary.loc[
        summary["customers"].idxmax()
    ]

    insights.append(
        f"{highest_clv['opportunity']} has the highest "
        f"annualized CLV contribution at "
        f"{format_currency(highest_clv['annualized_clv'])} "
        f"({format_pct(highest_clv['clv_share'])} of total "
        f"annualized CLV)."
    )

    insights.append(
        f"{highest_revenue['opportunity']} represents the "
        f"largest revenue pool at "
        f"{format_currency(highest_revenue['revenue'])} "
        f"({format_pct(highest_revenue['revenue_share'])} "
        f"of total revenue)."
    )

    insights.append(
        f"{largest['opportunity']} is the largest customer "
        f"group with {int(largest['customers']):,} customers "
        f"({format_pct(largest['customer_share'])} of the "
        f"customer base)."
    )

    priority_groups = {
        "Rescue",
        "Review",
        "Protect",
    }

    priority = summary[
        summary["opportunity"].isin(priority_groups)
    ]

    if not priority.empty:
        priority_customers = priority["customers"].sum()
        priority_revenue = priority["revenue"].sum()
        priority_clv = priority["annualized_clv"].sum()

        total_customers = len(customer)
        total_revenue = customer["revenue"].sum()
        total_clv = customer["annualized_clv"].sum()

        insights.append(
            f"Rescue, Review, and Protect together cover "
            f"{priority_customers:,} customers "
            f"({format_pct(priority_customers / total_customers * 100)}) "
            f"and represent "
            f"{format_currency(priority_revenue)} of revenue "
            f"({format_pct(priority_revenue / total_revenue * 100)}) "
            f"and "
            f"{format_currency(priority_clv)} of annualized CLV "
            f"({format_pct(priority_clv / total_clv * 100)})."
        )

    return insights


def render_report(
    customer: pd.DataFrame,
    summary: pd.DataFrame,
    priority_summary: pd.DataFrame,
    cross_tab: pd.DataFrame,
    segment_summary: pd.DataFrame,
    insights: list[str],
) -> str:
    """Render the complete Markdown management report."""

    total_customers = len(customer)
    total_revenue = customer["revenue"].sum()
    total_gross_profit = customer["gross_profit"].sum()
    total_clv = customer["annualized_clv"].sum()

    lines: list[str] = []

    lines.extend(
        [
            "# MAYASARI BAKERY — CUSTOMER OPPORTUNITY INSIGHTS",
            "",
            "## 1. Executive Summary",
            "",
            (
                "This report translates the customer-level opportunity "
                "classification into management-oriented insights. "
                "The analysis combines customer economic value, CLV, "
                "RFM behavior, and opportunity priority."
            ),
            "",
            "### Portfolio Snapshot",
            "",
            f"- Customers: **{total_customers:,}**",
            f"- Revenue: **{format_currency(total_revenue)}**",
            f"- Gross profit: **{format_currency(total_gross_profit)}**",
            f"- Annualized CLV: **{format_currency(total_clv)}**",
            "",
            "### Key Insights",
            "",
        ]
    )

    for index, insight in enumerate(insights, start=1):
        lines.append(f"{index}. {insight}")

    lines.extend(
        [
            "",
            "## 2. Opportunity Performance",
            "",
            (
                "Opportunity groups are evaluated using customer "
                "count, revenue, gross profit, and annualized CLV."
            ),
            "",
            "| Opportunity | Customers | Customer Share | Revenue | Revenue Share | Gross Profit | GP Share | Annualized CLV | CLV Share | Avg CLV | Avg Recency | Avg Frequency | Avg Margin |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    for _, row in summary.iterrows():
        lines.append(
            "| "
            f"{row['opportunity']} | "
            f"{int(row['customers']):,} | "
            f"{format_pct(row['customer_share'])} | "
            f"{format_currency(row['revenue'])} | "
            f"{format_pct(row['revenue_share'])} | "
            f"{format_currency(row['gross_profit'])} | "
            f"{format_pct(row['gross_profit_share'])} | "
            f"{format_currency(row['annualized_clv'])} | "
            f"{format_pct(row['clv_share'])} | "
            f"{format_currency(row['avg_annualized_clv'])} | "
            f"{row['avg_recency']:.1f}d | "
            f"{row['avg_frequency']:.1f} | "
            f"{row['avg_margin']:.2f}% |"
        )

    lines.extend(
        [
            "",
            "## 3. Management Priority View",
            "",
            (
                "Opportunity priority is interpreted as a decision-support "
                "indicator rather than a causal measure of customer risk."
            ),
            "",
            "| Priority | Customers | Customer Share | Revenue | Revenue Share | Annualized CLV | CLV Share |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    for _, row in priority_summary.iterrows():
        lines.append(
            "| "
            f"{int(row['opportunity_priority'])} | "
            f"{int(row['customers']):,} | "
            f"{format_pct(row['customer_share'])} | "
            f"{format_currency(row['revenue'])} | "
            f"{format_pct(row['revenue_share'])} | "
            f"{format_currency(row['annualized_clv'])} | "
            f"{format_pct(row['clv_share'])} |"
        )

    lines.extend(
        [
            "",
            "## 4. CLV Tier × Opportunity",
            "",
            (
                "This matrix shows how opportunity classifications are "
                "distributed across relative CLV tiers."
            ),
            "",
            "| CLV Tier | Protect | Rescue | Review | Develop | Grow | Monitor | Win-back |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    for tier, row in cross_tab.iterrows():
        lines.append(
            "| "
            f"{tier} | "
            f"{int(row['Protect']):,} | "
            f"{int(row['Rescue']):,} | "
            f"{int(row['Review']):,} | "
            f"{int(row['Develop']):,} | "
            f"{int(row['Grow']):,} | "
            f"{int(row['Monitor']):,} | "
            f"{int(row['Win-back']):,} |"
        )

    lines.extend(
        [
            "",
            "## 5. RFM Segment × Opportunity",
            "",
            (
                "The following table identifies the behavioral segments "
                "contained within each opportunity group."
            ),
            "",
            "| Segment | Opportunity | Customers | Revenue | Annualized CLV |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )

    for _, row in segment_summary.iterrows():
        lines.append(
            "| "
            f"{row['segment']} | "
            f"{row['opportunity']} | "
            f"{int(row['customers']):,} | "
            f"{format_currency(row['revenue'])} | "
            f"{format_currency(row['annualized_clv'])} |"
        )

    lines.extend(
        [
            "",
            "## 6. Management Interpretation",
            "",
            "### Protect",
            "",
            (
                "Protect customers should be treated as high-value "
                "relationships where retention is economically important. "
                "The objective is to reduce unnecessary churn risk and "
                "maintain purchasing continuity."
            ),
            "",
            "### Rescue",
            "",
            (
                "Rescue customers warrant targeted recovery actions. "
                "Their economic contribution should be considered when "
                "allocating retention effort, rather than treating all "
                "inactive customers equally."
            ),
            "",
            "### Review",
            "",
            (
                "Review represents customers requiring additional "
                "diagnostic attention. Management should investigate the "
                "combination of CLV, RFM behavior, and recent purchasing "
                "patterns before applying a specific intervention."
            ),
            "",
            "### Develop",
            "",
            (
                "Develop customers represent opportunities to increase "
                "customer value through frequency, basket expansion, "
                "cross-sell, or other relevant commercial mechanisms."
            ),
            "",
            "### Grow",
            "",
            (
                "Grow customers can be approached with measured "
                "development initiatives. The objective is to increase "
                "economic value without over-investing relative to their "
                "current contribution."
            ),
            "",
            "### Monitor",
            "",
            (
                "Monitor customers should remain under observation with "
                "lightweight engagement. Management attention can be "
                "increased if their behavioral or economic profile changes."
            ),
            "",
            "### Win-back",
            "",
            (
                "Win-back customers represent lapsed relationships where "
                "reactivation may be considered. Recovery economics should "
                "be evaluated before committing significant resources."
            ),
            "",
            "## 7. Management Priorities",
            "",
            "1. Protect economically important customer relationships.",
            "2. Prioritize Rescue customers using customer value rather than volume alone.",
            "3. Review high-value customers whose behavioral signals require investigation.",
            "4. Develop customers with credible potential for increased value.",
            "5. Use lightweight monitoring for lower-priority customers.",
            "6. Measure intervention outcomes before expanding campaign investment.",
            "",
            "## 8. Analytical Limitations",
            "",
            (
                "Opportunity classifications are analytical decision-support "
                "labels derived from the current CLV and RFM framework. "
                "They should not be interpreted as causal predictions of "
                "future customer behavior."
            ),
            "",
            (
                "Annualized CLV is a normalized customer-value indicator "
                "and should be interpreted alongside historical contribution "
                "and observed customer behavior."
            ),
            "",
        ]
    )

    return "\n".join(lines)


def generate_report() -> str:
    """Generate and persist the opportunity insights report."""

    customer = load_opportunity_data()

    validate_opportunity_data(customer)

    summary = build_opportunity_summary(customer)

    priority_summary = build_priority_summary(customer)

    cross_tab = build_cross_tab(customer)

    segment_summary = build_segment_summary(customer)

    insights = build_management_insights(
        customer,
        summary,
    )

    report = render_report(
        customer,
        summary,
        priority_summary,
        cross_tab,
        segment_summary,
        insights,
    )

    CUSTOMER_OPPORTUNITY_REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_REPORT.write_text(
        report,
        encoding="utf-8",
    )

    return report


def print_summary(
    customer: pd.DataFrame,
    summary: pd.DataFrame,
) -> None:
    """Print concise execution summary."""

    print()
    print("=" * 80)
    print("MAYASARI BAKERY — M12.2.4 OPPORTUNITY INSIGHTS")
    print("=" * 80)

    print()
    print(f"Customers             : {len(customer):,}")
    print(
        "Total revenue         : "
        f"{format_currency(customer['revenue'].sum())}"
    )
    print(
        "Total gross profit    : "
        f"{format_currency(customer['gross_profit'].sum())}"
    )
    print(
        "Total annualized CLV  : "
        f"{format_currency(customer['annualized_clv'].sum())}"
    )

    print()
    print("OPPORTUNITY SUMMARY")
    print("-" * 80)

    display = summary[
        [
            "opportunity",
            "customers",
            "revenue",
            "revenue_share",
            "annualized_clv",
            "clv_share",
            "avg_recency",
            "avg_frequency",
        ]
    ].copy()

    display["revenue"] = display["revenue"].map(
        format_currency
    )

    display["revenue_share"] = display[
        "revenue_share"
    ].map(format_pct)

    display["annualized_clv"] = display[
        "annualized_clv"
    ].map(format_currency)

    display["clv_share"] = display[
        "clv_share"
    ].map(format_pct)

    display["avg_recency"] = display[
        "avg_recency"
    ].map(
        lambda value: f"{value:.1f}d"
    )

    display["avg_frequency"] = display[
        "avg_frequency"
    ].map(
        lambda value: f"{value:.1f}"
    )

    print(display.to_string(index=False))

    print()
    print(
        "Generated report      : "
        f"{OUTPUT_REPORT}"
    )


def main() -> None:
    """Run M12.2.4 opportunity insights."""

    customer = load_opportunity_data()

    validate_opportunity_data(customer)

    summary = build_opportunity_summary(customer)

    report = generate_report()

    print_summary(
        customer,
        summary,
    )

    print()
    print(
        "Report generation      : "
        f"{'PASS' if report else 'REVIEW'}"
    )


if __name__ == "__main__":
    main()
