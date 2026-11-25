# Shared helpers and the schema

## `common/paths.py`

Every folder location is defined once here. Scripts use names such as `DATA_DIR` and `OUTPUT_DIR` rather than typing file paths.

- `PROJECT_ROOT` is found from this file's own location, so the project works wherever you put it.
- `OUTPUT_DIR` is created automatically if it does not exist.

## `common/db.py`

Three functions handle the database.

- **`get_connection(database=None)`** opens a connection to MySQL. The host, port and user come from environment variables (`MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`). If `MYSQL_PASSWORD` is not set, the script asks for it with a hidden prompt.
- **`split_statements(sql_text)`** splits a SQL file into single statements. It drops comment lines (those starting with `--`) and splits on `;`. This is safe for our files because no text value contains a semicolon.
- **`run_schema_file(connection, filename)`** reads a file from `schema/` and runs each statement in order.

## `schema/01_create_database.sql`

Creates the `noshowguard` database and switches to it. You can run this file by hand in MySQL Workbench.

## `schema/02_create_tables.sql`

Creates the two tables.

- **`clinics`**: one row per clinic, with a primary key `clinic_id`. `temp_c` can be empty.
- **`appointments`**: one row per booking, with a primary key `appointment_id`. `clinic_id` is a foreign key, so a booking cannot point to a clinic that does not exist.

The `DROP TABLE` lines at the top let you run the file again from scratch. `appointments` is dropped first because it depends on `clinics`.
