"""Task 2.1: create the database from schema/ and load outputs/load_data.sql into MySQL.

Steps:
  1. Run schema/01_create_database.sql (creates the database).
  2. Run schema/02_create_tables.sql (creates the two tables).
  3. Run each INSERT in outputs/load_data.sql.
  4. Try a duplicate appointment_id to show the error MySQL returns.

Set your MySQL login first (see .env.example), then from the project folder run:
    python -m part2_mysql.load_database
"""
import pymysql

from common.db import get_connection, run_schema_file
from common.paths import OUTPUT_DIR

DATABASE = "noshowguard"


def create_schema():
    """Create the database, then the tables. Returns a connection to the new database."""
    server_connection = get_connection()
    run_schema_file(server_connection, "01_create_database.sql")
    server_connection.close()

    database_connection = get_connection(DATABASE)
    run_schema_file(database_connection, "02_create_tables.sql")
    return database_connection


def load_rows(connection):
    """Run every INSERT in load_data.sql. Each line of that file is one statement."""
    lines = (OUTPUT_DIR / "load_data.sql").read_text(encoding="utf-8").splitlines()
    with connection.cursor() as cursor:
        for line in lines:
            if line.strip():
                cursor.execute(line)
    connection.commit()
    return len([line for line in lines if line.strip()])


def show_duplicate_key_error(connection):
    """Insert a second row with an existing ID and print the error (task 2.1).

    MySQL 8 reports: ERROR 1062 (23000): Duplicate entry 'A0001' for key 'appointments.PRIMARY'
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO appointments (appointment_id, patient_id, clinic_id) "
                "VALUES ('A0001', 'P999', 'C01')"
            )
        connection.commit()
        print("Unexpected: the duplicate insert worked")
    except pymysql.err.IntegrityError as error:
        connection.rollback()
        print("Duplicate insert was rejected, as expected:")
        print(" ", error)


def main():
    connection = create_schema()
    count = load_rows(connection)
    print(f"Loaded {count} INSERT statements")
    show_duplicate_key_error(connection)
    connection.close()


if __name__ == "__main__":
    main()
