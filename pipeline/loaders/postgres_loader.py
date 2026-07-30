"""
pipeline/loaders/postgres_loader.py

Database loader for the MedSave Data Engine.

Supports both SQLite (local development) and PostgreSQL/Supabase (production).
Backend selection mirrors backend/seed_data.py logic.

This loader is additive and idempotent:
    - Existing medicines and brands are never deleted
    - Duplicates are detected in Python before insertion
    - Re-running the pipeline on the same source is a no-op
    - Running the pipeline on new sources adds only truly new records

Duplicate detection:
    - Medicine  = (generic_name, dosage)
    - Brand     = (brand_name, generic_id)

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

    Additive and idempotent. Never deletes existing data.
    Backend chosen automatically from DATABASE_URL scheme.
    """

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self._conn = None
        self._medicine_id_map: dict[tuple[str, str], int] = {}
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
        logger.info("Loading %d medicines (additive)", len(medicines))

        cursor = self._conn.cursor()

        # Step 1: Load existing medicines into memory for duplicate detection
        cursor.execute("SELECT id, generic_name, dosage FROM medicines")
        for row in cursor.fetchall():
            key = (row[1], row[2])
            self._medicine_id_map[key] = row[0]

        existing_count = len(self._medicine_id_map)
        logger.info("Existing medicines in database: %d", existing_count)

        # Step 2: Deduplicate incoming medicines by (generic_name, dosage)
        seen_in_batch: dict[tuple[str, str], Medicine] = {}
        for m in medicines:
            key = (m.generic_name, m.dosage)
            if key not in seen_in_batch:
                seen_in_batch[key] = m

        # Step 3: Filter out ones that already exist in database
        new_medicines = [
            m for key, m in seen_in_batch.items()
            if key not in self._medicine_id_map
        ]

        skipped = len(seen_in_batch) - len(new_medicines)
        logger.info(
            "New medicines to insert: %d (skipped as duplicates: %d)",
            len(new_medicines), skipped
        )

        # Step 4: Insert only the new ones
        if new_medicines:
            placeholder = "?" if self._backend == "sqlite" else "%s"
            sql = (
                "INSERT INTO medicines "
                "(generic_name, salt, dosage, form, jan_price) "
                f"VALUES ({placeholder}, {placeholder}, {placeholder}, "
                f"{placeholder}, {placeholder})"
            )
            cursor.executemany(
                sql,
                [
                    (m.generic_name, m.salt, m.dosage, m.form, m.jan_price)
                    for m in new_medicines
                ]
            )

        # Step 5: Rebuild id map so brands can resolve foreign keys
        cursor.execute("SELECT id, generic_name, dosage FROM medicines")
        self._medicine_id_map = {}
        for row in cursor.fetchall():
            self._medicine_id_map[(row[1], row[2])] = row[0]

        logger.info(
            "Medicines inserted: %d, total in database: %d",
            len(new_medicines), len(self._medicine_id_map)
        )

    def load_brands(self, brands: list[Brand]) -> None:
        logger.info("Loading %d brands (additive)", len(brands))

        cursor = self._conn.cursor()

        # Step 1: Load existing brands for duplicate detection
        cursor.execute("SELECT brand_name, generic_id FROM brands")
        existing_brands: set[tuple[str, int]] = set()
        for row in cursor.fetchall():
            existing_brands.add((row[0], row[1]))

        logger.info("Existing brands in database: %d", len(existing_brands))

        # Step 2: Build candidate brand rows, resolving generic_id
        # We resolve by generic_name alone. If multiple dosages exist for
        # the same generic, pick the first — brand rows in the source
        # dataset are keyed to generic_name only.
        generic_name_to_id: dict[str, int] = {}
        for (generic_name, _dosage), medicine_id in self._medicine_id_map.items():
            generic_name_to_id.setdefault(generic_name, medicine_id)

        new_rows: list[tuple[str, int, float]] = []
        seen_in_batch: set[tuple[str, int]] = set()
        skipped_missing = 0
        skipped_duplicate = 0

        for brand in brands:
            generic_id = generic_name_to_id.get(brand.generic_name)
            if generic_id is None:
                skipped_missing += 1
                continue

            key = (brand.brand_name, generic_id)
            if key in existing_brands or key in seen_in_batch:
                skipped_duplicate += 1
                continue

            seen_in_batch.add(key)
            new_rows.append((brand.brand_name, generic_id, brand.mrp))

        logger.info(
            "New brands to insert: %d (duplicate: %d, missing generic: %d)",
            len(new_rows), skipped_duplicate, skipped_missing
        )

        # Step 3: Insert only new brands
        if new_rows:
            placeholder = "?" if self._backend == "sqlite" else "%s"
            sql = (
                "INSERT INTO brands (brand_name, generic_id, mrp) "
                f"VALUES ({placeholder}, {placeholder}, {placeholder})"
            )
            cursor.executemany(sql, new_rows)

        logger.info("Brands inserted: %d", len(new_rows))
