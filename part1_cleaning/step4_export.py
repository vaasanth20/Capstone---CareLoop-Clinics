"""Task 1.6: export the clean table and write load_data.sql.

Outputs:
  outputs/appointments_clean.csv  the 990 clean rows, 16 columns
  outputs/load_data.sql           one INSERT per line: clinics first, then appointments

Run from the project folder (after steps 2 and 3):
    python -m part1_cleaning.step4_export
"""
import pandas as pd

from common.paths import OUTPUT_DIR
from part1_cleaning.clean import add_features, clean_appointments

CLEAN_COLUMNS = [
    "appointment_id", "patient_id", "clinic_id", "booked_on", "appt_date", "age", "gender",
    "distance_km", "fee_inr", "booking_channel", "visit_type", "reminder_sent",
    "prior_no_shows", "status", "lead_days", "no_show",
]
CLINIC_COLUMNS = ["clinic_id", "clinic_name", "city", "tier", "latitude", "longitude", "temp_c"]


def sql_value(value):
    """One value as SQL: text in single quotes, numbers bare, missing as NULL."""
    if pd.isna(value):
        return "NULL"
    if isinstance(value, str):
        assert "'" not in value, f"apostrophe in {value!r}: this simple writer cannot escape it"
        return f"'{value}'"
    return str(value)


def insert_statement(table, columns, row):
    values = ", ".join(sql_value(row[column]) for column in columns)
    return f"INSERT INTO {table} VALUES ({values});"


def main():
    df = clean_appointments()
    df = add_features(df).sort_values("appointment_id")

    print("\nChecks before export")
    print("Distinct appointment_id:", df["appointment_id"].nunique(), "of", len(df), "rows")
    print("Missing values across the 16 columns:", int(df[CLEAN_COLUMNS].isnull().sum().sum()))
    assert df["appointment_id"].is_unique
    assert df[CLEAN_COLUMNS].isnull().sum().sum() == 0

    export = df[CLEAN_COLUMNS].copy()
    export["booked_on"] = export["booked_on"].dt.strftime("%Y-%m-%d")
    export["appt_date"] = export["appt_date"].dt.strftime("%Y-%m-%d")
    export.to_csv(OUTPUT_DIR / "appointments_clean.csv", index=False)

    clinics = pd.read_csv(OUTPUT_DIR / "clinics_enriched.csv")
    clinic_lines = [insert_statement("clinics", CLINIC_COLUMNS, row) for _, row in clinics.iterrows()]
    appointment_lines = [insert_statement("appointments", CLEAN_COLUMNS, row) for _, row in export.iterrows()]

    with open(OUTPUT_DIR / "load_data.sql", "w", encoding="utf-8") as file:
        file.write("\n".join(clinic_lines + appointment_lines) + "\n")

    print(f"Saved appointments_clean.csv ({len(export)} rows)")
    print(f"Saved load_data.sql ({len(clinic_lines)} clinic + {len(appointment_lines)} appointment INSERTs)")


if __name__ == "__main__":
    main()
