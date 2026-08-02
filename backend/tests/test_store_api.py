# backend/tests/test_store_api.py

"""
backend/tests/test_store_api.py

Test suite for Milestone 6 Phase 2 — Store Intelligence & Location Services.

Covers:
    GET /api/stores          — list, filter by pincode / city / state / proximity
    GET /api/stores/<id>     — single store by primary key

All tests run against the local SQLite database seeded with
backend/database/seed_data.py.

Seed data reference (used to write assertions):
    Store 1 — Jan Aushadhi Kendra - Sector 12  | Noida   | 201301 | UP
    Store 2 — Generic Pharma Plus               | Delhi   | 110092 | Delhi
    Store 3 — Affordable Meds Kendra            | Delhi   | 110024 | Delhi
    Store 4 — Jan Aushadhi Store - Andheri East | Mumbai  | 400059 | Maharashtra
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app import app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    os.environ["DATABASE_URL"] = "sqlite"
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def get_json(response):
    return response.get_json()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# All fields every store object must contain — no exceptions.
REQUIRED_STORE_FIELDS = [
    "id",
    "name",
    "address",
    "city",
    "state",
    "pincode",
    "latitude",
    "longitude",
    "phone",
    "distance_km",
    "estimated_distance",
    "travel_time",
]


def assert_store_shape(store):
    """Assert that a store dict contains every required field."""
    for field in REQUIRED_STORE_FIELDS:
        assert field in store, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# GET /api/stores — default listing
# ---------------------------------------------------------------------------

class TestStoreListDefault:

    def test_returns_200(self, client):
        r = client.get("/api/stores")
        assert r.status_code == 200

    def test_success_true(self, client):
        r = client.get("/api/stores")
        assert get_json(r)["success"] is True

    def test_data_key_present(self, client):
        r = client.get("/api/stores")
        assert "data" in get_json(r)

    def test_data_is_list(self, client):
        r = client.get("/api/stores")
        assert isinstance(get_json(r)["data"], list)

    def test_count_key_present(self, client):
        r = client.get("/api/stores")
        assert "count" in get_json(r)

    def test_count_matches_data_length(self, client):
        r = client.get("/api/stores")
        body = get_json(r)
        assert body["count"] == len(body["data"])

    def test_returns_seeded_stores(self, client):
        r = client.get("/api/stores")
        assert get_json(r)["count"] >= 4

    def test_each_store_has_required_fields(self, client):
        r = client.get("/api/stores")
        for store in get_json(r)["data"]:
            assert_store_shape(store)

    def test_id_is_integer(self, client):
        r = client.get("/api/stores")
        for store in get_json(r)["data"]:
            assert isinstance(store["id"], int)

    def test_name_is_string(self, client):
        r = client.get("/api/stores")
        for store in get_json(r)["data"]:
            assert isinstance(store["name"], str)

    def test_pincode_is_string(self, client):
        r = client.get("/api/stores")
        for store in get_json(r)["data"]:
            assert isinstance(store["pincode"], str)

    def test_future_fields_are_null(self, client):
        r = client.get("/api/stores")
        for store in get_json(r)["data"]:
            assert store["estimated_distance"] is None
            assert store["travel_time"] is None

    def test_distance_km_null_in_default_listing(self, client):
        r = client.get("/api/stores")
        for store in get_json(r)["data"]:
            assert store["distance_km"] is None

    def test_phone_null_for_seeded_stores(self, client):
        r = client.get("/api/stores")
        for store in get_json(r)["data"]:
            assert store["phone"] is None


# ---------------------------------------------------------------------------
# GET /api/stores?pincode=
# ---------------------------------------------------------------------------

class TestStoreFilterByPincode:

    def test_valid_pincode_returns_200(self, client):
        r = client.get("/api/stores?pincode=201301")
        assert r.status_code == 200

    def test_valid_pincode_success_true(self, client):
        r = client.get("/api/stores?pincode=201301")
        assert get_json(r)["success"] is True

    def test_valid_pincode_returns_correct_store(self, client):
        r = client.get("/api/stores?pincode=201301")
        data = get_json(r)["data"]
        assert len(data) == 1
        assert data[0]["pincode"] == "201301"
        assert data[0]["city"] == "Noida"

    def test_valid_pincode_store_has_all_fields(self, client):
        r = client.get("/api/stores?pincode=201301")
        for store in get_json(r)["data"]:
            assert_store_shape(store)

    def test_delhi_pincode_returns_correct_store(self, client):
        r = client.get("/api/stores?pincode=110092")
        data = get_json(r)["data"]
        assert len(data) == 1
        assert data[0]["city"] == "Delhi"

    def test_invalid_pincode_returns_empty_list(self, client):
        r = client.get("/api/stores?pincode=000000")
        body = get_json(r)
        assert r.status_code == 200
        assert body["success"] is True
        assert body["data"] == []
        assert body["count"] == 0

    def test_count_correct_for_pincode(self, client):
        r = client.get("/api/stores?pincode=201301")
        body = get_json(r)
        assert body["count"] == len(body["data"])


# ---------------------------------------------------------------------------
# GET /api/stores?city=
# ---------------------------------------------------------------------------

class TestStoreFilterByCity:

    def test_city_filter_returns_200(self, client):
        r = client.get("/api/stores?city=Delhi")
        assert r.status_code == 200

    def test_city_filter_success_true(self, client):
        r = client.get("/api/stores?city=Delhi")
        assert get_json(r)["success"] is True

    def test_city_filter_returns_only_delhi_stores(self, client):
        r = client.get("/api/stores?city=Delhi")
        for store in get_json(r)["data"]:
            assert store["city"] == "Delhi"

    def test_city_filter_returns_two_delhi_stores(self, client):
        r = client.get("/api/stores?city=Delhi")
        assert get_json(r)["count"] == 2

    def test_city_filter_case_insensitive(self, client):
        r_upper = client.get("/api/stores?city=DELHI")
        r_lower = client.get("/api/stores?city=delhi")
        assert get_json(r_upper)["count"] == get_json(r_lower)["count"]

    def test_city_filter_noida(self, client):
        r = client.get("/api/stores?city=Noida")
        assert get_json(r)["count"] == 1
        assert get_json(r)["data"][0]["city"] == "Noida"

    def test_city_filter_unknown_city_returns_empty(self, client):
        r = client.get("/api/stores?city=AtlantisCity")
        body = get_json(r)
        assert body["success"] is True
        assert body["data"] == []
        assert body["count"] == 0

    def test_city_filter_store_shape_correct(self, client):
        r = client.get("/api/stores?city=Mumbai")
        for store in get_json(r)["data"]:
            assert_store_shape(store)


# ---------------------------------------------------------------------------
# GET /api/stores?state=
# ---------------------------------------------------------------------------

class TestStoreFilterByState:

    def test_state_filter_returns_200(self, client):
        r = client.get("/api/stores?state=Delhi")
        assert r.status_code == 200

    def test_state_filter_success_true(self, client):
        r = client.get("/api/stores?state=Delhi")
        assert get_json(r)["success"] is True

    def test_state_filter_returns_delhi_stores(self, client):
        r = client.get("/api/stores?state=Delhi")
        body = get_json(r)
        assert body["count"] == 2
        for store in body["data"]:
            assert store["state"] == "Delhi"

    def test_state_filter_maharashtra(self, client):
        r = client.get("/api/stores?state=Maharashtra")
        body = get_json(r)
        assert body["count"] == 1
        assert body["data"][0]["city"] == "Mumbai"

    def test_state_filter_uttar_pradesh(self, client):
        r = client.get("/api/stores?state=Uttar Pradesh")
        body = get_json(r)
        assert body["count"] == 1
        assert body["data"][0]["city"] == "Noida"

    def test_state_filter_case_insensitive(self, client):
        r_title = client.get("/api/stores?state=Maharashtra")
        r_lower = client.get("/api/stores?state=maharashtra")
        assert get_json(r_title)["count"] == get_json(r_lower)["count"]

    def test_state_filter_unknown_returns_empty(self, client):
        r = client.get("/api/stores?state=Narnia")
        body = get_json(r)
        assert body["success"] is True
        assert body["count"] == 0
        assert body["data"] == []

    def test_state_filter_store_shape_correct(self, client):
        r = client.get("/api/stores?state=Delhi")
        for store in get_json(r)["data"]:
            assert_store_shape(store)


# ---------------------------------------------------------------------------
# GET /api/stores?lat=&lng=  — proximity search
# ---------------------------------------------------------------------------

class TestStoreProximitySearch:

    # Coordinates near Noida — closest store should be Noida (201301)
    _NOIDA_LAT = 28.59
    _NOIDA_LNG = 77.34

    # Coordinates near Mumbai — closest store should be Andheri (400059)
    _MUMBAI_LAT = 19.11
    _MUMBAI_LNG = 72.87

    def test_proximity_returns_200(self, client):
        r = client.get(f"/api/stores?lat={self._NOIDA_LAT}&lng={self._NOIDA_LNG}")
        assert r.status_code == 200

    def test_proximity_success_true(self, client):
        r = client.get(f"/api/stores?lat={self._NOIDA_LAT}&lng={self._NOIDA_LNG}")
        assert get_json(r)["success"] is True

    def test_proximity_returns_list(self, client):
        r = client.get(f"/api/stores?lat={self._NOIDA_LAT}&lng={self._NOIDA_LNG}")
        assert isinstance(get_json(r)["data"], list)

    def test_proximity_respects_limit(self, client):
        r = client.get(f"/api/stores?lat={self._NOIDA_LAT}&lng={self._NOIDA_LNG}")
        assert get_json(r)["count"] <= 5

    def test_proximity_nearest_store_is_noida(self, client):
        r = client.get(f"/api/stores?lat={self._NOIDA_LAT}&lng={self._NOIDA_LNG}")
        first = get_json(r)["data"][0]
        assert first["pincode"] == "201301"

    def test_proximity_nearest_store_is_mumbai(self, client):
        r = client.get(f"/api/stores?lat={self._MUMBAI_LAT}&lng={self._MUMBAI_LNG}")
        first = get_json(r)["data"][0]
        assert first["pincode"] == "400059"

    def test_proximity_distance_km_populated(self, client):
        r = client.get(f"/api/stores?lat={self._NOIDA_LAT}&lng={self._NOIDA_LNG}")
        for store in get_json(r)["data"]:
            if store["latitude"] is not None:
                assert store["distance_km"] is not None

    def test_proximity_distance_km_is_numeric(self, client):
        r = client.get(f"/api/stores?lat={self._NOIDA_LAT}&lng={self._NOIDA_LNG}")
        for store in get_json(r)["data"]:
            if store["distance_km"] is not None:
                assert isinstance(store["distance_km"], (int, float))

    def test_proximity_results_ordered_ascending(self, client):
        r = client.get(f"/api/stores?lat={self._NOIDA_LAT}&lng={self._NOIDA_LNG}")
        distances = [
            s["distance_km"]
            for s in get_json(r)["data"]
            if s["distance_km"] is not None
        ]
        assert distances == sorted(distances)

    def test_proximity_store_shape_correct(self, client):
        r = client.get(f"/api/stores?lat={self._NOIDA_LAT}&lng={self._NOIDA_LNG}")
        for store in get_json(r)["data"]:
            assert_store_shape(store)

    def test_invalid_lat_returns_400(self, client):
        r = client.get("/api/stores?lat=abc&lng=77.34")
        assert r.status_code == 400

    def test_invalid_lat_success_false(self, client):
        r = client.get("/api/stores?lat=abc&lng=77.34")
        assert get_json(r)["success"] is False

    def test_invalid_lat_error_code(self, client):
        r = client.get("/api/stores?lat=abc&lng=77.34")
        assert get_json(r)["error"] == "BAD_REQUEST"

    def test_invalid_lng_returns_400(self, client):
        r = client.get("/api/stores?lat=28.59&lng=notanumber")
        assert r.status_code == 400

    def test_partial_coords_falls_through_to_default(self, client):
        # Only lat provided without lng — should fall through to default listing
        r = client.get("/api/stores?lat=28.59")
        assert r.status_code == 200
        assert get_json(r)["success"] is True


# ---------------------------------------------------------------------------
# GET /api/stores/<id> — single store
# ---------------------------------------------------------------------------

class TestStoreById:

    def test_valid_id_returns_200(self, client):
        r = client.get("/api/stores/1")
        assert r.status_code == 200

    def test_valid_id_success_true(self, client):
        r = client.get("/api/stores/1")
        assert get_json(r)["success"] is True

    def test_valid_id_data_key_present(self, client):
        r = client.get("/api/stores/1")
        assert "data" in get_json(r)

    def test_valid_id_data_is_dict(self, client):
        r = client.get("/api/stores/1")
        assert isinstance(get_json(r)["data"], dict)

    def test_valid_id_returns_correct_store(self, client):
        r = client.get("/api/stores/1")
        store = get_json(r)["data"]
        assert store["id"] == 1
        assert store["pincode"] == "201301"
        assert store["city"] == "Noida"
        assert store["state"] == "Uttar Pradesh"

    def test_valid_id_all_fields_present(self, client):
        r = client.get("/api/stores/1")
        assert_store_shape(get_json(r)["data"])

    def test_valid_id_latitude_populated(self, client):
        r = client.get("/api/stores/1")
        store = get_json(r)["data"]
        assert store["latitude"] is not None
        assert store["longitude"] is not None

    def test_valid_id_future_fields_null(self, client):
        r = client.get("/api/stores/1")
        store = get_json(r)["data"]
        assert store["estimated_distance"] is None
        assert store["travel_time"] is None
        assert store["distance_km"] is None

    def test_all_seeded_stores_retrievable(self, client):
        for store_id in range(1, 5):
            r = client.get(f"/api/stores/{store_id}")
            assert r.status_code == 200
            assert get_json(r)["success"] is True

    def test_invalid_id_returns_404(self, client):
        r = client.get("/api/stores/999999")
        assert r.status_code == 404

    def test_invalid_id_success_false(self, client):
        r = client.get("/api/stores/999999")
        assert get_json(r)["success"] is False

    def test_invalid_id_error_code(self, client):
        r = client.get("/api/stores/999999")
        assert get_json(r)["error"] == "NOT_FOUND"

    def test_invalid_id_message_present(self, client):
        r = client.get("/api/stores/999999")
        data = get_json(r)
        assert "message" in data
        assert len(data["message"]) > 0

    def test_non_integer_id_returns_404(self, client):
        r = client.get("/api/stores/abc")
        assert r.status_code == 404

    def test_zero_id_returns_404(self, client):
        r = client.get("/api/stores/0")
        assert r.status_code == 404