"""
backend/api/search.py

Medicine search endpoint for the MedSave backend.

Searches both brand names and generic names using a partial match.
Returns matching medicines along with price comparison data and
calculated savings information.

Endpoint:
    GET /api/search?q=<query>

Query Parameters:
    q (str): The search term. Searches brand_name and generic_name.
             Returns an empty list when q is missing or blank.

Response:
    200 OK — List of matching medicine records.

    Each record contains:
        brand_name      (str)   Commercial name of the medicine.
        generic_name    (str)   Generic/scientific name.
        salt            (str)   Active pharmaceutical ingredient.
        dosage          (str)   Strength of the medicine.
        form            (str)   Physical form (Tablet, Capsule, etc).
        brand_price     (float) MRP of the branded medicine.
        generic_price   (float) Jan Aushadhi price of the generic.
        savings_percent (float) Percentage saved by choosing generic.
"""

import sqlite3

from flask import Blueprint, jsonify, request

from backend.database.connection import get_db_connection

search_bp = Blueprint("search", __name__)


@search_bp.route("/api/search", methods=["GET"])
def search_medicine():
    """
    Search medicines by brand name or generic name.

    Returns an empty list when the query is blank.
    Savings percentage is calculated as:
        ((brand_price - generic_price) / brand_price) * 100
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)

        if is_sqlite:
            sql = """
                SELECT
                    b.brand_name,
                    m.generic_name,
                    m.salt,
                    m.dosage,
                    m.form,
                    b.mrp        AS brand_price,
                    m.jan_price  AS generic_price
                FROM brands b
                JOIN medicines m ON b.generic_id = m.id
                WHERE b.brand_name LIKE ?
                   OR m.generic_name LIKE ?
                ORDER BY b.brand_name
            """
        else:
            sql = """
                SELECT
                    b.brand_name,
                    m.generic_name,
                    m.salt,
                    m.dosage,
                    m.form,
                    b.mrp        AS brand_price,
                    m.jan_price  AS generic_price
                FROM brands b
                JOIN medicines m ON b.generic_id = m.id
                WHERE b.brand_name ILIKE %s
                   OR m.generic_name ILIKE %s
                ORDER BY b.brand_name
            """

        search_term = f"%{query}%"
        cur.execute(sql, (search_term, search_term))
        rows = cur.fetchall()

        results = []
        for row in rows:
            brand_price = row["brand_price"]
            generic_price = row["generic_price"]

            savings_percent = 0.0
            if brand_price and brand_price > 0:
                savings_percent = round(
                    ((brand_price - generic_price) / brand_price) * 100, 1
                )

            results.append({
                "brand_name":     row["brand_name"],
                "generic_name":   row["generic_name"],
                "salt":           row["salt"],
                "dosage":         row["dosage"],
                "form":           row["form"],
                "brand_price":    brand_price,
                "generic_price":  generic_price,
                "savings_percent": savings_percent,
            })

        return jsonify(results)

    finally:
        conn.close()
