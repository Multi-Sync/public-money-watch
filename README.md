# Public Money Watch: Starter Kit, Round 1

## The task

**Circle the row.** From one year of U.S. Department of Labor contracts, flag the awards a
reviewer should open first. Tie each flag to its public record and to a rule you can state in
one sentence.

## Start in two minutes

No installs. Python 3.8 or newer, standard library only.

```
python3 baseline.py           # 470 flags on 2,358 awards -> flags.csv
python3 check.py flags.csv    # passes, and warns: 19.9% of awards is too many to read
```

The baseline flags competed awards that drew a single offer. It is correct, and it is too
blunt: it circles one award in five. Round 1 is about doing better than that. Fewer, sharper
flags, each one you can explain.

## What's in the box

- `data/dol_contracts_fy2024.csv`: the frozen data, 2,358 awards. Every entry is read against it.
- `data/DATA.md`: where the data came from, what each column means, and the traps.
- `baseline.py`: one red flag, end to end. Copy it and add your rules to `flags()`.
- `check.py`: run it before sending. It fails on untraceable flags and on accusation words.
- `fetch_data.py`: rebuilds the data from the USAspending API. Optional.
- `LICENSE`: MIT, for the code. The data is U.S. federal public domain.

## What to send

Email **hello@interworky.com** with:

1. A link to a public repo with your code and your `flags.csv`. `python3 check.py flags.csv`
   must pass.
2. One paragraph. For each flag: the rule in one sentence, why it signals risk (cite a
   source), and one honest reason an award could trip it.
3. The name you want credited.

## Rules

1. **A flag is a lead, not an accusation.** Describe the data, not the people. Use the legal
   words only where a source says so: an auditor estimates, a prosecutor charges, a court
   convicts. You flag.
2. **Every flag points to one row** in the frozen file and that award's USAspending page.
3. **State each rule in one sentence.** The code must do what the sentence says.
4. **Use the frozen file** so entries can be compared. You may join other public, free data if
   you name the source and your repo fetches it.
5. **Keep people out of it.** Publish nothing about a private person beyond the public record,
   and name no one as a suspect.

## How entries are read

A person reads every entry, in this order:

1. **Does it run?** Your repo produces your `flags.csv` from the frozen file.
2. **Is it traceable?** Every flag points to a row, every rule is stated.
3. **Is it sharp?** Would a reviewer want to open the rows you circled? Fewer, better flags
   beat many.
4. **Is it honest?** Your paragraph says what the flag cannot tell you.

Credit goes to the name you give. Round 1 is open until **31 October 2026**.

## Where to look next

- U.S. federal awards, contracts and grants: https://www.usaspending.gov
- Inspector General reports from every agency: https://www.oversight.gov
- Any country: the Open Contracting Partnership's guide to 73 procurement red flags, with
  formulas, for data in the Open Contracting Data Standard:
  https://www.open-contracting.org/resources/red-flags-in-public-procurement-a-guide-to-using-data-to-detect-and-mitigate-risks/
- Cardinal, an open-source library that computes those red flags:
  https://github.com/open-contracting/cardinal-rs

## Why this exists

The sixty-second brief at https://interworky.com asks who is circling the row. This kit is a
place to start.
