"""Dashboard source-of-truth contracts."""

from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[2] / "src"


EXPECTED_SOURCES = {
    "revenue_dashboard.py": "MONTHLY_PERFORMANCE_DATA",
    "product_dashboard.py": "PRODUCT_PERFORMANCE_DATA",
    "customer_dashboard.py": "CUSTOMER_PERFORMANCE_DATA",
    "profitability_dashboard.py": "PROFITABILITY_SUMMARY_DATA",
    "profitability_dashboard.py": "EXECUTIVE_KPIS_DATA",
}


def test_dashboard_source_contracts() -> None:
    """Dashboards must consume BI artifacts through path contracts."""

    for filename, expected_source in EXPECTED_SOURCES.items():
        source = (SRC_DIR / filename).read_text()

        assert expected_source in source, (
            f"{filename} must use {expected_source}"
        )


def test_dashboards_do_not_read_sales_directly() -> None:
    """Dashboards must not bypass the BI layer."""

    dashboard_files = (
        "revenue_dashboard.py",
        "product_dashboard.py",
        "customer_dashboard.py",
        "profitability_dashboard.py",
    )

    for filename in dashboard_files:
        source = (SRC_DIR / filename).read_text()

        assert "SALES_DATA" not in source, (
            f"{filename} directly depends on SALES_DATA"
        )
