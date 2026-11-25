# Part 1: cleaning the data

Part 1 turns the raw export (1,020 rows, with duplicates, typos and gaps) into a clean table of 990 rows. It runs in four steps, and each step is one script.

## Step 1: `step1_read_with_csv.py` (Task 1.1)

This step uses only Python's built-in `csv` module, with no pandas.

- **`parse_row(row)`** converts the number columns (`age`, `fee_inr`, `prior_no_shows` to whole numbers and `distance_km` to a decimal). If a value is blank, `int("")` raises `ValueError`, so the row is rejected.
- **`main()`** reads every row. Rows that convert go to `accepted`, and the rest go to `rejected` together with the reason. The rejected rows are saved to `outputs/rejected_rows.json`.

The lesson here is that a type check is not a validity check. A row with age 250 converts fine, so it is accepted. Part 1's pandas steps catch it later.

## `clean.py`: the cleaning rules

This is the file to read if you want to understand each fix. Each function does one job.

**Task 1.2, first pass**

| Function | What it does and why |
|---|---|
| `load_raw()` | Reads `data/appointments.csv` as it is. |
| `remove_exact_duplicates(df)` | Drops rows identical in every column. These are the same booking entered twice. |
| `standardise_booking_channel(df)` | Strips spaces, then fixes capitals. `"APP "`, `"app"` and `"App"` all become `"App"`. |
| `parse_dates(df)` | Converts date text to real dates. Text such as `"TBD"` becomes missing (`NaT`) because of `errors="coerce"`. |
| `drop_unusable_rows(df)` | Drops rows with no appointment date or no status. |

**Task 1.3, second pass** (run in this order so the quartiles are calculated after the gaps are filled)

| Function | What it does and why |
|---|---|
| `blank_impossible_ages(df)` | Ages below 1 or above 100 become missing. |
| `fill_with_median(df, column)` | Fills gaps with the median. The median is not pulled by extreme values, so it is a safer fill than the mean. |
| `cap_outliers(df, column)` | Calculates Q1, Q3 and IQR, then pulls values beyond the fences back to the fence with `np.clip`. It returns a report with the fences and the number of values changed. |
| `round_and_type(df)` | Rounds distance to one decimal and fee to whole rupees. |

**Task 1.4, features**

| Function | What it does |
|---|---|
| `add_features(df)` | Adds `lead_days` (days between booking and appointment) and `no_show` (1 or 0). |
| `numpy_summary(df)` | Computes column means, the share of bookings with a lead of more than 14 days, and how many distances are more than 2 standard deviations from the mean. It uses boolean masks, so there are no loops. |

`clean_appointments(log=print)` runs Tasks 1.2 and 1.3 in order and prints the row count after each step.

## Step 2: `step2_clean_and_summarise.py`

Calls `clean_appointments()`, adds the features, and prints the summary numbers. Run it to check the counts against the brief.

## Step 3: `step3_enrich_clinics.py` (Task 1.5)

Adds a temperature to each clinic from the free Open-Meteo weather API.

- **`fetch_first_temperature(latitude, longitude)`** makes the request with a 10-second timeout. It tries twice. It returns `(temperature, None)` on success, or `(None, reason)` if every attempt fails. It never invents a value.
- The API reply is checked in two places: the HTTP status must be 200, and the `hourly.temperature_2m` field must exist.

If the call fails, the clinic is still saved with an empty `temp_c`, and the reason is printed.

## Step 4: `step4_export.py` (Task 1.6)

Writes the two hand-off files for Part 2.

- **`sql_value(value)`** formats one value for SQL. Text is wrapped in single quotes, numbers are written as they are, and missing values become `NULL`. It stops with an error if a text value contains an apostrophe, because this simple writer cannot escape one.
- **`insert_statement(table, columns, row)`** builds one `INSERT` line.
- **`main()`** checks that `appointment_id` is unique and that no column is missing. It then writes `appointments_clean.csv` (16 columns) and `load_data.sql`. The clinic inserts come first, because appointments depend on clinics.

Building SQL with string formatting is fine for this fixed dataset. In a real application you would use parameterised queries instead.
