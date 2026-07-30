"""
pipeline/loaders/postgres_loader.py

Database loader for the MedSave Data Engine.

Supports both SQLite (local development) and PostgreSQL/Supabase (production).
Backend selection mirrors backend/seed_data.py logic to guarantee that
the pipeline writes to the same database the Flask API reads from.

This is the only layer in the pipeline permitted to execute SQL.
"""

from __future__ import annotations

import sqlite3

from pipeline.entities import Medicine, Brand
from pipeline.logger import get_logger

logger = get_logger(__name__)


def _is_postgres(url: str) -> bool:
    """Match the detection logic used in backend/seed_data.py."""
    return bool(url) and "postgresql://" in url and "@host:" not in url


class PostgresLoader:
    """
    Loads Medicine and Brand entities into the MedSave database.

    Despite the name, this loader supports both SQLite and PostgreSQL.
    The backend is chosen based on the DATABASE_URL scheme, mirroring
    the detection logic in backend/seed_data.py.
    """

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self._conn = None
        self._medicine_id_map: dict[str, int] = {}
        self._backend = "postgres" if _is_postgres(database_url) else "sqlite"
        logger.info("Loader backend selected: %s", self._backend)

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self) -> None:
        logger.info("Connecting to database")

        if self._backend == "sqlite":
            path = self.database_url.replace("sqlite:///", "")
            self._conn = sqlite3.connect(path)
        else:
            import psycopg2
            self._conn = psycopg2.connect(self.database_url)

        logger.info("Connection established")

    def commit(self) -> None:
        self._conn.commit()
        logger.info("Transaction committed")

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            logger.info("Connection closed")

    # ------------------------------------------------------------------
    # Load operations
    # ------------------------------------------------------------------

    def load_medicines(self, medicines: list[Medicine]) -> None:
        logger.info("Loading %d medicines", len(medicines))

        cursor = self._conn.cursor()

        # Wipe existing data so pipeline is idempotent
        cursor.execute("DELETE FROM brands")
        cursor.execute("DELETE FROM medicines")

        # Deduplicate by generic_name so brand mapping works cleanly
        seen: dict[str, Medicine] = {}
        for m in medicines:
            if m.generic_name not in seen:
                seen[m.generic_name] = m
        unique_medicines = list(seen.values())

        if self._backend == "sqlite":
            cursor.executemany(
                """
                INSERT INTO medicines (generic_name, salt, dosage, form, jan_price)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (m.generic_name, m.salt, m.dosage, m.form, m.jan_price)
                    for m in unique_medicines
                ]
            )
            cursor.execute("SELECT id, generic_name FROM medicines")
            for row in cursor.fetchall():
                self._medicine_id_map[row[1]] = row[0]

        else:
            from psycopg2.extras import execute_values
            result = execute_values(
                cursor,
                """
                INSERT INTO medicines (generic_name, salt, dosage, form, jan_price)
                VALUES %s
                RETURNING id, generic_name
                """,
                [
                    (m.generic_name, m.salt, m.dosage, m.form, m.jan_price)
                    for m in unique_medicines
                ],
                fetch=True
            )
            self._medicine_id_map = {row[1]: row[0] for row in result}

        logger.info("Medicines inserted: %d", len(self._medicine_id_map))

    def load_brands(self, brands: list[Brand]) -> None:
        logger.info("Loading %d brands", len(brands))

        rows = []
        skipped_missing = 0
        for brand in brands:
            generic_id = self._medicine_id_map.get(brand.generic_name)
            if generic_id is None:
                skipped_missing += 1
                continue
            rows.append((brand.brand_name, generic_id, brand.mrp))

        # Honor UNIQUE (brand_name, generic_id) constraint
        rows = list({(r[0], r[1]): r for r in rows}.values())

        cursor = self._conn.cursor()

        if self._backend == "sqlite":
            cursor.executemany(
                """
                INSERT OR IGNORE INTO brands (brand_name, generic_id, mrp)
                VALUES (?, ?, ?)
                """,
                rows
            )
        else:
            from psycopg2.extras import execute_values
            execute_values(
                cursor,
                """
                INSERT INTO brands (brand_name, generic_id, mrp)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                rows
            )

        logger.info(
            "Brands inserted: %d (missing generic: %d)",
            len(rows), skipped_missing
        )
