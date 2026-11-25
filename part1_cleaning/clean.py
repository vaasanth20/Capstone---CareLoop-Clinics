"""Cleaning rules for appointments.csv (Tasks 1.2 to 1.4).

Each function does one named fix, so you can see what changed and why.
clean_appointments() runs them in the order the brief asks for.
"""
import numpy as np
import pandas as pd

from common.paths import DATA_DIR

RAW_APPOINTMENTS = DATA_DIR / "appointments.csv"
VALID_AGE_RANGE = (1, 100)   # ages outside this range are typos, so they become missing
IQR_MULTIPLIER = 1.5         # the standard "Tukey fence" rule for outliers


# ---------- Task 1.2: first pass ----------

def load_raw():
    """Read the raw export exactly as it is (1,020 rows)."""
    return pd.read_csv(RAW_APPOINTMENTS)


def remove_exact_duplicates(df):
    """Drop rows that are identical in every column (the same booking typed twice)."""
    return df.drop_duplicates()


def standardise_booking_channel(df):
    """'APP ', 'app' and 'App' all become 'App'. Remove spaces first, then fix capitals."""
    df["booking_channel"] = df["booking_channel"].str.strip().str.title()
    return df


def parse_dates(df):
    """Turn text dates into real dates. Unreadable text such as 'TBD' becomes missing (NaT)."""
    df["appt_date"] = pd.to_datetime(df["appt_date"], errors="coerce")
    df["booked_on"] = pd.to_datetime(df["booked_on"])
    return df


def drop_unusable_rows(df):
    """A booking with no appointment date or no status cannot be analysed, so it is dropped."""
    return df.dropna(subset=["appt_date", "status"])


# ---------- Task 1.3: second pass (gaps and outliers) ----------

def blank_impossible_ages(df):
    """Ages below 1 or above 100 are impossible, so they are set to missing."""
    low, high = VALID_AGE_RANGE
    impossible = (df["age"] < low) | (df["age"] > high)
    df.loc[impossible, "age"] = np.nan
    return df


def fill_with_median(df, column):
    """Fill missing values with the column median. The median is not pulled by outliers."""
    df[column] = df[column].fillna(df[column].median())
    return df


def cap_outliers(df, column):
    """Pull values beyond the IQR fences back to the fence.

    Returns the dataframe and a small report with the quartiles, fences and count of
    values that were changed, so the numbers can be printed and checked.
    """
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - IQR_MULTIPLIER * iqr
    upper = q3 + IQR_MULTIPLIER * iqr

    capped = np.clip(df[column], lower, upper)
    report = {
        "q1": float(q1), "q3": float(q3), "lower_fence": float(lower), "upper_fence": float(upper),
        "capped": int((capped != df[column]).sum()),
    }
    df[column] = capped
    return df, report


def round_and_type(df):
    """Store distance with one decimal and fee as whole rupees."""
    df["age"] = df["age"].round().astype(int)
    df["distance_km"] = df["distance_km"].round(1)
    df["fee_inr"] = df["fee_inr"].round().astype(int)
    return df


# ---------- Task 1.4: features ----------

def add_features(df):
    """lead_days = days between booking and appointment. no_show = 1 for a no-show, else 0."""
    df["lead_days"] = (df["appt_date"] - df["booked_on"]).dt.days
    df["no_show"] = (df["status"] == "No-Show").astype(int)
    return df


def numpy_summary(df):
    """Summaries computed with NumPy and no loops (Task 1.4)."""
    # Column order in X: 0 age, 1 distance_km, 2 fee_inr, 3 lead_days
    X = df[["age", "distance_km", "fee_inr", "lead_days"]].to_numpy()

    means = X.mean(axis=0)
    long_lead_mask = X[:, 3] > 14
    distance = X[:, 1]
    z_scores = (distance - np.mean(distance)) / np.std(distance)   # np.std = population SD

    return {
        "column_means": means,
        "long_lead_count": int(long_lead_mask.sum()),
        "long_lead_share": round(100 * long_lead_mask.mean(), 1),
        "distance_outliers_z2": int((np.abs(z_scores) > 2).sum()),
    }


# ---------- The whole pipeline ----------

def clean_appointments(log=print):
    """Run Tasks 1.2 and 1.3 in order and print the count after each step."""
    raw = load_raw()
    log(f"Raw shape: {raw.shape}")
    log(f"Missing values per column:\n{raw.isnull().sum()}")
    log(f"Duplicate rows: {raw.duplicated().sum()}")

    df = remove_exact_duplicates(raw)
    log(f"(a) After dropping duplicates: {len(df)} rows")

    df = standardise_booking_channel(df)
    log(f"(b) Booking channels after cleaning: {sorted(df['booking_channel'].unique())}")

    df = parse_dates(df)
    log(f"(c) Unreadable appointment dates: {df['appt_date'].isna().sum()}")

    df = drop_unusable_rows(df)
    log(f"(d) After dropping unusable rows: {len(df)} rows")

    df = blank_impossible_ages(df)
    log(f"1.3(a) Missing ages, including impossible ones: {df['age'].isna().sum()}")

    df = fill_with_median(df, "age")
    df = fill_with_median(df, "distance_km")
    log(f"1.3(b) Median age: {df['age'].median()}, median distance: {df['distance_km'].median()}")

    df, distance_report = cap_outliers(df, "distance_km")
    log(f"1.3(c) distance_km: {distance_report}")
    df, fee_report = cap_outliers(df, "fee_inr")
    log(f"1.3(c) fee_inr: {fee_report}")

    df = round_and_type(df)
    return df
