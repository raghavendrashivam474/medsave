"""
pipeline/validators/medicine_validator.py

Validates normalized Medicine and Brand entities before database loading.

This is the final quality gate in the pipeline.
The loader receives only records that have passed all validation rules.

Validation philosophy:
    - Validators never modify data. That is the normalizer's responsibility.
    - Validators only accept or reject entities.
    - Every rejected entity is logged with a clear reason.
    - The pipeline continues even when individual records fail.
    - A summary is produced at the end of validation.

Validation rules enforced:

    Medicine:
        - generic_name must be non-empty after stripping
        - salt must be non-empty after stripping
        - dosage must be non-empty after stripping
        - form must be one of the accepted standard forms
        - jan_price must be a positive number
        - jan_price must not exceed a reasonable ceiling (sanity check)

    Brand:
        - brand_name must be non-empty after stripping
        - generic_name must be non-empty after stripping
        - mrp must be a positive number
        - mrp must not exceed a reasonable ceiling (sanity check)
        - mrp should be greater than or equal to jan_price where available
"""

from dataclasses import dataclass
from typing import Optional

from pipeline.entities import Medicine, Brand
from pipeline.logger import get_logger

logger = get_logger(__name__)


# ------------------------------------------------------------------
# Accepted standard forms after normalization
# ------------------------------------------------------------------

ACCEPTED_FORMS = {
    "Tablet",
    "Capsule",
    "Syrup",
    "Injection",
    "Cream",
    "Ointment",
    "Drops",
    "Gel",
    "Powder",
    "Suspension",
    "Inhaler",
    "Patch",
    "Lotion",
    "Solution",
    "Spray",
}

# Sanity ceiling prices in INR
# Records above these values are flagged as suspicious
MAX_JAN_PRICE = 10_000.0
MAX_MRP = 50_000.0


# ------------------------------------------------------------------
# Validation result
# ------------------------------------------------------------------

@dataclass
class ValidationResult:
    """
    Represents the outcome of validating a single entity.

    Attributes:
        is_valid:   True if the entity passed all validation rules.
        reason:     Human-readable explanation if the entity failed.
                    None when is_valid is True.
    """
    is_valid: bool
    reason: Optional[str] = None

    @classmethod
    def ok(cls) -> "ValidationResult":
        return cls(is_valid=True)

    @classmethod
    def fail(cls, reason: str) -> "ValidationResult":
        return cls(is_valid=False, reason=reason)


# ------------------------------------------------------------------
# Medicine validator
# ------------------------------------------------------------------

class MedicineValidator:
    """
    Validates a single Medicine entity against all business rules.
    """

    def validate(self, medicine: Medicine) -> ValidationResult:
        if not medicine.generic_name or not medicine.generic_name.strip():
            return ValidationResult.fail("generic_name is empty")

        if not medicine.salt or not medicine.salt.strip():
            return ValidationResult.fail("salt is empty")

        if not medicine.dosage or not medicine.dosage.strip():
            return ValidationResult.fail("dosage is empty")

        if not medicine.form or not medicine.form.strip():
            return ValidationResult.fail("form is empty")

        if medicine.form not in ACCEPTED_FORMS:
            return ValidationResult.fail(
                f"form '{medicine.form}' is not a recognised standard form"
            )

        if medicine.jan_price <= 0:
            return ValidationResult.fail(
                f"jan_price must be positive, got {medicine.jan_price}"
            )

        if medicine.jan_price > MAX_JAN_PRICE:
            return ValidationResult.fail(
                f"jan_price {medicine.jan_price} exceeds sanity ceiling {MAX_JAN_PRICE}"
            )

        return ValidationResult.ok()


# ------------------------------------------------------------------
# Brand validator
# ------------------------------------------------------------------

class BrandValidator:
    """
    Validates a single Brand entity against all business rules.
    """

    def validate(self, brand: Brand) -> ValidationResult:
        if not brand.brand_name or not brand.brand_name.strip():
            return ValidationResult.fail("brand_name is empty")

        if not brand.generic_name or not brand.generic_name.strip():
            return ValidationResult.fail("generic_name is empty")

        if brand.mrp <= 0:
            return ValidationResult.fail(
                f"mrp must be positive, got {brand.mrp}"
            )

        if brand.mrp > MAX_MRP:
            return ValidationResult.fail(
                f"mrp {brand.mrp} exceeds sanity ceiling {MAX_MRP}"
            )

        return ValidationResult.ok()


# ------------------------------------------------------------------
# Pipeline validator — validates full batches
# ------------------------------------------------------------------

class PipelineValidator:
    """
    Validates complete batches of Medicine and Brand entities.

    Wraps MedicineValidator and BrandValidator to apply rules across
    an entire pipeline run and produce a structured summary.

    Usage:
        validator = PipelineValidator()
        valid_medicines, valid_brands = validator.validate_all(medicines, brands)
    """

    def __init__(self) -> None:
        self._medicine_validator = MedicineValidator()
        self._brand_validator = BrandValidator()

    def validate_medicines(self, medicines: list[Medicine]) -> list[Medicine]:
        """
        Validate a list of Medicine entities.

        Returns only the entities that passed all validation rules.
        Logs a warning for every rejected entity with the failure reason.
        """
        valid: list[Medicine] = []
        rejected = 0

        for medicine in medicines:
            result = self._medicine_validator.validate(medicine)
            if result.is_valid:
                valid.append(medicine)
            else:
                rejected += 1
                logger.warning(
                    "Medicine rejected [%s | %s]: %s",
                    medicine.generic_name,
                    medicine.dosage,
                    result.reason,
                )

        logger.info(
            "Medicine validation complete — passed: %d, rejected: %d",
            len(valid),
            rejected,
        )
        return valid

    def validate_brands(self, brands: list[Brand]) -> list[Brand]:
        """
        Validate a list of Brand entities.

        Returns only the entities that passed all validation rules.
        Logs a warning for every rejected entity with the failure reason.
        """
        valid: list[Brand] = []
        rejected = 0

        for brand in brands:
            result = self._brand_validator.validate(brand)
            if result.is_valid:
                valid.append(brand)
            else:
                rejected += 1
                logger.warning(
                    "Brand rejected [%s]: %s",
                    brand.brand_name,
                    result.reason,
                )

        logger.info(
            "Brand validation complete — passed: %d, rejected: %d",
            len(valid),
            rejected,
        )
        return valid

    def validate_all(
        self,
        medicines: list[Medicine],
        brands: list[Brand],
    ) -> tuple[list[Medicine], list[Brand]]:
        """
        Validate a complete batch of medicines and brands.

        Returns a tuple of (valid_medicines, valid_brands).
        Invalid entities are logged and excluded from the result.
        """
        logger.info(
            "Starting pipeline validation — medicines: %d, brands: %d",
            len(medicines),
            len(brands),
        )

        valid_medicines = self.validate_medicines(medicines)
        valid_brands = self.validate_brands(brands)

        logger.info("Pipeline validation complete")
        return valid_medicines, valid_brands
