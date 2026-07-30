"""
pipeline/data_engine.py

Entry point for the MedSave Data Engine.
Orchestrates the full ingestion pipeline.

Usage:
    python -m pipeline.data_engine
"""

import logging
import sys

from pipeline.config import load_config, config
from pipeline.entities import Medicine, Brand
from pipeline.sources import BaseSource, KaggleSource
from pipeline.loaders import PostgresLoader
from pipeline.parsers.csv_parser import CsvParser
from pipeline.normalizers.medicine_normalizer import MedicineNormalizer


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def print_banner(version: str) -> None:
    print()
    print("=====================================")
    print()
    print("  MedSave Data Engine")
    print(f"  Version {version}")
    print()
    print("  Pipeline initialized successfully.")
    print()
    print("=====================================")
    print()


def initialize_pipeline() -> None:
    logger = logging.getLogger(__name__)

    cfg = load_config()
    logger.info("Configuration loaded.")
    logger.info("  DATABASE_URL  : %s", cfg.database_url)
    logger.info("  RAW_DIR       : %s", cfg.raw_dir)
    logger.info("  PROCESSED_DIR : %s", cfg.processed_dir)

    logger.info("Verifying pipeline layers.")
    logger.info("  [OK] Entities      : Medicine, Brand")
    logger.info("  [OK] Sources       : BaseSource, KaggleSource")
    logger.info("  [OK] Loaders       : PostgresLoader")
    logger.info("All pipeline layers verified.")


def main() -> None:
    configure_logging()
    print_banner(version="0.2 Sprint 2.2")
    initialize_pipeline()

    logger = logging.getLogger(__name__)

    logger.info("Starting full ingestion pipeline")

    source = KaggleSource()
    parser = CsvParser()
    normalizer = MedicineNormalizer()
    loader = PostgresLoader(config.database_url)

    logger.info("Using source: %s", source.get_source_name())

    path = source.fetch()
    medicines, brands = parser.parse(path)
    medicines, brands = normalizer.normalize_all(medicines, brands)

    loader.connect()
    try:
        loader.load_medicines(medicines)
        loader.load_brands(brands)
        loader.commit()
    finally:
        loader.close()

    print()
    print("Pipeline Complete")
    print()
    print(f"  Medicines Parsed : {len(medicines)}")
    print(f"  Brands Parsed    : {len(brands)}")
    print()
    logger.info("Ingestion completed successfully")


if __name__ == "__main__":
    main()
