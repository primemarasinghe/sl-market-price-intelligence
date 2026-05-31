import pdfplumber
import pandas as pd

# PDF path
PDF_PATH = "data/raw/price_report_20260529_e.pdf"

def extract_tables():

    print("Opening PDF...")

    all_tables = []

    with pdfplumber.open(PDF_PATH) as pdf:

        print(f"Total pages: {len(pdf.pages)}")

        for page_number, page in enumerate(pdf.pages):

            print(f"\nProcessing page {page_number + 1}")

            tables = page.extract_tables()

            print(f"Tables found: {len(tables)}")

            for table in tables:

                df = pd.DataFrame(table)

                all_tables.append(df)

    return all_tables


if __name__ == "__main__":

    extracted_tables = extract_tables()

    print(f"\nTotal extracted tables: {len(extracted_tables)}")

    # Display tables
    for i, table in enumerate(extracted_tables):

        print(f"\n===== TABLE {i + 1} =====")
        print(table.head())

        # Save each table
        table.to_csv(f"data/processed/table_{i + 1}.csv", index=False)

    print("\nExtraction completed successfully!")