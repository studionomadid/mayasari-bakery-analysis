"""
M24.3 — Mayasari Bakery Customer Insight Calculation Engine.

Calculates evidence metrics required by the customer insight framework.

The engine intentionally separates:
    1. validated input data,
    2. deterministic calculations,
    3. evidence metrics,
    4. validation.

No business recommendation text is generated here.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Final

import pandas as pd

from src.customer_insight_framework import (
    CUSTOMER_INSIGHT_FRAMEWORK,
    InsightDefinition,
    validate_framework,
)


ROOT: Final[Path] = Path(__file__).resolve().parents[1]

CUSTOMER_OPPORTUNITY_DATA: Final[Path] = (
    ROOT / "data" / "analytics" / "customer_opportunity.parquet"
)


REQUIRED_COLUMNS: Final[frozenset[str]] = frozenset(
    {
        "customer_id",
        "revenue",
        "gross_profit",
        "transactions",
        "active_months",
        "gross_margin_pct",
        "average_transaction_value",
        "historical_clv",
        "annualized_clv",
        "clv_tier",
        "recency",
        "frequency",
        "monetary",
        "rfm_score",
        "rfm_total",
        "segment",
        "opportunity",
        "opportunity_priority",
        "priority_rationale",
    }
)


CLV_TIER_ORDER: Final[tuple[str, ...]] = (
    "Platinum",
    "Gold",
    "Silver",
    "Bronze",
)


OPPORTUNITY_ORDER: Final[tuple[str, ...]] = (
    "Rescue",
    "Protect",
    "Develop",
    "Grow",
    "Win-back",
    "Monitor",
    "Review",
)


def load_customer_data(
    path: Path = CUSTOMER_OPPORTUNITY_DATA,
) -> pd.DataFrame:
    """Load and validate the customer opportunity dataset."""

    if not path.exists():
        raise FileNotFoundError(
            f"Customer opportunity dataset not found: {path}"
        )

    customer = pd.read_parquet(path)

    missing_columns = REQUIRED_COLUMNS.difference(customer.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            "Customer opportunity dataset is missing required columns: "
            f"{missing}"
        )

    if customer.empty:
        raise ValueError(
            "Customer opportunity dataset is empty."
        )

    result = customer.copy()

    if result["customer_id"].duplicated().any():
        raise ValueError(
            "Customer opportunity dataset contains duplicate customer IDs."
        )

    if result["customer_id"].isna().any():
        raise ValueError(
            "Customer opportunity dataset contains null customer IDs."
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
        "recency",
        "frequency",
        "monetary",
        "rfm_total",
        "opportunity_priority",
    ]

    for column in numeric_columns:
        result[column] = pd.to_numeric(
            result[column],
            errors="raise",
        )

    return result


def validate_customer_data(
    customer: pd.DataFrame,
) -> None:
    """Validate customer dataset integrity and business reconciliations."""

    if customer.empty:
        raise ValueError("Customer dataset is empty.")

    if customer["customer_id"].duplicated().any():
        raise ValueError(
            "Customer dataset contains duplicate customer IDs."
        )

    if customer["customer_id"].isna().any():
        raise ValueError(
            "Customer dataset contains null customer IDs."
        )

    if customer["revenue"].isna().any():
        raise ValueError("Revenue contains null values.")

    if customer["gross_profit"].isna().any():
        raise ValueError("Gross profit contains null values.")

    if customer["annualized_clv"].isna().any():
        raise ValueError("Annualized CLV contains null values.")

    if not set(customer["clv_tier"].unique()).issubset(
        set(CLV_TIER_ORDER)
    ):
        raise ValueError(
            "Customer dataset contains unexpected CLV tiers."
        )

    if not set(customer["opportunity"].unique()).issubset(
        set(OPPORTUNITY_ORDER)
    ):
        raise ValueError(
            "Customer dataset contains unexpected opportunity groups."
        )

    historical_clv_difference = (
        customer["historical_clv"].sum()
        - customer["gross_profit"].sum()
    )

    if abs(historical_clv_difference) > 0.01:
        raise ValueError(
            "Historical CLV does not reconcile with gross profit."
        )

    monetary_difference = (
        customer["monetary"].sum()
        - customer["revenue"].sum()
    )

    if abs(monetary_difference) > 0.01:
        raise ValueError(
            "RFM monetary value does not reconcile with revenue."
        )


def calculate_customer_value_concentration(
    customer: pd.DataFrame,
) -> dict[str, float]:
    """Calculate customer annualized CLV concentration metrics."""

    ordered = customer.sort_values(
        "annualized_clv",
        ascending=False,
    )

    total_clv = float(
        ordered["annualized_clv"].sum()
    )

    top_10 = float(
        ordered.head(10)["annualized_clv"].sum()
    )

    top_25 = float(
        ordered.head(25)["annualized_clv"].sum()
    )

    platinum = float(
        ordered.loc[
            ordered["clv_tier"] == "Platinum",
            "annualized_clv",
        ].sum()
    )

    return {
        "total_annualized_clv": total_clv,
        "top_10_clv": top_10,
        "top_25_clv": top_25,
        "top_10_clv_share": (
            top_10 / total_clv * 100
            if total_clv
            else 0.0
        ),
        "top_25_clv_share": (
            top_25 / total_clv * 100
            if total_clv
            else 0.0
        ),
        "platinum_clv_share": (
            platinum / total_clv * 100
            if total_clv
            else 0.0
        ),
    }


def calculate_clv_tier_economics(
    customer: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate economic contribution by CLV tier."""

    total_clv = float(
        customer["annualized_clv"].sum()
    )

    summary = (
        customer.groupby("clv_tier", as_index=False)
        .agg(
            customer_count=(
                "customer_id",
                "nunique",
            ),
            annualized_clv=(
                "annualized_clv",
                "sum",
            ),
            average_annualized_clv=(
                "annualized_clv",
                "mean",
            ),
            historical_clv=(
                "historical_clv",
                "sum",
            ),
        )
    )

    summary["customer_share"] = (
        summary["customer_count"]
        / customer["customer_id"].nunique()
        * 100
    )

    summary["clv_share"] = (
        summary["annualized_clv"]
        / total_clv
        * 100
        if total_clv
        else 0.0
    )

    summary["clv_tier"] = pd.Categorical(
        summary["clv_tier"],
        categories=CLV_TIER_ORDER,
        ordered=True,
    )

    return summary.sort_values(
        "clv_tier"
    ).reset_index(drop=True)


