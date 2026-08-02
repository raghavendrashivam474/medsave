# backend/api/stores.py

"""
backend/api/stores.py

Store locator endpoints for the MedSave backend.

Provides store discovery by pincode, city, state, or geographic proximity.
All responses follow the standard MedSave API envelope format.

Endpoints
---------
GET /api/stores
    List and filter stores.

    Query Parameters:
        pincode (str)   : Filter by exact pincode match.
        city    (str)   : Filter by city name (case-insensitive).
        state   (str)   : Filter by state name (case-insensitive).
        lat     (float) : User latitude for proximity search.
        lng     (float) : User longitude for proximity search.

    Priority order when multiple parameters are supplied:
        1. pincode  — exact match filter.
        2. city     — case-insensitive filter.
        3. state    — case-insensitive filter.
        4. lat+lng  — proximity sort, nearest 5 stores returned.
        5. default  — up to 20 stores, ordered by city then name.

GET /api/stores/<id>
    Return one store by primary key.

Response Format
---------------
Success (list):
    {
        "success": true,
        "count":   2,
        "data": [ { store }, { store } ]
    }

Success (single):
    {
        "success": true,
        "data": { store }
    }

Failure:
    {
        "success": false,
        "message": "Human-readable description.",
        "error":   "ERROR_CODE"
    }

Store Object Shape
------------------
Every store object always includes all fields.
Fields unavailable in the database are returned as null — never omitted.

    {
        "id":                 1,
        "name":               "Jan Aushadhi Kendra - Sector 12",
        "address":            "Shop 4, Huda Market, Sector 12",
        "city":               "Noida",
        "state":              "Uttar Pradesh",
        "pincode":            "201301",
        "latitude":           28.59,
        "longitude":          77.34,
        "phone":              null,
        "distance_km":        null,
        "estimated_distance": null,
        "travel_time":        null
    }

Notes
-----
- distance_km, estimated_distance, travel_time are placeholder fields.
  They are included in the response shape now so the frontend can build
  against a stable contract. Real values belong to a future milestone.
- distance_km is populated only for proximity searches using the
  flat-earth approximation (sufficient for city-level sorting).
- Haversine, Google Maps Distance Matrix, and route planning are
  explicitly out of scope for this sprint.
- Column names in the database are lat/lng. The API response uses
  latitude/longitude for clarity at the API boundary.
"""

import logging
import math
import sqlite3

from flask import Blueprint, jsonify, request

from backend.database.connection import get_db_connection

logger = logging.getLogger(__name__)

