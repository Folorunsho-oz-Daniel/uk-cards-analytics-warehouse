"""
load_raw_tables.py

Loads the generated CSV files into the Snowflake RAW schema.

For each table the script:
  1. truncates the table (so re-running never creates duplicates)
  2. uploads the CSV to the table's internal stage (PUT)
  3. bulk-loads it into the table (COPY INTO)
  4. cleans up the staged file
  5. compares the loaded row count with the CSV's row count

Credentials are never stored in this file. Connection settings come
from environment variables, and the password is requested with a
hidden prompt if SNOWFLAKE_PASSWORD is not set (CI sets it as a secret).
"""

import getpass
import os
import sys
from pathlib import Path

import pandas as pd
import snowflake.connector

OUTPUT_DIR = Path("data_generation/output")

# CSV file -> RAW table. Column order in each CSV matches its table.
TABLES = {
    "customers.csv": "CUSTOMERS",
    "accounts.csv": "ACCOUNTS",
    "transactions.csv": "TRANSACTIONS",
    "repayments.csv": "REPAYMENTS",
    "credit_decisions.csv": "CREDIT_DECISIONS",
}

REQUIRED_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
]


def get_connection():
    missing = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        sys.exit(f"Missing environment variables: {', '.join(missing)}")

    password = os.environ.get("SNOWFLAKE_PASSWORD") or getpass.getpass(
        "Snowflake password: "
    )

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=password,
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema="RAW",
    )


def load_table(cursor, csv_path, table):
    """Reloads one RAW table from its CSV. Returns the row count loaded."""
    # Start from an empty table and an empty stage, so the load is repeatable.
    cursor.execute(f"TRUNCATE TABLE {table}")
    cursor.execute(f"REMOVE @%{table}")

    # Upload the file to the table's own internal stage (@%TABLE_NAME).
    # as_posix() gives forward slashes, which Snowflake accepts on Windows.
    file_uri = csv_path.resolve().as_posix()
    cursor.execute(
        f"PUT 'file://{file_uri}' @%{table} AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
    )

    # Bulk-load the staged file. ON_ERROR = ABORT_STATEMENT means any bad
    # row stops the load loudly instead of being silently skipped.
    cursor.execute(
        f"""
        COPY INTO {table}
        FROM @%{table}
        FILE_FORMAT = (
            TYPE = CSV
            SKIP_HEADER = 1
            FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        )
        ON_ERROR = ABORT_STATEMENT
        FORCE = TRUE
        """
    )

    # Remove the staged copy now that it has been loaded.
    cursor.execute(f"REMOVE @%{table}")

    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    return cursor.fetchone()[0]


def main():
    for csv_name in TABLES:
        if not (OUTPUT_DIR / csv_name).exists():
            sys.exit(
                f"{OUTPUT_DIR / csv_name} not found. "
                "Run the data generation scripts first."
            )

    connection = get_connection()
    cursor = connection.cursor()
    mismatches = 0

    try:
        for csv_name, table in TABLES.items():
            csv_path = OUTPUT_DIR / csv_name
            expected = len(pd.read_csv(csv_path, usecols=[0]))
            loaded = load_table(cursor, csv_path, table)

            status = "OK" if loaded == expected else "MISMATCH"
            if loaded != expected:
                mismatches += 1
            print(f"{table:<18} expected {expected:>8,}   loaded {loaded:>8,}   {status}")
    finally:
        cursor.close()
        connection.close()

    if mismatches:
        sys.exit(f"{mismatches} table(s) did not reconcile.")
    print("\nAll tables loaded and reconciled.")


if __name__ == "__main__":
    main()