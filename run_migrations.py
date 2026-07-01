'''run_migrations.py'''
"""
Executes all *.sql files in Database/migrations in alphanumeric order.
Uses the project's existing psycopg2 connection pool (src.db.connection).
"""
import pathlib
import sys

# Ensure the project root is on PYTHONPATH for imports
sys.path.append(str(pathlib.Path(__file__).parent))

from src.db.connection import get_connection

MIGRATION_DIR = pathlib.Path(__file__).parent / "Database" / "migrations"

def apply_sql_file(sql_path: pathlib.Path):
    print(f"Applying {sql_path.name} …")
    sql = sql_path.read_text()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
    print("Done")

def main():
    for sql_file in sorted(MIGRATION_DIR.glob("*.sql")):
        apply_sql_file(sql_file)

if __name__ == "__main__":
    main()
