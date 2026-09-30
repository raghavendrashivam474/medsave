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

    - Medicine = (generic_name, dosage)
    - Brand = (brand_name, generic_id)

Brand-to-medicine resolution:

    - Brands are resolved using (generic_name, dosage)
    - This preserves dosage-specific brand relationships

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

        # Medicine identity:
        # (generic_name, dosage) -> database ID
        self._medicine_id_map: dict[tuple[str, str], int] = {}

        self._backend = (
            "postgres" if _is_postgres(database_url) else "sqlite"
        )

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
    # Medicine loading
    # ------------------------------------------------------------------

    def load_medicines(self, medicines: list[Medicine]) -> None:
        logger.info("Loading %d medicines (additive)", len(medicines))

        cursor = self._conn.cursor()

        # Step 1: Load existing medicines into memory.
        #
        # Medicine identity is:
        # (generic_name, dosage)
        cursor.execute(
            "SELECT id, generic_name, dosage FROM medicines"
        )

        for row in cursor.fetchall():
            key = (row[1], row[2])
            self._medicine_id_map[key] = row[0]

        existing_count = len(self._medicine_id_map)

        logger.info(
            "Existing medicines in database: %d",
            existing_count,
        )

        # Step 2: Deduplicate incoming medicines by:
        # (generic_name, dosage)
        seen_in_batch: dict[tuple[str, str], Medicine] = {}

        for medicine in medicines:
            key = (
                medicine.generic_name,
                medicine.dosage,
            )

            if key not in seen_in_batch:
                seen_in_batch[key] = medicine

        # Step 3: Filter out medicines already present.
        new_medicines = [
            medicine
            for key, medicine in seen_in_batch.items()
            if key not in self._medicine_id_map
        ]

        skipped = (
            len(seen_in_batch) - len(new_medicines)
        )

        logger.info(
            "New medicines to insert: %d "
            "(skipped as duplicates: %d)",
            len(new_medicines),
            skipped,
        )

        # Step 4: Insert only new medicines.
        if new_medicines:
            placeholder = (
                "?"
                if self._backend == "sqlite"
                else "%s"
            )

            sql = (
                "INSERT INTO medicines "
                "(generic_name, salt, dosage, form, jan_price) "
                f"VALUES ({placeholder}, {placeholder}, "
                f"{placeholder}, {placeholder}, {placeholder})"
            )

            cursor.executemany(
                sql,
                [
                    (
                        medicine.generic_name,
                        medicine.salt,
                        medicine.dosage,
                        medicine.form,
                        medicine.jan_price,
                    )
                    for medicine in new_medicines
                ],
            )

        # Step 5: Rebuild the medicine ID map.
        #
        # This is required so brands loaded immediately afterward
        # can resolve their foreign keys.
        cursor.execute(
            "SELECT id, generic_name, dosage FROM medicines"
        )

        self._medicine_id_map = {}

        for row in cursor.fetchall():
            self._medicine_id_map[
                (row[1], row[2])
            ] = row[0]

        logger.info(
            "Medicines inserted: %d, total in database: %d",
            len(new_medicines),
            len(self._medicine_id_map),
        )

    # ------------------------------------------------------------------
    # Brand loading
    # ------------------------------------------------------------------

    def load_brands(self, brands: list[Brand]) -> None:
        logger.info(
            "Loading %d brands (additive)",
            len(brands),
        )

        cursor = self._conn.cursor()

        # Step 1: Load existing brands for duplicate detection.
        #
        # Database-level brand identity remains:
        # (brand_name, generic_id)
        cursor.execute(
            "SELECT brand_name, generic_id FROM brands"
        )

        existing_brands: set[tuple[str, int]] = set()

        for row in cursor.fetchall():
            existing_brands.add(
                (row[0], row[1])
            )

        logger.info(
            "Existing brands in database: %d",
            len(existing_brands),
        )

        # Step 2: Resolve each brand against the exact
        # (generic_name, dosage) medicine identity.
        #
        # This is the critical dosage-aware relationship.
        new_rows: list[tuple[str, int, float]] = []

        seen_in_batch: set[tuple[str, int]] = set()

        skipped_missing = 0
        skipped_duplicate = 0

        for brand in brands:
            medicine_key = (
                brand.generic_name,
                brand.dosage,
            )

            medicine_id = self._medicine_id_map.get(
                medicine_key
            )

            if medicine_id is None:
                skipped_missing += 1

                logger.warning(
                    "Skipping brand '%s': medicine not found "
                    "for %s %s",
                    brand.brand_name,
                    brand.generic_name,
                    brand.dosage,
                )

                continue

            brand_key = (
                brand.brand_name,
                medicine_id,
            )

            if (
                brand_key in existing_brands
                or brand_key in seen_in_batch
            ):
                skipped_duplicate += 1
                continue

            seen_in_batch.add(brand_key)

            new_rows.append(
                (
                    brand.brand_name,
                    medicine_id,
                    brand.mrp,
                )
            )

        logger.info(
            "New brands to insert: %d "
            "(duplicate: %d, missing medicine: %d)",
            len(new_rows),
            skipped_duplicate,
            skipped_missing,
        )

        # Step 3: Insert only new brands.
        if new_rows:
            placeholder = (
                "?"
                if self._backend == "sqlite"
                else "%s"
            )

            sql = (
                "INSERT INTO brands "
                "(brand_name, generic_id, mrp) "
                f"VALUES ({placeholder}, {placeholder}, "
                f"{placeholder})"
            )

            cursor.executemany(
                sql,
                new_rows,
            )

        logger.info(
            "Brands inserted: %d",
            len(new_rows),
        )