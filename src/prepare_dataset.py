
import pandas as pd

from src.contracts.paths import PROCESSED_DIR, RAW_DATASET

SHEETS = [
    "customers",
    "products",
    "sales",
    "expenses",
    "monthly_kpi",
]


DATE_COLUMNS = {
    "customers": ["registration_date"],
    "products": [],
    "sales": ["transaction_date"],
    "expenses": ["expense_date"],
    "monthly_kpi": [],
}


NUMERIC_COLUMNS = {
    "customers": [
        "age",
    ],
    "products": [
        "price",
        "cost",
    ],
    "sales": [
        "line_id",
        "quantity",
        "unit_price",
        "discount_rate",
        "discount_amount",
        "net_sales",
        "product_cost",
        "gross_sales",
        "gross_profit",
    ],
    "expenses": [
        "amount",
    ],
    "monthly_kpi": [
        "transactions",
        "units_sold",
        "gross_sales",
        "discount",
        "net_sales",
        "product_cost",
        "gross_profit",
        "operating_expense",
        "estimated_operating_profit",
        "gross_margin_pct",
        "avg_transaction_value",
    ],
}


def load_raw_data() -> dict[str, pd.DataFrame]:
    """Load analytical sheets from the raw Excel workbook."""
    if not RAW_DATASET.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_DATASET}"
        )

    return pd.read_excel(
        RAW_DATASET,
        sheet_name=SHEETS,
    )


def normalize_dates(
    name: str,
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Convert configured date columns to pandas datetime."""
    for column in DATE_COLUMNS[name]:
        dataframe[column] = pd.to_datetime(
            dataframe[column],
            errors="raise",
        )

    return dataframe


def normalize_numeric(
    name: str,
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Convert configured numeric columns to numeric types."""
    for column in NUMERIC_COLUMNS[name]:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="raise",
        )

    return dataframe


def normalize_monthly_kpi(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Normalize monthly KPI month representation."""
    dataframe["month"] = pd.PeriodIndex(
        dataframe["month"],
        freq="M",
    )

    return dataframe


def add_sales_keys(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Add analytical keys used by downstream analysis."""
    dataframe["transaction_key"] = (
        dataframe["transaction_id"].astype("string")
    )

    dataframe["transaction_line_key"] = (
        dataframe["transaction_id"].astype("string")
        + "-"
        + dataframe["line_id"].astype("string")
    )

    dataframe["sales_month"] = (
        dataframe["transaction_date"]
        .dt.to_period("M")
    )

    return dataframe


def add_expense_keys(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Add monthly analytical key to expense records."""
    dataframe["expense_month"] = (
        dataframe["expense_date"]
        .dt.to_period("M")
    )

    return dataframe


def prepare_data(
    raw_data: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Normalize all raw analytical tables."""
    prepared = {}

    for name, dataframe in raw_data.items():
        dataframe = dataframe.copy()

        dataframe = normalize_dates(
            name,
            dataframe,
        )

        dataframe = normalize_numeric(
            name,
            dataframe,
        )

        if name == "monthly_kpi":
            dataframe = normalize_monthly_kpi(
                dataframe
            )

        if name == "sales":
            dataframe = add_sales_keys(
                dataframe
            )

        if name == "expenses":
            dataframe = add_expense_keys(
                dataframe
            )

        prepared[name] = dataframe

    return prepared


def save_processed_data(
    prepared: dict[str, pd.DataFrame],
) -> None:
    """Save normalized analytical tables as parquet files."""
    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for name, dataframe in prepared.items():
        output_path = (
            PROCESSED_DIR
            / f"{name}.parquet"
        )

        dataframe.to_parquet(
            output_path,
            index=False,
        )

        print(
            f"Saved {name:<12} "
            f"{len(dataframe):>8,} rows -> "
            f"{output_path}"
        )


def print_summary(
    prepared: dict[str, pd.DataFrame],
) -> None:
    """Print preparation summary."""
    print()
    print("=" * 80)
    print("PREPARED DATA SUMMARY")
    print("=" * 80)

    for name, dataframe in prepared.items():
        print(
            f"{name:<12} "
            f"{len(dataframe):>8,} rows x "
            f"{len(dataframe.columns):>2} columns"
        )

    print()
    print("SALES GRAIN")
    print("-" * 80)

    sales = prepared["sales"]

    print(
        f"Sales line records : "
        f"{len(sales):,}"
    )

    print(
        f"Unique transactions: "
        f"{sales['transaction_key'].nunique():,}"
    )

    print(
        f"Unique line keys   : "
        f"{sales['transaction_line_key'].nunique():,}"
    )

    print()
    print("DATE RANGES")
    print("-" * 80)

    print(
        "Sales      : "
        f"{sales['transaction_date'].min().date()} "
        f"-> "
        f"{sales['transaction_date'].max().date()}"
    )

    expenses = prepared["expenses"]

    print(
        "Expenses   : "
        f"{expenses['expense_date'].min().date()} "
        f"-> "
        f"{expenses['expense_date'].max().date()}"
    )


def main() -> None:
    print("=" * 80)
    print("MAYASARI BAKERY DATA PREPARATION")
    print("=" * 80)

    print()
    print(f"Source: {RAW_DATASET}")

    raw_data = load_raw_data()

    prepared = prepare_data(
        raw_data
    )

    save_processed_data(
        prepared
    )

    print_summary(
        prepared
    )

    print()
    print("=" * 80)
    print("DATA PREPARATION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
