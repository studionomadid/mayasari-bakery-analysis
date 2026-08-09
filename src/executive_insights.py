from pathlib import Path

import pandas as pd


ANALYTICS_DIR = Path("data/analytics")
REPORTS_DIR = Path("reports/insights")

EXECUTIVE_DATA = (
    ANALYTICS_DIR / "executive_kpis.parquet"
)

MONTHLY_DATA = (
    ANALYTICS_DIR / "monthly_performance.parquet"
)

CUSTOMER_DATA = (
    ANALYTICS_DIR / "customer_performance.parquet"
)

PRODUCT_DATA = (
    ANALYTICS_DIR / "product_performance.parquet"
)

PROFITABILITY_DATA = (
    ANALYTICS_DIR / "profitability_summary.parquet"
)

OUTPUT = (
    REPORTS_DIR / "executive_insights.md"
)


def load_data() -> dict[str, pd.DataFrame]:
    """Load and validate executive analytics datasets."""

    datasets = {
        "executive": EXECUTIVE_DATA,
        "monthly": MONTHLY_DATA,
        "customer": CUSTOMER_DATA,
        "product": PRODUCT_DATA,
        "profitability": PROFITABILITY_DATA,
    }

    for name, path in datasets.items():
        if not path.exists():
            raise FileNotFoundError(
                f"{name.title()} dataset not found: {path}"
            )

    data = {
        name: pd.read_parquet(path)
        for name, path in datasets.items()
    }

    if len(data["executive"]) != 1:
        raise ValueError(
            "Executive KPI dataset must contain "
            f"exactly 1 row, found "
            f"{len(data['executive'])}."
        )

    if len(data["profitability"]) != 1:
        raise ValueError(
            "Profitability dataset must contain "
            f"exactly 1 row, found "
            f"{len(data['profitability'])}."
        )

    if len(data["monthly"]) != 12:
        raise ValueError(
            "Monthly performance dataset must contain "
            f"12 rows, found {len(data['monthly'])}."
        )

    if len(data["customer"]) != 850:
        raise ValueError(
            "Customer performance dataset must contain "
            f"850 rows, found {len(data['customer'])}."
        )

    if len(data["product"]) != 28:
        raise ValueError(
            "Product performance dataset must contain "
            f"28 rows, found {len(data['product'])}."
        )

    return data


def format_currency(value: float) -> str:
    """Format IDR values for management reporting."""

    if abs(value) >= 1_000_000_000:
        return (
            f"Rp {value / 1_000_000_000:.1f}B"
        )

    if abs(value) >= 1_000_000:
        return (
            f"Rp {value / 1_000_000:.1f}M"
        )

    if abs(value) >= 1_000:
        return (
            f"Rp {value / 1_000:.1f}K"
        )

    return f"Rp {value:,.0f}"


