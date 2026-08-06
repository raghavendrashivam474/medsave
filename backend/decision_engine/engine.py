"""
Decision Engine
===============
Core routing layer for MedSave intelligence.

Responsibilities:
    - Receive incoming decision requests.
    - Inspect the current DECISION_MODE configuration.
    - Route to the Rule Provider or AI Provider accordingly.
    - Return a unified response to the caller.

Configuration:
    Set the DECISION_MODE environment variable to control behavior.

    DECISION_MODE=rule    -> Use deterministic rules only (default).
    DECISION_MODE=ai      -> Use AI provider only.
    DECISION_MODE=hybrid  -> Try rules first, fall back to AI.

Extension:
    To add a new AI provider, implement the AIProviderBase interface
    inside decision_engine/providers/ and update the configuration loader.
    No changes to this file are required.
"""

import os
import logging
from .providers.rule_provider import RuleProvider
from .providers.ai_provider import AIProviderBase

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Central decision router for MedSave.

    This class is the single entry point for all intelligent decisions.
    It reads DECISION_MODE from the environment and delegates accordingly.

    Attributes:
        mode (str): The active decision mode. Defaults to "rule".
        rule_provider (RuleProvider): The deterministic rule engine.
        ai_provider (AIProviderBase or None): The active AI provider, if any.
    """

    SUPPORTED_MODES = {"rule", "ai", "hybrid"}

    def __init__(self, ai_provider: AIProviderBase = None):
        """
        Initialize the Decision Engine.

        Args:
            ai_provider (AIProviderBase, optional):
                An AI provider instance implementing AIProviderBase.
                If None, AI routing will be unavailable even in hybrid mode.
        """
        self.mode = self._load_mode()
        self.rule_provider = RuleProvider()
        self.ai_provider = ai_provider

        logger.info(
            "DecisionEngine initialized | mode=%s | ai_provider=%s",
            self.mode,
            type(self.ai_provider).__name__ if self.ai_provider else "None",
        )

    def _load_mode(self) -> str:
        """
        Load and validate DECISION_MODE from environment.

        Returns:
            str: One of "rule", "ai", or "hybrid". Defaults to "rule".
        """
        raw = os.environ.get("DECISION_MODE", "rule").strip().lower()

        if raw not in self.SUPPORTED_MODES:
            logger.warning(
                "Unknown DECISION_MODE '%s'. Falling back to 'rule'.", raw
            )
            return "rule"

        return raw

    def process(self, request: dict) -> dict:
        """
        Process a decision request and return a unified response.

        This is the main entry point. Call this method from any part
        of the application that needs an intelligent decision.

        Args:
            request (dict): The decision request payload.
                Expected keys may include:
                    - "type"    : str  — The type of decision requested.
                    - "context" : dict — Supporting data for the decision.
                    - "query"   : str  — A natural language query (future use).

        Returns:
            dict: A unified response containing:
                - "source"   : str  — Which provider answered ("rule" or "ai").
                - "result"   : any  — The decision result.
                - "confident": bool — Whether the provider is confident.
                - "mode"     : str  — The active DECISION_MODE.

        Raises:
            ValueError: If the request payload is missing or not a dict.
        """
        if not isinstance(request, dict):
            raise ValueError("DecisionEngine.process() expects a dict payload.")

        logger.debug("DecisionEngine.process() called | mode=%s", self.mode)

        if self.mode == "rule":
            return self._route_to_rules(request)

        if self.mode == "ai":
            return self._route_to_ai(request)

        if self.mode == "hybrid":
            return self._route_hybrid(request)

        # Fallback — should never reach here
        return self._route_to_rules(request)

    def _route_to_rules(self, request: dict) -> dict:
        """
        Delegate entirely to the Rule Provider.

        Args:
            request (dict): The incoming decision request.

        Returns:
            dict: Response from the Rule Provider with source tagged as "rule".
        """
        logger.debug("Routing to RuleProvider.")
        result = self.rule_provider.evaluate(request)
        result["source"] = "rule"
        result["mode"] = self.mode
        return result

    def _route_to_ai(self, request: dict) -> dict:
        """
        Delegate entirely to the AI Provider.

        If no AI provider is configured, falls back to rules gracefully.

        Args:
            request (dict): The incoming decision request.

        Returns:
            dict: Response from the AI Provider with source tagged as "ai".
        """
        if self.ai_provider is None:
            logger.warning(
                "DECISION_MODE=ai but no AI provider is configured. "
                "Falling back to rule provider."
            )
            return self._route_to_rules(request)

        logger.debug("Routing to AI Provider: %s", type(self.ai_provider).__name__)
        result = self.ai_provider.query(request)
        result["source"] = "ai"
        result["mode"] = self.mode
        return result

    def _route_hybrid(self, request: dict) -> dict:
        """
        Try Rule Provider first. If not confident, escalate to AI Provider.

        Hybrid routing logic:
            1. Ask the Rule Provider to evaluate.
            2. If confident -> return rule result immediately.
            3. If not confident and AI provider exists -> escalate to AI.
            4. If not confident and no AI provider -> return rule result anyway.

        Args:
            request (dict): The incoming decision request.

        Returns:
            dict: Response from whichever provider answered.
        """
        logger.debug("Hybrid routing: trying RuleProvider first.")
        rule_result = self.rule_provider.evaluate(request)
        rule_result["mode"] = self.mode

        if rule_result.get("confident", False):
            logger.debug("RuleProvider is confident. Returning rule result.")
            rule_result["source"] = "rule"
            return rule_result

        logger.debug(
            "RuleProvider not confident. Attempting AI escalation."
        )

        if self.ai_provider is None:
            logger.warning(
                "Hybrid mode: RuleProvider not confident but no AI provider "
                "is configured. Returning rule result with low confidence."
            )
            rule_result["source"] = "rule"
            return rule_result

        ai_result = self.ai_provider.query(request)
        ai_result["source"] = "ai"
        ai_result["mode"] = self.mode
        return ai_result
