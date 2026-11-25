# Part 3: predicting no-shows

The goal is a risk score the front desk can use the evening before an appointment, to decide whom to phone. Only about 1 booking in 5 is a no-show, so accuracy alone is misleading: a model that always says "will attend" is 75% accurate and catches no one.

## Rules that protect the results

- **The test set is for reporting only.** Models, settings and thresholds are chosen using training data alone.
- **Cross-validation** (repeatedly splitting the training data) gives the honest estimate used for every choice.

## `features.py` (shared)

- **`build_features(df)`** returns the 11 input columns. `reminder_sent` is mapped from Yes/No to 1/0. `booking_channel` and `visit_type` are one-hot encoded with `get_dummies`, which creates one 0/1 column per category.
- The columns left out are IDs, dates, `clinic_id`, `gender` and `status`. `status` is the answer. The IDs and dates would let the model memorise individual patients.
- **`load_split()`** splits the data with `test_size=0.2` and `random_state=42`. Every script calls this function, so they all use the same rows.

## `compare_models.py` (Tasks 3.1 to 3.4)

Each model is evaluated the same way by **`print_metrics`**, which prints accuracy, precision, recall, F1, ROC-AUC and the confusion matrix.

- **Baseline (3.1):** predicting "Attended" for everyone gives the accuracy to beat.
- **Logistic regression (3.2):** the scaler is fitted on training rows only, then applied to the test rows. The reminder effect is calculated in two steps:
  1. The coefficient is per standard deviation of the scaled column, so divide by the scaler's SD (`scaler.scale_`) to get the effect of a real 0 to 1 change.
  2. Take `exp()` to turn the log-odds into an odds ratio.
- **Decision tree (3.3):** trained with no depth limit and then with depth 3. A big gap between training and test accuracy means it memorised the training data.
- **Random forest (3.4):** an ensemble of 100 trees. The top three feature importances are printed, and a comparison table is built for the report.

## `choose_and_test.py` (Task 3.5)

This is the script that makes the final choice, in four steps:

1. **`tune_forest`** runs a grid search over tree count and depth, scored by ROC-AUC.
2. **`pick_winner`** compares four candidates by 5-fold ROC-AUC on the training set. The highest wins.
3. **`pick_threshold`** gets out-of-fold predictions (each training row predicted by a model that did not see it), tries thresholds 0.5 and 0.35, and keeps the one with the higher F1.
4. **`score_test_once`** fits the winner on all training rows and scores the test set once. It saves `outputs/test_risk_scores.csv`.

**Why logistic regression is in a pipeline:** a `Pipeline` re-fits the scaler inside each fold. If the scaler were fitted on the whole training set first, each validation fold would influence it, and the score would look slightly better than it really is.

**Why recall matters here:** a missed warning costs an empty appointment slot. An extra phone call costs about a minute. So the threshold that catches more no-shows is preferred, even at the cost of more false alarms.
