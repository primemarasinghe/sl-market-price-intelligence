import os
import re
from datetime import datetime

import pdfplumber
import pandas as pd

from pdf_utils import get_latest_pdf_path
def extract_report_date(text):

    match = re.search(

        r'(\d{1,2}\s+[A-Za-z]+,\s+\d{4})',

        text

    )

    if match:

        date_str = match.group(1)

        report_date = datetime.strptime(

            date_str,

            "%d %B, %Y"

        ).strftime("%Y-%m-%d")

        return report_date

    return None
# PDF path
PDF_PATH = str(get_latest_pdf_path())

# Output CSV
OUTPUT_CSV = "data/processed/structured_prices.csv"

# Extract report date from filename
filename = os.path.basename(PDF_PATH)

match = re.search(r'(\d{8})', filename)

if match:
    raw_date = match.group(1)

    REPORT_DATE = (
        f"{raw_date[:4]}-"
        f"{raw_date[4:6]}-"
        f"{raw_date[6:]}"
    )
else:
    REPORT_DATE = None


def extract_text_from_pdf(pdf_path):

    full_text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if text:
                full_text += text + "\n"

    return full_text


def extract_commodity_rows(text, report_date):

    rows = []

    lines = text.split("\n")

    pattern = re.compile(
        r"^(.*?)\s+(Rs\./kg|Rs\./Nut|Rs\./Ltr|Rs\./Each)\s+(.+)"
    )

    for line in lines:

        line = re.sub(
            r'(\d)\s+(\d+\.\d+)',
            r'\1\2',
            line
        )

        match = pattern.match(line)

        if not match:
            continue

        commodity = match.group(1).strip()
        unit = match.group(2).strip()
        remaining = match.group(3)

        prices = re.findall(
            r'\d+(?:,\d{3})*\.\d+|n\.a\.',
            remaining
        )

        if len(prices) < 2:
            continue

        while len(prices) < 10:
            prices.append("n.a.")

        prices = prices[:10]

        cleaned_prices = []

        for value in prices:

            if value == "n.a.":
                cleaned_prices.append("n.a.")
            else:
                cleaned_prices.append(
                    float(value.replace(",", ""))
                )

        row = {
            "report_date": report_date,
            "commodity": commodity,
            "unit": unit,

            "wholesale_pettah_last_week": cleaned_prices[0],
            "wholesale_pettah_today": cleaned_prices[1],

            "wholesale_dambulla_last_week": cleaned_prices[2],
            "wholesale_dambulla_today": cleaned_prices[3],

            "retail_pettah_last_week": cleaned_prices[4],
            "retail_pettah_today": cleaned_prices[5],

            "retail_dambulla_last_week": cleaned_prices[6],
            "retail_dambulla_today": cleaned_prices[7],

            "retail_narahenpita_last_week": cleaned_prices[8],
            "retail_narahenpita_today": cleaned_prices[9]
        }

        rows.append(row)

    return rows


def main():

    print("=" * 50)
    print("CBSL PRICE REPORT PARSER")
    print("=" * 50)

    print(f"\nReport Date: {REPORT_DATE}")

    print("\nExtracting text from PDF...")

    text = extract_text_from_pdf(PDF_PATH)

    report_date = extract_report_date(text)

    if report_date is None:

        report_date = REPORT_DATE

    print(f"Report Date: {report_date}")

    rows = extract_commodity_rows(

        text,

        report_date

    )

    df = pd.DataFrame(rows)

    print("\nPreview:")
    print(df.head())

    # Save CSV
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"\nStructured dataset saved:")
    print(OUTPUT_CSV)

    print(f"\nTotal records: {len(df)}")


if __name__ == "__main__":
    main()