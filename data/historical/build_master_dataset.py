import os
import re
import pdfplumber
import pandas as pd
from datetime import datetime

RAW_FOLDER = "data/raw"
OUTPUT_FILE = "data/historical/master_prices.csv"

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


def clean_number_spacing(text):

    text = re.sub(
        r'(\d)\s+(\d+\.\d+)',
        r'\1\2',
        text
    )

    return text


def extract_text(pdf_path):

    full_text = ""

    try:

        with pdfplumber.open(pdf_path) as pdf:

            for page in pdf.pages:

                text = page.extract_text()

                if text:
                    full_text += text + "\n"

    except Exception as e:

        print(f"Error reading {pdf_path}: {e}")

    return full_text


def extract_report_date(text):

    match = re.search(
        r'(\d{1,2}\s+[A-Za-z]+,\s+\d{4})',
        text
    )

    if not match:
        return None

    try:

        return datetime.strptime(
            match.group(1),
            "%d %B, %Y"
        ).strftime("%Y-%m-%d")

    except:
        return None


def parse_rows(text, report_date):

    rows = []

    lines = text.split("\n")

    commodity_pattern = re.compile(
        r'^(.*?)\s+(Rs\./kg|Rs\./Nut|Rs\./Ltr|Rs\./Each)\s+(.*)$'
    )

    for line in lines:

        line = clean_number_spacing(line)

        match = commodity_pattern.match(line)

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

        cleaned_prices = []

        for value in prices:

            if value == "n.a.":
                cleaned_prices.append("n.a.")
            else:
                cleaned_prices.append(
                    value.replace(",", "")
                )

        while len(cleaned_prices) < 10:
            cleaned_prices.append("n.a.")

        cleaned_prices = cleaned_prices[:10]

        row = {
            "report_date": report_date,
            "commodity": commodity,
            "unit": unit
        }

        for i in range(10):

            value = cleaned_prices[i]

            if value == "n.a.":
                row[COLUMN_NAMES[i]] = "n.a."
            else:
                row[COLUMN_NAMES[i]] = float(value)

        rows.append(row)

    return rows


def main():

    all_rows = []

    pdf_files = sorted([
        f for f in os.listdir(RAW_FOLDER)
        if f.endswith(".pdf")
    ])

    total_files = len(pdf_files)

    print(f"\nFound {total_files} PDFs\n")

    for index, pdf_file in enumerate(pdf_files):

        pdf_path = os.path.join(
            RAW_FOLDER,
            pdf_file
        )

        print(
            f"[{index+1}/{total_files}] Processing {pdf_file}"
        )

        text = extract_text(pdf_path)

        match = re.search(
            r'price_report_(\d{8})_e\.pdf',
            pdf_file
        )

        if not match:
            continue

        report_date = datetime.strptime(
            match.group(1),
            "%Y%m%d"
        ).strftime("%Y-%m-%d")

        if not report_date:
            print("Date not found. Skipping.")
            continue

        rows = parse_rows(
            text,
            report_date
        )

        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)

    df.drop_duplicates(
        subset=["report_date", "commodity"],
        inplace=True
    )

    df.sort_values(
        by=["report_date", "commodity"],
        inplace=True
    )

    os.makedirs(
        "data/historical",
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n========================")
    print("BUILD COMPLETED")
    print("========================")
    print(f"Total rows: {len(df)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()