def build_business_insights(
    data: dict[str, pd.DataFrame],
) -> dict[str, object]:
    """Calculate management-level business insights."""

    executive = data["executive"].iloc[0]
    monthly = data["monthly"].copy()
    customer = data["customer"].copy()
    product = data["product"].copy()
    profitability = data["profitability"].iloc[0]

    monthly = monthly.sort_values(
        "sales_month"
    ).reset_index(drop=True)

    # --------------------------------------------------
    # Business performance
    # --------------------------------------------------

    revenue = float(executive["revenue"])
    gross_profit = float(executive["gross_profit"])
    operating_expense = float(
        executive["operating_expense"]
    )
    operating_profit = float(
        executive["operating_profit"]
    )

    gross_margin = float(
        profitability["gross_margin_pct"]
    )

    operating_margin = (
        operating_profit
        / revenue
        * 100
    )

    # --------------------------------------------------
    # Revenue performance
    # --------------------------------------------------

    peak_index = monthly["revenue"].idxmax()
    lowest_index = monthly["revenue"].idxmin()

    peak_month = monthly.loc[
        peak_index,
        "sales_month",
    ]

    lowest_month = monthly.loc[
        lowest_index,
        "sales_month",
    ]

    peak_revenue = float(
        monthly.loc[
            peak_index,
            "revenue",
        ]
    )

    lowest_revenue = float(
        monthly.loc[
            lowest_index,
            "revenue",
        ]
    )

    growth = monthly[
        "mom_revenue_growth_pct"
    ].dropna()

    best_growth_index = (
        monthly[
            "mom_revenue_growth_pct"
        ].idxmax()
    )

    worst_growth_index = (
        monthly[
            "mom_revenue_growth_pct"
        ].idxmin()
    )

    best_growth_month = monthly.loc[
        best_growth_index,
        "sales_month",
    ]

    worst_growth_month = monthly.loc[
        worst_growth_index,
        "sales_month",
    ]

    best_growth = float(
        monthly.loc[
            best_growth_index,
            "mom_revenue_growth_pct",
        ]
    )

    worst_growth = float(
        monthly.loc[
            worst_growth_index,
            "mom_revenue_growth_pct",
        ]
    )

    # --------------------------------------------------
    # Customer insights
    # --------------------------------------------------

    customer = customer.sort_values(
        "revenue",
        ascending=False,
    ).reset_index(drop=True)

    customer_total_revenue = (
        customer["revenue"].sum()
    )

    top10_customer_share = (
        customer.head(10)["revenue"].sum()
        / customer_total_revenue
        * 100
    )

    top20_customer_share = (
        customer.head(20)["revenue"].sum()
        / customer_total_revenue
        * 100
    )

    average_customer_revenue = (
        customer["revenue"].mean()
    )

    average_customer_clv = (
        customer["historical_clv"].mean()
    )

    top_customer = customer.iloc[0]

    # --------------------------------------------------
    # Product insights
    # --------------------------------------------------

    product = product.sort_values(
        "revenue",
        ascending=False,
    ).reset_index(drop=True)

    product_total_revenue = (
        product["revenue"].sum()
    )

    top10_product_share = (
        product.head(10)["revenue"].sum()
        / product_total_revenue
        * 100
    )

    top_product = product.iloc[0]

    highest_margin_product = product.loc[
        product["gross_margin_pct"].idxmax()
    ]

    lowest_margin_product = product.loc[
        product["gross_margin_pct"].idxmin()
    ]

    # --------------------------------------------------
    # Insight classification
    # --------------------------------------------------

    risk_areas = []
    opportunities = []

    if top10_customer_share >= 30:
        risk_areas.append(
            "Revenue concentration among the top "
            "customer group is relatively high."
        )

    if top10_product_share >= 60:
        risk_areas.append(
            "Product revenue is concentrated in a "
            "small number of products."
        )

    if worst_growth < -5:
        risk_areas.append(
            f"Revenue declined materially in "
            f"{worst_growth_month} "
            f"({worst_growth:.2f}% MoM)."
        )

    if best_growth >= 20:
        opportunities.append(
            f"{best_growth_month} demonstrated strong "
            f"revenue momentum "
            f"({best_growth:.2f}% MoM)."
        )

    if (
        highest_margin_product["gross_margin_pct"]
        - lowest_margin_product["gross_margin_pct"]
        >= 10
    ):
        opportunities.append(
            "There is a meaningful margin gap between "
            "products, indicating potential for "
            "product-mix optimization."
        )

    opportunities.append(
        f"{top_product['product_name']} is the leading "
        "revenue-generating product."
    )

    opportunities.append(
        f"{top_customer['customer_id']} is the highest-"
        "value customer by historical revenue."
    )

    return {
        "revenue": revenue,
        "gross_profit": gross_profit,
        "operating_expense": operating_expense,
        "operating_profit": operating_profit,
        "gross_margin": gross_margin,
        "operating_margin": operating_margin,
        "peak_month": peak_month,
        "peak_revenue": peak_revenue,
        "lowest_month": lowest_month,
        "lowest_revenue": lowest_revenue,
        "best_growth_month": best_growth_month,
        "best_growth": best_growth,
        "worst_growth_month": worst_growth_month,
        "worst_growth": worst_growth,
        "customer_count": len(customer),
        "average_customer_revenue": average_customer_revenue,
        "average_customer_clv": average_customer_clv,
        "top10_customer_share": top10_customer_share,
        "top20_customer_share": top20_customer_share,
        "top_customer_id": top_customer["customer_id"],
        "top_customer_revenue": float(
            top_customer["revenue"]
        ),
        "product_count": len(product),
        "top10_product_share": top10_product_share,
        "top_product_id": top_product["product_id"],
        "top_product_name": top_product["product_name"],
        "top_product_revenue": float(
            top_product["revenue"]
        ),
        "highest_margin_product": (
            highest_margin_product["product_name"]
        ),
        "highest_margin": float(
            highest_margin_product["gross_margin_pct"]
        ),
        "lowest_margin_product": (
            lowest_margin_product["product_name"]
        ),
        "lowest_margin": float(
            lowest_margin_product["gross_margin_pct"]
        ),
        "risk_areas": risk_areas,
        "opportunities": opportunities,
    }


