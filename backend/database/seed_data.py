"""
backend/database/seed_data.py

Seeds the MedSave database with demonstration data.

Supports both PostgreSQL (production) and SQLite (local development).
Backend is selected automatically from the DATABASE_URL environment variable.

This script:
    1. Reads and executes schema.sql to create all tables.
    2. Inserts sample medicines, brands, and stores.

Schema version: v0.5.0

Changes from v0.4.0:
    - medicines table now includes manufacturer, therapeutic_category, schedule
      columns (all nullable — seed data leaves them NULL for now).
    - brands table now includes manufacturer column (nullable).
    - stores table now includes state and phone columns.
      Seed data includes state for all sample stores.
      Phone is left NULL (not available for demonstration data).

SQLite compatibility:
    - schema.sql uses PostgreSQL SERIAL syntax.
    - SQLite uses INTEGER PRIMARY KEY for autoincrement.
    - This script rewrites SERIAL to INTEGER PRIMARY KEY when running SQLite.
    - COMMENT ON statements are stripped (SQLite does not support them).
    - CHECK constraints are stripped (limited SQLite support).
    - CREATE INDEX IF NOT EXISTS is supported in SQLite 3.3.0+.

Usage:
    python backend/database/seed_data.py
"""

import os
import re
import sqlite3

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def _is_postgres(url: str) -> bool:
    """
    Determine whether DATABASE_URL points to a live PostgreSQL instance.
    Mirrors the detection logic in backend/database/connection.py.
    """
    return (
        bool(url)
        and "postgresql://" in url
        and "@host:" not in url
    )


def _adapt_schema_for_sqlite(schema_sql: str) -> str:
    """
    Adapt PostgreSQL schema.sql syntax to SQLite-compatible syntax.

    Transformations applied:
        - SERIAL PRIMARY KEY  -> INTEGER PRIMARY KEY
        - COMMENT ON ...      -> removed (SQLite does not support)
        - CHECK constraints   -> removed (SQLite support is limited)
        - FLOAT               -> REAL  (SQLite type affinity)

    Returns the adapted SQL string.
    """
    sql = schema_sql

    # Replace SERIAL PRIMARY KEY with SQLite equivalent
    sql = sql.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY")

    # Remove COMMENT ON lines entirely
    sql = re.sub(r"COMMENT ON [^\n]+;\n?", "", sql)

    # Remove CHECK constraints inline within column definitions
    # Matches: CHECK (expression) including nested parens
    sql = re.sub(r"\s*CHECK\s*\([^)]+\)", "", sql)

    # SQLite uses REAL not FLOAT (both work but REAL is canonical)
    sql = sql.replace(" FLOAT", " REAL")

    return sql


