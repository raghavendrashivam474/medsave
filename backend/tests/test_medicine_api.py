"""
backend/tests/test_medicine_api.py

Test suite for MS6 Part 1 — Medicine Details API and Search API.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app import app


@pytest.fixture
def client():
    os.environ["DATABASE_URL"] = "sqlite"
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def get_json(response):
    return response.get_json()


class TestMedicineDetailsAPI:

    def test_known_medicine_returns_200(self, client):
        r = client.get("/api/medicine/1")
        assert r.status_code == 200

    def test_response_success_true(self, client):
        r = client.get("/api/medicine/1")
        data = get_json(r)
        assert data["success"] is True

    def test_medicine_key_present(self, client):
        r = client.get("/api/medicine/1")
        data = get_json(r)
        assert "medicine" in data

    def test_brands_key_present(self, client):
        r = client.get("/api/medicine/1")
        data = get_json(r)
        assert "brands" in data

    def test_brands_is_list(self, client):
        r = client.get("/api/medicine/1")
        data = get_json(r)
        assert isinstance(data["brands"], list)

    def test_medicine_has_all_required_fields(self, client):
        required = [
            "id", "generic_name", "salt", "dosage", "form",
            "jan_price", "manufacturer", "therapeutic_category", "schedule",
        ]
        r = client.get("/api/medicine/1")
        medicine = get_json(r)["medicine"]
        for field in required:
            assert field in medicine

    def test_medicine_correct_values_for_id_1(self, client):
        r = client.get("/api/medicine/1")
        m = get_json(r)["medicine"]
        assert m["id"] == 1
        assert m["generic_name"] == "Paracetamol"
        assert m["salt"] == "Paracetamol"
        assert m["dosage"] == "500MG"
        assert m["form"] == "Tablet"
        assert m["jan_price"] == 10.0

    def test_nullable_columns_present_and_null(self, client):
        r = client.get("/api/medicine/1")
        m = get_json(r)["medicine"]
        assert "manufacturer" in m
        assert "therapeutic_category" in m
        assert "schedule" in m

    def test_medicine_with_multiple_brands_returns_all(self, client):
        r = client.get("/api/medicine/1")
        brands = get_json(r)["brands"]
        assert len(brands) == 3

    def test_brands_ordered_by_mrp_ascending(self, client):
        r = client.get("/api/medicine/1")
        brands = get_json(r)["brands"]
        mrps = [b["mrp"] for b in brands]
        assert mrps == sorted(mrps)

    def test_brands_have_all_required_fields(self, client):
        required = ["id", "brand_name", "mrp", "manufacturer", "savings", "savings_percent"]
        r = client.get("/api/medicine/1")
        for brand in get_json(r)["brands"]:
            for field in required:
                assert field in brand

    def test_savings_calculated_correctly(self, client):
        r = client.get("/api/medicine/1")
        brands = get_json(r)["brands"]
        crocin = next(b for b in brands if b["brand_name"] == "Crocin")
        assert crocin["savings"] == 25.0
        assert crocin["savings_percent"] == 71.4

    def test_savings_nonnegative(self, client):
        for med_id in range(1, 9):
            r = client.get(f"/api/medicine/{med_id}")
            for brand in get_json(r)["brands"]:
                if brand["savings"] is not None:
                    assert brand["savings"] >= 0

    def test_medicine_with_one_brand(self, client):
        r = client.get("/api/medicine/6")
        data = get_json(r)
        assert data["success"] is True
        assert len(data["brands"]) == 1
        assert data["brands"][0]["brand_name"] == "Zyrtec"

    def test_missing_medicine_returns_404(self, client):
        r = client.get("/api/medicine/999999")
        assert r.status_code == 404

    def test_missing_medicine_success_false(self, client):
        r = client.get("/api/medicine/999999")
        data = get_json(r)
        assert data["success"] is False

    def test_missing_medicine_error_code(self, client):
        r = client.get("/api/medicine/999999")
        data = get_json(r)
        assert data["error"] == "NOT_FOUND"

    def test_missing_medicine_message_present(self, client):
        r = client.get("/api/medicine/999999")
        data = get_json(r)
        assert "message" in data
        assert len(data["message"]) > 0

    def test_non_integer_id_returns_404(self, client):
        r = client.get("/api/medicine/abc")
        assert r.status_code == 404

    def test_zero_id_returns_404(self, client):
        r = client.get("/api/medicine/0")
        assert r.status_code == 404


class TestSearchAPI:

    def test_empty_query_returns_empty_list(self, client):
        r = client.get("/api/search?q=")
        assert r.status_code == 200
        assert get_json(r) == []

    def test_missing_query_returns_empty_list(self, client):
        r = client.get("/api/search")
        assert r.status_code == 200
        assert get_json(r) == []

    def test_generic_name_search_returns_results(self, client):
        r = client.get("/api/search?q=Paracetamol")
        assert r.status_code == 200
        data = get_json(r)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_partial_generic_name_returns_results(self, client):
        r = client.get("/api/search?q=para")
        data = get_json(r)
        assert len(data) > 0
        generic_names = [row["generic_name"] for row in data]
        assert any("Paracetamol" in name for name in generic_names)

    def test_brand_name_search_returns_parent_medicine(self, client):
        r = client.get("/api/search?q=Crocin")
        data = get_json(r)
        assert len(data) > 0
        generic_names = [row["generic_name"] for row in data]
        assert "Paracetamol" in generic_names

    def test_partial_brand_name_returns_results(self, client):
        r = client.get("/api/search?q=croc")
        data = get_json(r)
        assert len(data) > 0

    def test_unknown_term_returns_empty_list(self, client):
        r = client.get("/api/search?q=xyznotamedicine99999")
        assert r.status_code == 200
        assert get_json(r) == []

    def test_result_has_brand_name(self, client):
        r = client.get("/api/search?q=para")
        for row in get_json(r):
            assert "brand_name" in row

    def test_result_has_generic_name(self, client):
        r = client.get("/api/search?q=para")
        for row in get_json(r):
            assert "generic_name" in row

    def test_result_has_salt(self, client):
        r = client.get("/api/search?q=para")
        for row in get_json(r):
            assert "salt" in row

    def test_result_has_dosage(self, client):
        r = client.get("/api/search?q=para")
        for row in get_json(r):
            assert "dosage" in row

    def test_result_has_form(self, client):
        r = client.get("/api/search?q=para")
        for row in get_json(r):
            assert "form" in row

    def test_result_has_brand_price(self, client):
        r = client.get("/api/search?q=para")
        for row in get_json(r):
            assert "brand_price" in row

    def test_result_has_generic_price(self, client):
        r = client.get("/api/search?q=para")
        for row in get_json(r):
            assert "generic_price" in row

    def test_result_has_savings_percent(self, client):
        r = client.get("/api/search?q=para")
        for row in get_json(r):
            assert "savings_percent" in row

    def test_result_has_medicine_id(self, client):
        r = client.get("/api/search?q=para")
        for row in get_json(r):
            assert "medicine_id" in row

    def test_medicine_id_is_integer(self, client):
        r = client.get("/api/search?q=para")
        for row in get_json(r):
            assert isinstance(row["medicine_id"], int)

    def test_result_has_match_type(self, client):
        r = client.get("/api/search?q=para")
        for row in get_json(r):
            assert "match_type" in row

    def test_match_type_values_valid(self, client):
        r = client.get("/api/search?q=para")
        for row in get_json(r):
            assert row["match_type"] in ("generic", "brand")

    def test_generic_search_has_generic_match_type(self, client):
        r = client.get("/api/search?q=Paracetamol")
        data = get_json(r)
        match_types = [row["match_type"] for row in data]
        assert "generic" in match_types

    def test_brand_search_has_brand_match_type(self, client):
        r = client.get("/api/search?q=Crocin")
        data = get_json(r)
        match_types = [row["match_type"] for row in data]
        assert "brand" in match_types

    def test_savings_percent_nonnegative(self, client):
        r = client.get("/api/search?q=para")
        for row in get_json(r):
            assert row["savings_percent"] >= 0

    def test_savings_percent_for_crocin(self, client):
        r = client.get("/api/search?q=Crocin")
        data = get_json(r)
        crocin_rows = [row for row in data if row["brand_name"] == "Crocin"]
        assert len(crocin_rows) == 1
        assert crocin_rows[0]["savings_percent"] == 71.4

    def test_exact_generic_match_ranked_first(self, client):
        r = client.get("/api/search?q=Paracetamol")
        data = get_json(r)
        assert len(data) > 0
        assert data[0]["generic_name"] == "Paracetamol"
        assert data[0]["match_type"] == "generic"


class TestHealthAPI:

    def test_health_returns_200(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200

    def test_health_returns_status_ok(self, client):
        data = get_json(client.get("/api/health"))
        assert data["status"] == "ok"

    def test_health_returns_database_connected(self, client):
        data = get_json(client.get("/api/health"))
        assert data["database"] == "connected"