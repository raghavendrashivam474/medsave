"""
backend/models

Data models for the MedSave backend.

These models represent the shape of data returned by the database.
They are intentionally simple dataclasses used for type clarity.
They are not ORM models. MedSave uses raw SQL with psycopg2/sqlite3.

Current models:
    Medicine — represents a generic medicine record as returned by search.
    Store    — represents a Jan Aushadhi pharmacy store record.

Schema version: v0.5.0

Changes from v0.4.0:
    Medicine:
        No changes to the search response shape. The search API returns
        a joined view across medicines and brands. The new nullable columns
        (manufacturer, therapeutic_category, schedule) are not yet exposed
        through the search endpoint. They will be surfaced in a future
        milestone when the medicine detail endpoint is implemented.

    Store:
        Added state and phone fields matching the new schema columns.
        Both are Optional — existing store records may not have this data.

These models are not yet used throughout the codebase but are
defined here to document the expected data shapes and support
future refactoring toward a service layer.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Medicine:
    """
    Represents a medicine record as returned by the search API.

    This is the API layer model. It reflects the joined view produced
    by the search query across the brands and medicines tables.

    It is separate from the pipeline entity (pipeline/entities/medicine.py)
    which is used internally by the Data Engine.

    Note:
        The new schema v0.5.0 columns (manufacturer, therapeutic_category,
        schedule) are not yet included here. They will be added when a
        medicine detail endpoint is implemented in a future milestone.
    """
    brand_name:           str
    generic_name:         str
    salt:                 str
    dosage:               str
    form:                 str
    brand_price:          float
    generic_price:        float
    savings_percent:      float


@dataclass
class Store:
    """
    Represents a pharmacy store record as returned by the stores API.

    Schema v0.5.0 additions:
        state — Indian state name. Nullable. Populated during Phase 4.
        phone — Contact phone number. Nullable. Populated during Phase 4.

    All new fields are Optional to preserve compatibility with existing
    store records that pre-date the v0.5.0 schema migration.
    """
    id:           int
    name:         str
    address:      str
    city:         str
    pincode:      str
    lat:          Optional[float]
    lng:          Optional[float]
    state:        Optional[str]  = None
    phone:        Optional[str]  = None
    distance_km:  Optional[float] = None
