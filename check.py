#!/usr/bin/env python3
"""Check a submission before you send it.

    python3 check.py flags.csv

Passing means the file is well formed and every flag is traceable. It does not mean
the flags are good; a person reads that part.

Fails when:
  - the header is not exactly: award_key,flag,value,source,note
  - an award_key is not in the frozen dataset
  - a source is not that award's USAspending page
  - a flag name is not snake_case, 3 to 40 characters
  - a value is empty, or the same (award_key, flag) appears twice
  - a flag name or note uses an accusation word. A flag is a lead, not an accusation.
    If your reasoning needs those words, put them in your paragraph, with a source.
Warns when one flag fires on more than 10% of awards: it tells a reviewer little.
Warns when a flagged recipient looks like a person rather than a company. Some of
    these awards went to sole proprietors, and flagging one can be right. Rule 5 asks
    you to know when you are doing it.
"""
import csv
import re
import sys
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data" / "dol_contracts_fy2024.csv"
HEADER = ["award_key", "flag", "value", "source", "note"]
FLAG_NAME = re.compile(r"^[a-z][a-z0-9_]{2,39}$")
ACCUSATION = re.compile(
    r"\b(fraud\w*|corrupt\w*|brib\w*|kickbacks?|steal\w*|stole\w*|theft|thie\w*|guilty|"
    r"criminal\w*|crimes?|illegal\w*|embezzl\w*|scam\w*|launder\w*|rigged)\b", re.I)

# Words that only ever appear in an organisation's name. Absence of all of them,
# in a two or three word all-alphabetic name, means the recipient is probably a
# person: 18 of the 811 recipients in the frozen file are.
ORG = re.compile(
    r"(CORPORAT|INCORPORAT|COMPAN|LIMITED|PARTNER|\bINC\b|\bLLC\b|\bCORP\b|\bCO\b|\bLTD\b|"
    r"\bLP\b|\bLLP\b|\bPLLC\b|\bPC\b|\bPBC\b|UNIVERS|COLLEGE|INSTITUT|ASSOCIAT|FOUNDAT|"
    r"SERVICE|SYSTEM|GROUP|SOLUTION|BOARD|NATION|COMMUNICAT|TECHNOLOG|CONSULT|ENTERPRIS|"
    r"CENTER|CENTRE|TRUST|BANK|SCHOOL|HOSPITAL|AGENC|COUNCIL|SOCIET|PRESS|MEDIA|\bLAB|"
    r"HOLDING|INDUSTR|SUPPL|CONSTRUCT|ENGINEER|MANAGEM|STATE|NATIONAL|FEDERAL|AMERICAN|"
    r"RESEARCH|RADIO|SANITAR|PUBLISH|DESIGN|STUDIO|GLOBAL|WORLDWIDE|VENTURE|CAPITAL|"
    r"NETWORK|SOFTWARE|DATA|STAFFING|SECURIT|LOGISTIC|TRANSPORT|BUILDER|CONTRACT|POWER)", re.I)


def looks_like_a_person(name):
    """Advisory, and deliberately loose. It is a prompt to think, not a rule."""
    n = name.strip()
    if not n or ORG.search(n):
        return False
    if re.search(r"[^A-Za-z .\'-]", n):      # digits or commas mean an organisation
        return False
    return len(n.split()) in (2, 3)


def main(path):
    with DATA.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    pages = {r["contract_award_unique_key"]: r["usaspending_permalink"] for r in rows}
    who = {r["contract_award_unique_key"]: r["recipient_name"] for r in rows}

    errors, seen, per_flag = [], set(), Counter()
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header != HEADER:
            sys.exit(f"FAIL: header is {header}, expected {HEADER}")
        for n, row in enumerate(reader, start=2):
            if len(row) != len(HEADER):
                errors.append(f"line {n}: {len(row)} columns, expected {len(HEADER)}")
                continue
            key, flag, value, source, note = (c.strip() for c in row)
            if key not in pages:
                errors.append(f"line {n}: award_key {key!r} is not in the frozen dataset")
            elif source != pages[key]:
                errors.append(f"line {n}: source should be {pages[key]}")
            if not FLAG_NAME.match(flag):
                errors.append(f"line {n}: flag {flag!r} is not snake_case, 3 to 40 characters")
            if not value:
                errors.append(f"line {n}: value is empty")
            if (key, flag) in seen:
                errors.append(f"line {n}: {flag} on {key} appears twice")
            seen.add((key, flag))
            for text in (flag.replace("_", " "), note):   # "_" is a word character; split names first
                m = ACCUSATION.search(text)
                if m:
                    errors.append(f"line {n}: {m.group(0)!r} reads as an accusation; "
                                  "describe the data, not the people")
            per_flag[flag] += 1

    for e in errors[:50]:
        print("FAIL:", e)
    if len(errors) > 50:
        print(f"... and {len(errors) - 50} more")
    for flag, k in per_flag.most_common():
        share = k / len(pages)
        warn = "   WARNING: fires on more than 10% of awards" if share > 0.10 else ""
        print(f"{flag}: {k} awards ({share:.1%}){warn}")
    people = sorted({who[k] for k, _ in seen if looks_like_a_person(who.get(k, ""))})
    if people:
        print(f"\nWARNING: {len(people)} flagged recipients look like people, not companies:")
        for n in people:
            print(f"   {n}")
        print("   Rule 5: keep people out of it. These awards are public and flagging one")
        print("   can be right, but say so deliberately, and never name anyone as a suspect.")

    if errors:
        sys.exit(f"{len(errors)} problems. Nothing sent is better than something untraceable.")
    print(f"OK: {sum(per_flag.values())} flags, all traceable to a public row.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
