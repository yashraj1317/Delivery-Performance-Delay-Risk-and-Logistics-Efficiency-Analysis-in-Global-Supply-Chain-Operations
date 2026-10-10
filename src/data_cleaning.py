"""
data_cleaning.py
-----------------
Step 1 of the methodology: Data Cleaning & Validation.

- Loads the raw dataset (prefers a real uploaded file over the synthetic sample)
- Supports plain .csv and compressed .csv.gz files (and utf-8 / latin-1 encodings)
- Validates shipping duration values
- Removes inconsistent / duplicate / missing-critical-field records
- Standardizes region & market naming
- Computes the Delivery Delay Gap and On-time / Delayed / Early classification
- Optionally writes a cleaned file to data/processed/

Can be imported (see `load_and_clean()`) or run standalone:
    python src/data_cleaning.py
"""

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Preference order: a real dataset dropped in by the user, then the synthetic sample.
CANDIDATE_FILES = [
    RAW_DIR / "supply_chain_data.csv.gz",        # <-- REAL dataset (compressed, fits GitHub's 25 MB limit)
    RAW_DIR / "supply_chain_data.csv",           # <-- or the REAL dataset as a plain CSV
    RAW_DIR / "DataCoSupplyChainDataset.csv",    # common Kaggle filename
    RAW_DIR / "sample_supply_chain_data.csv",    # synthetic fallback (auto-generated)
]

CRITICAL_COLUMNS = [
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Late_delivery_risk",
    "Shipping Mode",
    "Order Region",
    "Market",
]


def find_source_file() -> Path:
    for f in CANDIDATE_FILES:
        if f.exists():
            return f
    # No dataset in the repo: auto-generate the synthetic demo dataset so the app still runs
    # (this is what happens on Streamlit Cloud when the data folder is not uploaded).
    import generate_sample_data
    generate_sample_data.main()
    return generate_sample_data.OUT_PATH


def read_dataset(path: Path) -> pd.DataFrame:
    """Read a CSV / CSV.GZ, falling back to latin-1 if utf-8 fails (the real file needs this)."""
    try:
        return pd.read_csv(path, low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(path, low_memory=False, encoding="latin-1")


def standardize_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    text_cols = ["Market", "Order Region", "Order Country", "Customer Country",
                 "Shipping Mode", "Customer Segment", "Delivery Status", "Order Status"]
    for col in text_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
                .replace({"nan": np.nan})
            )
    return df


def load_and_clean(verbose: bool = True, save: bool = True) -> pd.DataFrame:
    """Load, clean and classify the dataset.

    save=True  -> also writes data/processed/cleaned_supply_chain_data.csv
    save=False -> skip writing (used by the dashboard, e.g. on Streamlit Cloud)
    """
    src = find_source_file()
    df = read_dataset(src)
    n_start = len(df)

    # 1. Drop exact duplicate rows
    df = df.drop_duplicates()

    # 2. Drop rows missing any critical field
    df = df.dropna(subset=[c for c in CRITICAL_COLUMNS if c in df.columns])

    # 3. Validate shipping duration values (must be non-negative, reasonable range)
    df = df[
        (df["Days for shipping (real)"] >= 0) & (df["Days for shipping (real)"] <= 60) &
        (df["Days for shipment (scheduled)"] >= 0) & (df["Days for shipment (scheduled)"] <= 60)
    ].copy()

    # 4. Standardize categorical/text fields
    df = standardize_text_columns(df)

    # 5. Compute Delivery Delay Gap and classification
    df["Delivery Delay Gap"] = df["Days for shipping (real)"] - df["Days for shipment (scheduled)"]

    def classify(gap):
        if gap > 0:
            return "Delayed"
        elif gap < 0:
            return "Early"
        return "On-time"

    df["Delivery Classification"] = df["Delivery Delay Gap"].apply(classify)

    # 6. Ensure Late_delivery_risk is a clean 0/1 int
    df["Late_delivery_risk"] = pd.to_numeric(df["Late_delivery_risk"], errors="coerce").fillna(0).astype(int)

    n_end = len(df)
    if verbose:
        print(f"Source file: {src.name}")
        print(f"Rows in:  {n_start}")
        print(f"Rows out: {n_end}  ({n_start - n_end} removed in cleaning)")

    if save:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        out_path = PROCESSED_DIR / "cleaned_supply_chain_data.csv"
        df.to_csv(out_path, index=False)
        if verbose:
            print(f"Cleaned dataset written to: {out_path}")

    return df


if __name__ == "__main__":
    load_and_clean()
