"""
backend/api/recommendations.py

Medicine recommendation endpoint for the MedSave backend.

This is the primary integration point between the Decision Engine
and the frontend. All recommendation logic routes through the
Decision Engine rather than standalone helper functions.

Endpoints
---------
POST /api/recommendations
    Process a recommendation request through the Decision Engine.

    Request body (JSON):
        {
            "type":    "cheapest_alternative" | "best_savings"
                       | "generic_check" | "stock_check"
                       | "brand_alternatives" | "recommendation_score",
            "context": {
                "medicine_name": "Paracetamol",
                "medicine_id":   1,
                "location":      "Noida"
            }
        }

    Response (200):
        {
            "success":      true,
            "result":       { ... },
            "confident":    true,
            "rule_matched": "_rule_cheapest_alternative",
            "message":      "Cheapest alternative for ...",
            "source":       "rule",
            "mode":         "rule"
        }

    Response (400) — bad request body:
        {
            "success": false,
            "message": "Request body must be JSON with a 'type' field.",
            "error":   "BAD_REQUEST"
        }

    Response (500) — unexpected failure:
        {
            "success": false,
            "message": "An unexpected error occurred.",
            "error":   "SERVER_ERROR"
        }

GET /api/recommendations/health
    Verify that the Decision Engine is operational.

    Response (200):
        {
            "success": true,
            "engine":  "operational",
            "mode":    "rule",
            "rules":   6
        }

Design notes
------------
- The Decision Engine instance is created once at module load.
  This is safe — DecisionEngine holds no mutable per-request state.

- Request validation happens before the engine is called.
  The engine itself also validates but API validation is clearer.

- VALID_TYPES is the canonical list of supported request types.
  Adding a new rule to RuleProvider does not require updating this
  list unless the frontend needs to call it. This list protects
  the API contract.
"""

import logging

from flask import Blueprint, jsonify, request as flask_request

from backend.decision_engine import DecisionEngine

logger = logging.getLogger(__name__)

recommendations_bp = Blueprint("recommendations", __name__)

# -----------------------------------------------------------------------
# Engine — created once at module load, reused across requests
# -----------------------------------------------------------------------

_engine = DecisionEngine()

# -----------------------------------------------------------------------
# Valid request types — matches RuleProvider rules
# -----------------------------------------------------------------------

VALID_TYPES = {
    "cheapest_alternative",
    "best_savings",
    "generic_check",
    "stock_check",
    "brand_alternatives",
    "recommendation_score",
}


# -----------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------

@recommendations_bp.route("/api/recommendations", methods=["POST"])
def get_recommendation():
    """
    Process a recommendation request through the Decision Engine.

    Accepts JSON body with "type" and optional "context".
    Routes through DecisionEngine.process() which dispatches to
    RuleProvider or AI provider based on DECISION_MODE.
    """
    try:
        body = flask_request.get_json(silent=True)

        if not body or not isinstance(body, dict):
            return jsonify({
                "success": False,
                "message": "Request body must be JSON with a 'type' field.",
                "error":   "BAD_REQUEST",
            }), 400

        request_type = body.get("type", "").strip()

        if not request_type:
            return jsonify({
                "success": False,
                "message": "Field 'type' is required.",
                "error":   "BAD_REQUEST",
            }), 400

        if request_type not in VALID_TYPES:
            return jsonify({
                "success": False,
                "message": (
                    f"Unknown request type '{request_type}'. "
                    f"Valid types: {sorted(VALID_TYPES)}."
                ),
                "error":   "BAD_REQUEST",
            }), 400

        engine_request = {
            "type":    request_type,
            "context": body.get("context", {}),
        }

        engine_result = _engine.process(engine_request)

        return jsonify({
            "success": True,
            **engine_result,
        }), 200

    except Exception:
        logger.exception("POST /api/recommendations failed")
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred.",
            "error":   "SERVER_ERROR",
        }), 500


@recommendations_bp.route("/api/recommendations/health", methods=["GET"])
def recommendations_health():
    """
    Verify that the Decision Engine is operational.

    Returns engine mode and active rule count.
    """
    try:
        rule_count = len(_engine.rule_provider.RULE_REGISTRY)
        return jsonify({
            "success": True,
            "engine":  "operational",
            "mode":    _engine.mode,
            "rules":   rule_count,
        }), 200
    except Exception:
        logger.exception("GET /api/recommendations/health failed")
        return jsonify({
            "success": False,
            "engine":  "error",
        }), 500
