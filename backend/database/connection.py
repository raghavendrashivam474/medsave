"""
backend/database/connection.py

Shared database connection factory for the MedSave Flask backend.

Supports both SQLite (local development) and PostgreSQL (production).
Backend is selected automatically from the DATABASE_URL environment variable.

All API modules import get_db_connection() from this module.
Connection logic is never duplicated across routes.

Usage:
    from backend.database.connection import get_db_connection

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(...)
        results = cur.fetchall()
    finally:
        conn.close()
"""

import os
import sqlite3

import psycopg2
from psycopg2.extras import RealDictCursor


def _is_postgres(url: str) -> bool:
    """
    Determine whether the DATABASE_URL points to a live PostgreSQL instance.

    Returns False for placeholder URLs containing '@host:' which are used
    in documentation examples and are not real connections.
    """
    return (
        bool(url)
        and "postgresql://" in url
        and "@host:" not in url
    )


def get_db_connection():
    """
    Return an open database connection.

    Automatically selects PostgreSQL or SQLite based on DATABASE_URL.

    For PostgreSQL connections, RealDictCursor is applied so that all
    rows are returned as dictionaries keyed by column name.

    For SQLite connections, sqlite3.Row is applied for the same effect.

    The caller is responsible for closing the connection.

    Returns:
        An open psycopg2 connection (PostgreSQL) or sqlite3 connection (SQLite).

    Raises:
        psycopg2.OperationalError: If PostgreSQL connection fails.
        sqlite3.OperationalError:  If SQLite database cannot be opened.
    """
    database_url = os.getenv("DATABASE_URL", "")

    if _is_postgres(database_url):
        return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

    # SQLite fallback — resolve path relative to this file
    db_path = os.path.join(os.path.dirname(__file__), "..", "database.db")
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
