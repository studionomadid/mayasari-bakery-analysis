from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ANALYTICS_DIR = Path("data/analytics")
FIGURES_DIR = Path("reports/figures")

EXECUTIVE_DATA = ANALYTICS_DIR / "executive_kpis.parquet"

EXECUTIVE_FIGURES = FIGURES_DIR / "executive"


def load_executive_data() -> pd.Series:
    """Load executive KPI dataset."""

    if not EXECUTIVE_DATA.exists():
        raise FileNotFoundError(
            f"Executive KPI dataset not found: "
            f"{EXECUTIVE_DATA}"
        )

    data = pd.read_parquet(
        EXECUTIVE_DATA
    )

    if len(data) != 1:
        raise ValueError(
            "Executive KPI dataset must "
            "contain exactly one row."
        )

    required_columns = {
        "revenue",
        "gross_profit",
        "gross_margin_pct",
        "transactions",
        "active_customers",
        "products",
        "average_transaction_value",
        "operating_expense",
        "operating_profit",
    }

    missing_columns = (
        required_columns
        - set(data.columns)
    )

    if missing_columns:
        raise ValueError(
            "Executive KPI dataset is missing "
            f"columns: {sorted(missing_columns)}"
        )

    if data[
        list(required_columns)
    ].isna().any().any():
        raise ValueError(
            "Executive KPI dataset contains "
            "unexpected null values."
        )

    return data.iloc[0]


def format_currency(value: float) -> str:
    """Format IDR values compactly."""

    if abs(value) >= 1_000_000_000:
        return f"Rp {value / 1_000_000_000:.1f}B"

    if abs(value) >= 1_000_000:
        return f"Rp {value / 1_000_000:.1f}M"

    if abs(value) >= 1_000:
        return f"Rp {value / 1_000:.1f}K"

    return f"Rp {value:,.0f}"


def create_executive_kpi_overview(
    kpi: pd.Series,
) -> Path:
    """Create executive KPI overview figure."""

    EXECUTIVE_FIGURES.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics = [
        (
            "Revenue",
            format_currency(
                kpi["revenue"]
            ),
        ),
        (
            "Gross Profit",
            format_currency(
                kpi["gross_profit"]
            ),
        ),
        (
            "Gross Margin",
            f"{kpi['gross_margin_pct']:.1f}%",
        ),
        (
            "Transactions",
            f"{int(kpi['transactions']):,}",
        ),
        (
            "Active Customers",
            f"{int(kpi['active_customers']):,}",
        ),
        (
            "Products",
            f"{int(kpi['products']):,}",
        ),
        (
            "Avg Transaction",
            format_currency(
                kpi["average_transaction_value"]
            ),
        ),
        (
            "Operating Profit",
            format_currency(
                kpi["operating_profit"]
            ),
        ),
    ]

    figure, axes = plt.subplots(
        2,
        4,
        figsize=(16, 7),
    )

    figure.suptitle(
        "Mayasari Bakery — Executive KPI Overview",
        fontsize=18,
        fontweight="bold",
    )

    for axis, (label, value) in zip(
        axes.flat,
        metrics,
    ):
        axis.axis("off")

        axis.text(
            0.5,
            0.62,
            value,
            ha="center",
            va="center",
            fontsize=22,
            fontweight="bold",
        )

        axis.text(
            0.5,
            0.30,
            label,
            ha="center",
            va="center",
            fontsize=11,
        )

    figure.text(
        0.5,
        0.03,
        "Source: Mayasari Bakery analytical datasets",
        ha="center",
        fontsize=9,
    )

    figure.tight_layout(
        rect=(0, 0.06, 1, 0.93)
    )

    output = (
        EXECUTIVE_FIGURES
        / "executive_kpi_overview.png"
    )

    figure.savefig(
        output,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(figure)

    return output


def validate_output(
    output: Path,
) -> bool:
    """Validate generated visualization."""

    exists = output.exists()

    valid_size = (
        output.stat().st_size > 0
        if exists
        else False
    )

    passed = exists and valid_size

    print()
    print("=" * 80)
    print("M11 VISUALIZATION VALIDATION")
    print("=" * 80)

    print(
        f"Output exists : "
        f"{'PASS' if exists else 'REVIEW'}"
    )

    print(
        f"Output size   : "
        f"{output.stat().st_size:,} bytes"
        if exists
        else "Output size   : REVIEW"
    )

    print("-" * 80)

    print(
        f"Validation    : "
        f"{'PASS' if passed else 'REVIEW'}"
    )

    return passed


def main() -> None:
    """Generate M11 executive visualization."""

    kpi = load_executive_data()

    print("=" * 80)
    print("MAYASARI BAKERY — M11 VISUALIZATION")
    print("=" * 80)

    print()
    print("EXECUTIVE KPI INPUT")
    print("-" * 80)

    print(
        f"Revenue          : "
        f"{format_currency(kpi['revenue'])}"
    )

    print(
        f"Gross profit     : "
        f"{format_currency(kpi['gross_profit'])}"
    )

    print(
        f"Gross margin     : "
        f"{kpi['gross_margin_pct']:.2f}%"
    )

    print(
        f"Transactions     : "
        f"{int(kpi['transactions']):,}"
    )

    print(
        f"Customers        : "
        f"{int(kpi['active_customers']):,}"
    )

    print(
        f"Operating profit : "
        f"{format_currency(kpi['operating_profit'])}"
    )

    output = create_executive_kpi_overview(
        kpi
    )

    print()
    print(
        f"Generated figure : {output}"
    )

    if not validate_output(output):
        raise SystemExit(1)

    print()
    print("=" * 80)
    print(
        "M11.2 EXECUTIVE KPI VISUALIZATION: PASS"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
