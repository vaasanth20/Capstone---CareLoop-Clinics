"""Task 3.5: tune, choose the model and the threshold using TRAINING data only,
then score the test set once and save test_risk_scores.csv.

Order of work (the test set is not touched until step 4):
  1. Tune the random forest with cross-validation on the training set.
  2. Compare the candidate models by 5-fold ROC-AUC on the training set. Highest wins.
  3. Pick the probability threshold using out-of-fold predictions on the training set.
  4. Fit the winner on all training rows and score the test set once.

Run from the project folder:
    python -m part3_model.choose_and_test
"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, cross_val_predict, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from common.paths import OUTPUT_DIR
from part3_model.features import load_split

RANDOM_STATE = 42
CV_FOLDS = 5
THRESHOLDS_TO_COMPARE = [0.5, 0.35]
RISK_FILE = OUTPUT_DIR / "test_risk_scores.csv"


def make_candidates(tuned_forest):
    """The models we compare. Logistic regression sits in a pipeline so the scaler is
    re-fitted inside each fold, and the validation fold never influences the scaler."""
    return {
        "logistic regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000)),
        ]),
        "tree, depth 3": DecisionTreeClassifier(max_depth=3, random_state=RANDOM_STATE),
        "random forest": RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE),
        "tuned forest": tuned_forest,
    }


def tune_forest(X_train, y_train):
    """Grid search over forest size and depth, scored by cross-validated ROC-AUC."""
    grid = GridSearchCV(
        RandomForestClassifier(random_state=RANDOM_STATE),
        {"n_estimators": [100, 200], "max_depth": [3, 5, 8]},
        cv=CV_FOLDS, scoring="roc_auc",
    )
    grid.fit(X_train, y_train)
    print("Best forest settings:", grid.best_params_)
    print(f"Best cross-validated ROC-AUC: {grid.best_score_:.4f}")
    return grid.best_estimator_


def pick_winner(candidates, X_train, y_train):
    """Return the name of the model with the highest 5-fold training ROC-AUC."""
    print("\n5-fold ROC-AUC on the training set:")
    scores = {}
    for name, model in candidates.items():
        scores[name] = cross_val_score(model, X_train, y_train, cv=CV_FOLDS, scoring="roc_auc").mean()
        print(f"  {name:22s} {scores[name]:.4f}")
    winner = max(scores, key=scores.get)
    print("Winner:", winner)
    return winner


def pick_threshold(model, X_train, y_train):
    """Compare thresholds using out-of-fold training predictions and keep the best F1."""
    out_of_fold = cross_val_predict(model, X_train, y_train, cv=CV_FOLDS, method="predict_proba")[:, 1]
    results = []
    print("\nOut-of-fold training predictions:")
    for threshold in THRESHOLDS_TO_COMPARE:
        flagged = (out_of_fold >= threshold).astype(int)
        row = {
            "threshold": threshold,
            "precision": precision_score(y_train, flagged),
            "recall": recall_score(y_train, flagged),
            "F1": f1_score(y_train, flagged),
            "flagged": int(flagged.sum()),
        }
        results.append(row)
        print(f"  threshold {threshold}: precision {row['precision']:.2f}, recall {row['recall']:.2f}, "
              f"F1 {row['F1']:.2f}, flagged {row['flagged']}")
    best = max(results, key=lambda row: row["F1"])
    print(f"Chosen threshold: {best['threshold']} (highest F1). Recall matters here: a missed "
          f"warning costs an empty slot, while an extra call costs only a minute.")
    return best["threshold"]


def score_test_once(model, X_test, y_test, ids_test, threshold):
    """The only use of the test set: report the final numbers and save the risk file."""
    probabilities = model.predict_proba(X_test)[:, 1]
    flagged = (probabilities >= threshold).astype(int)
    print("\nFinal test-set evaluation (run once):")
    print(f"  precision {precision_score(y_test, flagged):.2f}")
    print(f"  recall    {recall_score(y_test, flagged):.2f}")
    print(f"  flagged   {flagged.sum()} of {len(flagged)}")
    print(f"  ROC-AUC   {roc_auc_score(y_test, probabilities):.3f}")

    risk = pd.DataFrame({
        "appointment_id": ids_test.values,
        "no_show": y_test.values,
        "risk_prob": probabilities.round(4),
        "flag": flagged,
    })
    risk.to_csv(RISK_FILE, index=False)
    print(f"Saved {RISK_FILE.name} ({len(risk)} rows)")


def main():
    X_train, X_test, y_train, y_test, ids_test = load_split()

    tuned_forest = tune_forest(X_train, y_train)
    candidates = make_candidates(tuned_forest)
    winner_name = pick_winner(candidates, X_train, y_train)
    winner = candidates[winner_name]

    threshold = pick_threshold(winner, X_train, y_train)

    winner.fit(X_train, y_train)     # the pipeline fits its own scaler
    score_test_once(winner, X_test, y_test, ids_test, threshold)


if __name__ == "__main__":
    main()
