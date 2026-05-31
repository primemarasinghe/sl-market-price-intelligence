import pandas as pd
import os
from pathlib import Path

DAILY_FILE = "data/processed/final_prices.csv"
MASTER_FILE = "data/historical/master_prices.csv"

def read_csv_if_nonempty(path):

    file_path = Path(path)

    if not file_path.exists() or file_path.stat().st_size == 0:
        return None

    return pd.read_csv(file_path)


daily_df = pd.read_csv(DAILY_FILE)
master_df = read_csv_if_nonempty(MASTER_FILE)

if master_df is not None:

    combined_df = pd.concat(
        [master_df, daily_df],
        ignore_index=True
    )

else:

    combined_df = daily_df.copy()

dedupe_columns = [
    column for column in ["report_date", "commodity"]
    if column in combined_df.columns
]

if dedupe_columns:
    combined_df.drop_duplicates(
        subset=dedupe_columns,
        inplace=True
    )

combined_df.to_csv(MASTER_FILE, index=False)

print("Master dataset updated successfully!")
print(f"Total rows: {len(combined_df)}")