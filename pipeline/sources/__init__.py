"""
pipeline/sources

Exports all available data source adapters.
"""

from pipeline.sources.base import BaseSource
from pipeline.sources.kaggle import KaggleSource

__all__ = ["BaseSource", "KaggleSource"]
