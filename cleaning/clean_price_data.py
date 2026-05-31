import pandas as pd
import os

# Input extracted table
INPUT_FILE = "data/processed/table_3.csv"

# Output cleaned dataset
OUTPUT_FILE = "data/processed/cleaned_prices.csv"


def clean_price_data():

    print("Loading extracted table...")

    df = pd.read_csv(INPUT_FILE)

    print("\nOriginal Shape:")
    print(df.shape)

    # Remove completely empty rows
    df.dropna(how="all", inplace=True)

    # Remove completely empty columns
    df.dropna(axis=1, how="all", inplace=True)

    print("\nAfter removing empty rows/columns:")
    print(df.shape)

    # Reset index
    df.reset_index(drop=True, inplace=True)

    print("\nPreview of raw data:")
    print(df.head())

    # Replace newline characters
    df = df.replace(r"\n", " ", regex=True)

    # Strip spaces
    df = df.apply(lambda col: col.astype(str).str.strip())

    # Replace common missing values
    df.replace(["n.a.", "nan", "None"], pd.NA, inplace=True)

    print("\nData cleaned successfully!")

    # Save cleaned file
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nCleaned dataset saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":

    clean_price_data()