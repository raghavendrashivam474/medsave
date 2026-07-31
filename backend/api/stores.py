"""
backend/api/stores.py

Pharmacy store lookup endpoint for the MedSave backend.

Supports lookup by pincode or by geographic coordinates.
When coordinates are provided, stores are sorted by approximate
distance from the user and limited to the 5 nearest results.

Endpoint:
    GET /api/stores

Query Parameters:
    pincode (str, optional): Filter stores by pincode.
    lat     (float, optional): User latitude for proximity search.
    lng     (float, optional): User longitude for proximity search.

When neither pincode nor coordinates are provided, up to 10 stores
are returned without filtering.

Distance Calculation:
    Uses a flat-earth approximation sufficient for city-level proximity.
    1 degree latitude  ≈ 111 km
    1 degree longitude ≈ 85 km (approximate for India)

    This is intentionally simple. Haversine or Google Maps Distance
    Matrix belong to a later milestone.
"""

import math
import sqlite3

from flask import Blueprint, jsonify, request

from backend.database.connection import get_db_connection

stores_bp = Blueprint("stores", __name__)

# Approximate conversion factors for India
_KM_PER_LAT_DEGREE = 111.0
_KM_PER_LNG_DEGREE = 85.0

# Maximum results returned for proximity search
_PROXIMITY_LIMIT = 5


def _calculate_distance(user_lat: float, user_lng: float, store_lat: float, store_lng: float) -> float:
    """
    Calculate approximate distance in kilometres between two coordinates.

    Uses a flat-earth approximation. Accurate enough for city-level
    proximity sorting. Not suitable for precise navigation distances.
    """
    delta_lat = (user_lat - store_lat) * _KM_PER_LAT_DEGREE
    delta_lng = (user_lng - store_lng) * _KM_PER_LNG_DEGREE
    return math.sqrt(delta_lat ** 2 + delta_lng ** 2)


@stores_bp.route("/api/stores", methods=["GET"])
def get_stores():
    """
    Return pharmacy stores filtered by pincode or proximity.

    Priority order:
        1. Pincode filter when pincode parameter is provided.
        2. Proximity sort when lat and lng are provided.
        3. Default listing (up to 10 stores) when no parameters provided.
    """
    pincode = request.args.get("pincode", "").strip()
    lat_str = request.args.get("lat", "").strip()
    lng_str = request.args.get("lng", "").strip()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        placeholder = "?" if is_sqlite else "%s"

        # --- Pincode search ---
        if pincode:
            cur.execute(
                f"SELECT * FROM stores WHERE pincode = {placeholder}",
                (pincode,)
            )
            rows = cur.fetchall()
            return jsonify([dict(row) for row in rows])

        # --- Proximity search ---
        if lat_str and lng_str:
            try:
                user_lat = float(lat_str)
                user_lng = float(lng_str)
            except ValueError:
                return jsonify({"error": "lat and lng must be valid numbers"}), 400

            cur.execute("SELECT * FROM stores")
            rows = cur.fetchall()

            stores_with_distance = []
            for row in rows:
                store = dict(row)
                if store.get("lat") is not None and store.get("lng") is not None:
                    store["distance_km"] = round(
                        _calculate_distance(user_lat, user_lng, store["lat"], store["lng"]),
                        2
                    )
                else:
                    store["distance_km"] = None
                stores_with_distance.append(store)

            # Sort by distance, push stores without coordinates to end
            stores_with_distance.sort(
                key=lambda s: s["distance_km"] if s["distance_km"] is not None else float("inf")
            )

            return jsonify(stores_with_distance[:_PROXIMITY_LIMIT])

        # --- Default listing ---
        cur.execute("SELECT * FROM stores LIMIT 10")
        rows = cur.fetchall()
        return jsonify([dict(row) for row in rows])

    finally:
        conn.close()
