"""Task 4.4(a): join the AI reasons to the bookings and cross-tab them against reminders.

Question: for each reason patients gave, how many of those bookings had a reminder sent?

Run from the project folder (after analyse_notes):
    python -m part4_genai.crosstab
"""
import pandas as pd

from common.paths import OUTPUT_DIR


def main():
    notes = pd.read_csv(OUTPUT_DIR / "notes_analysed.csv")
    appointments = pd.read_csv(OUTPUT_DIR / "appointments_clean.csv")

    merged = notes.merge(appointments[["appointment_id", "reminder_sent"]],
                         on="appointment_id", how="left")
    print(f"Merged rows: {len(merged)}")
    print("Bookings with reminder_sent = No:", int((merged["reminder_sent"] == "No").sum()))

    table = pd.crosstab(merged["root_cause"], merged["reminder_sent"], margins=True)
    print("\nroot_cause by reminder_sent:")
    print(table.to_string())

    table.to_csv(OUTPUT_DIR / "root_cause_by_reminder.csv")


if __name__ == "__main__":
    main()
