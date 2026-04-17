"""
Raw inventory text file processor.
Reads tab-separated .txt exports, cleans them, and writes clean_catalog.csv
ready for django-import-export ingestion via ProductResource.
"""

import pandas as pd

INPUT_FILES = ["بناية الاسدي.txt", "محلات الاسدي.txt"]
OUTPUT_FILE = "clean_catalog.csv"

# Maps Arabic source column headers to English field names.
COLUMN_MAP = {
    "إسم المادة": "name_ar",
    "رمز المادة": "item_code",
    "المجموعة": "brand",
    "العدد": "Total_Quantity",
    "عدد تعبئة 1": "pieces_per_package",
    "المخزن": "Warehouse_Location",
    "سعر الجملة": "wholesale_price",
}

# Warehouse location values (after stripping whitespace) → Django model fields.
WAREHOUSE_RENAME = {
    "مخزن البناية": "qty_building_warehouse",
    "بحر": "qty_sea_warehouse",
    "محل": "qty_shop",
}

EXPECTED_QTY_COLS = ["qty_building_warehouse", "qty_sea_warehouse", "qty_shop"]
INDEX_COLS = [
    "name_ar",
    "item_code",
    "brand",
    "category",
    "pieces_per_package",
]


def _read_tsv(path: str) -> pd.DataFrame:
    """Try utf-16; fall back to utf-8 on decode errors."""
    kwargs = dict(sep="\t", dtype=str)
    try:
        return pd.read_csv(path, encoding="utf-16", **kwargs)
    except (UnicodeDecodeError, UnicodeError):
        return pd.read_csv(path, encoding="utf-8", **kwargs)


def _process_file(path: str) -> pd.DataFrame:
    df = _read_tsv(path)

    # Keep only mapped columns that actually exist in this file.
    present = [col for col in COLUMN_MAP if col in df.columns]
    df = df[present].rename(columns=COLUMN_MAP).copy()

    # Drop rows with no product name.
    df = df[df["name_ar"].notna() & (df["name_ar"].str.strip() != "")]

    # --- Fill defaults and normalise text ---
    df["item_code"] = df["item_code"].fillna("NO_CODE").str.strip()
    df["brand"] = df["brand"].fillna("غير مصنف").str.strip()

    df["pieces_per_package"] = (
        df["pieces_per_package"]
        .fillna("1")
        .str.strip()
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(1)
        .astype(int)
    )

    # Strip thousands-separator commas then coerce to float.
    df["Total_Quantity"] = (
        df["Total_Quantity"]
        .str.replace(",", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0.0)
    )

    # Clean wholesale price: strip " د.ع" suffix + thousands commas → float.
    df["wholesale_price"] = (
        df["wholesale_price"]
        .fillna("0")
        .str.replace(" د.ع", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0.0)
    )

    # Normalise warehouse names (e.g. 'مخزن البناية ' → 'مخزن البناية').
    df["Warehouse_Location"] = df["Warehouse_Location"].str.strip()

    # Augment: category mirrors brand (raw data conflates the two).
    df["category"] = df["brand"]

    return df


def main() -> None:
    frames = [_process_file(f) for f in INPUT_FILES]
    combined = pd.concat(frames, ignore_index=True)

    # Drop display/showroom rows — only stock warehouse locations are relevant.
    combined = combined[combined["Warehouse_Location"].isin(WAREHOUSE_RENAME)]

    # Pivot: one row per product, warehouse quantities as separate columns.
    # wholesale_price is aggregated (not in the index) so a product with
    # mismatched prices across source files stays as ONE row with the max price.
    pivot = combined.pivot_table(
        index=INDEX_COLS,
        columns="Warehouse_Location",
        values=["Total_Quantity", "wholesale_price"],
        aggfunc={"Total_Quantity": "sum", "wholesale_price": "max"},
        fill_value=0,
    )

    # pivot.columns is a MultiIndex: (value_name, warehouse).
    # Collapse wholesale_price's per-warehouse sub-columns into one column
    # by taking the max across warehouses.
    wholesale = pivot["wholesale_price"].max(axis=1)

    # Keep only the Total_Quantity sub-frame (warehouse columns).
    pivot = pivot["Total_Quantity"].copy()
    pivot["wholesale_price"] = wholesale

    pivot = pivot.reset_index()
    pivot.columns.name = None
    pivot = pivot.rename(columns=WAREHOUSE_RENAME)

    # Guarantee all three quantity columns exist even if absent from source data.
    for col in EXPECTED_QTY_COLS:
        if col not in pivot.columns:
            pivot[col] = 0

    pivot = pivot[INDEX_COLS + ["wholesale_price"] + EXPECTED_QTY_COLS]

    # --- Guarantee strict item_code uniqueness ---

    # Step 1: Replace NO_CODE / blank with sequenced NO_CODE_N.
    no_code_mask = pivot["item_code"].isin(["NO_CODE", "", None]) | pivot["item_code"].isna()
    no_code_counter = range(1, no_code_mask.sum() + 1)
    pivot.loc[no_code_mask, "item_code"] = [f"NO_CODE_{i}" for i in no_code_counter]

    # Step 2: For any remaining duplicated codes, append _1, _2, … to the
    # second and subsequent occurrences (first occurrence keeps original code).
    dupes_mask = pivot.duplicated(subset=["item_code"], keep="first")
    if dupes_mask.any():
        dup_counts: dict[str, int] = {}
        new_codes = []
        for code, is_dup in zip(pivot["item_code"], dupes_mask):
            if is_dup:
                dup_counts[code] = dup_counts.get(code, 0) + 1
                new_codes.append(f"{code}_{dup_counts[code]}")
            else:
                new_codes.append(code)
        pivot["item_code"] = new_codes

    pivot.to_csv(OUTPUT_FILE, encoding="utf-8-sig", index=False)
    print(f"Done. Unique items exported: {len(pivot):,}")


if __name__ == "__main__":
    main()
