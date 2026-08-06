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
           from decision_engine import DecisionEngine
           from decision_engine.providers.ollama_provider import OllamaProvider

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
        Send a request to the AI provider and return a structured response.

        Args:
            request (dict): The decision request payload.
                Expected keys:
                    - "type"    : str  — The decision type.
                    - "context" : dict — Supporting data.
                    - "query"   : str  — Optional natural language query.

        Returns:
            dict: Must contain:
                - "result"   : any  — The AI provider's answer.
                - "confident": bool — Whether the provider is confident.
                - "message"  : str  — Human-readable explanation.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must implement the query() method."
        )

    def health_check(self) -> bool:
        """
        Optional health check to verify the provider is reachable.

        Override this method in your provider to implement a real check.
        Default implementation returns False (provider not configured).

        Returns:
            bool: True if the provider is reachable and ready, False otherwise.
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
        """
        Return a graceful unavailable response.

        Args:
            request (dict): Ignored. No AI provider is available.

        Returns:
            dict: A safe, low-confidence unavailable response.
        """
        logger.warning(
            "UnreachableAIProvider queried — no real AI provider is configured."
        )
        return {
            "result": None,
            "confident": False,
            "message": (
                "No AI provider is currently configured. "
                "The system is operating in rule-only mode. "
                "Configure an AI provider to enable intelligent escalation."
            ),
        }

    def health_check(self) -> bool:
        return False
