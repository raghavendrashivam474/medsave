"""
backend/api/health.py

Health check endpoint for the MedSave backend.

Used to verify that the Flask application and database connection
are operational. Suitable for deployment health monitoring.

Endpoint:
    GET /api/health

Response:
    200 OK    — Backend and database are operational.
    500 Error — Database connection failed.
"""

from flask import Blueprint, jsonify
from backend.database.connection import get_db_connection

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    """
    Verify backend availability and database connectivity.

    Returns a 200 response with status information when healthy.
    Returns a 500 response with error details when the database
    connection cannot be established.
    """
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({
            "status": "ok",
            "database": "connected",
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "database": "unreachable",
            "detail": str(e),
        }), 500
