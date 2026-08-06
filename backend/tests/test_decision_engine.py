"""
Decision Engine Tests
=====================
Tests for the MedSave Hybrid Decision Engine.

Coverage:
    - DecisionEngine routing in all three modes.
    - RuleProvider rule matching and no-match fallback.
    - AIProviderBase interface enforcement.
    - UnreachableAIProvider graceful fallback.
    - Configuration loading and invalid mode handling.

Run with:
    pytest tests/test_decision_engine.py -v
"""

import os
import pytest
from unittest.mock import patch

from decision_engine import DecisionEngine
from decision_engine.providers.rule_provider import RuleProvider
from decision_engine.providers.ai_provider import AIProviderBase, UnreachableAIProvider


# ==============================================================
# Fixtures
# ==============================================================

@pytest.fixture
def rule_engine():
    """Decision Engine in rule mode (default)."""
    with patch.dict(os.environ, {"DECISION_MODE": "rule"}):
        return DecisionEngine()


@pytest.fixture
def hybrid_engine():
    """Decision Engine in hybrid mode with no AI provider."""
    with patch.dict(os.environ, {"DECISION_MODE": "hybrid"}):
        return DecisionEngine()


@pytest.fixture
def sample_cheapest_request():
    return {
        "type": "cheapest_alternative",
        "context": {"medicine_name": "Paracetamol"},
    }


@pytest.fixture
def sample_generic_request():
    return {
        "type": "generic_check",
        "context": {"medicine_name": "Ibuprofen"},
    }


@pytest.fixture
def sample_stock_request():
    return {
        "type": "stock_check",
        "context": {"medicine_name": "Amoxicillin", "location": "Cape Town"},
    }


@pytest.fixture
def unknown_request():
    return {
        "type": "unknown_type",
        "context": {},
    }


# ==============================================================
# Decision Engine — Mode Loading
# ==============================================================

