import pdfplumber
import pandas as pd
import re

# PDF path
PDF_PATH = "data/raw/price_report_20260529_e.pdf"

# Output CSV
OUTPUT_CSV = "data/processed/final_prices.csv"

# Final schema columns
COLUMN_NAMES = [
    "wholesale_pettah_last_week",
    "wholesale_pettah_today",
    "wholesale_dambulla_last_week",
    "wholesale_dambulla_today",
    "retail_pettah_last_week",
    "retail_pettah_today",
    "retail_dambulla_last_week",
    "retail_dambulla_today",
    "retail_narahenpita_last_week",
    "retail_narahenpita_today"
]


def extract_text():

    full_text = ""

    with pdfplumber.open(PDF_PATH) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if text:
                full_text += text + "\n"

    return full_text


def clean_number_spacing(text):

    """
    Fix broken PDF number spacing

    Examples:
    6 00.00 -> 600.00
    1 20.00 -> 120.00
    9 0.00  -> 90.00
    """

    text = re.sub(r'(\d)\s+(\d+\.\d+)', r'\1\2', text)

    return text


def parse_rows(text):

    rows = []

    # Split into lines
    lines = text.split("\n")

    # Flexible commodity pattern
    commodity_pattern = re.compile(
        r'^(.*?)\s+(Rs\./kg|Rs\./Nut|Rs\./Ltr|Rs\./Each)\s+(.*)$'
    )

    for line in lines:

        # Clean spacing issues
        line = clean_number_spacing(line)

        # Match commodity rows
        match = commodity_pattern.match(line)

        if not match:
            continue

        commodity = match.group(1).strip()
        unit = match.group(2).strip()
        remaining = match.group(3)

        # Extract prices + n.a.
        prices = re.findall(r'\d+(?:,\d{3})*\.\d+|n\.a\.', remaining)

        # Skip rows with almost no data
        if len(prices) < 2:
            continue

        # Remove commas from prices
        cleaned_prices = []

        for value in prices:

            if value == "n.a.":
                cleaned_prices.append("n.a.")
            else:
                cleaned_prices.append(value.replace(",", ""))

        # Pad missing values up to 10 columns
        while len(cleaned_prices) < 10:
            cleaned_prices.append("n.a.")

        # Trim extra values if PDF becomes messy
        cleaned_prices = cleaned_prices[:10]

        # Create structured row
        row_data = {
            "commodity": commodity,
            "unit": unit
        }

        # Map prices into columns
        for i in range(10):

            value = cleaned_prices[i]

            if value == "n.a.":
                row_data[COLUMN_NAMES[i]] = "n.a."
            else:
                row_data[COLUMN_NAMES[i]] = float(value)

        rows.append(row_data)

    return rows


def main():

    print("=" * 60)
    print("CBSL PRICE REPORT PARSER")
    print("=" * 60)

    print("\nExtracting PDF text...")

    text = extract_text()

    print("Parsing commodity rows...")

    rows = parse_rows(text)

    print(f"\nTotal rows extracted: {len(rows)}")

    # Create dataframe
    df = pd.DataFrame(rows)

    print("\nDataset Preview:")
    print(df.head())

    # Save CSV
    df.to_csv(OUTPUT_CSV, index=False)

    print("\nCSV exported successfully!")
    print(f"Saved to: {OUTPUT_CSV}")

    print("\nParsing completed successfully.")


if __name__ == "__main__":
    main()