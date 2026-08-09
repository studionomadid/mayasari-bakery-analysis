"""Customer opportunity dependency contracts."""

from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[2] / "src"

OPPORTUNITY_FILE = (
    SRC_DIR / "customer_opportunity_analysis.py"
)


def test_opportunity_uses_customer_performance_for_clv() -> None:
    """Opportunity analysis must consume customer performance metrics."""

    source = OPPORTUNITY_FILE.read_text()

    assert "CUSTOMER_PERFORMANCE_DATA" in source
    assert "CUSTOMER_DATASET = CUSTOMER_PERFORMANCE_DATA" in source


def test_opportunity_uses_sales_for_rfm() -> None:
    """Opportunity analysis must retain transaction-level sales input."""

    source = OPPORTUNITY_FILE.read_text()

    assert "SALES_DATA" in source
    assert "SALES_DATASET = SALES_DATA" in source


def test_opportunity_requires_rfm_transaction_columns() -> None:
    """RFM logic must retain transaction-grain source columns."""

    source = OPPORTUNITY_FILE.read_text()

    required_columns = (
        '"transaction_key"',
        '"transaction_date"',
        '"customer_id"',
        '"net_sales"',
    )

    for column in required_columns:
        assert column in source, (
            f"RFM dependency missing required column: {column}"
        )
