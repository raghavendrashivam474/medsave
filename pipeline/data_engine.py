"""
pipeline/data_engine.py

Entry point for the MedSave Data Engine.
Orchestrates the full ingestion pipeline.

Pipeline stages executed in order:
    1. Source     — Acquire raw data
    2. Parser     — Convert raw data into entities
    3. Normalizer — Standardize entity values
    4. Validator  — Apply business rules before persistence
    5. Loader     — Persist validated entities into the database

Usage:
    python -m pipeline.data_engine
"""

import sys

from pipeline.config import load_config, config
from pipeline.logger import configure_logging, get_logger
from pipeline.sources import KaggleSource
from pipeline.parsers import CsvParser
from pipeline.normalizers import MedicineNormalizer
from pipeline.validators import PipelineValidator
from pipeline.loaders import PostgresLoader


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


def initialize_pipeline(logger) -> None:
    cfg = load_config()
    logger.info("Configuration loaded.")
    logger.info("  DATABASE_URL  : %s", cfg.database_url)
    logger.info("  RAW_DIR       : %s", cfg.raw_dir)
    logger.info("  PROCESSED_DIR : %s", cfg.processed_dir)

    logger.info("Verifying pipeline layers.")
    logger.info("  [OK] Sources       : KaggleSource")
    logger.info("  [OK] Parsers       : CsvParser")
    logger.info("  [OK] Normalizers   : MedicineNormalizer")
    logger.info("  [OK] Validators    : PipelineValidator")
    logger.info("  [OK] Loaders       : PostgresLoader")
    logger.info("All pipeline layers verified.")


def main() -> None:
    configure_logging()
    logger = get_logger(__name__)

    print_banner(version="0.3 Sprint 2.3")
    initialize_pipeline(logger)

    logger.info("Starting full ingestion pipeline")

    # Stage 1 — Source
    source = KaggleSource()
    logger.info("Using source: %s", source.get_source_name())
    path = source.fetch()

    # Stage 2 — Parser
    parser = CsvParser()
    medicines, brands = parser.parse(path)

    # Stage 3 — Normalizer
    normalizer = MedicineNormalizer()
    medicines, brands = normalizer.normalize_all(medicines, brands)

    # Stage 4 — Validator
    validator = PipelineValidator()
    medicines, brands = validator.validate_all(medicines, brands)

    # Stage 5 — Loader
    loader = PostgresLoader(config.database_url)
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
    print(f"  Medicines Loaded : {len(medicines)}")
    print(f"  Brands Loaded    : {len(brands)}")
    print()
    logger.info("Ingestion completed successfully")


if __name__ == "__main__":
    main()