def render_report(
    insights: dict[str, object],
) -> Path:
    """Generate executive insights Markdown report."""

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = f"""# Mayasari Bakery — Executive Insights

## 1. Executive Overview

Mayasari Bakery generated **{format_currency(insights["revenue"])}**
in annual revenue with **{format_currency(insights["gross_profit"])}**
in gross profit.

The business achieved a **{insights["gross_margin"]:.2f}% gross margin**
and a **{insights["operating_margin"]:.2f}% operating margin** after
operating expenses of **{format_currency(insights["operating_expense"])}**.

Overall, the business demonstrates positive operating profitability,
with the main management questions centered on revenue momentum,
customer concentration, product mix, and margin optimization.

---

## 2. Revenue Insights

### Peak Performance

The strongest monthly revenue was recorded in **{insights["peak_month"]}**,
with revenue reaching **{format_currency(insights["peak_revenue"])}**.

The strongest month-over-month growth occurred in
**{insights["best_growth_month"]}**, at **{insights["best_growth"]:.2f}%**.

### Weakest Performance

The lowest monthly revenue occurred in **{insights["lowest_month"]}**,
at **{format_currency(insights["lowest_revenue"])}**.

The weakest month-over-month performance occurred in
**{insights["worst_growth_month"]}**, with revenue changing by
**{insights["worst_growth"]:.2f}%**.

### Management Interpretation

The monthly pattern indicates that revenue performance is not completely
uniform throughout the year. Management should identify the operational
and commercial drivers behind high-growth periods and determine whether
they can be replicated through campaign timing, product availability,
inventory planning, or customer activation.

---

## 3. Customer Insights

The analysis contains **{insights["customer_count"]:,} customers**.

Average historical customer revenue is
**{format_currency(insights["average_customer_revenue"])}**, while
average historical CLV is **{format_currency(insights["average_customer_clv"])}**.

The top 10 customers contribute approximately
**{insights["top10_customer_share"]:.2f}%** of total customer revenue.

The top 20 customers contribute approximately
**{insights["top20_customer_share"]:.2f}%**.

The highest-revenue customer is **{insights["top_customer_id"]}**,
with historical revenue of
**{format_currency(insights["top_customer_revenue"])}**.

### Management Interpretation

Customer revenue is distributed across a broad customer base, but the
contribution of the highest-value customers should still be monitored.
Retention and relationship-building programs should prioritize valuable
customers without creating excessive dependency on a small customer group.

---

## 4. Product Insights

The product portfolio contains **{insights["product_count"]} products**.

The top 10 products contribute approximately
**{insights["top10_product_share"]:.2f}%** of total product revenue.

The leading product is **{insights["top_product_name"]}**
(**{insights["top_product_id"]}**), generating
**{format_currency(insights["top_product_revenue"])}**.

The highest gross-margin product is
**{insights["highest_margin_product"]}**, with a margin of
**{insights["highest_margin"]:.2f}%**.

The lowest gross-margin product is
**{insights["lowest_margin_product"]}**, with a margin of
**{insights["lowest_margin"]:.2f}%**.

### Management Interpretation

Product performance indicates a meaningful opportunity to optimize the
product mix. High-revenue products should remain operational priorities,
while high-margin products can be evaluated for bundling, promotion,
cross-selling, or increased visibility.

---

## 5. Profitability Insights

The business generated:

| Metric | Value |
|---|---:|
| Revenue | {format_currency(insights["revenue"])} |
| Gross Profit | {format_currency(insights["gross_profit"])} |
| Gross Margin | {insights["gross_margin"]:.2f}% |
| Operating Expense | {format_currency(insights["operating_expense"])} |
| Operating Profit | {format_currency(insights["operating_profit"])} |
| Operating Margin | {insights["operating_margin"]:.2f}% |

The positive operating margin indicates that gross profit is sufficient
to cover the current operating expense structure.

Management should therefore focus not only on increasing revenue, but
also on protecting gross margin and improving the contribution of
higher-margin products and customers.

---

## 6. Key Risks

"""

    if insights["risk_areas"]:
        for risk in insights["risk_areas"]:
            report += f"- {risk}\n"
    else:
        report += (
            "- No major automated risk flags were identified "
            "from the current KPI thresholds.\n"
        )

    report += f"""
---

## 7. Business Opportunities

"""

    for opportunity in insights["opportunities"]:
        report += f"- {opportunity}\n"

    report += f"""
---

## 8. Management Priorities

### Priority 1 — Protect Revenue Momentum

Investigate the drivers behind the strongest revenue-growth periods and
identify which commercial or operational factors can be reproduced.

### Priority 2 — Optimize Product Mix

Maintain availability of leading revenue products while increasing the
visibility and contribution of products with stronger margins.

### Priority 3 — Strengthen High-Value Customers

Use customer revenue and CLV data to prioritize retention, repeat
purchase, and targeted relationship strategies.

### Priority 4 — Protect Profitability

Monitor product costs and operating expenses so revenue growth translates
into sustainable operating profit rather than volume growth alone.

---

## 9. Executive Takeaway

Mayasari Bakery currently demonstrates a healthy operating structure with
**{insights["gross_margin"]:.2f}% gross margin** and
**{insights["operating_margin"]:.2f}% operating margin**.

The next stage of business improvement should focus on converting the
existing revenue base into stronger and more predictable profitability
through **revenue momentum management, customer retention, product-mix
optimization, and margin protection**.

---

*Generated from Mayasari Bakery analytical datasets.*
"""

    OUTPUT.write_text(
        report,
        encoding="utf-8",
    )

    return OUTPUT


