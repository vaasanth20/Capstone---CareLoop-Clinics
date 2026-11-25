"""Task 1.1: read the raw file with Python's csv module (no pandas).

Each row is converted to the right types. Rows that cannot be converted (a blank
number, for example) go to a 'rejected' list and are saved to outputs/rejected_rows.json.

Run from the project folder:
    python -m part1_cleaning.step1_read_with_csv
"""
import csv
import json

from common.paths import DATA_DIR, OUTPUT_DIR

RAW_FILE = DATA_DIR / "appointments.csv"
REJECTED_FILE = OUTPUT_DIR / "rejected_rows.json"


def parse_row(row):
    """Convert the number columns. Raises ValueError if one of them is blank or not a number."""
    converted = dict(row)
    converted["age"] = int(row["age"])
    converted["fee_inr"] = int(row["fee_inr"])
    converted["prior_no_shows"] = int(row["prior_no_shows"])
    converted["distance_km"] = float(row["distance_km"])
    return converted


def main():
    with open(RAW_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        print("Header:", reader.fieldnames)
        rows = list(reader)
    print("Rows read:", len(rows))

    accepted, rejected = [], []
    for row in rows:
        try:
            accepted.append(parse_row(row))
        except ValueError as error:
            rejected.append({"row": row, "reason": str(error)})

    print("Accepted:", len(accepted))
    print("Rejected:", len(rejected))
    # A type check is not a validity check: impossible ages such as 250 still pass here.
    # The pandas cleaning in part1_cleaning/clean.py handles those.

    with open(REJECTED_FILE, "w", encoding="utf-8") as file:
        json.dump(rejected, file, indent=2)
    print("Saved", REJECTED_FILE.name)


if __name__ == "__main__":
    main()
