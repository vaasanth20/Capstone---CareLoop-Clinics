"""Tasks 3.1 to 3.4: baseline, logistic regression, decision tree and random forest.

These models are compared on the test set for reporting only. The model is NOT
chosen here. That choice is made in choose_and_test.py from training data alone.

Run from the project folder:
    python -m part3_model.compare_models
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from part3_model.features import load_split

RANDOM_STATE = 42


def print_metrics(name, y_true, y_pred, probabilities):
    """Print the five numbers the brief asks for. Each one is explained in the README."""
    print(f"{name}")
    print(f"  accuracy  {accuracy_score(y_true, y_pred):.3f}")
    print(f"  precision {precision_score(y_true, y_pred):.2f}")
    print(f"  recall    {recall_score(y_true, y_pred):.2f}")
    print(f"  F1        {f1_score(y_true, y_pred):.2f}")
    print(f"  ROC-AUC   {roc_auc_score(y_true, probabilities):.3f}")
    print("  confusion [[TN, FP], [FN, TP]]:", confusion_matrix(y_true, y_pred).tolist())


def task_3_1_baseline(y_train, y_test):
    print("== 3.1 Split and baseline ==")
    print(f"Train rows: {len(y_train)}  Test rows: {len(y_test)}")
    print(f"No-shows in test set: {int(y_test.sum())}")
    always_attended = np.zeros(len(y_test), dtype=int)
    correct = int((always_attended == y_test).sum())
    print(f"Baseline accuracy (always 'Attended'): {accuracy_score(y_test, always_attended):.4f} "
          f"({correct} of {len(y_test)})")


def task_3_2_logistic(X_train, X_test, y_train, y_test):
    print("\n== 3.2 Logistic regression ==")
    # The scaler learns the mean and spread from the training rows only.
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000).fit(X_train_scaled, y_train)
    probabilities = model.predict_proba(X_test_scaled)[:, 1]
    print_metrics("Logistic regression (threshold 0.5)", y_test,
                  (probabilities >= 0.5).astype(int), probabilities)

    print("\nCoefficients (fitted on scaled features):")
    for name, coefficient in zip(X_train.columns, model.coef_[0]):
        print(f"  {name:28s} {coefficient:+.3f}")

    # Reminder effect. Two steps: the coefficient is per standard deviation, so divide by
    # the scaler's SD to get the effect of a No -> Yes change, then take exp().
    reminder_index = list(X_train.columns).index("reminder_sent")
    coefficient = model.coef_[0][reminder_index]
    sd = scaler.scale_[reminder_index]
    print(f"\nreminder_sent: exp(coef) per 1 SD = {np.exp(coefficient):.2f}")
    print(f"reminder_sent: exp(coef / SD) for No -> Yes = {np.exp(coefficient / sd):.2f}")
    print("Both numbers differ because the first is per 1 SD of a scaled 0/1 column, "
          "and the second is for the real 0 -> 1 change.")
    print("In this model, holding other features constant, reminders go with lower odds of "
          "a no-show. This is an association, not proof that reminders cause fewer no-shows.")
    return model, scaler, probabilities


def task_3_3_tree(X_train, X_test, y_train, y_test):
    print("\n== 3.3 Decision tree and overfitting ==")
    for depth in [None, 3]:
        tree = DecisionTreeClassifier(max_depth=depth, random_state=RANDOM_STATE)
        tree.fit(X_train, y_train)
        print(f"max_depth={depth}: depth reached={tree.get_depth()}, "
              f"train accuracy={tree.score(X_train, y_train):.3f}, "
              f"test accuracy={tree.score(X_test, y_test):.3f}")
    print("A large gap between train and test accuracy means the tree memorised the training data.")


def task_3_4_forest(X_train, X_test, y_train, y_test, logistic_probs):
    print("\n== 3.4 Random forest and comparison ==")
    forest = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)
    forest.fit(X_train, y_train)
    forest_probs = forest.predict_proba(X_test)[:, 1]
    print_metrics("Random forest (threshold 0.5)", y_test, forest.predict(X_test), forest_probs)

    importances = pd.Series(forest.feature_importances_, index=X_train.columns)
    print("Top three importances:")
    print(importances.sort_values(ascending=False).head(3).round(3).to_string())

    tree3 = DecisionTreeClassifier(max_depth=3, random_state=RANDOM_STATE).fit(X_train, y_train)
    tree3_probs = tree3.predict_proba(X_test)[:, 1]

    rows = []
    for name, pred, probs in [
        ("Logistic regression", (logistic_probs >= 0.5).astype(int), logistic_probs),
        ("Tree, depth 3", tree3.predict(X_test), tree3_probs),
        ("Random forest", forest.predict(X_test), forest_probs),
    ]:
        rows.append({"model": name,
                     "accuracy": round(accuracy_score(y_test, pred), 3),
                     "recall": round(recall_score(y_test, pred), 2),
                     "ROC-AUC": round(roc_auc_score(y_test, probs), 3)})
    print("\nComparison on the test set (for reporting only):")
    print(pd.DataFrame(rows).to_string(index=False))


def main():
    X_train, X_test, y_train, y_test, _ = load_split()
    task_3_1_baseline(y_train, y_test)
    _, _, logistic_probs = task_3_2_logistic(X_train, X_test, y_train, y_test)
    task_3_3_tree(X_train, X_test, y_train, y_test)
    task_3_4_forest(X_train, X_test, y_train, y_test, logistic_probs)


if __name__ == "__main__":
    main()
