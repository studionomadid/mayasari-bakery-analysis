from pathlib import Path

import pandas as pd


DATASET_PATH = Path(
    "data/raw/mayasari_bakery_2025_synthetic.xlsx"
)


def load_workbook(path: Path) -> dict[str, pd.DataFrame]:
    """Load all analytical sheets from the source workbook."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    sheets = pd.read_excel(
        path,
        sheet_name=[
            "customers",
            "products",
            "sales",
            "expenses",
            "monthly_kpi",
        ],
    )

    return sheets


def profile_dataframe(
    name: str,
    dataframe: pd.DataFrame,
) -> None:
    """Print a concise profile for a dataframe."""
    print("=" * 80)
    print(f"TABLE: {name}")
    print("=" * 80)

    print(f"Rows    : {len(dataframe):,}")
    print(f"Columns : {len(dataframe.columns)}")
    print()

    print("DATA TYPES")
    print("-" * 80)

    print(dataframe.dtypes.to_string())
    print()

    print("MISSING VALUES")
    print("-" * 80)

    missing = dataframe.isna().sum()

    if missing.sum() == 0:
        print("No missing values.")
    else:
        print(
            missing[missing > 0]
            .sort_values(ascending=False)
            .to_string()
        )

    print()

    print("DUPLICATE ROWS")
    print("-" * 80)

    print(
        f"Duplicate rows: "
        f"{dataframe.duplicated().sum():,}"
    )

    print()

    print("SAMPLE")
    print("-" * 80)

    print(
        dataframe.head(3).to_string(
            index=False
        )
    )

    print()


def main() -> None:
    print("=" * 80)
    print("MAYASARI BAKERY DATA PROFILING")
    print("=" * 80)
    print(f"Dataset: {DATASET_PATH}")
    print()

    sheets = load_workbook(DATASET_PATH)

    for name, dataframe in sheets.items():
        profile_dataframe(
            name,
            dataframe,
        )

    print("=" * 80)
    print("DATA PROFILING COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
