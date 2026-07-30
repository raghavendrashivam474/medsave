from pathlib import Path
import subprocess

from pipeline.config import config
from pipeline.sources.base import BaseSource


class KaggleSource(BaseSource):

    DATASET = "pranayverma472/medicine-recommendation-system"
    FILE_NAME = "medicine_dataset.csv"

    def get_source_name(self) -> str:
        return "kaggle"

    def get_metadata(self) -> dict:
        return {
            "source_name": "Kaggle Medicine Dataset",
            "source_url": f"https://www.kaggle.com/datasets/{self.DATASET}",
            "format": "csv",
            "records": 25000
        }

    def fetch(self) -> Path:

        raw_path = Path(config.raw_dir) / self.FILE_NAME

        # If file already exists, use it. No download required.
        if raw_path.exists():
            return raw_path

        # Otherwise download from Kaggle
        subprocess.run(
            [
                "kaggle", "datasets", "download",
                "-d", self.DATASET,
                "-f", self.FILE_NAME,
                "-p", config.raw_dir,
                "--unzip"
            ],
            check=True,
            capture_output=True
        )

        return raw_path