def seed():
    """
    Create all tables and insert demonstration data.

    Connects to PostgreSQL or SQLite based on DATABASE_URL.
    Reads schema.sql from the same directory as this file.
    Inserts sample medicines, brands, and stores.
    """
    database_url = os.getenv("DATABASE_URL", "")
    is_postgres = _is_postgres(database_url)

    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

    if is_postgres:
        print("Seeding PostgreSQL database...")
        conn = psycopg2.connect(database_url)
        param_marker = "%s"
    else:
        print("Seeding local SQLite database...")
        db_path = os.path.join(os.path.dirname(__file__), "database.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        param_marker = "?"

    cur = conn.cursor()

    # ------------------------------------------------------------------
    # Apply schema
    # ------------------------------------------------------------------

    with open(schema_path, "r") as f:
        schema_sql = f.read()

    if is_postgres:
        cur.execute(schema_sql)
    else:
        adapted = _adapt_schema_for_sqlite(schema_sql)
        cur.executescript(adapted)

    # ------------------------------------------------------------------
    # Sample medicines (Jan Aushadhi generics)
    #
    # Column order matches schema v0.5.0:
    #     generic_name, salt, dosage, form, jan_price
    #
    # New nullable columns (manufacturer, therapeutic_category, schedule)
    # are not included in the INSERT — they default to NULL.
    # This preserves compatibility with the pipeline loader pattern.
    # ------------------------------------------------------------------

    medicines = [
        ("Paracetamol",   "Paracetamol",                "500MG", "Tablet",  10.0),
        ("Amoxicillin",   "Amoxicillin",                "250MG", "Capsule", 25.0),
        ("Metformin",     "Metformin Hydrochloride",     "500MG", "Tablet",  15.0),
        ("Atorvastatin",  "Atorvastatin",                "10MG",  "Tablet",  20.0),
        ("Azithromycin",  "Azithromycin",                "500MG", "Tablet",  45.0),
        ("Cetirizine",    "Cetirizine Hydrochloride",    "10MG",  "Tablet",   5.0),
        ("Omeprazole",    "Omeprazole",                  "20MG",  "Capsule", 12.0),
        ("Amlodipine",    "Amlodipine Besylate",         "5MG",   "Tablet",   8.0),
    ]

    cur.executemany(
        f"INSERT INTO medicines (generic_name, salt, dosage, form, jan_price) "
        f"VALUES ({param_marker}, {param_marker}, {param_marker}, "
        f"{param_marker}, {param_marker})",
        medicines,
    )

    # ------------------------------------------------------------------
    # Sample brands
    #
    # Column order: brand_name, generic_id, mrp
    #
    # New nullable column (manufacturer) is not included in the INSERT.
    # ------------------------------------------------------------------

    brands = [
        ("Crocin",    1, 35.0),
        ("Dolo 650",  1, 30.0),
        ("Calpol",    1, 32.0),
        ("Mox",       2, 75.0),
        ("Novamox",   2, 80.0),
        ("Glycomet",  3, 55.0),
        ("Lipitor",   4, 120.0),
        ("Atorva",    4, 90.0),
        ("Azithral",  5, 150.0),
        ("Zyrtec",    6, 25.0),
        ("Omez",      7, 60.0),
        ("Amlokind",  8, 45.0),
    ]

    cur.executemany(
        f"INSERT INTO brands (brand_name, generic_id, mrp) "
        f"VALUES ({param_marker}, {param_marker}, {param_marker})",
        brands,
    )

    # ------------------------------------------------------------------
    # Sample stores
    #
    # Column order: name, address, city, pincode, lat, lng, state
    #
    # New column (phone) is not included — NULL for demonstration data.
    # State is included — it is known for all sample stores.
    # ------------------------------------------------------------------

    stores = [
        (
            "Jan Aushadhi Kendra - Sector 12",
            "Shop 4, Huda Market, Sector 12",
            "Noida", "201301", 28.59, 77.34,
            "Uttar Pradesh",
        ),
        (
            "Generic Pharma Plus",
            "Main Road, Karkarduma",
            "Delhi", "110092", 28.64, 77.30,
            "Delhi",
        ),
        (
            "Affordable Meds Kendra",
            "G-6, Lajpat Nagar II",
            "Delhi", "110024", 28.56, 77.24,
            "Delhi",
        ),
        (
            "Jan Aushadhi Store - Andheri East",
            "Marol Pipe Line, JB Nagar",
            "Mumbai", "400059", 19.11, 72.87,
            "Maharashtra",
        ),
    ]

    cur.executemany(
        f"INSERT INTO stores (name, address, city, pincode, lat, lng, state) "
        f"VALUES ({param_marker}, {param_marker}, {param_marker}, "
        f"{param_marker}, {param_marker}, {param_marker}, {param_marker})",
        stores,
    )

    conn.commit()
    cur.close()
    conn.close()

    print("Database seeded successfully.")
    print(f"  Medicines : {len(medicines)}")
    print(f"  Brands    : {len(brands)}")
    print(f"  Stores    : {len(stores)}")


if __name__ == "__main__":
    seed()
