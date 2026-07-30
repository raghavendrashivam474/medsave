"""
pipeline/config.py

Configuration module for the MedSave Data Engine.
Reads environment variables from backend/.env so pipeline and Flask
API share the same database configuration.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# Load backend/.env so pipeline uses same DATABASE_URL as Flask
_BACKEND_ENV = Path(__file__).resolve().parent.parent / "backend" / ".env"
if _BACKEND_ENV.exists():
    load_dotenv(_BACKEND_ENV)


@dataclass(frozen=True)
class PipelineConfig:
    database_url: str
    raw_dir: str
    processed_dir: str


def load_config() -> PipelineConfig:
    return PipelineConfig(
        database_url=os.environ.get(
            "DATABASE_URL",
            "sqlite:///backend/database.db"
        ),
        raw_dir=os.environ.get("RAW_DIR", "pipeline/raw"),
        processed_dir=os.environ.get("PROCESSED_DIR", "pipeline/processed"),
    )


config = load_config()
