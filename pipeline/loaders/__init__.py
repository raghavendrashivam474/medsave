"""
pipeline/loaders

Exports all available database loader implementations.
"""

from pipeline.loaders.postgres_loader import PostgresLoader

__all__ = ["PostgresLoader"]
