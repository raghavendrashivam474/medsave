"""
pipeline/loaders/postgres_loader.py

PostgreSQL loader for the MedSave Data Engine.

The loader is the only layer in the pipeline permitted to interact
with the database. All other layers (parsers, normalizers, validators)
operate exclusively on pipeline entities.

Responsibilities (future sprints):
    - Connect to PostgreSQL using the configured DATABASE_URL
    - Insert validated Medicine entities into the medicines table
    - Resolve medicine IDs after insertion
    - Insert validated Brand entities into the brands table
    - Handle duplicates gracefully

This sprint defines the public interface only.
No SQL insertion logic is implemented here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pipeline.entities.medicine import Medicine
    from pipeline.entities.brand import Brand


class PostgresLoader:
    """
    Loads validated pipeline entities into the MedSave PostgreSQL database.

    This class is the single point of contact between the Data Engine
    and the database. Nothing outside this class should construct or
    execute SQL queries.

    Usage (future):
        loader = PostgresLoader(database_url="postgresql://...")
        loader.connect()
        loader.load_medicines(medicines)
        loader.load_brands(brands)
        loader.close()
    """

    def __init__(self, database_url: str) -> None:
        """
        Initialize the loader with a database connection string.

        Args:
            database_url: A fully qualified PostgreSQL connection string.
                          Example: postgresql://user:password@localhost/medsave
        """
        self.database_url = database_url
        self._connection = None

    def connect(self) -> None:
        """
        Establish a connection to the PostgreSQL database.

        Not implemented in Sprint 2.1.

        Raises:
            NotImplementedError: Always. Implementation pending.
        """
        raise NotImplementedError(
            "PostgresLoader.connect() is not yet implemented. "
            "This will be built in Sprint 2.2."
        )

    def load_medicines(self, medicines: list[Medicine]) -> None:
        """
        Insert a list of Medicine entities into the medicines table.

        Duplicate handling and ID resolution will be implemented
        in a future sprint.

        Args:
            medicines: A list of validated Medicine entities.

        Raises:
            NotImplementedError: Always. Implementation pending.
        """
        raise NotImplementedError(
            "PostgresLoader.load_medicines() is not yet implemented. "
            "This will be built in Sprint 2.2."
        )

    def load_brands(self, brands: list[Brand]) -> None:
        """
        Insert a list of Brand entities into the brands table.

        Brand insertion requires that the corresponding Medicine
        records already exist so that foreign key IDs can be resolved.

        Args:
            brands: A list of validated Brand entities.

        Raises:
            NotImplementedError: Always. Implementation pending.
        """
        raise NotImplementedError(
            "PostgresLoader.load_brands() is not yet implemented. "
            "This will be built in Sprint 2.2."
        )

    def close(self) -> None:
        """
        Close the database connection cleanly.

        Not implemented in Sprint 2.1.

        Raises:
            NotImplementedError: Always. Implementation pending.
        """
        raise NotImplementedError(
            "PostgresLoader.close() is not yet implemented. "
            "This will be built in Sprint 2.2."
        )
