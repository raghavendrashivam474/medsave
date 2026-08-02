"""
backend/api

API blueprint registry for the MedSave Flask application.

Each endpoint group is defined in its own module and exposed here.
The Flask application (app.py) imports and registers all blueprints
directly from each module. This package init exists for completeness
and to support any future consolidated imports.

Blueprints
----------
health_bp   : GET /api/health
search_bp   : GET /api/search
medicine_bp : GET /api/medicine/<id>
stores_bp   : GET /api/stores, GET /api/stores/<id>
"""

from backend.api.health   import health_bp
from backend.api.medicine import medicine_bp
from backend.api.search   import search_bp
from backend.api.stores   import stores_bp

__all__ = ["health_bp", "medicine_bp", "search_bp", "stores_bp"]