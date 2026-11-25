# Code overview

This project answers one question: **which appointments are most likely to be missed, why, and what CareLoop should do first.**

The work runs in four parts. Each part reads the output of the one before it.

```
data/appointments.csv
   │  Part 1: clean, check, export
   ▼
outputs/appointments_clean.csv ──► Part 2: load into MySQL, answer business questions
   │
   └──► Part 3: predict no-shows, choose a model, save risk scores
                                                 
data/followup_notes.csv ──► Part 4: Gemini reads each note, returns a reason
                              │
                              └──► joined with Part 1's table to see reasons vs reminders
```

## How the folders fit together

| Folder | What it is for | Read this first |
|---|---|---|
| `data/` | The three original files. Never edited. | — |
| `schema/` | SQL to import into MySQL. | [Part 2](part2_mysql.md) |
| `common/` | Shared helpers: folder paths and the MySQL connection. | [Shared helpers](common_and_schema.md) |
| `part1_cleaning/` | Reading, cleaning and checking the data. | [Part 1](part1_cleaning.md) |
| `part2_mysql/` | Loading the database and running SQL. | [Part 2](part2_mysql.md) |
| `part3_model/` | Machine learning. | [Part 3](part3_model.md) |
| `part4_genai/` | Gemini API and validation. | [Part 4](part4_genai.md) |
| `outputs/` | Files the scripts create. | — |

## Conventions used in the code

- **Each script has a `main()` function** and runs only when you start it with `python -m`. You can read a file top to bottom and find the steps in order.
- **Functions do one thing**, and their names say what. For example `remove_exact_duplicates` only removes duplicates.
- **Shared logic lives in one place.** `part1_cleaning/clean.py` holds the cleaning rules, and the step scripts call them. `part3_model/features.py` holds the split, so every model sees the same rows.
- **No secrets in files.** MySQL credentials come from environment variables or a hidden prompt. The Gemini key is typed at run time.
- **Random seed 42 and a test size of 0.2** are set once, as the brief requires, and reused everywhere.
