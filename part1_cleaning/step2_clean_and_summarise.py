"""Tasks 1.2 to 1.4: clean the appointments and print the summary numbers.

Run from the project folder:
    python -m part1_cleaning.step2_clean_and_summarise
"""
from part1_cleaning.clean import add_features, clean_appointments, numpy_summary


def main():
    df = clean_appointments()
    df = add_features(df)

    print("\nTask 1.4 features")
    print("lead_days range:", df["lead_days"].min(), "to", df["lead_days"].max())
    print("No-shows:", df["no_show"].sum(), "of", len(df),
          f"({round(100 * df['no_show'].mean(), 1)}%)")

    summary = numpy_summary(df)
    print("Column means [age, distance, fee, lead_days]:", summary["column_means"].round(2))
    print("Bookings with lead_days > 14:", summary["long_lead_count"],
          f"({summary['long_lead_share']}%)")
    print("Distance values with |z| > 2:", summary["distance_outliers_z2"])


if __name__ == "__main__":
    main()
