#!/usr/bin/env python3
"""Rebuild the dataset from USAspending. You do not need this to enter round 1.

The frozen file in data/ is the one every entry is read against. USAspending keeps
updating, so a fresh pull will differ a little; this script writes it next to the
frozen file instead of over it.

    python3 fetch_data.py                   # ask the API, wait, write data/refetched.csv
    python3 fetch_data.py --from-zip X.zip  # trim a download you already have

Standard library only.
"""
import csv
import io
import json
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

API = "https://api.usaspending.gov/api/v2"
REQUEST = {
    "filters": {
        "award_type_codes": ["A", "B", "C", "D"],  # contracts: BPA call, purchase order, delivery order, definitive
        "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Labor"}],
        "time_period": [{"start_date": "2023-10-01", "end_date": "2024-09-30"}],  # FY2024
    },
    "file_format": "csv",
}

# The columns kept from Contracts_PrimeAwardSummaries. Definitions: data/DATA.md.
KEEP = [
    "contract_award_unique_key", "award_id_piid", "parent_award_id_piid",
    "usaspending_permalink",
    "award_type", "prime_award_base_transaction_description",
    "recipient_name", "recipient_uei", "recipient_parent_name",
    "recipient_state_code",
    "awarding_sub_agency_name", "awarding_office_name",
    "total_obligated_amount", "obligated_amount_from_COVID-19_supplementals",
    "current_total_value_of_award", "potential_total_value_of_award",
    "period_of_performance_start_date", "period_of_performance_current_end_date",
    "period_of_performance_potential_end_date",
    "extent_competed_code", "extent_competed",
    "solicitation_procedures_code", "solicitation_procedures",
    "number_of_offers_received",
    "other_than_full_and_open_competition_code", "other_than_full_and_open_competition",
    "type_of_set_aside_code", "type_of_set_aside",
    "naics_code", "naics_description",
    "product_or_service_code", "product_or_service_code_description",
    "primary_place_of_performance_state_code",
    "last_modified_date",
]


def post(path, body):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def download():
    job = post("/download/awards/", REQUEST)
    print("requested", job["file_name"])
    while True:
        with urllib.request.urlopen(job["status_url"], timeout=60) as r:
            status = json.load(r)
        if status["status"] == "finished":
            break
        if status["status"] == "failed":
            sys.exit(f"USAspending could not build the file: {status.get('message')}")
        print(" ", status["status"], status.get("seconds_elapsed"), "s")
        time.sleep(15)
    with urllib.request.urlopen(job["file_url"], timeout=300) as r:
        return r.read()


def trim(zip_bytes, out):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        name = next(n for n in z.namelist() if "Contracts_PrimeAwardSummaries" in n)
        with z.open(name) as raw:
            reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8"))
            missing = [c for c in KEEP if c not in reader.fieldnames]
            if missing:
                sys.exit(f"USAspending changed its columns; missing: {missing}")
            rows = sorted(({c: r[c] for c in KEEP} for r in reader),
                          key=lambda r: r["contract_award_unique_key"])
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KEEP)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} awards -> {out}")


if __name__ == "__main__":
    here = Path(__file__).resolve().parent / "data"
    if len(sys.argv) >= 3 and sys.argv[1] == "--from-zip":
        trim(Path(sys.argv[2]).read_bytes(), sys.argv[3] if len(sys.argv) > 3 else here / "refetched.csv")
    else:
        trim(download(), here / "refetched.csv")