def validate_output(
    output: Path,
) -> bool:
    """Validate generated executive insights report."""

    exists = output.exists()

    valid_size = (
        output.stat().st_size > 0
        if exists
        else False
    )

    if exists:
        content = output.read_text(
            encoding="utf-8"
        )
    else:
        content = ""

    required_sections = [
        "# Mayasari Bakery — Executive Insights",
        "## 1. Executive Overview",
        "## 2. Revenue Insights",
        "## 3. Customer Insights",
        "## 4. Product Insights",
        "## 5. Profitability Insights",
        "## 6. Key Risks",
        "## 7. Business Opportunities",
        "## 8. Management Priorities",
        "## 9. Executive Takeaway",
    ]

    sections_valid = all(
        section in content
        for section in required_sections
    )

    passed = (
        exists
        and valid_size
        and sections_valid
    )

    print()
    print("=" * 80)
    print(
        "M12.1 EXECUTIVE INSIGHTS VALIDATION"
    )
    print("=" * 80)

    print(
        f"Output exists     : "
        f"{'PASS' if exists else 'REVIEW'}"
    )

    print(
        f"Output size       : "
        f"{output.stat().st_size:,} bytes"
        if exists
        else "Output size       : REVIEW"
    )

    print(
        f"Required sections : "
        f"{'PASS' if sections_valid else 'REVIEW'}"
    )

    print("-" * 80)

    print(
        f"Validation        : "
        f"{'PASS' if passed else 'REVIEW'}"
    )

    return passed


def main() -> None:
    """Generate M12.1 executive insights."""

    print("=" * 80)
    print(
        "MAYASARI BAKERY — M12.1 EXECUTIVE INSIGHTS"
    )
    print("=" * 80)

    data = load_data()

    insights = build_business_insights(
        data
    )

    print()
    print("EXECUTIVE INSIGHT SUMMARY")
    print("-" * 80)

    print(
        f"Revenue              : "
        f"{format_currency(insights['revenue'])}"
    )

    print(
        f"Gross profit         : "
        f"{format_currency(insights['gross_profit'])}"
    )

    print(
        f"Gross margin         : "
        f"{insights['gross_margin']:.2f}%"
    )

    print(
        f"Operating profit     : "
        f"{format_currency(insights['operating_profit'])}"
    )

    print(
        f"Operating margin     : "
        f"{insights['operating_margin']:.2f}%"
    )

    print(
        f"Peak revenue month   : "
        f"{insights['peak_month']}"
    )

    print(
        f"Best MoM growth      : "
        f"{insights['best_growth_month']} "
        f"({insights['best_growth']:.2f}%)"
    )

    print(
        f"Top product          : "
        f"{insights['top_product_name']}"
    )

    print(
        f"Top customer         : "
        f"{insights['top_customer_id']}"
    )

    print(
        f"Top 10 customer share: "
        f"{insights['top10_customer_share']:.2f}%"
    )

    print(
        f"Top 10 product share : "
        f"{insights['top10_product_share']:.2f}%"
    )

    output = render_report(
        insights
    )

    print()
    print(
        f"Generated report     : {output}"
    )

    if not validate_output(output):
        raise SystemExit(1)

    print()
    print("=" * 80)
    print(
        "M12.1 EXECUTIVE INSIGHTS: PASS"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
