"""Task 3.1 (shared): build the model's inputs and split the data.

Used by compare_models.py and choose_and_test.py, so both see exactly the same split.
The split is random_state=42 and test_size=0.2, as the brief requires.
"""
import pandas as pd
from sklearn.model_selection import train_test_split

from common.paths import OUTPUT_DIR

CLEAN_FILE = OUTPUT_DIR / "appointments_clean.csv"
RANDOM_STATE = 42
TEST_SIZE = 0.2

NUMBER_COLUMNS = ["age", "distance_km", "fee_inr", "lead_days", "prior_no_shows"]
CATEGORY_COLUMNS = ["booking_channel", "visit_type"]


def build_features(df):
    """Return X (11 numeric columns) for the model.

    Not used as features: patient_id, appointment_id, dates, clinic_id, gender and status.
    status is the answer, and the IDs and dates would let the model memorise patients.
    """
    X = df[NUMBER_COLUMNS].copy()
    X["reminder_sent"] = df["reminder_sent"].map({"Yes": 1, "No": 0})   # Yes/No -> 1/0
    X = pd.concat([X, pd.get_dummies(df[CATEGORY_COLUMNS], dtype=int)], axis=1)   # one-hot
    return X


def load_split():
    """Load the clean file and split it. Returns train/test features, labels and test IDs."""
    df = pd.read_csv(CLEAN_FILE)
    X = build_features(df)
    y = df["no_show"]
    ids = df["appointment_id"]

    X_train, X_test, y_train, y_test, _, ids_test = train_test_split(
        X, y, ids, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    return X_train, X_test, y_train, y_test, ids_test
