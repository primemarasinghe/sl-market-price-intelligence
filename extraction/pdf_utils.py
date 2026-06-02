from pathlib import Path
import re


PDF_NAME_PATTERN = re.compile(r"price_report_(\d{8})_e\.pdf$")


def get_latest_pdf_path(raw_folder="data/raw"):

    raw_path = Path(raw_folder)

    candidates = []

    for pdf_file in raw_path.glob("price_report_*_e.pdf"):

        match = PDF_NAME_PATTERN.search(pdf_file.name)

        if not match:
            continue

        candidates.append((match.group(1), pdf_file))

    if not candidates:
        raise FileNotFoundError(
            f"No price_report_YYYYMMDD_e.pdf files found in {raw_folder}"
        )

    candidates.sort(key=lambda item: item[0])

    return candidates[-1][1]