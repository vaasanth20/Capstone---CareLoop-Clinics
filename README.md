# CareLoop No-Show Guard

Which appointments are most likely to be missed, why patients miss them, and what CareLoop should do first.

The project has four parts. Each part lives in its own folder, and each folder runs on its own from the command line.

## Code explanations

Each part has a plain-language walkthrough of its code in `docs/`:

- [Overview and how the folders fit together](docs/00_overview.md)
- [Shared helpers and the schema](docs/common_and_schema.md)
- [Part 1: cleaning](docs/part1_cleaning.md)
- [Part 2: MySQL](docs/part2_mysql.md)
- [Part 3: model](docs/part3_model.md)
- [Part 4: Gemini](docs/part4_genai.md)

## Folder layout

```
noshowguard/
├── data/                      Original files. Never edited.
│   ├── appointments.csv
│   ├── clinics.csv
│   └── followup_notes.csv
├── schema/                    SQL to import into MySQL (the only SQL files in the project)
│   ├── 01_create_database.sql
│   └── 02_create_tables.sql
├── common/                    Shared helpers: folder paths, MySQL connection
│   ├── paths.py
│   └── db.py
├── part1_cleaning/            Part 1: Python and data foundations
│   ├── step1_read_with_csv.py     Task 1.1  read with the csv module
│   ├── clean.py                   Tasks 1.2 to 1.4  the cleaning rules, one function each
│   ├── step2_clean_and_summarise.py   prints the cleaning steps and summary numbers
│   ├── step3_enrich_clinics.py    Task 1.5  clinic temperatures from a free API
│   └── step4_export.py            Task 1.6  clean CSV and load_data.sql
├── part2_mysql/               Part 2: SQL in MySQL
│   ├── load_database.py           Task 2.1  create schema, load data, show duplicate error
│   └── business_queries.py        Tasks 2.2 to 2.5  every query, with a pandas cross-check
├── part3_model/               Part 3: machine learning
│   ├── features.py                Task 3.1  inputs and the train/test split (shared)
│   ├── compare_models.py          Tasks 3.1 to 3.4  baseline, logistic, tree, forest
│   └── choose_and_test.py         Task 3.5  choose the model and threshold, then test once
├── part4_genai/               Part 4: Gemini API
│   ├── prompts.py                 the prompts, in one place
│   ├── schemas.py                 Pydantic checks and the allowed-list check
│   ├── gemini_client.py           API wrapper (the key is typed at run time)
│   ├── first_call.py              Task 4.1  one call on note N001
│   ├── analyse_notes.py           Task 4.2  first 10 notes, saved to outputs/
│   ├── stress_test.py             Task 4.3  bad replies, and prompt comparison
│   └── crosstab.py                Task 4.4  reasons against reminder_sent
├── docs/                      Code explanations, one Markdown file per part
├── outputs/                   Files the pipeline creates
├── requirements.txt
├── .env.example
└── .gitignore
```

The design choice: each part's SQL, prompts and maths sit in the Python file that uses them. There are no separate query files to switch between. The only SQL files are the two schema files, because you import those into MySQL Workbench.

## Setup

1. **Install MySQL 8** (MySQL Installer on Windows, or Homebrew on macOS) and MySQL Workbench. Remember the root password.
2. **Install Python 3.11 or newer**, then from this folder:
   ```
   python -m venv .venv
   .venv\Scripts\activate          (macOS/Linux: source .venv/bin/activate)
   pip install -r requirements.txt
   ```
3. **Set your MySQL login** (the password is asked for if you leave it out):
   ```
   set MYSQL_USER=root               (macOS/Linux: export MYSQL_USER=root)
   ```

## Run order

Run each command from the project folder.

| Step | Command | Makes |
|---|---|---|
| 1.1 | `python -m part1_cleaning.step1_read_with_csv` | `outputs/rejected_rows.json` |
| 1.2–1.4 | `python -m part1_cleaning.step2_clean_and_summarise` | prints the numbers |
| 1.5 | `python -m part1_cleaning.step3_enrich_clinics` | `outputs/clinics_enriched.csv` |
| 1.6 | `python -m part1_cleaning.step4_export` | `outputs/appointments_clean.csv`, `outputs/load_data.sql` |
| 2.1 | `python -m part2_mysql.load_database` | creates the MySQL database and loads it |
| 2.2–2.5 | `python -m part2_mysql.business_queries` | prints every query result |
| 3.1–3.4 | `python -m part3_model.compare_models` | prints model comparison |
| 3.5 | `python -m part3_model.choose_and_test` | `outputs/test_risk_scores.csv` |
| 4.1 | `python -m part4_genai.first_call` | asks for your Gemini key |
| 4.2 | `python -m part4_genai.analyse_notes` | `outputs/notes_analysed.csv` |
| 4.3 | `python -m part4_genai.stress_test` | prints the validation errors and prompt comparison |
| 4.4 | `python -m part4_genai.crosstab` | `outputs/root_cause_by_reminder.csv` |

**Importing the schema by hand (optional):** in MySQL Workbench, open `schema/01_create_database.sql` and run it, then open `schema/02_create_tables.sql` and run it. `load_database.py` does the same thing automatically.

**Never put your Gemini key in a file.** The Part 4 scripts ask for it at run time, and the input is hidden.

## Results so far

- **Part 1:** 1,020 raw rows become 990 clean rows. 218 of them are no-shows (22.0%).
- **Part 2 (MySQL):** Hadapsar Care Centre (Pune) has the highest rate among clinics with 95+ bookings, at 27.3%. Bookings made 31+ days ahead have a 60.5% no-show rate, the highest lead-time band.
- **Part 3:** The logistic regression is chosen by training-set cross-validation (ROC-AUC 0.774, the highest). On the test set it reaches ROC-AUC 0.789. At threshold 0.35 it flags 49 of 198 bookings, with recall 0.57.
- **Part 4:** Not run yet. It needs your Gemini key.

## Known gaps

- **Clinic temperatures are blank.** The weather API host was blocked in the environment where this was built (HTTP 403 from the proxy). `step3_enrich_clinics.py` leaves the value empty and prints the reason, as the brief requires. Run it on your own machine to fill them in.
- **MySQL was tested on MariaDB 10.11**, which is MySQL-compatible for these queries. The brief asks for MySQL 8; please run it once on MySQL 8 to confirm.

## Limitations

1. The cleaning medians, quartiles and fences were calculated on all 990 rows before the split, so test rows had a small indirect influence on the cleaning.
2. The split is random, not past-to-future, and the same patient can appear in both train and test.
3. The data are observational. The reminder association (odds about 0.31 times for a No-to-Yes change) is not proof that reminders cause fewer no-shows.
4. Clinic-level sample sizes are small (82 to 160 bookings), so clinic rankings are uncertain.
5. Part 4 can only be checked against the 10 notes in the brief, which are an illustration and cannot show the real reasons clinic-wide.
