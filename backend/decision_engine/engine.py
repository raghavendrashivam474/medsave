"""
backend/decision_engine/engine.py

MedSave Hybrid Decision Engine
================================
Central routing layer for all recommendation and decision logic.

The Decision Engine is the single entry point for intelligent decisions.
All backend recommendation logic routes through this class.

Architecture:
    ┌─────────────────────────────────┐
    │         Decision Engine         │
    │                                 │
    │   Can Rules Answer?             │
    │         │                       │
    │  ┌──────┴──────┐                │
    │  │             │                │
    │ Rules      AI Interface         │
    │  │             │                │
    │  └──────┬──────┘                │
    │         ▼                       │
    │    Backend Response             │
    └─────────────────────────────────┘

Modes (set via DECISION_MODE environment variable):
    rule   : Use deterministic rules only. Default. No AI needed.
    ai     : Use AI provider only. Falls back to rules if no provider.
    hybrid : Try rules first. Escalate to AI if not confident.

Usage:
    from backend.decision_engine import DecisionEngine

    engine = DecisionEngine()
    result = engine.process({
        "type":    "cheapest_alternative",
        "context": {"medicine_name": "Paracetamol"},
    })

Response shape:
    {
        "result":       dict | None,  # Rule-specific result payload
        "confident":    bool,         # Whether the engine is confident
        "rule_matched": str | None,   # Name of matched rule or None
        "message":      str,          # Human-readable explanation
        "source":       str,          # "rule" or "ai"
        "mode":         str,          # Active DECISION_MODE
    }
"""

import logging
import os

from backend.decision_engine.providers.rule_provider import RuleProvider
from backend.decision_engine.providers.ai_provider import AIProviderBase

logger = logging.getLogger(__name__)

SUPPORTED_MODES = {"rule", "ai", "hybrid"}


class DecisionEngine:
    """
    Routes decision requests to the appropriate provider.

    Instantiate once at application startup and reuse across requests.
    Thread-safe — no mutable state is modified after __init__.

    Parameters
    ----------
    ai_provider : AIProviderBase or None
        Optional AI provider. When None, AI-mode requests fall back
        to the rule provider. Pass an AIProviderBase subclass instance
        to enable AI or hybrid mode.
    """

    def __init__(self, ai_provider: AIProviderBase | None = None):
        self.mode          = self._load_mode()
        self.rule_provider = RuleProvider()
        self.ai_provider   = ai_provider

        logger.info(
            "DecisionEngine initialized | mode=%s | ai_provider=%s",
            self.mode,
            type(self.ai_provider).__name__ if self.ai_provider else "None",
        )

    def _load_mode(self) -> str:
        """
        Read DECISION_MODE from the environment.

        Falls back to "rule" for unknown values.
        """
        raw = os.environ.get("DECISION_MODE", "rule").strip().lower()
        if raw not in SUPPORTED_MODES:
            logger.warning(
                "Unknown DECISION_MODE '%s'. Falling back to 'rule'.",
                raw,
            )
            return "rule"
        return raw

    def process(self, request: dict) -> dict:
        """
        Process a decision request and return a structured result.

        Parameters
        ----------
        request : dict
            Must be a dict. Must contain "type" key.
            May contain "context" dict with request-specific data.

        Returns
        -------
        dict
            Always returns a dict. Never raises unhandled exceptions.
            Shape: result, confident, rule_matched, message, source, mode.

        Raises
        ------
        ValueError
            If request is not a dict.
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

        # Defensive fallback — should never reach here
        return self._route_to_rules(request)

    def _route_to_rules(self, request: dict) -> dict:
        """Route the request directly to the RuleProvider."""
        logger.debug("Routing to RuleProvider.")
        result = self.rule_provider.evaluate(request)
        result["source"] = "rule"
        result["mode"]   = self.mode
        return result

    def _route_to_ai(self, request: dict) -> dict:
        """
        Route the request to the configured AI provider.

        Falls back to rules when no AI provider is configured.
        """
        if not self.ai_provider:
            logger.warning(
                "DECISION_MODE=ai but no AI provider is configured. "
                "Falling back to rule provider."
            )
            return self._route_to_rules(request)

        logger.debug(
            "Routing to AI Provider: %s",
            type(self.ai_provider).__name__,
        )
        result = self.ai_provider.query(request)
        result["source"] = "ai"
        result["mode"]   = self.mode
        return result

    def _route_hybrid(self, request: dict) -> dict:
        """
        Try rules first. Escalate to AI when rules are not confident.

        If AI is not configured and rules are not confident, returns
        the rule result with low confidence — never fails.
        """
        logger.debug("Hybrid routing: trying RuleProvider first.")

        rule_result = self.rule_provider.evaluate(request)
        rule_result["mode"] = self.mode

        if rule_result.get("confident", False):
            logger.debug("RuleProvider is confident. Returning rule result.")
            rule_result["source"] = "rule"
            return rule_result

        logger.debug("RuleProvider not confident. Attempting AI escalation.")

        if not self.ai_provider:
            logger.warning(
                "Hybrid mode: RuleProvider not confident but no AI provider "
                "is configured. Returning rule result with low confidence."
            )
            rule_result["source"] = "rule"
            return rule_result

        ai_result = self.ai_provider.query(request)
        ai_result["source"] = "ai"
        ai_result["mode"]   = self.mode
        return ai_result
