"""
Rule Provider
=============
Deterministic rule-based decision engine for MedSave.

Responsibilities:
    - Execute business logic rules against incoming requests.
    - Produce structured recommendations.
    - Signal confidence level so the Decision Engine can escalate if needed.

Design:
    Rules are explicit, auditable, and offline-capable.
    No external service or API key is required.

Extending Rules:
    Add new rule methods following the pattern:
        def _rule_<name>(self, request: dict) -> dict | None

    Register them inside the RULE_REGISTRY in __init__().
    Return None if the rule does not apply to the given request.
    Return a result dict if the rule fires.

Confidence:
    confident=True  -> Decision Engine will use this result directly.
    confident=False -> In hybrid mode, Decision Engine may escalate to AI.
"""

import logging

logger = logging.getLogger(__name__)


class RuleProvider:
    """
    Executes deterministic rules and returns structured decisions.

    Each rule is a method that inspects the request and either
    returns a result or returns None to indicate it does not apply.

    Rules are evaluated in the order they appear in RULE_REGISTRY.
    The first rule that returns a result wins.
    """

    def __init__(self):
        """
        Initialize the Rule Provider and register all active rules.

        Add new rule methods to RULE_REGISTRY to activate them.
        Rules are evaluated in list order — place higher-priority rules first.
        """
        self.RULE_REGISTRY = [
            self._rule_cheapest_alternative,
            self._rule_generic_available,
            self._rule_out_of_stock_warning,
        ]

        logger.info(
            "RuleProvider initialized | active_rules=%d", len(self.RULE_REGISTRY)
        )

    def evaluate(self, request: dict) -> dict:
        """
        Evaluate all registered rules against the incoming request.

        Iterates through the rule registry in order. Returns the result
        of the first rule that applies. If no rule matches, returns a
        default low-confidence response.

        Args:
            request (dict): The decision request payload.
                Expected keys:
                    - "type"    : str  — Decision type identifier.
                    - "context" : dict — Supporting data.

        Returns:
            dict: Decision result containing:
                - "result"      : any  — The decision output.
                - "confident"   : bool — Confidence flag.
                - "rule_matched": str  — Name of the rule that fired, or None.
                - "message"     : str  — Human-readable explanation.
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

        logger.debug("No rule matched for request: %s", request.get("type"))
        return self._no_match_response()

    # ------------------------------------------------------------------
    # Rule Implementations
    # ------------------------------------------------------------------

    def _rule_cheapest_alternative(self, request: dict) -> dict | None:
        """
        Rule: Recommend the cheapest available alternative for a medicine.

        Fires when:
            request["type"] == "cheapest_alternative"

        Args:
            request (dict): Must contain type and context with medicine data.

        Returns:
            dict | None: Result if rule applies, None otherwise.
        """
        if request.get("type") != "cheapest_alternative":
            return None

        context = request.get("context", {})
        medicine_name = context.get("medicine_name", "Unknown")

        # Placeholder logic — replace with real database query
        # when medicine repository integration is added.
        logger.debug(
            "_rule_cheapest_alternative fired for medicine: %s", medicine_name
        )

        return {
            "result": {
                "recommendation": "cheapest_alternative",
                "medicine": medicine_name,
                "note": "Rule fired. Connect to medicine repository for real data.",
            },
            "confident": True,
            "message": (
                f"Cheapest alternative rule evaluated for '{medicine_name}'."
            ),
        }

    def _rule_generic_available(self, request: dict) -> dict | None:
        """
        Rule: Check whether a generic version of a medicine is available.

        Fires when:
            request["type"] == "generic_check"

        Args:
            request (dict): Must contain type and context with medicine data.

        Returns:
            dict | None: Result if rule applies, None otherwise.
        """
        if request.get("type") != "generic_check":
            return None

        context = request.get("context", {})
        medicine_name = context.get("medicine_name", "Unknown")

        logger.debug(
            "_rule_generic_available fired for medicine: %s", medicine_name
        )

        return {
            "result": {
                "recommendation": "generic_check",
                "medicine": medicine_name,
                "generic_available": None,
                "note": "Rule fired. Connect to medicine repository for real data.",
            },
            "confident": True,
            "message": (
                f"Generic availability rule evaluated for '{medicine_name}'."
            ),
        }

    def _rule_out_of_stock_warning(self, request: dict) -> dict | None:
        """
        Rule: Warn if a medicine may be out of stock at nearby stores.

        Fires when:
            request["type"] == "stock_check"

        Args:
            request (dict): Must contain type and context with location data.

        Returns:
            dict | None: Result if rule applies, None otherwise.
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

        return {
            "result": {
                "recommendation": "stock_check",
                "medicine": medicine_name,
                "location": location,
                "in_stock": None,
                "note": "Rule fired. Connect to store repository for real data.",
            },
            "confident": False,
            "message": (
                f"Stock check rule evaluated for '{medicine_name}' "
                f"at location '{location}'. Confidence is low without live data."
            ),
        }

    # ------------------------------------------------------------------
    # Default Response
    # ------------------------------------------------------------------

    def _no_match_response(self) -> dict:
        """
        Return a default response when no rule matches the request.

        Returns:
            dict: Low-confidence empty result indicating no rule fired.
        """
        return {
            "result": None,
            "confident": False,
            "rule_matched": None,
            "message": (
                "No deterministic rule matched this request. "
                "Consider escalating to an AI provider or adding a new rule."
            ),
        }
