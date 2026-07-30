"""
pipeline/entities/medicine.py

Represents a generic medicine in the MedSave pipeline.

This entity is the internal data model used throughout the pipeline.
It is intentionally decoupled from the database schema.
Database IDs, foreign keys, and SQL concerns belong to the loader layer.
"""

from dataclasses import dataclass


@dataclass
class Medicine:
    """
    Represents a generic medicine as understood by the Data Engine.

    Attributes:
        generic_name: The generic/scientific name of the medicine.
        salt:         The active pharmaceutical ingredient (API).
        dosage:       Strength of the medicine (e.g. 500mg, 10mg).
        form:         Physical form (e.g. Tablet, Capsule, Syrup).
        jan_price:    Price listed under the Jan Aushadhi scheme (in INR).
    """

    generic_name: str
    salt: str
    dosage: str
    form: str
    jan_price: float

    def __post_init__(self) -> None:
        if not self.generic_name:
            raise ValueError("generic_name cannot be empty.")
        if not self.salt:
            raise ValueError("salt cannot be empty.")
        if not self.dosage:
            raise ValueError("dosage cannot be empty.")
        if not self.form:
            raise ValueError("form cannot be empty.")
        if self.jan_price < 0:
            raise ValueError("jan_price cannot be negative.")
