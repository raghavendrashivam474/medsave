"""
pipeline/parsers/csv_parser.py

Converts raw CSV files into Medicine and Brand entities.
Tolerant of UTF-8 BOMs (commonly present in exported/downloaded CSVs).
"""

import csv
from pathlib import Path

from pipeline.entities import Medicine, Brand
from pipeline.logger import get_logger

logger = get_logger(__name__)


class CsvParser:

    REQUIRED_COLUMNS = {
        "name", "salt", "dosage", "form", "brand_name", "mrp", "jan_price"
    }

    def parse(self, path: Path) -> tuple[list[Medicine], list[Brand]]:
        logger.info("Starting CSV parse: %s", path)

        medicines: list[Medicine] = []
        brands: list[Brand] = []
        skipped = 0

        # utf-8-sig auto-strips any leading BOM
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            missing = self.REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"CSV missing required columns: {missing}")

            for row in reader:
                try:
                    medicine = Medicine(
                        generic_name=row["name"].strip(),
                        salt=row["salt"].strip(),
                        dosage=row["dosage"].strip(),
                        form=row["form"].strip(),
                        jan_price=float(row["jan_price"]),
                    )
                    brand = Brand(
                        brand_name=row["brand_name"].strip(),
                        generic_name=row["name"].strip(),
                        mrp=float(row["mrp"]),
                    )
                    medicines.append(medicine)
                    brands.append(brand)
                except (ValueError, KeyError) as e:
                    skipped += 1
                    logger.debug("Skipping invalid row: %s", e)
                    continue

        logger.info(
            "Parsed %d medicines, %d brands (skipped: %d)",
            len(medicines), len(brands), skipped
        )
        return medicines, brands
