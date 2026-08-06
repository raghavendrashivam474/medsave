"""
backend/tests/test_decision_engine.py

Test suite for Sprint 2 — Decision Engine Integration.

Covers:
    - DecisionEngine routing (rule / ai / hybrid modes)
    - RuleProvider all six rules with real database data
    - Recommendations API endpoint
    - Edge cases and error handling
    - Regression: existing tests must still pass

All tests run against the local SQLite database seeded with
backend/database/seed_data.py.

Seed data reference:
    Medicines:
        id=1  Paracetamol   500MG  Tablet   ₹10.0
        id=2  Amoxicillin   250MG  Capsule  ₹25.0
        id=3  Metformin     500MG  Tablet   ₹15.0
        id=4  Atorvastatin  10MG   Tablet   ₹20.0
        id=5  Azithromycin  500MG  Tablet   ₹45.0
        id=6  Cetirizine    10MG   Tablet   ₹5.0
        id=7  Omeprazole    20MG   Capsule  ₹12.0
        id=8  Amlodipine    5MG    Tablet   ₹8.0

    Brands for Paracetamol (id=1):
        Crocin   ₹35.0  savings=25.0  savings_pct=71.4
        Dolo 650 ₹30.0  savings=20.0  savings_pct=66.7
        Calpol   ₹32.0  savings=22.0  savings_pct=68.8

    Cheapest brand for Paracetamol: Dolo 650 (₹30.0)
    Best savings for Paracetamol:   Crocin   (71.4%)
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

os.environ["DATABASE_URL"] = "sqlite"
os.environ["DECISION_MODE"] = "rule"

from backend.app import app
from backend.decision_engine import DecisionEngine
from backend.decision_engine.providers.rule_provider import RuleProvider
from backend.decision_engine.providers.ai_provider import (
    AIProviderBase,
    UnreachableAIProvider,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    os.environ["DATABASE_URL"] = "sqlite"
    os.environ["DECISION_MODE"] = "rule"
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def engine():
    """Fresh DecisionEngine in rule mode for each test."""
    os.environ["DECISION_MODE"] = "rule"
    return DecisionEngine()


@pytest.fixture
def rule_provider():
    """Fresh RuleProvider for each test."""
    return RuleProvider()


def get_json(response):
    return response.get_json()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_request(request_type, medicine_name=None, medicine_id=None, location=None):
    """Build a well-formed engine request dict."""
    context = {}
    if medicine_name is not None:
        context["medicine_name"] = medicine_name
    if medicine_id is not None:
        context["medicine_id"] = medicine_id
    if location is not None:
        context["location"] = location
    return {"type": request_type, "context": context}


# ---------------------------------------------------------------------------
# DecisionEngine — initialization
# ---------------------------------------------------------------------------

class TestDecisionEngineInit:

    def test_engine_creates_rule_provider(self, engine):
        assert engine.rule_provider is not None

    def test_engine_default_mode_is_rule(self, engine):
        assert engine.mode == "rule"

    def test_engine_ai_provider_none_by_default(self, engine):
        assert engine.ai_provider is None

    def test_engine_rule_registry_not_empty(self, engine):
        assert len(engine.rule_provider.RULE_REGISTRY) > 0

    def test_engine_rejects_non_dict_request(self, engine):
        with pytest.raises(ValueError):
            engine.process("not a dict")

    def test_engine_rejects_list_request(self, engine):
        with pytest.raises(ValueError):
            engine.process(["type", "cheapest_alternative"])

    def test_engine_rejects_none_request(self, engine):
        with pytest.raises(ValueError):
            engine.process(None)


# ---------------------------------------------------------------------------
# DecisionEngine — mode routing
# ---------------------------------------------------------------------------

class TestDecisionEngineRouting:

    def test_rule_mode_returns_source_rule(self, engine):
        req = make_request("cheapest_alternative", medicine_name="Paracetamol")
        result = engine.process(req)
        assert result["source"] == "rule"

    def test_rule_mode_returns_mode_rule(self, engine):
        req = make_request("cheapest_alternative", medicine_name="Paracetamol")
        result = engine.process(req)
        assert result["mode"] == "rule"

    def test_result_always_has_source(self, engine):
        req = make_request("generic_check", medicine_name="Paracetamol")
        result = engine.process(req)
        assert "source" in result

    def test_result_always_has_mode(self, engine):
        req = make_request("generic_check", medicine_name="Paracetamol")
        result = engine.process(req)
        assert "mode" in result

    def test_result_always_has_confident(self, engine):
        req = make_request("generic_check", medicine_name="Paracetamol")
        result = engine.process(req)
        assert "confident" in result

    def test_result_always_has_message(self, engine):
        req = make_request("generic_check", medicine_name="Paracetamol")
        result = engine.process(req)
        assert "message" in result

    def test_unknown_mode_falls_back_to_rule(self):
        os.environ["DECISION_MODE"] = "invalid_mode"
        e = DecisionEngine()
        assert e.mode == "rule"
        os.environ["DECISION_MODE"] = "rule"

    def test_ai_mode_without_provider_falls_back_to_rules(self):
        os.environ["DECISION_MODE"] = "ai"
        e = DecisionEngine()
        req = make_request("cheapest_alternative", medicine_name="Paracetamol")
        result = e.process(req)
        # Falls back to rules — source should still be rule
        assert result["source"] == "rule"
        os.environ["DECISION_MODE"] = "rule"

    def test_hybrid_mode_confident_rule_returns_rule_source(self):
        os.environ["DECISION_MODE"] = "hybrid"
        e = DecisionEngine()
        req = make_request("cheapest_alternative", medicine_name="Paracetamol")
        result = e.process(req)
        # Rule is confident for known medicine — should not escalate
        assert result["source"] == "rule"
        assert result["confident"] is True
        os.environ["DECISION_MODE"] = "rule"

    def test_hybrid_mode_no_match_returns_rule_source_without_ai(self):
        os.environ["DECISION_MODE"] = "hybrid"
        e = DecisionEngine()
        req = make_request("unknown_type_xyz")
        result = e.process(req)
        # No rule matches, no AI — returns rule result with low confidence
        assert result["source"] == "rule"
        assert result["confident"] is False
        os.environ["DECISION_MODE"] = "rule"


# ---------------------------------------------------------------------------
# DecisionEngine — AI provider interface
# ---------------------------------------------------------------------------

class MockAIProvider(AIProviderBase):
    """Test double for AIProviderBase."""

    def query(self, request: dict) -> dict:
        return {
            "result":    {"mock": True},
            "confident": True,
            "message":   "Mock AI response.",
        }

    def health_check(self) -> bool:
        return True


class TestAIProviderInterface:

    def test_unreachable_provider_returns_dict(self):
        provider = UnreachableAIProvider()
        result = provider.query({"type": "test"})
        assert isinstance(result, dict)

    def test_unreachable_provider_confident_false(self):
        provider = UnreachableAIProvider()
        result = provider.query({"type": "test"})
        assert result["confident"] is False

    def test_unreachable_provider_result_none(self):
        provider = UnreachableAIProvider()
        result = provider.query({"type": "test"})
        assert result["result"] is None

    def test_unreachable_provider_health_false(self):
        provider = UnreachableAIProvider()
        assert provider.health_check() is False

    def test_mock_provider_query_returns_dict(self):
        provider = MockAIProvider()
        result = provider.query({"type": "test"})
        assert isinstance(result, dict)

    def test_mock_provider_health_true(self):
        provider = MockAIProvider()
        assert provider.health_check() is True

    def test_engine_with_ai_provider_routes_to_ai(self):
        os.environ["DECISION_MODE"] = "ai"
        e = DecisionEngine(ai_provider=MockAIProvider())
        req = make_request("cheapest_alternative", medicine_name="Paracetamol")
        result = e.process(req)
        assert result["source"] == "ai"
        assert result["result"]["mock"] is True
        os.environ["DECISION_MODE"] = "rule"


# ---------------------------------------------------------------------------
# RuleProvider — cheapest_alternative
# ---------------------------------------------------------------------------

class TestRuleCheapestAlternative:

    def test_known_medicine_returns_result(self, rule_provider):
        req = make_request("cheapest_alternative", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"] is not None

    def test_confident_true_for_known_medicine(self, rule_provider):
        req = make_request("cheapest_alternative", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["confident"] is True

    def test_cheapest_brand_is_dolo_650(self, rule_provider):
        # Dolo 650 = ₹30.0, Calpol = ₹32.0, Crocin = ₹35.0
        req = make_request("cheapest_alternative", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"]["brand_name"] == "Dolo 650"

    def test_cheapest_brand_price_correct(self, rule_provider):
        req = make_request("cheapest_alternative", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"]["brand_price"] == 30.0

    def test_savings_calculated_correctly(self, rule_provider):
        # jan_price=10.0, mrp=30.0 => savings=20.0, pct=66.7
        req = make_request("cheapest_alternative", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"]["savings"] == 20.0
        assert result["result"]["savings_percent"] == 66.7

    def test_generic_price_in_result(self, rule_provider):
        req = make_request("cheapest_alternative", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"]["generic_price"] == 10.0

    def test_generic_name_in_result(self, rule_provider):
        req = make_request("cheapest_alternative", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"]["generic_name"] == "Paracetamol"

    def test_rule_matched_name_correct(self, rule_provider):
        req = make_request("cheapest_alternative", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["rule_matched"] == "_rule_cheapest_alternative"

    def test_unknown_medicine_returns_none_result(self, rule_provider):
        req = make_request("cheapest_alternative", medicine_name="XyzUnknownMed9999")
        result = rule_provider.evaluate(req)
        assert result["result"] is None

    def test_unknown_medicine_confident_false(self, rule_provider):
        req = make_request("cheapest_alternative", medicine_name="XyzUnknownMed9999")
        result = rule_provider.evaluate(req)
        assert result["confident"] is False

    def test_lookup_by_medicine_id(self, rule_provider):
        req = make_request("cheapest_alternative", medicine_id=1)
        result = rule_provider.evaluate(req)
        assert result["result"]["generic_name"] == "Paracetamol"

    def test_wrong_type_returns_none_from_rule(self, rule_provider):
        # Rule should not fire for wrong type
        req = make_request("generic_check", medicine_name="Paracetamol")
        # Rule _rule_cheapest_alternative returns None — another rule handles it
        result = rule_provider._rule_cheapest_alternative(req)
        assert result is None

    def test_cetirizine_cheapest_is_zyrtec(self, rule_provider):
        req = make_request("cheapest_alternative", medicine_name="Cetirizine")
        result = rule_provider.evaluate(req)
        assert result["result"]["brand_name"] == "Zyrtec"

    def test_atorvastatin_cheapest_is_atorva(self, rule_provider):
        # Atorva=₹90, Lipitor=₹120
        req = make_request("cheapest_alternative", medicine_name="Atorvastatin")
        result = rule_provider.evaluate(req)
        assert result["result"]["brand_name"] == "Atorva"


# ---------------------------------------------------------------------------
# RuleProvider — best_savings
# ---------------------------------------------------------------------------

class TestRuleBestSavings:

    def test_known_medicine_returns_result(self, rule_provider):
        req = make_request("best_savings", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"] is not None

    def test_confident_true_for_known_medicine(self, rule_provider):
        req = make_request("best_savings", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["confident"] is True

    def test_best_savings_brand_is_crocin(self, rule_provider):
        # Crocin: savings_pct=71.4, Calpol=68.8, Dolo=66.7
        req = make_request("best_savings", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"]["brand_name"] == "Crocin"

    def test_best_savings_percent_correct(self, rule_provider):
        req = make_request("best_savings", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"]["savings_percent"] == 71.4

    def test_best_savings_amount_correct(self, rule_provider):
        # Crocin: mrp=35.0 - jan=10.0 = 25.0
        req = make_request("best_savings", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"]["savings"] == 25.0

    def test_rule_matched_name_correct(self, rule_provider):
        req = make_request("best_savings", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["rule_matched"] == "_rule_best_savings"

    def test_unknown_medicine_confident_false(self, rule_provider):
        req = make_request("best_savings", medicine_name="NoSuchMed99")
        result = rule_provider.evaluate(req)
        assert result["confident"] is False

    def test_lookup_by_id(self, rule_provider):
        req = make_request("best_savings", medicine_id=1)
        result = rule_provider.evaluate(req)
        assert result["result"]["generic_name"] == "Paracetamol"

    def test_atorvastatin_best_savings_is_lipitor(self, rule_provider):
        # Lipitor=₹120 jan=₹20 => savings=100 pct=83.3
        # Atorva=₹90  jan=₹20 => savings=70  pct=77.8
        req = make_request("best_savings", medicine_name="Atorvastatin")
        result = rule_provider.evaluate(req)
        assert result["result"]["brand_name"] == "Lipitor"


# ---------------------------------------------------------------------------
# RuleProvider — generic_check
# ---------------------------------------------------------------------------

class TestRuleGenericAvailable:

    def test_known_medicine_returns_result(self, rule_provider):
        req = make_request("generic_check", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"] is not None

    def test_known_medicine_generic_available_true(self, rule_provider):
        req = make_request("generic_check", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"]["generic_available"] is True

    def test_known_medicine_confident_true(self, rule_provider):
        req = make_request("generic_check", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["confident"] is True

    def test_known_medicine_jan_price_correct(self, rule_provider):
        req = make_request("generic_check", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"]["jan_price"] == 10.0

    def test_known_medicine_id_returned(self, rule_provider):
        req = make_request("generic_check", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"]["medicine_id"] == 1

    def test_unknown_medicine_generic_available_false(self, rule_provider):
        req = make_request("generic_check", medicine_name="NoSuchMed99")
        result = rule_provider.evaluate(req)
        assert result["result"]["generic_available"] is False

    def test_unknown_medicine_still_confident_true(self, rule_provider):
        # Absence is also a definitive answer
        req = make_request("generic_check", medicine_name="NoSuchMed99")
        result = rule_provider.evaluate(req)
        assert result["confident"] is True

    def test_rule_matched_name_correct(self, rule_provider):
        req = make_request("generic_check", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["rule_matched"] == "_rule_generic_available"

    def test_all_seed_medicines_available(self, rule_provider):
        medicines = [
            "Paracetamol", "Amoxicillin", "Metformin",
            "Atorvastatin", "Azithromycin", "Cetirizine",
            "Omeprazole", "Amlodipine",
        ]
        for name in medicines:
            req = make_request("generic_check", medicine_name=name)
            result = rule_provider.evaluate(req)
            assert result["result"]["generic_available"] is True, (
                f"{name} should be available"
            )


# ---------------------------------------------------------------------------
# RuleProvider — stock_check
# ---------------------------------------------------------------------------

class TestRuleStockCheck:

    def test_known_medicine_with_brands_in_stock(self, rule_provider):
        req = make_request("stock_check", medicine_name="Paracetamol", location="Noida")
        result = rule_provider.evaluate(req)
        assert result["result"]["in_stock"] is True

    def test_confident_true_for_known_medicine(self, rule_provider):
        req = make_request("stock_check", medicine_name="Paracetamol", location="Noida")
        result = rule_provider.evaluate(req)
        assert result["confident"] is True

    def test_brand_count_correct(self, rule_provider):
        req = make_request("stock_check", medicine_name="Paracetamol", location="Noida")
        result = rule_provider.evaluate(req)
        assert result["result"]["brand_count"] == 3

    def test_rule_matched_name_correct(self, rule_provider):
        req = make_request("stock_check", medicine_name="Paracetamol", location="Noida")
        result = rule_provider.evaluate(req)
        assert result["rule_matched"] == "_rule_out_of_stock_warning"

    def test_unknown_medicine_confident_false(self, rule_provider):
        req = make_request("stock_check", medicine_name="NoSuchMed99", location="Noida")
        result = rule_provider.evaluate(req)
        assert result["confident"] is False

    def test_unknown_medicine_in_stock_none(self, rule_provider):
        req = make_request("stock_check", medicine_name="NoSuchMed99", location="Noida")
        result = rule_provider.evaluate(req)
        assert result["result"]["in_stock"] is None

    def test_location_preserved_in_result(self, rule_provider):
        req = make_request("stock_check", medicine_name="Paracetamol", location="Delhi")
        result = rule_provider.evaluate(req)
        assert result["result"]["location"] == "Delhi"


# ---------------------------------------------------------------------------
# RuleProvider — brand_alternatives
# ---------------------------------------------------------------------------

class TestRuleBrandAlternatives:

    def test_known_medicine_returns_brands_list(self, rule_provider):
        req = make_request("brand_alternatives", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert isinstance(result["result"]["brands"], list)

    def test_paracetamol_has_three_brands(self, rule_provider):
        req = make_request("brand_alternatives", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"]["brand_count"] == 3

    def test_brands_ordered_by_price_ascending(self, rule_provider):
        req = make_request("brand_alternatives", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        prices = [b["brand_price"] for b in result["result"]["brands"]]
        assert prices == sorted(prices)

    def test_each_brand_has_required_fields(self, rule_provider):
        req = make_request("brand_alternatives", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        required = ["brand_id", "brand_name", "brand_price", "savings", "savings_percent"]
        for brand in result["result"]["brands"]:
            for field in required:
                assert field in brand, f"Missing field: {field}"

    def test_savings_nonnegative_for_all_brands(self, rule_provider):
        req = make_request("brand_alternatives", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        for brand in result["result"]["brands"]:
            if brand["savings"] is not None:
                assert brand["savings"] >= 0

    def test_confident_true_for_known_medicine(self, rule_provider):
        req = make_request("brand_alternatives", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["confident"] is True

    def test_rule_matched_name_correct(self, rule_provider):
        req = make_request("brand_alternatives", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["rule_matched"] == "_rule_brand_alternatives"

    def test_unknown_medicine_confident_false(self, rule_provider):
        req = make_request("brand_alternatives", medicine_name="NoSuchMed99")
        result = rule_provider.evaluate(req)
        assert result["confident"] is False

    def test_cetirizine_has_one_brand(self, rule_provider):
        req = make_request("brand_alternatives", medicine_name="Cetirizine")
        result = rule_provider.evaluate(req)
        assert result["result"]["brand_count"] == 1


# ---------------------------------------------------------------------------
# RuleProvider — recommendation_score
# ---------------------------------------------------------------------------

class TestRuleRecommendationScore:

    def test_known_medicine_returns_scored_brands(self, rule_provider):
        req = make_request("recommendation_score", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"] is not None
        assert len(result["result"]["brands"]) == 3

    def test_each_brand_has_score(self, rule_provider):
        req = make_request("recommendation_score", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        for brand in result["result"]["brands"]:
            assert "score" in brand
            assert isinstance(brand["score"], float)

    def test_scores_between_0_and_100(self, rule_provider):
        req = make_request("recommendation_score", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        for brand in result["result"]["brands"]:
            assert 0.0 <= brand["score"] <= 100.0

    def test_brands_ordered_by_score_descending(self, rule_provider):
        req = make_request("recommendation_score", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        scores = [b["score"] for b in result["result"]["brands"]]
        assert scores == sorted(scores, reverse=True)

    def test_top_brand_marked_recommended(self, rule_provider):
        req = make_request("recommendation_score", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["result"]["brands"][0]["recommended"] is True

    def test_other_brands_not_recommended(self, rule_provider):
        req = make_request("recommendation_score", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        for brand in result["result"]["brands"][1:]:
            assert brand["recommended"] is False

    def test_top_pick_key_present(self, rule_provider):
        req = make_request("recommendation_score", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert "top_pick" in result["result"]
        assert isinstance(result["result"]["top_pick"], str)

    def test_confident_true_for_known_medicine(self, rule_provider):
        req = make_request("recommendation_score", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["confident"] is True

    def test_rule_matched_name_correct(self, rule_provider):
        req = make_request("recommendation_score", medicine_name="Paracetamol")
        result = rule_provider.evaluate(req)
        assert result["rule_matched"] == "_rule_recommendation_score"

    def test_unknown_medicine_confident_false(self, rule_provider):
        req = make_request("recommendation_score", medicine_name="NoSuchMed99")
        result = rule_provider.evaluate(req)
        assert result["confident"] is False


# ---------------------------------------------------------------------------
# RuleProvider — no match
# ---------------------------------------------------------------------------

class TestRuleProviderNoMatch:

    def test_unknown_type_returns_no_match(self, rule_provider):
        req = {"type": "completely_unknown_type_xyz", "context": {}}
        result = rule_provider.evaluate(req)
        assert result["result"] is None

    def test_unknown_type_confident_false(self, rule_provider):
        req = {"type": "completely_unknown_type_xyz", "context": {}}
        result = rule_provider.evaluate(req)
        assert result["confident"] is False

    def test_unknown_type_rule_matched_none(self, rule_provider):
        req = {"type": "completely_unknown_type_xyz", "context": {}}
        result = rule_provider.evaluate(req)
        assert result["rule_matched"] is None

    def test_empty_request_returns_no_match(self, rule_provider):
        result = rule_provider.evaluate({})
        assert result["confident"] is False


# ---------------------------------------------------------------------------
# Recommendations API — POST /api/recommendations
# ---------------------------------------------------------------------------

class TestRecommendationsAPI:

    def test_cheapest_alternative_returns_200(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "cheapest_alternative",
            "context": {"medicine_name": "Paracetamol"},
        })
        assert r.status_code == 200

    def test_cheapest_alternative_success_true(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "cheapest_alternative",
            "context": {"medicine_name": "Paracetamol"},
        })
        assert get_json(r)["success"] is True

    def test_response_has_result_key(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "cheapest_alternative",
            "context": {"medicine_name": "Paracetamol"},
        })
        assert "result" in get_json(r)

    def test_response_has_confident_key(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "cheapest_alternative",
            "context": {"medicine_name": "Paracetamol"},
        })
        assert "confident" in get_json(r)

    def test_response_has_source_key(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "cheapest_alternative",
            "context": {"medicine_name": "Paracetamol"},
        })
        assert "source" in get_json(r)

    def test_response_has_mode_key(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "cheapest_alternative",
            "context": {"medicine_name": "Paracetamol"},
        })
        assert "mode" in get_json(r)

    def test_response_has_message_key(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "cheapest_alternative",
            "context": {"medicine_name": "Paracetamol"},
        })
        assert "message" in get_json(r)

    def test_dolo_650_is_cheapest_for_paracetamol(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "cheapest_alternative",
            "context": {"medicine_name": "Paracetamol"},
        })
        data = get_json(r)
        assert data["result"]["brand_name"] == "Dolo 650"

    def test_best_savings_returns_crocin(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "best_savings",
            "context": {"medicine_name": "Paracetamol"},
        })
        data = get_json(r)
        assert data["result"]["brand_name"] == "Crocin"

    def test_generic_check_paracetamol_available(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "generic_check",
            "context": {"medicine_name": "Paracetamol"},
        })
        data = get_json(r)
        assert data["result"]["generic_available"] is True

    def test_stock_check_paracetamol_in_stock(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "stock_check",
            "context": {"medicine_name": "Paracetamol", "location": "Noida"},
        })
        data = get_json(r)
        assert data["result"]["in_stock"] is True

    def test_brand_alternatives_returns_brands(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "brand_alternatives",
            "context": {"medicine_name": "Paracetamol"},
        })
        data = get_json(r)
        assert data["result"]["brand_count"] == 3

    def test_recommendation_score_returns_scored_brands(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "recommendation_score",
            "context": {"medicine_name": "Paracetamol"},
        })
        data = get_json(r)
        assert len(data["result"]["brands"]) == 3

    def test_missing_body_returns_400(self, client):
        r = client.post("/api/recommendations",
                        content_type="application/json", data="")
        assert r.status_code == 400

    def test_missing_body_success_false(self, client):
        r = client.post("/api/recommendations",
                        content_type="application/json", data="")
        assert get_json(r)["success"] is False

    def test_missing_body_error_bad_request(self, client):
        r = client.post("/api/recommendations",
                        content_type="application/json", data="")
        assert get_json(r)["error"] == "BAD_REQUEST"

    def test_missing_type_returns_400(self, client):
        r = client.post("/api/recommendations", json={"context": {}})
        assert r.status_code == 400

    def test_unknown_type_returns_400(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "unknown_type_xyz",
            "context": {},
        })
        assert r.status_code == 400

    def test_unknown_type_error_bad_request(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "unknown_type_xyz",
            "context": {},
        })
        assert get_json(r)["error"] == "BAD_REQUEST"

    def test_unknown_medicine_confident_false(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "cheapest_alternative",
            "context": {"medicine_name": "NoSuchMed99"},
        })
        data = get_json(r)
        assert data["success"] is True
        assert data["confident"] is False

    def test_lookup_by_medicine_id(self, client):
        r = client.post("/api/recommendations", json={
            "type":    "cheapest_alternative",
            "context": {"medicine_id": 1},
        })
        data = get_json(r)
        assert data["result"]["generic_name"] == "Paracetamol"

    def test_all_valid_types_return_200(self, client):
        valid_types = [
            "cheapest_alternative",
            "best_savings",
            "generic_check",
            "stock_check",
            "brand_alternatives",
            "recommendation_score",
        ]
        for t in valid_types:
            r = client.post("/api/recommendations", json={
                "type":    t,
                "context": {"medicine_name": "Paracetamol"},
            })
            assert r.status_code == 200, f"Type '{t}' returned {r.status_code}"


# ---------------------------------------------------------------------------
# Recommendations API — GET /api/recommendations/health
# ---------------------------------------------------------------------------

class TestRecommendationsHealthAPI:

    def test_returns_200(self, client):
        r = client.get("/api/recommendations/health")
        assert r.status_code == 200

    def test_success_true(self, client):
        r = client.get("/api/recommendations/health")
        assert get_json(r)["success"] is True

    def test_engine_operational(self, client):
        r = client.get("/api/recommendations/health")
        assert get_json(r)["engine"] == "operational"

    def test_mode_present(self, client):
        r = client.get("/api/recommendations/health")
        assert "mode" in get_json(r)

    def test_rules_count_correct(self, client):
        r = client.get("/api/recommendations/health")
        assert get_json(r)["rules"] == 6
