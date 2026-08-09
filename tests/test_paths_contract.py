from pathlib import Path

from src.contracts.paths import (
    ANALYTICS_DIR,
    CUSTOMER_FIGURES_DIR,
    CUSTOMER_OPPORTUNITY_DATA,
    CUSTOMER_OPPORTUNITY_REPORT,
    CUSTOMER_PERFORMANCE_DATA,
    EXECUTIVE_FIGURES_DIR,
    EXECUTIVE_INSIGHTS_REPORT,
    EXECUTIVE_KPIS_DATA,
    FIGURES_DIR,
    INSIGHTS_DIR,
    MONTHLY_PERFORMANCE_DATA,
    PRODUCT_FIGURES_DIR,
    PRODUCT_PERFORMANCE_DATA,
    PROFITABILITY_FIGURES_DIR,
    PROFITABILITY_SUMMARY_DATA,
    PROJECT_ROOT,
    RAW_DATASET,
    REPORTS_DIR,
    SALES_FIGURES_DIR,
)


def test_project_root_is_repository_root() -> None:
    assert PROJECT_ROOT == Path(__file__).resolve().parents[1]


def test_raw_dataset_is_under_data_raw() -> None:
    assert RAW_DATASET == (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "mayasari_bakery_2025_synthetic.xlsx"
    )


def test_analytics_directory_contract() -> None:
    assert ANALYTICS_DIR == PROJECT_ROOT / "data" / "analytics"


def test_reports_directory_contract() -> None:
    assert REPORTS_DIR == PROJECT_ROOT / "reports"


def test_insights_directory_contract() -> None:
    assert INSIGHTS_DIR == REPORTS_DIR / "insights"


def test_figures_directory_contract() -> None:
    assert FIGURES_DIR == REPORTS_DIR / "figures"


def test_analytics_data_contracts() -> None:
    assert EXECUTIVE_KPIS_DATA == ANALYTICS_DIR / "executive_kpis.parquet"
    assert MONTHLY_PERFORMANCE_DATA == (
        ANALYTICS_DIR / "monthly_performance.parquet"
    )
    assert CUSTOMER_PERFORMANCE_DATA == (
        ANALYTICS_DIR / "customer_performance.parquet"
    )
    assert PRODUCT_PERFORMANCE_DATA == (
        ANALYTICS_DIR / "product_performance.parquet"
    )
    assert PROFITABILITY_SUMMARY_DATA == (
        ANALYTICS_DIR / "profitability_summary.parquet"
    )
    assert CUSTOMER_OPPORTUNITY_DATA == (
        ANALYTICS_DIR / "customer_opportunity.parquet"
    )


def test_figure_directory_contracts() -> None:
    assert EXECUTIVE_FIGURES_DIR == FIGURES_DIR / "executive"
    assert CUSTOMER_FIGURES_DIR == FIGURES_DIR / "customers"
    assert PRODUCT_FIGURES_DIR == FIGURES_DIR / "products"
    assert PROFITABILITY_FIGURES_DIR == FIGURES_DIR / "profitability"
    assert SALES_FIGURES_DIR == FIGURES_DIR / "sales"


def test_report_contracts() -> None:
    assert EXECUTIVE_INSIGHTS_REPORT == (
        INSIGHTS_DIR / "executive_insights.md"
    )
    assert CUSTOMER_OPPORTUNITY_REPORT == (
        INSIGHTS_DIR / "customer_opportunity_insights.md"
    )


def test_all_figure_directories_are_under_figures_root() -> None:
    figure_directories = [
        EXECUTIVE_FIGURES_DIR,
        CUSTOMER_FIGURES_DIR,
        PRODUCT_FIGURES_DIR,
        PROFITABILITY_FIGURES_DIR,
        SALES_FIGURES_DIR,
    ]

    for directory in figure_directories:
        assert FIGURES_DIR in directory.parents


def test_all_analytics_data_files_are_under_analytics_root() -> None:
    analytics_files = [
        EXECUTIVE_KPIS_DATA,
        MONTHLY_PERFORMANCE_DATA,
        CUSTOMER_PERFORMANCE_DATA,
        PRODUCT_PERFORMANCE_DATA,
        PROFITABILITY_SUMMARY_DATA,
        CUSTOMER_OPPORTUNITY_DATA,
    ]

    for data_file in analytics_files:
        assert ANALYTICS_DIR in data_file.parents