stores_bp = Blueprint("stores", __name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Approximate flat-earth conversion factors for India.
# Accurate enough for city-level proximity sorting.
# Haversine belongs to a future milestone.
_KM_PER_LAT_DEGREE = 111.0
_KM_PER_LNG_DEGREE = 85.0

# Maximum results returned for proximity and default listings.
_PROXIMITY_LIMIT = 5
_DEFAULT_LIMIT   = 20


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_store(row, distance_km=None):
    """
    Convert a database row into a complete store API object.

    All fields are always present. Missing values are returned as null.
    Database columns lat/lng are exposed as latitude/longitude at the
    API boundary for clarity.

    Parameters
    ----------
    row : sqlite3.Row or psycopg2 RealDictRow
        A single row from the stores table.
    distance_km : float or None
        Pre-calculated distance. Only populated for proximity searches.

    Returns
    -------
    dict
        Complete store object matching the documented API shape.
    """
    return {
        "id":                 row["id"],
        "name":               row["name"],
        "address":            row["address"],
        "city":               row["city"],
        "state":              row["state"],
        "pincode":            row["pincode"],
        "latitude":           row["lat"],
        "longitude":          row["lng"],
        "phone":              row["phone"],
        "distance_km":        distance_km,
        "estimated_distance": None,
        "travel_time":        None,
    }


def _flat_distance(user_lat, user_lng, store_lat, store_lng):
    """
    Calculate approximate distance in kilometres between two coordinates.

    Uses a flat-earth approximation. Sufficient for city-level proximity
    sorting. Not suitable for navigation or precise distance display.

    Parameters
    ----------
    user_lat, user_lng   : float  User's coordinates.
    store_lat, store_lng : float  Store's coordinates.

    Returns
    -------
    float
        Approximate distance in kilometres, rounded to 2 decimal places.
    """
    delta_lat = (user_lat - store_lat) * _KM_PER_LAT_DEGREE
    delta_lng = (user_lng - store_lng) * _KM_PER_LNG_DEGREE
    return round(math.sqrt(delta_lat ** 2 + delta_lng ** 2), 2)


def _success_list(stores):
    """Return a standard success envelope for a list of stores."""
    return jsonify({
        "success": True,
        "count":   len(stores),
        "data":    stores,
    }), 200


def _success_one(store):
    """Return a standard success envelope for a single store."""
    return jsonify({
        "success": True,
        "data":    store,
    }), 200


def _not_found(message):
    """Return a standard 404 not-found envelope."""
    return jsonify({
        "success": False,
        "message": message,
        "error":   "NOT_FOUND",
    }), 404


def _bad_request(message):
    """Return a standard 400 bad-request envelope."""
    return jsonify({
        "success": False,
        "message": message,
        "error":   "BAD_REQUEST",
    }), 400


def _server_error(context):
    """Return a standard 500 server-error envelope. Never expose internals."""
    logger.exception("Store API error: %s", context)
    return jsonify({
        "success": False,
        "message": "An unexpected error occurred.",
        "error":   "SERVER_ERROR",
    }), 500


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@stores_bp.route("/api/stores", methods=["GET"])
def get_stores():
    """
    List stores with optional filtering.

    Supports filtering by pincode, city, state, or proximity.
    See module docstring for priority order and response format.
    """
    pincode = request.args.get("pincode", "").strip()
    city    = request.args.get("city",    "").strip()
    state   = request.args.get("state",   "").strip()
    lat_raw = request.args.get("lat",     "").strip()
    lng_raw = request.args.get("lng",     "").strip()

    conn = None
    try:
        conn = get_db_connection()
        cur  = conn.cursor()

        is_sqlite   = isinstance(conn, sqlite3.Connection)
        placeholder = "?" if is_sqlite else "%s"
        ilike       = "LIKE" if is_sqlite else "ILIKE"

        # ----------------------------------------------------------------
        # 1. Pincode filter
        # ----------------------------------------------------------------
        if pincode:
            cur.execute(
                f"""
                SELECT *
                FROM   stores
                WHERE  pincode = {placeholder}
                ORDER  BY name ASC
                """,
                (pincode,),
            )
            rows   = cur.fetchall()
            stores = [_build_store(r) for r in rows]
            return _success_list(stores)

        # ----------------------------------------------------------------
        # 2. City filter
        # ----------------------------------------------------------------
        if city:
            cur.execute(
                f"""
                SELECT *
                FROM   stores
                WHERE  LOWER(city) {ilike} LOWER({placeholder})
                ORDER  BY name ASC
                """,
                (city,),
            )
            rows   = cur.fetchall()
            stores = [_build_store(r) for r in rows]
            return _success_list(stores)

        # ----------------------------------------------------------------
        # 3. State filter
        # ----------------------------------------------------------------
        if state:
            cur.execute(
                f"""
                SELECT *
                FROM   stores
                WHERE  LOWER(state) {ilike} LOWER({placeholder})
                ORDER  BY city ASC, name ASC
                """,
                (state,),
            )
            rows   = cur.fetchall()
            stores = [_build_store(r) for r in rows]
            return _success_list(stores)

        # ----------------------------------------------------------------
        # 4. Proximity search
        # ----------------------------------------------------------------
        if lat_raw and lng_raw:
            try:
                user_lat = float(lat_raw)
                user_lng = float(lng_raw)
            except ValueError:
                return _bad_request(
                    "lat and lng must be valid numeric values."
                )

            cur.execute("SELECT * FROM stores")
            rows = cur.fetchall()

            with_distance = []
            for row in rows:
                if row["lat"] is not None and row["lng"] is not None:
                    dist = _flat_distance(
                        user_lat, user_lng, row["lat"], row["lng"]
                    )
                    with_distance.append(_build_store(row, distance_km=dist))
                else:
                    # Stores without coordinates go to end
                    with_distance.append(_build_store(row))

            with_distance.sort(
                key=lambda s: s["distance_km"]
                if s["distance_km"] is not None
                else float("inf")
            )

            return _success_list(with_distance[:_PROXIMITY_LIMIT])

        # ----------------------------------------------------------------
        # 5. Default listing
        # ----------------------------------------------------------------
        cur.execute(
            f"""
            SELECT *
            FROM   stores
            ORDER  BY city ASC, name ASC
            LIMIT  {_DEFAULT_LIMIT}
            """
        )
        rows   = cur.fetchall()
        stores = [_build_store(r) for r in rows]
        return _success_list(stores)

    except Exception as exc:
        return _server_error(f"GET /api/stores — {exc}")

    finally:
        if conn:
            conn.close()


@stores_bp.route("/api/stores/<int:store_id>", methods=["GET"])
def get_store_by_id(store_id):
    """
    Return one store by primary key.

    Returns 404 when the store does not exist.
    Returns 500 on unexpected database failure.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur  = conn.cursor()

        is_sqlite   = isinstance(conn, sqlite3.Connection)
        placeholder = "?" if is_sqlite else "%s"

        cur.execute(
            f"""
            SELECT *
            FROM   stores
            WHERE  id = {placeholder}
            """,
            (store_id,),
        )
        row = cur.fetchone()

        if row is None:
            return _not_found(f"Store with id {store_id} not found.")

        return _success_one(_build_store(row))

    except Exception as exc:
        return _server_error(f"GET /api/stores/{store_id} — {exc}")

    finally:
        if conn:
            conn.close()