def calculate_rfm_customer_quality(
    customer: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate customer behavior summary by RFM segment."""

    total_customers = customer["customer_id"].nunique()

    summary = (
        customer.groupby("segment", as_index=False)
        .agg(
            customer_count=(
                "customer_id",
                "nunique",
            ),
            revenue=(
                "revenue",
                "sum",
            ),
            gross_profit=(
                "gross_profit",
                "sum",
            ),
            average_rfm=(
                "rfm_total",
                "mean",
            ),
            average_recency=(
                "recency",
                "mean",
            ),
            average_frequency=(
                "frequency",
                "mean",
            ),
            average_monetary=(
                "monetary",
                "mean",
            ),
        )
    )

    summary["customer_share"] = (
        summary["customer_count"]
        / total_customers
        * 100
    )

    return summary.sort_values(
        "customer_count",
        ascending=False,
    ).reset_index(drop=True)


def calculate_customer_opportunity_priority(
    customer: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate customer opportunity economics and priority."""

    total_customers = customer["customer_id"].nunique()

    total_clv = float(
        customer["annualized_clv"].sum()
    )

    summary = (
        customer.groupby(
            "opportunity",
            as_index=False,
        )
        .agg(
            customer_count=(
                "customer_id",
                "nunique",
            ),
            annualized_clv=(
                "annualized_clv",
                "sum",
            ),
            average_annualized_clv=(
                "annualized_clv",
                "mean",
            ),
            average_priority=(
                "opportunity_priority",
                "mean",
            ),
        )
    )

    summary["customer_share"] = (
        summary["customer_count"]
        / total_customers
        * 100
    )

    summary["clv_share"] = (
        summary["annualized_clv"]
        / total_clv
        * 100
        if total_clv
        else 0.0
    )

    summary["opportunity"] = pd.Categorical(
        summary["opportunity"],
        categories=OPPORTUNITY_ORDER,
        ordered=True,
    )

    return summary.sort_values(
        "opportunity"
    ).reset_index(drop=True)


def calculate_rescue_economics(
    customer: pd.DataFrame,
) -> dict[str, float]:
    """Calculate economic metrics for Rescue customers."""

    rescue = customer.loc[
        customer["opportunity"] == "Rescue"
    ]

    total_customers = customer["customer_id"].nunique()

    total_clv = float(
        customer["annualized_clv"].sum()
    )

    rescue_clv = float(
        rescue["annualized_clv"].sum()
    )

    platinum_count = int(
        (
            rescue["clv_tier"] == "Platinum"
        ).sum()
    )

    return {
        "rescue_customer_count": float(
            rescue["customer_id"].nunique()
        ),
        "rescue_customer_share": (
            rescue["customer_id"].nunique()
            / total_customers
            * 100
            if total_customers
            else 0.0
        ),
        "rescue_annualized_clv": rescue_clv,
        "rescue_clv_share": (
            rescue_clv / total_clv * 100
            if total_clv
            else 0.0
        ),
        "rescue_average_clv": (
            float(
                rescue["annualized_clv"].mean()
            )
            if not rescue.empty
            else 0.0
        ),
        "rescue_platinum_count": float(
            platinum_count
        ),
    }


def calculate_high_value_at_risk(
    customer: pd.DataFrame,
) -> dict[str, float]:
    """Calculate economics of At Risk customers."""

    at_risk = customer.loc[
        customer["segment"] == "At Risk"
    ]

    total_clv = float(
        customer["annualized_clv"].sum()
    )

    at_risk_clv = float(
        at_risk["annualized_clv"].sum()
    )

    return {
        "at_risk_customer_count": float(
            at_risk["customer_id"].nunique()
        ),
        "at_risk_annualized_clv": at_risk_clv,
        "at_risk_clv_share": (
            at_risk_clv / total_clv * 100
            if total_clv
            else 0.0
        ),
        "at_risk_platinum_count": float(
            (
                at_risk["clv_tier"] == "Platinum"
            ).sum()
        ),
        "at_risk_gold_count": float(
            (
                at_risk["clv_tier"] == "Gold"
            ).sum()
        ),
    }


def calculate_customer_profitability(
    customer: pd.DataFrame,
) -> dict[str, float]:
    """Calculate customer profitability metrics."""

    total_revenue = float(
        customer["revenue"].sum()
    )

    total_gross_profit = float(
        customer["gross_profit"].sum()
    )

    top_customer_profit = float(
        customer.sort_values(
            "gross_profit",
            ascending=False,
        )
        .head(10)["gross_profit"]
        .sum()
    )

    return {
        "total_revenue": total_revenue,
        "total_gross_profit": total_gross_profit,
        "overall_gross_margin": (
            total_gross_profit
            / total_revenue
            * 100
            if total_revenue
            else 0.0
        ),
        "top_customer_profit_share": (
            top_customer_profit
            / total_gross_profit
            * 100
            if total_gross_profit
            else 0.0
        ),
        "average_customer_gross_profit": float(
            customer["gross_profit"].mean()
        ),
    }


def calculate_priority_group_clv_share(
    customer: pd.DataFrame,
) -> float:
    """Calculate CLV share covered by priority 1-3 opportunities."""

    priority_groups = {
        "Rescue",
        "Protect",
        "Develop",
    }

    total_clv = float(
        customer["annualized_clv"].sum()
    )

    priority_clv = float(
        customer.loc[
            customer["opportunity"].isin(priority_groups),
            "annualized_clv",
        ].sum()
    )

    return (
        priority_clv / total_clv * 100
        if total_clv
        else 0.0
    )


def calculate_all_insights(
    customer: pd.DataFrame,
) -> dict[str, object]:
    """Calculate all evidence required by the framework."""

    validate_framework()
    validate_customer_data(customer)

    tier_economics = calculate_clv_tier_economics(
        customer
    )

    opportunity_priority = (
        calculate_customer_opportunity_priority(
            customer
        )
    )

    return {
        "customer_value_concentration": (
            calculate_customer_value_concentration(
                customer
            )
        ),
        "clv_tier_economics": tier_economics,
        "rfm_customer_quality": (
            calculate_rfm_customer_quality(
                customer
            )
        ),
        "customer_opportunity_priority": (
            opportunity_priority
        ),
        "rescue_economics": (
            calculate_rescue_economics(
                customer
            )
        ),
        "high_value_at_risk": (
            calculate_high_value_at_risk(
                customer
            )
        ),
        "customer_profitability": (
            calculate_customer_profitability(
                customer
            )
        ),
        "priority_group_clv_share": (
            calculate_priority_group_clv_share(
                customer
            )
        ),
    }


def validate_insight_results(
    customer: pd.DataFrame,
    results: dict[str, object],
) -> None:
    """Validate calculated insight results against source data."""

    expected_ids = {
        definition.insight_id
        for definition in CUSTOMER_INSIGHT_FRAMEWORK
    }

    result_ids = {
        key
        for key in results
        if key in expected_ids
    }

    if result_ids != expected_ids:
        missing = expected_ids - result_ids
        raise ValueError(
            "Insight result set does not match framework. "
            f"Missing: {sorted(missing)}"
        )

    concentration = results[
        "customer_value_concentration"
    ]

    assert isinstance(concentration, dict)

    expected_total_clv = float(
        customer["annualized_clv"].sum()
    )

    if abs(
        concentration["total_annualized_clv"]
        - expected_total_clv
    ) > 0.01:
        raise ValueError(
            "Total annualized CLV does not reconcile."
        )

    tiers = results["clv_tier_economics"]

    assert isinstance(tiers, pd.DataFrame)

    if (
        tiers["customer_count"].sum()
        != customer["customer_id"].nunique()
    ):
        raise ValueError(
            "CLV tier customer counts do not reconcile."
        )

    if abs(
        tiers["annualized_clv"].sum()
        - expected_total_clv
    ) > 0.01:
        raise ValueError(
            "CLV tier annualized CLV does not reconcile."
        )

    segments = results["rfm_customer_quality"]

    assert isinstance(segments, pd.DataFrame)

    if (
        segments["customer_count"].sum()
        != customer["customer_id"].nunique()
    ):
        raise ValueError(
            "RFM segment customer counts do not reconcile."
        )

    opportunities = results[
        "customer_opportunity_priority"
    ]

    assert isinstance(opportunities, pd.DataFrame)

    if (
        opportunities["customer_count"].sum()
        != customer["customer_id"].nunique()
    ):
        raise ValueError(
            "Opportunity customer counts do not reconcile."
        )

    if abs(
        opportunities["annualized_clv"].sum()
        - expected_total_clv
    ) > 0.01:
        raise ValueError(
            "Opportunity annualized CLV does not reconcile."
        )

    profitability = results[
        "customer_profitability"
    ]

    assert isinstance(profitability, dict)

    expected_revenue = float(
        customer["revenue"].sum()
    )

    expected_gross_profit = float(
        customer["gross_profit"].sum()
    )

    if abs(
        profitability["total_revenue"]
        - expected_revenue
    ) > 0.01:
        raise ValueError(
            "Customer revenue does not reconcile."
        )

    if abs(
        profitability["total_gross_profit"]
        - expected_gross_profit
    ) > 0.01:
        raise ValueError(
            "Customer gross profit does not reconcile."
        )


def build_framework_catalog() -> pd.DataFrame:
    """Return the framework as a tabular catalog."""

    return pd.DataFrame(
        [
            asdict(definition)
            for definition in CUSTOMER_INSIGHT_FRAMEWORK
        ]
    )


def print_insight_summary(
    results: dict[str, object],
) -> None:
    """Print a concise evidence summary."""

    concentration = results[
        "customer_value_concentration"
    ]

    rescue = results["rescue_economics"]

    risk = results["high_value_at_risk"]

    profitability = results[
        "customer_profitability"
    ]

    print("=" * 100)
    print("M24.3 — CUSTOMER INSIGHT EVIDENCE SUMMARY")
    print("=" * 100)

    print(
        "\nCustomer Value Concentration"
    )
    print(
        f"Total annualized CLV : "
        f"Rp {concentration['total_annualized_clv']:,.0f}"
    )
    print(
        f"Top 10 CLV share      : "
        f"{concentration['top_10_clv_share']:.2f}%"
    )
    print(
        f"Top 25 CLV share      : "
        f"{concentration['top_25_clv_share']:.2f}%"
    )
    print(
        f"Platinum CLV share    : "
        f"{concentration['platinum_clv_share']:.2f}%"
    )

    print(
        "\nRescue Economics"
    )
    print(
        f"Rescue customers      : "
        f"{rescue['rescue_customer_count']:.0f}"
    )
    print(
        f"Rescue CLV share      : "
        f"{rescue['rescue_clv_share']:.2f}%"
    )
    print(
        f"Rescue Platinum      : "
        f"{rescue['rescue_platinum_count']:.0f}"
    )

    print(
        "\nAt-Risk Economics"
    )
    print(
        f"At-Risk customers     : "
        f"{risk['at_risk_customer_count']:.0f}"
    )
    print(
        f"At-Risk CLV share     : "
        f"{risk['at_risk_clv_share']:.2f}%"
    )
    print(
        f"At-Risk Platinum      : "
        f"{risk['at_risk_platinum_count']:.0f}"
    )
    print(
        f"At-Risk Gold          : "
        f"{risk['at_risk_gold_count']:.0f}"
    )

    print(
        "\nCustomer Profitability"
    )
    print(
        f"Revenue               : "
        f"Rp {profitability['total_revenue']:,.0f}"
    )
    print(
        f"Gross profit          : "
        f"Rp {profitability['total_gross_profit']:,.0f}"
    )
    print(
        f"Gross margin          : "
        f"{profitability['overall_gross_margin']:.2f}%"
    )

    print("\n" + "=" * 100)
    print("M24.3 ENGINE VALID")
    print("=" * 100)


def main() -> None:
    """Run the customer insight evidence engine."""

    customer = load_customer_data()

    results = calculate_all_insights(
        customer
    )

    validate_insight_results(
        customer,
        results,
    )

    print_insight_summary(
        results
    )


if __name__ == "__main__":
    main()
