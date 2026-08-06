"""
backend/app.py

MedSave Flask application entry point.

Responsibilities:
    - Initialize the Flask application
    - Register all API blueprints
    - Serve the frontend static files
    - Provide a local development entry point

All route logic lives inside backend/api/.
All database connection logic lives inside backend/database/connection.py.
All recommendation logic routes through the Decision Engine.
This file is intentionally thin.
"""

import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from backend.api.health           import health_bp
from backend.api.medicine         import medicine_bp
from backend.api.search           import search_bp
from backend.api.stores           import stores_bp
from backend.api.recommendations  import recommendations_bp

load_dotenv()

app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path="",
)

CORS(app)

# Register API blueprints
app.register_blueprint(health_bp)
app.register_blueprint(medicine_bp)
app.register_blueprint(search_bp)
app.register_blueprint(stores_bp)
app.register_blueprint(recommendations_bp)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
