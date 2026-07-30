"""
pipeline/config.py

Configuration module for the MedSave Data Engine.

Loads all environment variables required by the pipeline.
No business logic lives here.

Environment Variables:
    DATABASE_URL:   PostgreSQL connection string.
                    Defaults to the MedSave SQLite database for local development.
    RAW_DIR:        Directory where raw downloaded files are stored.
                    Defaults to pipeline/raw/
    PROCESSED_DIR:  Directory where processed files are stored.
                    Defaults to pipeline/processed/

Usage:
    from pipeline.config import config

    print(config.database_url)
    print(config.raw_dir)
    print(config.processed_dir)
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineConfig:
    """
    Immutable configuration object for the MedSave Data Engine.

    All values are loaded once at startup and remain constant
    throughout the lifetime of the pipeline process.

    Attributes:
        database_url:   PostgreSQL or SQLite connection string.
        raw_dir:        Absolute or relative path to raw data directory.
        processed_dir:  Absolute or relative path to processed data directory.
    """

    database_url: str
    raw_dir: str
    processed_dir: str


def load_config() -> PipelineConfig:
    """
    Load pipeline configuration from environment variables.

    Falls back to safe local development defaults if environment
    variables are not set.

    Returns:
        A fully populated PipelineConfig instance.
    """
    return PipelineConfig(
        database_url=os.environ.get(
            "DATABASE_URL",
            "sqlite:///backend/medsave.db"
        ),
        raw_dir=os.environ.get(
            "RAW_DIR",
            "pipeline/raw"
        ),
        processed_dir=os.environ.get(
            "PROCESSED_DIR",
            "pipeline/processed"
        ),
    )


# Module-level singleton.
# Import this directly rather than calling load_config() each time.
config = load_config()
