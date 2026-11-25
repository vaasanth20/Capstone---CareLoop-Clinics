"""Task 2.2 to 2.5: the business questions, answered with SQL.

Every query is in this file, next to the code that runs it, so you can read the SQL
and its result together. Each query has a short note above it saying what it answers.

The clinic counts are also rebuilt with pandas (groupby) and compared with the SQL,
because a manager should be able to trust the numbers.

Run from the project folder (after load_database):
    python -m part2_mysql.business_queries
"""
import pandas as pd

from common.db import get_connection
from common.paths import OUTPUT_DIR
from part2_mysql.load_database import DATABASE

# ---- The queries -----------------------------------------------------------------

# Check: the totals must match Part 1 (990 bookings, 218 no-shows).
TOTALS = """
SELECT COUNT(*) AS appointments, SUM(no_show) AS no_shows
FROM appointments;
"""

# 2.2: no-show rate per clinic. HAVING keeps clinics with at least 95 bookings.
CLINIC_RATES_95_PLUS = """
SELECT c.clinic_name, c.city,
       COUNT(*) AS appointments,
       SUM(a.no_show) AS no_shows,
       ROUND(100.0 * SUM(a.no_show) / COUNT(*), 1) AS no_show_pct
FROM appointments AS a
JOIN clinics AS c ON c.clinic_id = a.clinic_id
GROUP BY c.clinic_id, c.clinic_name, c.city
HAVING COUNT(*) >= 95
ORDER BY no_show_pct DESC;
"""

# 2.2 (continued): the same query without HAVING, so all 8 clinics show.
CLINIC_RATES_ALL = """
SELECT c.clinic_name, c.city,
       COUNT(*) AS appointments,
       SUM(a.no_show) AS no_shows,
       ROUND(100.0 * SUM(a.no_show) / COUNT(*), 1) AS no_show_pct
FROM appointments AS a
JOIN clinics AS c ON c.clinic_id = a.clinic_id
GROUP BY c.clinic_id, c.clinic_name, c.city
ORDER BY no_show_pct DESC;
"""

# 2.3: does booking far ahead matter? CASE WHEN makes the four bands.
# ORDER BY MIN(lead_days) sorts the bands by lead time, not alphabetically.
LEAD_TIME_BANDS = """
SELECT CASE WHEN lead_days BETWEEN 1 AND 7   THEN '1-7'
            WHEN lead_days BETWEEN 8 AND 14  THEN '8-14'
            WHEN lead_days BETWEEN 15 AND 30 THEN '15-30'
            ELSE '31+' END AS lead_band,
       COUNT(*) AS appointments,
       SUM(no_show) AS no_shows,
       ROUND(100.0 * SUM(no_show) / COUNT(*), 1) AS no_show_pct
FROM appointments
GROUP BY lead_band
ORDER BY MIN(lead_days);
"""

# 2.4: month-by-month trend. LAG gives the change from the previous month, in points.
MONTHLY_TREND = """
WITH monthly AS (
    SELECT SUBSTR(appt_date, 1, 7) AS month,
           COUNT(*) AS appointments,
           ROUND(100.0 * SUM(no_show) / COUNT(*), 1) AS no_show_pct
    FROM appointments
    GROUP BY SUBSTR(appt_date, 1, 7)
)
SELECT month,
       appointments,
       no_show_pct,
       ROUND(no_show_pct - LAG(no_show_pct) OVER (ORDER BY month), 1) AS change_pp
FROM monthly
ORDER BY month;
"""

# 2.5: rank clinics inside each city, and compare each clinic with the overall rate.
CITY_RANKS = """
WITH clinic_rates AS (
    SELECT c.clinic_name AS clinic, c.city AS city,
           ROUND(100.0 * SUM(a.no_show) / COUNT(*), 1) AS no_show_pct
    FROM appointments AS a
    JOIN clinics AS c ON c.clinic_id = a.clinic_id
    GROUP BY c.clinic_id, c.clinic_name, c.city
)
SELECT clinic, city, no_show_pct,
       RANK() OVER (PARTITION BY city ORDER BY no_show_pct DESC) AS rank_in_city,
       CASE WHEN no_show_pct > (SELECT ROUND(100.0 * SUM(no_show) / COUNT(*), 2) FROM appointments)
            THEN 'above'
            WHEN no_show_pct < (SELECT ROUND(100.0 * SUM(no_show) / COUNT(*), 2) FROM appointments)
            THEN 'below'
            ELSE 'equal' END AS vs_overall
FROM clinic_rates
ORDER BY city, rank_in_city;
"""

# Used only for the pandas cross-check.
CLINIC_COUNTS = """
SELECT clinic_id, COUNT(*) AS appointments, SUM(no_show) AS no_shows
FROM appointments
GROUP BY clinic_id;
"""


# ---- Running the queries -----------------------------------------------------------

def run_query(connection, sql):
    """Run one query and return the result as a pandas DataFrame."""
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)


def check_against_pandas(connection):
    """Rebuild the clinic counts with groupby and confirm they equal the SQL counts."""
    appointments = pd.read_csv(OUTPUT_DIR / "appointments_clean.csv")
    pandas_counts = (
        appointments.groupby("clinic_id")["no_show"]
        .agg(appointments="size", no_shows="sum")
        .reset_index()
    )
    sql_counts = run_query(connection, CLINIC_COUNTS)
    merged = pandas_counts.merge(sql_counts, on="clinic_id", suffixes=("_pandas", "_sql"))
    matches = (
        (merged["appointments_pandas"] == merged["appointments_sql"].astype(int))
        & (merged["no_shows_pandas"] == merged["no_shows_sql"].astype(int))
    )
    print("Pandas and SQL clinic counts match:", bool(matches.all()))


def main():
    connection = get_connection(DATABASE)
    queries = [
        ("Totals (should be 990 and 218)", TOTALS),
        ("2.2 Clinic rates, 95+ bookings", CLINIC_RATES_95_PLUS),
        ("2.2 Clinic rates, all clinics", CLINIC_RATES_ALL),
        ("2.3 Lead-time bands", LEAD_TIME_BANDS),
        ("2.4 Monthly trend", MONTHLY_TREND),
        ("2.5 Rank within city", CITY_RANKS),
    ]
    for title, sql in queries:
        print(f"\n== {title} ==")
        print(run_query(connection, sql).to_string(index=False))

    print()
    check_against_pandas(connection)
    connection.close()


if __name__ == "__main__":
    main()
