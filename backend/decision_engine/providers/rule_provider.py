"""
Rule Provider
=============
Deterministic rule-based decision engine for MedSave.

Sprint 2 — Real Implementation
-------------------------------
Rules are now connected to the real MedSave database.
All rules produce genuine recommendations from live data,
not placeholder strings.

Responsibilities:
    - Execute business logic rules against incoming requests.
    - Query the database for real medicine and brand data.
    - Produce structured, data-driven recommendations.
    - Signal confidence level so the Decision Engine can escalate.

Rules (Sprint 2):
    _rule_cheapest_alternative    : Find cheapest branded alternative for a generic.
    _rule_best_savings            : Find the brand with the highest savings percent.
    _rule_generic_available       : Confirm a generic medicine exists in the database.
    _rule_out_of_stock_warning    : Warn when no brands exist for a generic.
    _rule_brand_alternatives      : List all brands for a given generic medicine.
    _rule_recommendation_score    : Score and rank brands by savings and price.

Design:
    Rules are explicit, auditable, and offline-capable.
    No external service or API key is required.
    All rules use the shared get_db_connection() factory.

Extending Rules:
    Add new rule methods following the pattern:
        def _rule_<name>(self, request: dict) -> dict | None

    Register them inside RULE_REGISTRY in __init__().
    Return None if the rule does not apply to the given request.
    Return a result dict if the rule fires.

Confidence:
    confident=True  -> Decision Engine will use this result directly.
    confident=False -> In hybrid mode, Decision Engine may escalate to AI.

Request format:
    {
        "type":    "cheapest_alternative" | "best_savings" | "generic_check"
                   | "stock_check" | "brand_alternatives" | "recommendation_score",
        "context": {
            "medicine_name": str,   # generic name
            "medicine_id":   int,   # primary key (optional, preferred)
            "location":      str,   # for stock_check
        }
    }
"""

import logging
import sqlite3

from backend.database.connection import get_db_connection

logger = logging.getLogger(__name__)


