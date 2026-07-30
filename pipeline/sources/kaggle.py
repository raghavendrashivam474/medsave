"""
pipeline/sources/kaggle.py

Kaggle data source adapter for the MedSave Data Engine.

This is a skeleton implementation. No downloading or parsing logic
is included in this sprint. Methods raise NotImplementedError to
signal that the implementation is pending.

Future implementation will:
    - Authenticate using the Kaggle API
    - Download the medicine dataset
    - Store raw files in pipeline/raw/
    - Return the file path for the parser layer
"""

from typing import Any

from pipeline.sources.base import BaseSource


class KaggleSource(BaseSource):
    """
    Data source adapter for Kaggle medicine datasets.

    Inherits from BaseSource and will eventually handle
    authentication, download, and raw file management
    for Kaggle-hosted medicine datasets.

    Usage (future):
        source = KaggleSource()
        metadata = source.get_metadata()
        raw_data = source.fetch()
    """

    def get_source_name(self) -> str:
        """
        Return the identifier for this source.

        Returns:
            "kaggle"
        """
        return "kaggle"

    def fetch(self) -> Any:
        """
        Download raw medicine data from Kaggle.

        Not implemented in Sprint 2.1.

        Raises:
            NotImplementedError: Always. Implementation pending.
        """
        raise NotImplementedError(
            "KaggleSource.fetch() is not yet implemented. "
            "This will be built in Sprint 2.2."
        )

    def get_metadata(self) -> dict[str, Any]:
        """
        Return metadata describing the Kaggle medicine dataset.

        Not implemented in Sprint 2.1.

        Raises:
            NotImplementedError: Always. Implementation pending.
        """
        raise NotImplementedError(
            "KaggleSource.get_metadata() is not yet implemented. "
            "This will be built in Sprint 2.2."
        )
