"""
pipeline/sources/base.py

Defines the base interface for all MedSave data sources.

Every data source (Kaggle, Jan Aushadhi, CDSCO, NPPA, etc.) must
inherit from BaseSource and implement all abstract methods.

This ensures the pipeline can treat all sources uniformly regardless
of where the data physically comes from.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseSource(ABC):
    """
    Abstract base class for all MedSave data sources.

    Subclasses must implement:
        - get_source_name()
        - fetch()
        - get_metadata()

    The pipeline orchestrator will call these methods in order:
        1. get_source_name()  -- for logging and identification
        2. get_metadata()     -- to inspect source before fetching
        3. fetch()            -- to retrieve raw data
    """

    @abstractmethod
    def get_source_name(self) -> str:
        """
        Return the unique identifier for this data source.

        Examples:
            "kaggle"
            "jan_aushadhi"
            "cdsco"
            "nppa"

        Returns:
            A lowercase string identifying the source.
        """
        ...

    @abstractmethod
    def fetch(self) -> Any:
        """
        Retrieve raw data from the source.

        The return type is intentionally Any because different sources
        may return different raw formats (CSV, JSON, HTML, etc.).
        The parser layer is responsible for interpreting the output.

        Returns:
            Raw data in whatever format the source provides.

        Raises:
            NotImplementedError: If the source has not been implemented.
            ConnectionError:     If the source cannot be reached.
        """
        ...

    @abstractmethod
    def get_metadata(self) -> dict[str, Any]:
        """
        Return descriptive metadata about this data source.

        Metadata helps the pipeline log and audit where data came from.

        Expected keys:
            source_name:  Human readable name of the source.
            source_url:   URL or path to the data.
            format:       Data format (csv, json, html, etc).
            description:  Short description of what this source provides.

        Returns:
            A dictionary containing source metadata.
        """
        ...
