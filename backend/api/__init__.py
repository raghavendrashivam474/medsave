"""
backend/api

Registers all API blueprints for the MedSave Flask application.

Each endpoint group is defined in its own module and registered
here as a Blueprint. The Flask application imports and registers
all blueprints from this package.
"""

from backend.api.health import health_bp
from backend.api.search import search_bp
from backend.api.stores import stores_bp

__all__ = ["health_bp", "search_bp", "stores_bp"]
