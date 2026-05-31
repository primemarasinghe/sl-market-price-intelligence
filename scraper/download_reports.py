import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# CBSL Daily Price Report page
URL = "https://www.cbsl.gov.lk/en/statistics/economic-indicators/price-report"

# Save folder
SAVE_FOLDER = "data/raw"

os.makedirs(SAVE_FOLDER, exist_ok=True)

def download_latest_price_report():

    print("Connecting to CBSL Daily Price Report page...")

    response = requests.get(URL)

    if response.status_code != 200:
        print("Failed to access CBSL website.")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    pdf_links = []

    # Find ONLY daily price report PDFs
    for link in soup.find_all("a", href=True):

        href = link["href"]

        # Detect correct report pattern
        if "price_report_" in href and href.endswith(".pdf"):
            full_url = urljoin(URL, href)
            pdf_links.append(full_url)

    if not pdf_links:
        print("No price report PDFs found.")
        return

    # Latest report usually appears first
    latest_pdf = pdf_links[0]

    print(f"Latest report found:")
    print(latest_pdf)

    # Download PDF
    pdf_response = requests.get(latest_pdf)

    if pdf_response.status_code != 200:
        print("Failed to download PDF.")
        return

    # Extract filename from URL
    filename = latest_pdf.split("/")[-1]

    save_path = os.path.join(SAVE_FOLDER, filename)

    with open(save_path, "wb") as file:
        file.write(pdf_response.content)

    print(f"\nReport downloaded successfully!")
    print(f"Saved to: {save_path}")

if __name__ == "__main__":
    download_latest_price_report()