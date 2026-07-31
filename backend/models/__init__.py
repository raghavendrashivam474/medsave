"""
backend/models

Data models for the MedSave backend.

These models represent the shape of data returned by the database.
They are intentionally simple dataclasses used for type clarity.
They are not ORM models. MedSave uses raw SQL with psycopg2/sqlite3.

Current models:
    Medicine — represents a generic medicine record.
    Store    — represents a Jan Aushadhi pharmacy store record.

These models are not yet used throughout the codebase but are
defined here to document the expected data shapes and support
future refactoring toward a service layer.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Medicine:
    """
    Represents a medicine record as returned by the database.

    This is the API layer model. It is separate from the pipeline
    entity (pipeline/entities/medicine.py) which is used internally
    by the data engine.
    """
    brand_name:      str
    generic_name:    str
    salt:            str
    dosage:          str
    form:            str
    brand_price:     float
    generic_price:   float
    savings_percent: float


@dataclass
class Store:
    """
    Represents a pharmacy store record as returned by the database.
    """
    id:           int
    name:         str
    address:      str
    city:         str
    pincode:      str
    lat:          Optional[float]
    lng:          Optional[float]
    distance_km:  Optional[float] = None
