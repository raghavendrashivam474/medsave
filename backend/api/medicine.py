# backend/api/medicine.py

"""
backend/api/medicine.py

Medicine detail endpoint for the MedSave backend.

Returns one complete medicine record along with all associated branded
alternatives and calculated savings information.

Endpoint:
    GET /api/medicine/<id>

Path Parameter:
    id (int): The primary key of the medicine in the medicines table.

Response shape
--------------
Success (200):
    {
        "success": true,
        "medicine": {
            "id":                   1,
            "generic_name":         "Paracetamol",
            "salt":                 "Paracetamol",
            "dosage":               "500MG",
            "form":                 "Tablet",
            "jan_price":            10.0,
            "manufacturer":         null,
            "therapeutic_category": null,
            "schedule":             null
        },
        "brands": [
            {
                "id":              1,
                "brand_name":      "Crocin",
                "mrp":             35.0,
                "manufacturer":    null,
                "savings":         25.0,
                "savings_percent": 71.4
            }
        ]
    }

Not found (404):
    {
        "success": false,
        "message": "Medicine not found.",
        "error":   "NOT_FOUND"
    }

Server error (500):
    {
        "success": false,
        "message": "An unexpected error occurred.",
        "error":   "SERVER_ERROR"
    }

Design notes
------------
- Row access uses column names (row["col"]) throughout because
  connection.py sets sqlite3.Row / RealDictCursor on every connection.
  Index-based access (row[0]) is intentionally avoided — it breaks
  silently if column order ever changes.

- Savings are calculated in Python, not SQL, so the logic is visible,
  testable, and easy to adjust independently of the query.

- savings_percent is calculated as:
      ((mrp - jan_price) / mrp) * 100
  This matches the existing search.py convention:
      ((brand_price - generic_price) / brand_price) * 100

- Brands are ordered by mrp ASC so the cheapest branded option
  appears first — most useful ordering for a comparison screen.

- try/except/finally ensures the connection is always closed and
  errors always return JSON, never an unhandled 500 HTML page.
"""

import logging
import sqlite3

from flask import Blueprint, jsonify

from backend.database.connection import get_db_connection

logger = logging.getLogger(__name__)

medicine_bp = Blueprint("medicine", __name__)


def _calculate_savings(jan_price, mrp):
    """
    Return (savings, savings_percent) for one brand comparison.

    Savings      = mrp - jan_price
    Savings %    = (savings / mrp) * 100  rounded to 1 decimal place

    Returns (None, None) when either price is missing or not positive.
    Returns (0, 0.0) when the branded price is not higher than the
    Jan Aushadhi price — savings exist but are zero or negative.

    Parameters
    ----------
    jan_price : float or None
        Jan Aushadhi price from the medicines table.
    mrp : float or None
        Maximum Retail Price from the brands table.

    Returns
    -------
    tuple[float | None, float | None]
    """
    if jan_price is None or mrp is None:
        return None, None

    if jan_price <= 0 or mrp <= 0:
        return None, None

    savings = mrp - jan_price

    if savings <= 0:
        return 0, 0.0

    savings_percent = round((savings / mrp) * 100, 1)
    return savings, savings_percent


@medicine_bp.route("/api/medicine/<int:medicine_id>", methods=["GET"])
def get_medicine(medicine_id):
    """
    Return one medicine with all associated brands and savings data.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        is_sqlite = isinstance(conn, sqlite3.Connection)
        placeholder = "?" if is_sqlite else "%s"

        # ── 1. Fetch the medicine ─────────────────────────────────────────
        cur.execute(
            f"""
            SELECT
                id,
                generic_name,
                salt,
                dosage,
                form,
                jan_price,
                manufacturer,
                therapeutic_category,
                schedule
            FROM medicines
            WHERE id = {placeholder}
            """,
            (medicine_id,),
        )

        row = cur.fetchone()

        if row is None:
            return jsonify({
                "success": False,
                "message": "Medicine not found.",
                "error":   "NOT_FOUND",
            }), 404

        medicine = {
            "id":                   row["id"],
            "generic_name":         row["generic_name"],
            "salt":                 row["salt"],
            "dosage":               row["dosage"],
            "form":                 row["form"],
            "jan_price":            row["jan_price"],
            "manufacturer":         row["manufacturer"],
            "therapeutic_category": row["therapeutic_category"],
            "schedule":             row["schedule"],
        }

        # ── 2. Fetch all brands for this medicine ─────────────────────────
        cur.execute(
            f"""
            SELECT
                id,
                brand_name,
                mrp,
                manufacturer
            FROM brands
            WHERE generic_id = {placeholder}
            ORDER BY mrp ASC
            """,
            (medicine_id,),
        )

        brand_rows = cur.fetchall()

        brands = []
        for b in brand_rows:
            savings, savings_percent = _calculate_savings(
                medicine["jan_price"], b["mrp"]
            )
            brands.append({
                "id":              b["id"],
                "brand_name":      b["brand_name"],
                "mrp":             b["mrp"],
                "manufacturer":    b["manufacturer"],
                "savings":         savings,
                "savings_percent": savings_percent,
            })

        # ── 3. Return combined response ───────────────────────────────────
        return jsonify({
            "success":  True,
            "medicine": medicine,
            "brands":   brands,
        }), 200

    except Exception as exc:
        # Log the real error internally. Never expose it to the client.
        logger.exception("GET /api/medicine/%s failed", medicine_id)
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred.",
            "error":   "SERVER_ERROR",
        }), 500

    finally:
        if conn:
            conn.close()