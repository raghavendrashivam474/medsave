"""
pipeline/entities/brand.py

Represents a branded medicine in the MedSave pipeline.

Branded medicines reference their generic counterpart by name, not by
database ID. ID resolution is the responsibility of the loader layer.
"""

from dataclasses import dataclass


@dataclass
class Brand:
    """
    Represents a branded medicine as understood by the Data Engine.

    Attributes:
        brand_name:   The commercial name of the medicine.
        generic_name: The generic medicine this brand corresponds to.
                      Stored as a name here. The loader resolves the ID.
        mrp:          Maximum Retail Price of the branded medicine (in INR).
    """

    brand_name: str
    generic_name: str
    mrp: float

    def __post_init__(self) -> None:
        if not self.brand_name:
            raise ValueError("brand_name cannot be empty.")
        if not self.generic_name:
            raise ValueError("generic_name cannot be empty.")
        if self.mrp < 0:
            raise ValueError("mrp cannot be negative.")
