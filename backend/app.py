"""
backend/app.py

MedSave Flask application entry point.

Responsibilities:
    - Initialize the Flask application
    - Register all API blueprints
    - Serve the frontend static files and root index.html
    - Provide a local development entry point
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.api.health   import health_bp
from backend.api.medicine import medicine_bp
from backend.api.search   import search_bp
from backend.api.stores   import stores_bp

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
)

CORS(app)

# Register API blueprints
app.register_blueprint(health_bp)
app.register_blueprint(medicine_bp)
app.register_blueprint(search_bp)
app.register_blueprint(stores_bp)


@app.route("/")
def serve_index():
    """Serve the root frontend application."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    """Serve static frontend assets with fallback to index.html."""
    target_file = FRONTEND_DIR / path
    if target_file.exists() and target_file.is_file():
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
