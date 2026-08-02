# backend/api/search.py

"""
backend/api/search.py

Medicine search endpoint for the MedSave backend.

Searches both brand names and generic names using a partial match.
Returns matching medicines along with price comparison data and
calculated savings information.

Endpoint:
    GET /api/search?q=<query>

Query Parameters:
    q (str): The search term. Minimum 1 character.
             Returns an empty list when q is missing or blank.
             This preserves the original behaviour exactly.

Response (unchanged structure — backward compatible)
----------------------------------------------------
    200 OK — List of matching medicine records.

    Each record contains:
        medicine_id     (int)   NEW — primary key of the medicine.
        brand_name      (str)   Commercial name of the medicine.
        generic_name    (str)   Generic/scientific name.
        salt            (str)   Active pharmaceutical ingredient.
        dosage          (str)   Strength of the medicine.
        form            (str)   Physical form (Tablet, Capsule, etc).
        brand_price     (float) MRP of the branded medicine.
        generic_price   (float) Jan Aushadhi price of the generic.
        savings_percent (float) Percentage saved by choosing generic.
        match_type      (str)   NEW — "generic" or "brand".

Enhancements over original
--------------------------
1.  Ranking: exact generic name match → partial generic → brand match.
    Within each rank, results are ordered by generic_name then brand_name.
    Previously all results were ordered only by brand_name.

2.  Partial match on generic_name was already present. Now explicit.

3.  medicine_id added — frontend needs this to link to /api/medicine/<id>.

4.  match_type added — frontend can label results clearly.

5.  Savings percent formula aligned with medicine.py:
        ((brand_price - generic_price) / brand_price) * 100
    Formula was already correct in original — no change to values.

Backward compatibility
----------------------
- No existing fields removed.
- No existing field renamed.
- No existing field changes type.
- Empty-query behaviour unchanged: returns [].
- Response is still a bare JSON array. No envelope wrapper added.
  (Existing consumers depend on this shape.)
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
    Results are ranked: exact generic match first, then partial
    generic match, then brand name match.
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)

        search_term = f"%{query}%"

        if is_sqlite:
            # SQLite: LOWER() for case-insensitive comparison.
            # UNION merges generic matches and brand matches.
            # Outer query joins back to get all medicine columns,
            # groups by medicine+brand to deduplicate, keeps best rank.
            sql = """
                SELECT
                    m.id            AS medicine_id,
                    b.id            AS brand_id,
                    b.brand_name,
                    m.generic_name,
                    m.salt,
                    m.dosage,
                    m.form,
                    b.mrp           AS brand_price,
                    m.jan_price     AS generic_price,
                    MIN(sub.rank)   AS best_rank,
                    sub.match_type
                FROM (
                    SELECT
                        m2.id       AS medicine_id,
                        b2.id       AS brand_id,
                        CASE
                            WHEN LOWER(m2.generic_name) = LOWER(?)
                            THEN 0
                            ELSE 1
                        END         AS rank,
                        'generic'   AS match_type
                    FROM medicines m2
                    JOIN brands b2 ON b2.generic_id = m2.id
                    WHERE LOWER(m2.generic_name) LIKE LOWER(?)

                    UNION ALL

                    SELECT
                        m3.id       AS medicine_id,
                        b3.id       AS brand_id,
                        2           AS rank,
                        'brand'     AS match_type
                    FROM brands b3
                    JOIN medicines m3 ON m3.id = b3.generic_id
                    WHERE LOWER(b3.brand_name) LIKE LOWER(?)
                ) sub
                JOIN medicines m  ON m.id  = sub.medicine_id
                JOIN brands    b  ON b.id  = sub.brand_id
                GROUP BY m.id, b.id
                ORDER BY best_rank ASC, m.generic_name ASC, b.brand_name ASC
            """
            params = (query, search_term, search_term)

        else:
            # PostgreSQL: ILIKE for case-insensitive comparison.
            sql = """
                SELECT
                    m.id            AS medicine_id,
                    b.id            AS brand_id,
                    b.brand_name,
                    m.generic_name,
                    m.salt,
                    m.dosage,
                    m.form,
                    b.mrp           AS brand_price,
                    m.jan_price     AS generic_price,
                    MIN(sub.rank)   AS best_rank,
                    sub.match_type
                FROM (
                    SELECT
                        m2.id       AS medicine_id,
                        b2.id       AS brand_id,
                        CASE
                            WHEN LOWER(m2.generic_name) = LOWER(%s)
                            THEN 0
                            ELSE 1
                        END         AS rank,
                        'generic'   AS match_type
                    FROM medicines m2
                    JOIN brands b2 ON b2.generic_id = m2.id
                    WHERE m2.generic_name ILIKE %s

                    UNION ALL

                    SELECT
                        m3.id       AS medicine_id,
                        b3.id       AS brand_id,
                        2           AS rank,
                        'brand'     AS match_type
                    FROM brands b3
                    JOIN medicines m3 ON m3.id = b3.generic_id
                    WHERE b3.brand_name ILIKE %s
                ) sub
                JOIN medicines m  ON m.id  = sub.medicine_id
                JOIN brands    b  ON b.id  = sub.brand_id
                GROUP BY m.id, b.id, sub.match_type
                ORDER BY best_rank ASC, m.generic_name ASC, b.brand_name ASC
            """
            params = (query, search_term, search_term)

        cur.execute(sql, params)
        rows = cur.fetchall()

        results = []
        for row in rows:
            brand_price   = row["brand_price"]
            generic_price = row["generic_price"]

            savings_percent = 0.0
            if brand_price and brand_price > 0:
                savings_percent = round(
                    ((brand_price - generic_price) / brand_price) * 100, 1
                )

            results.append({
                "medicine_id":     row["medicine_id"],
                "brand_name":      row["brand_name"],
                "generic_name":    row["generic_name"],
                "salt":            row["salt"],
                "dosage":          row["dosage"],
                "form":            row["form"],
                "brand_price":     brand_price,
                "generic_price":   generic_price,
                "savings_percent": savings_percent,
                "match_type":      row["match_type"],
            })

        return jsonify(results)

    finally:
        conn.close()