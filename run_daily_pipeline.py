import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


STEPS = [
    ["scraper/download_reports.py"],
    ["extraction/debug_pdf_lines.py"],
    ["data/historical/update_master_dataset.py"],
    ["cleaning/curate_dataset.py"],
    ["data/warehouse/build_star_schema.py"],
]


def run_step(script_path):

    full_path = PROJECT_ROOT / script_path

    print(f"\n=== Running {script_path} ===")

    result = subprocess.run(
        [sys.executable, str(full_path)],
        cwd=str(PROJECT_ROOT),
        check=False,
    )

    if result.returncode != 0:
        raise SystemExit(
            f"Step failed: {script_path} (exit code {result.returncode})"
        )


def main():

    for step in STEPS:

        run_step(step[0])

    print("\nDaily pipeline completed successfully.")
    print("fact_price_final.csv was regenerated in data/star_schema/")


if __name__ == "__main__":
    main()