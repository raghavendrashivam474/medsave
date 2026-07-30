"""
pipeline/normalizers/medicine_normalizer.py

Normalizes medicine entities into consistent standard format.
"""

from pipeline.entities import Medicine, Brand
from pipeline.logger import get_logger

logger = get_logger(__name__)

class MedicineNormalizer:

    def normalize_medicine(self, medicine: Medicine) -> Medicine:
        return Medicine(
            generic_name = self.normalize_name(medicine.generic_name),
            salt = self.normalize_name(medicine.salt),
            dosage = medicine.dosage.upper().strip(),
            form = self.normalize_form(medicine.form),
            jan_price = round(medicine.jan_price, 2)
        )

    def normalize_brand(self, brand: Brand) -> Brand:
        return Brand(
            brand_name = self.normalize_name(brand.brand_name),
            generic_name = self.normalize_name(brand.generic_name),
            mrp = round(brand.mrp, 2)
        )

    def normalize_name(self, name: str) -> str:
        name = name.strip()
        name = name.title()
        return ' '.join(name.split())

    def normalize_form(self, form: str) -> str:
        form = form.strip().lower()
        match form:
            case 'tab' | 'tablets' | 'tbl':
                return 'Tablet'
            case 'cap' | 'capsules':
                return 'Capsule'
            case 'syp' | 'syrup':
                return 'Syrup'
            case 'inj' | 'injection':
                return 'Injection'
            case _:
                return form.title()

    def normalize_all(self, medicines: list[Medicine], brands: list[Brand]) -> tuple[list[Medicine], list[Brand]]:
        logger.info("Starting normalization")

        norm_medicines = [self.normalize_medicine(m) for m in medicines]
        norm_brands = [self.normalize_brand(b) for b in brands]

        logger.info("Normalization complete")

        return norm_medicines, norm_brands