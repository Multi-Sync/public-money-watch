#!/usr/bin/env python3
"""Baseline: one red flag, end to end. Copy it, change the rule, add your own.

Flag: single_offer_competed
  The award was competed (extent_competed_code A, D, F or CDO) but the contracting
  office reported exactly one offer. A competition that draws a single bidder is a
  documented procurement red flag (Open Contracting Partnership, "Red flags in public
  procurement", 2024). It is a lead, not a finding: specialized work often draws one
  bidder for honest reasons.

    python3 baseline.py           # writes flags.csv
    python3 check.py flags.csv    # checks it before you send it

Standard library only. Python 3.8+.
"""
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data" / "dol_contracts_fy2024.csv"

# FPDS extent_competed codes that mean the award was competed:
# A full and open, D full and open after exclusion of sources,
# F competed under simplified acquisition, CDO competitive delivery order.
COMPETED = {"A", "D", "F", "CDO"}


def offers(row):
    """number_of_offers_received as an int, or None when the office left it blank."""
    raw = row["number_of_offers_received"].strip()
    try:
        return int(float(raw))
    except ValueError:
        return None


def flags(row):
    """Yield (flag, value) for every rule this award trips. Add your rules here."""
    if row["extent_competed_code"] in COMPETED and offers(row) == 1:
        yield ("single_offer_competed",
               f"extent_competed_code={row['extent_competed_code']}; number_of_offers_received=1")


def main():
    total = flagged = 0
    with DATA.open(newline="", encoding="utf-8") as f, \
            open("flags.csv", "w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["award_key", "flag", "value", "source", "note"])
        for row in csv.DictReader(f):
            total += 1
            for flag, value in flags(row):
                w.writerow([row["contract_award_unique_key"], flag, value,
                            row["usaspending_permalink"], ""])
                flagged += 1
    print(f"{flagged} flags on {total} awards -> flags.csv")


if __name__ == "__main__":
    main()