class TestDecisionEngineConfiguration:

    def test_default_mode_is_rule(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("DECISION_MODE", None)
            engine = DecisionEngine()
            assert engine.mode == "rule"

    def test_rule_mode_loads_correctly(self):
        with patch.dict(os.environ, {"DECISION_MODE": "rule"}):
            engine = DecisionEngine()
            assert engine.mode == "rule"

    def test_hybrid_mode_loads_correctly(self):
        with patch.dict(os.environ, {"DECISION_MODE": "hybrid"}):
            engine = DecisionEngine()
            assert engine.mode == "hybrid"

    def test_ai_mode_loads_correctly(self):
        with patch.dict(os.environ, {"DECISION_MODE": "ai"}):
            engine = DecisionEngine()
            assert engine.mode == "ai"

    def test_invalid_mode_falls_back_to_rule(self):
        with patch.dict(os.environ, {"DECISION_MODE": "invalid_mode"}):
            engine = DecisionEngine()
            assert engine.mode == "rule"

    def test_uppercase_mode_normalised(self):
        with patch.dict(os.environ, {"DECISION_MODE": "RULE"}):
            engine = DecisionEngine()
            assert engine.mode == "rule"


# ==============================================================
# Decision Engine — Rule Mode Routing
# ==============================================================

class TestDecisionEngineRuleMode:

    def test_process_returns_dict(self, rule_engine, sample_cheapest_request):
        result = rule_engine.process(sample_cheapest_request)
        assert isinstance(result, dict)

    def test_process_source_is_rule(self, rule_engine, sample_cheapest_request):
        result = rule_engine.process(sample_cheapest_request)
        assert result["source"] == "rule"

    def test_process_mode_is_rule(self, rule_engine, sample_cheapest_request):
        result = rule_engine.process(sample_cheapest_request)
        assert result["mode"] == "rule"

    def test_process_contains_result_key(self, rule_engine, sample_cheapest_request):
        result = rule_engine.process(sample_cheapest_request)
        assert "result" in result

    def test_process_contains_confident_key(self, rule_engine, sample_cheapest_request):
        result = rule_engine.process(sample_cheapest_request)
        assert "confident" in result

    def test_invalid_payload_raises_value_error(self, rule_engine):
        with pytest.raises(ValueError):
            rule_engine.process("not a dict")

    def test_invalid_payload_none_raises_value_error(self, rule_engine):
        with pytest.raises(ValueError):
            rule_engine.process(None)


# ==============================================================
# Decision Engine — AI Mode Routing (no provider configured)
# ==============================================================

class TestDecisionEngineAIModeNoProvider:

    def test_ai_mode_falls_back_to_rules_when_no_provider(
        self, sample_cheapest_request
    ):
        with patch.dict(os.environ, {"DECISION_MODE": "ai"}):
            engine = DecisionEngine(ai_provider=None)
            result = engine.process(sample_cheapest_request)
            # Falls back to rule provider
            assert result["source"] == "rule"

    def test_ai_mode_still_returns_dict(self, sample_cheapest_request):
        with patch.dict(os.environ, {"DECISION_MODE": "ai"}):
            engine = DecisionEngine(ai_provider=None)
            result = engine.process(sample_cheapest_request)
            assert isinstance(result, dict)


# ==============================================================
# Decision Engine — AI Mode Routing (mock provider)
# ==============================================================

class MockAIProvider(AIProviderBase):
    """Mock AI provider for testing purposes."""

    def query(self, request: dict) -> dict:
        return {
            "result": {"mock": True},
            "confident": True,
            "message": "Mock AI provider responded.",
        }


class TestDecisionEngineAIModeWithProvider:

    def test_ai_mode_uses_ai_provider(self, sample_cheapest_request):
        with patch.dict(os.environ, {"DECISION_MODE": "ai"}):
            engine = DecisionEngine(ai_provider=MockAIProvider())
            result = engine.process(sample_cheapest_request)
            assert result["source"] == "ai"

    def test_ai_mode_returns_ai_result(self, sample_cheapest_request):
        with patch.dict(os.environ, {"DECISION_MODE": "ai"}):
            engine = DecisionEngine(ai_provider=MockAIProvider())
            result = engine.process(sample_cheapest_request)
            assert result["result"]["mock"] is True


# ==============================================================
# Decision Engine — Hybrid Mode Routing
# ==============================================================

class TestDecisionEngineHybridMode:

    def test_hybrid_uses_rules_when_confident(self, sample_cheapest_request):
        with patch.dict(os.environ, {"DECISION_MODE": "hybrid"}):
            engine = DecisionEngine()
            result = engine.process(sample_cheapest_request)
            # cheapest_alternative rule fires with confident=True
            assert result["source"] == "rule"

    def test_hybrid_escalates_to_ai_when_not_confident(self, sample_stock_request):
        with patch.dict(os.environ, {"DECISION_MODE": "hybrid"}):
            engine = DecisionEngine(ai_provider=MockAIProvider())
            result = engine.process(sample_stock_request)
            # stock_check rule fires with confident=False -> escalates to AI
            assert result["source"] == "ai"

    def test_hybrid_stays_on_rules_when_not_confident_and_no_ai(
        self, sample_stock_request
    ):
        with patch.dict(os.environ, {"DECISION_MODE": "hybrid"}):
            engine = DecisionEngine(ai_provider=None)
            result = engine.process(sample_stock_request)
            assert result["source"] == "rule"


# ==============================================================
# Rule Provider — Rule Matching
# ==============================================================

class TestRuleProvider:

    def setup_method(self):
        self.provider = RuleProvider()

    def test_cheapest_alternative_rule_fires(self, sample_cheapest_request):
        result = self.provider.evaluate(sample_cheapest_request)
        assert result["rule_matched"] == "_rule_cheapest_alternative"

    def test_generic_check_rule_fires(self, sample_generic_request):
        result = self.provider.evaluate(sample_generic_request)
        assert result["rule_matched"] == "_rule_generic_available"

    def test_stock_check_rule_fires(self, sample_stock_request):
        result = self.provider.evaluate(sample_stock_request)
        assert result["rule_matched"] == "_rule_out_of_stock_warning"

    def test_no_match_returns_none_result(self, unknown_request):
        result = self.provider.evaluate(unknown_request)
        assert result["result"] is None

    def test_no_match_rule_matched_is_none(self, unknown_request):
        result = self.provider.evaluate(unknown_request)
        assert result["rule_matched"] is None

    def test_no_match_confident_is_false(self, unknown_request):
        result = self.provider.evaluate(unknown_request)
        assert result["confident"] is False

    def test_cheapest_alternative_confident_true(self, sample_cheapest_request):
        result = self.provider.evaluate(sample_cheapest_request)
        assert result["confident"] is True

    def test_stock_check_confident_false(self, sample_stock_request):
        result = self.provider.evaluate(sample_stock_request)
        assert result["confident"] is False

    def test_result_contains_message(self, sample_cheapest_request):
        result = self.provider.evaluate(sample_cheapest_request)
        assert "message" in result

    def test_result_contains_result_key(self, sample_cheapest_request):
        result = self.provider.evaluate(sample_cheapest_request)
        assert "result" in result


# ==============================================================
# AI Provider Interface
# ==============================================================

class TestAIProviderInterface:

    def test_abstract_class_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            AIProviderBase()

    def test_subclass_without_query_cannot_be_instantiated(self):
        class IncompleteProvider(AIProviderBase):
            pass

        with pytest.raises(TypeError):
            IncompleteProvider()

    def test_valid_subclass_can_be_instantiated(self):
        provider = MockAIProvider()
        assert provider is not None

    def test_mock_provider_query_returns_dict(self, sample_cheapest_request):
        provider = MockAIProvider()
        result = provider.query(sample_cheapest_request)
        assert isinstance(result, dict)

    def test_mock_provider_health_check_default_false(self):
        provider = MockAIProvider()
        assert provider.health_check() is False


# ==============================================================
# Unreachable AI Provider
# ==============================================================

class TestUnreachableAIProvider:

    def setup_method(self):
        self.provider = UnreachableAIProvider()

    def test_query_returns_dict(self, sample_cheapest_request):
        result = self.provider.query(sample_cheapest_request)
        assert isinstance(result, dict)

    def test_query_result_is_none(self, sample_cheapest_request):
        result = self.provider.query(sample_cheapest_request)
        assert result["result"] is None

    def test_query_confident_is_false(self, sample_cheapest_request):
        result = self.provider.query(sample_cheapest_request)
        assert result["confident"] is False

    def test_health_check_returns_false(self):
        assert self.provider.health_check() is False
