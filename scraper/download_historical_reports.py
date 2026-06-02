import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

BASE_URL = "https://www.cbsl.gov.lk/en/statistics/economic-indicators/price-report"

SAVE_FOLDER = "data/raw"

os.makedirs(SAVE_FOLDER, exist_ok=True)

# Download every matching report from the CBSL archive starting in 2023.
START_DATE = datetime(2023, 1, 1)

downloaded = 0
visited_pages = 0

page = 0

while True:

    page_url = f"{BASE_URL}?page={page}"

    print(f"\nChecking page {page}")

    response = requests.get(page_url)

    if response.status_code != 200:
        print("Page not accessible.")
        break

    soup = BeautifulSoup(response.text, "html.parser")

    pdf_found = False

    for link in soup.find_all("a", href=True):

        href = link["href"]

        if "price_report_" not in href:
            continue

        if ".pdf" not in href:
            continue

        pdf_found = True

        full_url = urljoin(BASE_URL, href)

        match = re.search(
            r'price_report_(\d{8})_e\.pdf',
            href
        )

        if not match:
            continue

        report_date = datetime.strptime(
            match.group(1),
            "%Y%m%d"
        )

        if report_date < START_DATE:
            print("\nReached 2023 archive limit.")
            print(f"Downloaded reports: {downloaded}")
            exit()

        filename = os.path.basename(href)

        filepath = os.path.join(
            SAVE_FOLDER,
            filename
        )

        if os.path.exists(filepath):
            print(f"Already exists: {filename}")
            continue

        print(f"Downloading: {filename}")

        pdf_response = requests.get(full_url)

        if pdf_response.status_code == 200:

            with open(filepath, "wb") as f:
                f.write(pdf_response.content)

            downloaded += 1

    if not pdf_found:
        print("No PDFs found.")
        break

    page += 1
    visited_pages += 1

print("\nCompleted.")
print(f"Pages visited: {visited_pages}")
print(f"Reports downloaded: {downloaded}")