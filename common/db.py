"""Connecting to MySQL and running SQL files.

Credentials come from environment variables, never from the code. If MYSQL_PASSWORD
is not set, the script asks for it, so the password is never saved in a file.
"""
import getpass
import os

import pymysql

from common.paths import SCHEMA_DIR

DEFAULT_DATABASE = None


def get_connection(database=DEFAULT_DATABASE):
    """Open a connection to the MySQL server (and to one database, if given)."""
    password = os.environ.get("MYSQL_PASSWORD") or getpass.getpass("MySQL password: ")
    return pymysql.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ.get("MYSQL_USER", "root"),
        password=password,
        database=database,
    )


def split_statements(sql_text):
    """Split a SQL file into single statements.

    Comment lines (starting with --) are removed first. Splitting on ';' is safe here
    because none of our SQL text values contain a semicolon.
    """
    lines = [line for line in sql_text.splitlines() if not line.strip().startswith("--")]
    statements = "\n".join(lines).split(";")
    return [statement.strip() for statement in statements if statement.strip()]


def run_schema_file(connection, filename):
    """Run every statement in one file from the schema/ folder."""
    sql_text = (SCHEMA_DIR / filename).read_text(encoding="utf-8")
    with connection.cursor() as cursor:
        for statement in split_statements(sql_text):
            cursor.execute(statement)
    connection.commit()
