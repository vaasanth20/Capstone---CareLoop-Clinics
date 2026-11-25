# Part 2: MySQL

Part 2 loads the clean data into MySQL and answers the business questions with SQL.

## `schema/` (import these in MySQL Workbench)

Read [common/db.py](common_and_schema.md) to see how these files are run from Python. The table definitions are explained in [common_and_schema.md](common_and_schema.md).

## `load_database.py` (Task 2.1)

Run with `python -m part2_mysql.load_database`.

1. **`create_schema()`** runs `01_create_database.sql` on the server, then `02_create_tables.sql` inside the new database. It returns a connection to that database.
2. **`load_rows(connection)`** reads `outputs/load_data.sql`, runs each line as one `INSERT`, and commits once at the end. The clinic lines come first, so the foreign key is satisfied.
3. **`show_duplicate_key_error(connection)`** tries to insert a second row with the ID `A0001`. MySQL refuses it with error 1062, and the script prints that error. The `try` / `except` shows the pattern: catch the specific `IntegrityError`, then roll back so the connection stays usable.

## `business_queries.py` (Tasks 2.2 to 2.5)

Every query is a named string at the top of the file, with a note above it saying what it answers. Then `main()` runs them in order and prints each result.

| Query | Question it answers | Key SQL idea |
|---|---|---|
| `TOTALS` | Do we have 990 bookings and 218 no-shows? | `COUNT(*)` and `SUM(no_show)` |
| `CLINIC_RATES_95_PLUS` | Which clinics have the highest no-show rate? | `JOIN`, `GROUP BY`, `HAVING` (filters groups, not rows) |
| `CLINIC_RATES_ALL` | Same, for all 8 clinics | Same query without `HAVING` |
| `LEAD_TIME_BANDS` | Does booking far ahead matter? | `CASE WHEN` creates the bands. `ORDER BY MIN(lead_days)` sorts them by lead time, not by label text. |
| `MONTHLY_TREND` | How does the rate change month to month? | A CTE (`WITH`), and `LAG()` to compare with the previous row |
| `CITY_RANKS` | Which clinic is worst within its city? | `RANK() OVER (PARTITION BY city ...)`, and a scalar subquery for the overall rate |

**Why `HAVING` and not `WHERE`?** `WHERE` filters individual rows before grouping. `HAVING` filters after grouping, so it can test `COUNT(*)`.

**`check_against_pandas(connection)`** rebuilds the clinic counts with pandas `groupby` and compares them with the SQL counts. If they differ, a number is wrong somewhere.

**`run_query(connection, sql)`** runs a query and returns a DataFrame. The column names come from `cursor.description`, so the output has the same headings as the SQL.
