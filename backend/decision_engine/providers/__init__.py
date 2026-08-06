"""
Decision Engine Providers
=========================
Contains all provider implementations for the Decision Engine.

Providers:
    - RuleProvider   : Deterministic rule-based decisions (active).
    - AIProviderBase : Abstract interface for future AI providers (placeholder).

To add a new provider:
    1. Create a new file inside this directory.
    2. Implement the AIProviderBase interface.
    3. Pass your provider instance to DecisionEngine() at startup.
    4. No other changes are required.
"""

from backend.decision_engine.providers.rule_provider import RuleProvider
from backend.decision_engine.providers.ai_provider import AIProviderBase

__all__ = ["RuleProvider", "AIProviderBase"]