class RuleProvider:
    """
    Executes deterministic rules and returns structured decisions.

    Each rule is a method that inspects the request and either
    returns a result dict or returns None to indicate it does not apply.

    Rules are evaluated in the order they appear in RULE_REGISTRY.
    The first rule that returns a result wins.
    """

    def __init__(self):
        self.RULE_REGISTRY = [
            self._rule_cheapest_alternative,
            self._rule_best_savings,
            self._rule_generic_available,
            self._rule_out_of_stock_warning,
            self._rule_brand_alternatives,
            self._rule_recommendation_score,
        ]

        logger.info(
            "RuleProvider initialized | active_rules=%d",
            len(self.RULE_REGISTRY),
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def evaluate(self, request: dict) -> dict:
        """
        Evaluate all rules against the request.

        Iterates RULE_REGISTRY in order. Returns the first rule result
        that is not None. Falls through to _no_match_response() if
        no rule applies.

        Parameters
        ----------
        request : dict
            Must contain "type". May contain "context".

        Returns
        -------
        dict
            Contains: result, confident, rule_matched, message.
            Source and mode are added by the Decision Engine.
        """
        logger.debug(
            "RuleProvider.evaluate() called | request_type=%s",
            request.get("type", "unknown"),
        )

        for rule in self.RULE_REGISTRY:
            result = rule(request)
            if result is not None:
                logger.debug("Rule matched: %s", rule.__name__)
                result["rule_matched"] = rule.__name__
                return result

        logger.debug(
            "No rule matched for request: %s",
            request.get("type"),
        )
        return self._no_match_response()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_medicine_row(context: dict):
        """
        Fetch a medicine row from the database.

        Tries medicine_id first (exact), then falls back to
        case-insensitive generic_name match.

        Returns the row dict or None if not found.
        """
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            is_sqlite = isinstance(conn, sqlite3.Connection)
            ph = "?" if is_sqlite else "%s"

            medicine_id = context.get("medicine_id")
            if medicine_id:
                cur.execute(
                    f"SELECT * FROM medicines WHERE id = {ph}",
                    (medicine_id,),
                )
                row = cur.fetchone()
                if row:
                    return dict(row)

            medicine_name = context.get("medicine_name", "").strip()
            if medicine_name:
                if is_sqlite:
                    cur.execute(
                        f"SELECT * FROM medicines WHERE LOWER(generic_name) = LOWER({ph})",
                        (medicine_name,),
                    )
                else:
                    cur.execute(
                        f"SELECT * FROM medicines WHERE generic_name ILIKE {ph}",
                        (medicine_name,),
                    )
                row = cur.fetchone()
                if row:
                    return dict(row)

            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def _get_brands_for_medicine(medicine_id: int) -> list:
        """
        Fetch all brands for a given medicine_id, ordered by mrp ASC.

        Returns a list of dicts. Empty list if no brands exist.
        """
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            is_sqlite = isinstance(conn, sqlite3.Connection)
            ph = "?" if is_sqlite else "%s"

            cur.execute(
                f"""
                SELECT id, brand_name, mrp, manufacturer
                FROM brands
                WHERE generic_id = {ph}
                ORDER BY mrp ASC
                """,
                (medicine_id,),
            )
            return [dict(r) for r in cur.fetchall()]
        finally:
            if conn:
                conn.close()

    @staticmethod
    def _calculate_savings(jan_price: float, mrp: float):
        """
        Return (savings, savings_percent) for one brand comparison.

        Returns (None, None) when prices are missing or not positive.
        Returns (0, 0.0) when savings are zero or negative.
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

    # ------------------------------------------------------------------
    # Rules
    # ------------------------------------------------------------------

    def _rule_cheapest_alternative(self, request: dict) -> dict | None:
        """
        Find the cheapest branded alternative for a generic medicine.

        Fires when request type is "cheapest_alternative".

        Returns the brand with the lowest MRP along with savings
        calculated against the Jan Aushadhi generic price.

        Confident: True when a medicine and at least one brand exist.
        Confident: False when medicine is not found or has no brands.
        """
        if request.get("type") != "cheapest_alternative":
            return None

        context = request.get("context", {})
        medicine_name = context.get("medicine_name", "Unknown")

        logger.debug(
            "_rule_cheapest_alternative fired for medicine: %s",
            medicine_name,
        )

        medicine = self._get_medicine_row(context)

        if not medicine:
            return {
                "result":    None,
                "confident": False,
                "message":   f"Generic medicine '{medicine_name}' not found in database.",
            }

        brands = self._get_brands_for_medicine(medicine["id"])

        if not brands:
            return {
                "result":    None,
                "confident": False,
                "message":   (
                    f"No branded alternatives found for '{medicine['generic_name']}'. "
                    f"Jan Aushadhi price: ₹{medicine['jan_price']}"
                ),
            }

        # brands are already sorted by mrp ASC — first is cheapest
        cheapest = brands[0]
        savings, savings_percent = self._calculate_savings(
            medicine["jan_price"], cheapest["mrp"]
        )

        return {
            "result": {
                "recommendation":  "cheapest_alternative",
                "generic_name":    medicine["generic_name"],
                "generic_price":   medicine["jan_price"],
                "brand_id":        cheapest["id"],
                "brand_name":      cheapest["brand_name"],
                "brand_price":     cheapest["mrp"],
                "manufacturer":    cheapest["manufacturer"],
                "savings":         savings,
                "savings_percent": savings_percent,
            },
            "confident": True,
            "message":   (
                f"Cheapest alternative for '{medicine['generic_name']}' is "
                f"'{cheapest['brand_name']}' at ₹{cheapest['mrp']}. "
                f"Save ₹{savings} ({savings_percent}%) vs branded price."
            ),
        }

    def _rule_best_savings(self, request: dict) -> dict | None:
        """
        Find the brand offering the highest savings percentage.

        Fires when request type is "best_savings".

        Compares all brands for a generic and returns the one where
        (brand_mrp - jan_price) / brand_mrp is maximised.

        Confident: True when medicine and at least one brand exist.
        Confident: False when medicine not found or no brands.
        """
        if request.get("type") != "best_savings":
            return None

        context = request.get("context", {})
        medicine_name = context.get("medicine_name", "Unknown")

        logger.debug(
            "_rule_best_savings fired for medicine: %s",
            medicine_name,
        )

        medicine = self._get_medicine_row(context)

        if not medicine:
            return {
                "result":    None,
                "confident": False,
                "message":   f"Generic medicine '{medicine_name}' not found in database.",
            }

        brands = self._get_brands_for_medicine(medicine["id"])

        if not brands:
            return {
                "result":    None,
                "confident": False,
                "message":   (
                    f"No branded alternatives found for '{medicine['generic_name']}'."
                ),
            }

        # Score every brand and pick the one with highest savings_percent
        best = None
        best_pct = -1.0

        for brand in brands:
            savings, savings_pct = self._calculate_savings(
                medicine["jan_price"], brand["mrp"]
            )
            if savings_pct is not None and savings_pct > best_pct:
                best_pct = savings_pct
                best = {**brand, "savings": savings, "savings_percent": savings_pct}

        if best is None:
            return {
                "result":    None,
                "confident": False,
                "message":   (
                    f"Could not calculate savings for '{medicine['generic_name']}'."
                ),
            }

        return {
            "result": {
                "recommendation":  "best_savings",
                "generic_name":    medicine["generic_name"],
                "generic_price":   medicine["jan_price"],
                "brand_id":        best["id"],
                "brand_name":      best["brand_name"],
                "brand_price":     best["mrp"],
                "manufacturer":    best["manufacturer"],
                "savings":         best["savings"],
                "savings_percent": best["savings_percent"],
            },
            "confident": True,
            "message":   (
                f"Best savings for '{medicine['generic_name']}' is "
                f"'{best['brand_name']}' — save {best['savings_percent']}% "
                f"(₹{best['savings']}) by choosing Jan Aushadhi generic."
            ),
        }

    def _rule_generic_available(self, request: dict) -> dict | None:
        """
        Confirm whether a generic medicine exists in the database.

        Fires when request type is "generic_check".

        Returns availability status and the Jan Aushadhi price
        when the medicine is found.

        Confident: True always — database presence is deterministic.
        """
        if request.get("type") != "generic_check":
            return None

        context = request.get("context", {})
        medicine_name = context.get("medicine_name", "Unknown")

        logger.debug(
            "_rule_generic_available fired for medicine: %s",
            medicine_name,
        )

        medicine = self._get_medicine_row(context)

        if medicine:
            return {
                "result": {
                    "recommendation":    "generic_available",
                    "generic_name":      medicine["generic_name"],
                    "generic_available": True,
                    "medicine_id":       medicine["id"],
                    "jan_price":         medicine["jan_price"],
                    "dosage":            medicine["dosage"],
                    "form":              medicine["form"],
                },
                "confident": True,
                "message":   (
                    f"'{medicine['generic_name']}' is available as a Jan Aushadhi "
                    f"generic at ₹{medicine['jan_price']} per {medicine['form']}."
                ),
            }

        return {
            "result": {
                "recommendation":    "generic_not_found",
                "generic_name":      medicine_name,
                "generic_available": False,
                "medicine_id":       None,
                "jan_price":         None,
                "dosage":            None,
                "form":              None,
            },
            "confident": True,
            "message":   (
                f"'{medicine_name}' was not found in the Jan Aushadhi database. "
                f"It may be available under a different name or dosage."
            ),
        }

    def _rule_out_of_stock_warning(self, request: dict) -> dict | None:
        """
        Warn when a generic medicine has no associated brands in the database.

        Fires when request type is "stock_check".

        Checks whether any brand records exist for the given medicine.
        This is a proxy for availability — if no brands are listed,
        the medicine may not be widely stocked.

        Confident: True when medicine is found (answer is definitive).
        Confident: False when medicine itself is not found.
        """
        if request.get("type") != "stock_check":
            return None

        context = request.get("context", {})
        medicine_name = context.get("medicine_name", "Unknown")
        location = context.get("location", "Unknown")

        logger.debug(
            "_rule_out_of_stock_warning fired | medicine=%s | location=%s",
            medicine_name,
            location,
        )

        medicine = self._get_medicine_row(context)

        if not medicine:
            return {
                "result": {
                    "recommendation": "medicine_not_found",
                    "medicine":       medicine_name,
                    "location":       location,
                    "in_stock":       None,
                },
                "confident": False,
                "message":   (
                    f"'{medicine_name}' not found in database. "
                    f"Cannot determine stock status."
                ),
            }

        brands = self._get_brands_for_medicine(medicine["id"])
        in_stock = len(brands) > 0

        return {
            "result": {
                "recommendation": "stock_check",
                "medicine":       medicine["generic_name"],
                "medicine_id":    medicine["id"],
                "location":       location,
                "in_stock":       in_stock,
                "brand_count":    len(brands),
            },
            "confident": True,
            "message":   (
                f"'{medicine['generic_name']}' has {len(brands)} branded alternative(s) "
                f"in the database. "
                + (
                    "Likely available at Jan Aushadhi stores."
                    if in_stock
                    else "No brands found — may not be stocked at all locations."
                )
            ),
        }

    def _rule_brand_alternatives(self, request: dict) -> dict | None:
        """
        List all branded alternatives for a generic medicine.

        Fires when request type is "brand_alternatives".

        Returns all brands with savings calculations, ordered by price.
        Useful for building comparison displays in the frontend.

        Confident: True when medicine is found.
        Confident: False when medicine is not found.
        """
        if request.get("type") != "brand_alternatives":
            return None

        context = request.get("context", {})
        medicine_name = context.get("medicine_name", "Unknown")

        logger.debug(
            "_rule_brand_alternatives fired for medicine: %s",
            medicine_name,
        )

        medicine = self._get_medicine_row(context)

        if not medicine:
            return {
                "result":    None,
                "confident": False,
                "message":   f"Generic medicine '{medicine_name}' not found in database.",
            }

        brands = self._get_brands_for_medicine(medicine["id"])

        enriched_brands = []
        for brand in brands:
            savings, savings_pct = self._calculate_savings(
                medicine["jan_price"], brand["mrp"]
            )
            enriched_brands.append({
                "brand_id":        brand["id"],
                "brand_name":      brand["brand_name"],
                "brand_price":     brand["mrp"],
                "manufacturer":    brand["manufacturer"],
                "savings":         savings,
                "savings_percent": savings_pct,
            })

        return {
            "result": {
                "recommendation": "brand_alternatives",
                "generic_name":   medicine["generic_name"],
                "generic_price":  medicine["jan_price"],
                "medicine_id":    medicine["id"],
                "brand_count":    len(enriched_brands),
                "brands":         enriched_brands,
            },
            "confident": True,
            "message":   (
                f"Found {len(enriched_brands)} branded alternative(s) for "
                f"'{medicine['generic_name']}'. "
                f"Jan Aushadhi price: ₹{medicine['jan_price']}."
            ),
        }

    def _rule_recommendation_score(self, request: dict) -> dict | None:
        """
        Score and rank all brands for a generic medicine.

        Fires when request type is "recommendation_score".

        Scoring criteria (100 points total):
            savings_score : 70 points — based on savings_percent / max_savings_percent
            price_score   : 30 points — based on (1 - mrp / max_mrp)

        Brands are ranked by score descending.
        The top-ranked brand is marked as the recommended choice.

        Confident: True when medicine and brands are found.
        Confident: False when medicine or brands are not found.
        """
        if request.get("type") != "recommendation_score":
            return None

        context = request.get("context", {})
        medicine_name = context.get("medicine_name", "Unknown")

        logger.debug(
            "_rule_recommendation_score fired for medicine: %s",
            medicine_name,
        )

        medicine = self._get_medicine_row(context)

        if not medicine:
            return {
                "result":    None,
                "confident": False,
                "message":   f"Generic medicine '{medicine_name}' not found in database.",
            }

        brands = self._get_brands_for_medicine(medicine["id"])

        if not brands:
            return {
                "result":    None,
                "confident": False,
                "message":   (
                    f"No brands found for '{medicine['generic_name']}'. "
                    f"Cannot produce recommendation scores."
                ),
            }

        # Calculate savings for every brand
        scored = []
        for brand in brands:
            savings, savings_pct = self._calculate_savings(
                medicine["jan_price"], brand["mrp"]
            )
            scored.append({
                "brand_id":        brand["id"],
                "brand_name":      brand["brand_name"],
                "brand_price":     brand["mrp"],
                "manufacturer":    brand["manufacturer"],
                "savings":         savings,
                "savings_percent": savings_pct if savings_pct is not None else 0.0,
            })

        max_savings_pct = max(b["savings_percent"] for b in scored) or 1.0
        max_mrp = max(b["brand_price"] for b in scored) or 1.0

        for brand in scored:
            savings_score = (brand["savings_percent"] / max_savings_pct) * 70
            price_score   = (1 - brand["brand_price"] / max_mrp) * 30
            brand["score"] = round(savings_score + price_score, 1)

        scored.sort(key=lambda b: b["score"], reverse=True)

        # Mark top brand as recommended
        if scored:
            scored[0]["recommended"] = True
        for brand in scored[1:]:
            brand["recommended"] = False

        return {
            "result": {
                "recommendation": "recommendation_score",
                "generic_name":   medicine["generic_name"],
                "generic_price":  medicine["jan_price"],
                "medicine_id":    medicine["id"],
                "brand_count":    len(scored),
                "brands":         scored,
                "top_pick":       scored[0]["brand_name"] if scored else None,
            },
            "confident": True,
            "message":   (
                f"Scored {len(scored)} brand(s) for '{medicine['generic_name']}'. "
                f"Top recommendation: '{scored[0]['brand_name']}' "
                f"(score: {scored[0]['score']}/100)."
            ),
        }

    # ------------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------------

    def _no_match_response(self) -> dict:
        """
        Return a standard no-match response when no rule fires.

        This is never an error — it means the request type is not
        handled by any current rule. The Decision Engine will
        escalate to AI in hybrid mode.
        """
        return {
            "result":       None,
            "confident":    False,
            "rule_matched": None,
            "message":      (
                "No deterministic rule matched this request. "
                "Consider escalating to an AI provider or adding a new rule."
            ),
        }
