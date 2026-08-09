"""
Shared project path contracts.

This module is the single source of truth for filesystem paths used by
the Mayasari Bakery Analysis project.

No analysis logic should live here.
Only stable project and dataset paths belong in this module.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# PROJECT ROOT
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# TOP-LEVEL DIRECTORIES
# ---------------------------------------------------------------------------

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
ANALYTICS_DIR = DATA_DIR / "analytics"

REPORTS_DIR = PROJECT_ROOT / "reports"
INSIGHTS_DIR = REPORTS_DIR / "insights"
FIGURES_DIR = REPORTS_DIR / "figures"


# ---------------------------------------------------------------------------
# RAW DATASET
# ---------------------------------------------------------------------------

RAW_DATASET = RAW_DIR / "mayasari_bakery_2025_synthetic.xlsx"


# ---------------------------------------------------------------------------
# PROCESSED DATASETS
# ---------------------------------------------------------------------------

SALES_DATA = PROCESSED_DIR / "sales.parquet"
CUSTOMERS_DATA = PROCESSED_DIR / "customers.parquet"
PRODUCTS_DATA = PROCESSED_DIR / "products.parquet"
EXPENSES_DATA = PROCESSED_DIR / "expenses.parquet"
MONTHLY_KPI_DATA = PROCESSED_DIR / "monthly_kpi.parquet"


# ---------------------------------------------------------------------------
# ANALYTICS DATASETS
# ---------------------------------------------------------------------------

EXECUTIVE_KPIS_DATA = ANALYTICS_DIR / "executive_kpis.parquet"
MONTHLY_PERFORMANCE_DATA = ANALYTICS_DIR / "monthly_performance.parquet"
CUSTOMER_PERFORMANCE_DATA = ANALYTICS_DIR / "customer_performance.parquet"
PRODUCT_PERFORMANCE_DATA = ANALYTICS_DIR / "product_performance.parquet"
PROFITABILITY_SUMMARY_DATA = ANALYTICS_DIR / "profitability_summary.parquet"
CUSTOMER_OPPORTUNITY_DATA = ANALYTICS_DIR / "customer_opportunity.parquet"


# ---------------------------------------------------------------------------
# REPORT OUTPUTS
# ---------------------------------------------------------------------------

EXECUTIVE_INSIGHTS_REPORT = INSIGHTS_DIR / "executive_insights.md"
CLV_INSIGHTS_REPORT = INSIGHTS_DIR / "clv_insights.md"
CUSTOMER_OPPORTUNITY_REPORT = INSIGHTS_DIR / "customer_opportunity_insights.md"


# ---------------------------------------------------------------------------
# FIGURE DIRECTORIES
# ---------------------------------------------------------------------------

EXECUTIVE_FIGURES_DIR = FIGURES_DIR / "executive"
CUSTOMER_FIGURES_DIR = FIGURES_DIR / "customers"
PRODUCT_FIGURES_DIR = FIGURES_DIR / "products"
PROFITABILITY_FIGURES_DIR = FIGURES_DIR / "profitability"
SALES_FIGURES_DIR = FIGURES_DIR / "sales"


__all__ = [
    "ANALYTICS_DIR",
    "CLV_INSIGHTS_REPORT",
    "CUSTOMERS_DATA",
    "CUSTOMER_FIGURES_DIR",
    "CUSTOMER_OPPORTUNITY_DATA",
    "CUSTOMER_OPPORTUNITY_REPORT",
    "CUSTOMER_PERFORMANCE_DATA",
    "DATA_DIR",
    "EXECUTIVE_FIGURES_DIR",
    "EXECUTIVE_INSIGHTS_REPORT",
    "EXECUTIVE_KPIS_DATA",
    "EXPENSES_DATA",
    "FIGURES_DIR",
    "INSIGHTS_DIR",
    "MONTHLY_KPI_DATA",
    "MONTHLY_PERFORMANCE_DATA",
    "PROCESSED_DIR",
    "PRODUCTS_DATA",
    "PRODUCT_FIGURES_DIR",
    "PRODUCT_PERFORMANCE_DATA",
    "PROFITABILITY_FIGURES_DIR",
    "PROFITABILITY_SUMMARY_DATA",
    "PROJECT_ROOT",
    "RAW_DATASET",
    "RAW_DIR",
    "REPORTS_DIR",
    "SALES_DATA",
    "SALES_FIGURES_DIR",
]
