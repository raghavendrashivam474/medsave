"""
pipeline/data_engine.py

Entry point for the MedSave Data Engine.

Responsibilities:
    - Load configuration
    - Initialize logging
    - Verify pipeline modules are importable
    - Display startup banner

No ingestion occurs when this file is executed directly.
This file confirms that the Data Engine architecture is correctly
wired and ready for Sprint 2.2.

Usage:
    python pipeline/data_engine.py
"""

import logging
import sys

from pipeline.config import load_config
from pipeline.entities import Medicine, Brand
from pipeline.sources import BaseSource, KaggleSource
from pipeline.loaders import PostgresLoader


def configure_logging() -> None:
    """
    Set up logging for the Data Engine.

    Outputs to stdout with timestamp, level, and message.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def print_banner(version: str) -> None:
    """
    Print the MedSave Data Engine startup banner.

    Args:
        version: The current version string of the Data Engine.
    """
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
    """
    Verify that all pipeline layers are importable and report their status.

    This does not execute any ingestion logic.
    It confirms the architecture is correctly wired.
    """
    logger = logging.getLogger(__name__)

    config = load_config()
    logger.info("Configuration loaded.")
    logger.info("  DATABASE_URL  : %s", config.database_url)
    logger.info("  RAW_DIR       : %s", config.raw_dir)
    logger.info("  PROCESSED_DIR : %s", config.processed_dir)

    logger.info("Verifying pipeline layers.")

    logger.info("  [OK] Entities      : Medicine, Brand")
    logger.info("  [OK] Sources       : BaseSource, KaggleSource")
    logger.info("  [OK] Loaders       : PostgresLoader")

    logger.info("All pipeline layers verified.")


def main() -> None:
    """
    Main entry point for the MedSave Data Engine.
    """
    configure_logging()
    print_banner(version="0.1")
    initialize_pipeline()


if __name__ == "__main__":
    main()
