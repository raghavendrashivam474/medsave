"""
AI Provider Interface
=====================
Abstract base class for all future AI provider integrations in MedSave.

Purpose:
    Define a stable contract that any AI provider must fulfill.
    The Decision Engine depends only on this interface, never on
    a specific provider implementation.

Design Principle:
    AI is an enhancement, not a dependency.
    The system must function fully without any AI provider configured.

How to Add a Provider:
    1. Create a new file, e.g.:
           decision_engine/providers/ollama_provider.py
           decision_engine/providers/openai_provider.py

    2. Subclass AIProviderBase and implement the query() method.

    3. Pass your provider instance to DecisionEngine() at startup:
           from backend.decision_engine import DecisionEngine
           from backend.decision_engine.providers.ollama_provider import OllamaProvider

           engine = DecisionEngine(ai_provider=OllamaProvider())

    4. No changes to the Decision Engine are required.

Providers NOT implemented in this sprint:
    - OpenAI
    - Gemini
    - Ollama
    - Any local model

This file is intentionally kept as an interface only.
"""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AIProviderBase(ABC):
    """
    Abstract base class for MedSave AI providers.

    All AI providers must inherit from this class and implement
    the query() method. This ensures the Decision Engine can swap
    providers without any internal changes.

    Contract:
        - query() receives the same request dict as the Decision Engine.
        - query() must return a dict with at least "result" and "confident".
        - Providers must not raise unhandled exceptions — catch and return
          a graceful error response instead.
    """

    @abstractmethod
    def query(self, request: dict) -> dict:
        """
        Process a decision request and return a structured result.

        Parameters
        ----------
        request : dict
            The same request dict passed to DecisionEngine.process().
            Must contain at least a "type" key.

        Returns
        -------
        dict
            Must contain:
                result    : The recommendation or decision output.
                confident : bool — whether the provider is confident.
            May contain:
                message   : Human-readable explanation.
                source    : Will be set by the Decision Engine.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must implement the query() method."
        )

    def health_check(self) -> bool:
        """
        Return True if the provider is reachable and operational.

        Default implementation returns False.
        Concrete providers should override this.
        """
        logger.debug(
            "%s.health_check() called — default implementation returns False.",
            type(self).__name__,
        )
        return False

    def __repr__(self) -> str:
        return f"<AIProvider: {type(self).__name__}>"


class UnreachableAIProvider(AIProviderBase):
    """
    Placeholder AI provider used when no real provider is configured.

    Returns a graceful not-available response without raising exceptions.
    This allows the Decision Engine to handle the no-AI case cleanly.

    This class is for internal use by the Decision Engine only.
    Do not configure this as an intentional provider.
    """

    def query(self, request: dict) -> dict:
        logger.warning(
            "UnreachableAIProvider queried — no real AI provider is configured."
        )
        return {
            "result":    None,
            "confident": False,
            "message":   (
                "No AI provider is currently configured. "
                "The system is operating in rule-only mode. "
                "Configure an AI provider to enable intelligent escalation."
            ),
        }

    def health_check(self) -> bool:
        return False
