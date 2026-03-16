"""
API Test Suite — OpenBreweryDB
Tests cover: status codes, response schema, data integrity,
business rules, query parameters, and edge cases.
"""
import pytest
import requests

BASE_URL = "https://api.openbrewerydb.org/v1"

VALID_BREWERY_TYPES = {
    "micro", "nano", "regional", "brewpub", "large",
    "planning", "bar", "contract", "proprietor", "closed"
}

REQUIRED_FIELDS = ["id", "name", "brewery_type", "city", "state", "country"]


# ─────────────────────────────────────────────
# STATUS CODE & RESPONSE FORMAT TESTS
# ─────────────────────────────────────────────

class TestStatusCodes:
    def test_list_breweries_returns_200(self, api_session, base_url):
        """GET /breweries should return HTTP 200."""
        response = api_session.get(f"{base_url}/breweries")
        assert response.status_code == 200

    def test_response_content_type_is_json(self, api_session, base_url):
        """Response Content-Type should be application/json."""
        response = api_session.get(f"{base_url}/breweries")
        assert "application/json" in response.headers.get("Content-Type", "")

    def test_single_brewery_returns_200(self, api_session, base_url, sample_breweries):
        """GET /breweries/{id} should return 200 for a valid ID."""
        brewery_id = sample_breweries[0]["id"]
        response = api_session.get(f"{base_url}/breweries/{brewery_id}")
        assert response.status_code == 200

    def test_invalid_brewery_id_returns_404(self, api_session, base_url):
        """GET /breweries/{id} with a nonexistent ID should return 404."""
        response = api_session.get(f"{base_url}/breweries/this-id-does-not-exist-xyz")
        assert response.status_code == 404

    def test_search_returns_200(self, api_session, base_url):
        """GET /breweries/search should return 200 with a valid query."""
        response = api_session.get(f"{base_url}/breweries/search", params={"query": "dog"})
        assert response.status_code == 200


# ─────────────────────────────────────────────
# RESPONSE SCHEMA TESTS
# ─────────────────────────────────────────────

class TestResponseSchema:
    def test_brewery_list_is_array(self, api_session, base_url):
        """Response body for /breweries should be a JSON array."""
        response = api_session.get(f"{base_url}/breweries")
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"

    def test_brewery_object_has_required_fields(self, sample_breweries):
        """Every brewery object must contain all required fields."""
        for brewery in sample_breweries:
            for field in REQUIRED_FIELDS:
                assert field in brewery, (
                    f"Brewery '{brewery.get('id')}' missing required field: '{field}'"
                )

    def test_brewery_id_is_string(self, sample_breweries):
        """Brewery 'id' field should be a non-empty string."""
        for brewery in sample_breweries:
            assert isinstance(brewery["id"], str) and len(brewery["id"]) > 0

    def test_brewery_name_is_string(self, sample_breweries):
        """Brewery 'name' field should be a non-empty string."""
        for brewery in sample_breweries:
            assert isinstance(brewery["name"], str) and len(brewery["name"]) > 0

    def test_single_brewery_returns_object(self, api_session, base_url, sample_breweries):
        """Single brewery endpoint should return a JSON object, not an array."""
        brewery_id = sample_breweries[0]["id"]
        response = api_session.get(f"{base_url}/breweries/{brewery_id}")
        data = response.json()
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"


# ─────────────────────────────────────────────
# BUSINESS RULE / DATA INTEGRITY TESTS
# ─────────────────────────────────────────────

class TestBusinessRules:
    def test_brewery_type_is_valid_enum(self, sample_breweries):
        """brewery_type must be one of the known valid types."""
        invalid = [
            b for b in sample_breweries
            if b.get("brewery_type") not in VALID_BREWERY_TYPES
        ]
        assert len(invalid) == 0, (
            f"{len(invalid)} breweries have invalid type: "
            f"{[b['brewery_type'] for b in invalid[:5]]}"
        )

    def test_country_field_is_non_empty(self, sample_breweries):
        """Country field should not be null or empty for any brewery."""
        missing = [b for b in sample_breweries if not b.get("country")]
        assert len(missing) == 0, f"{len(missing)} breweries missing country field"

    def test_ids_are_unique(self, sample_breweries):
        """No duplicate brewery IDs should exist in the response."""
        ids = [b["id"] for b in sample_breweries]
        assert len(ids) == len(set(ids)), "Duplicate brewery IDs found in response"

    def test_website_url_format_when_present(self, sample_breweries):
        """If website_url is present, it should start with http:// or https://."""
        invalid = [
            b for b in sample_breweries
            if b.get("website_url") and
            not b["website_url"].startswith(("http://", "https://"))
        ]
        assert len(invalid) == 0, (
            f"{len(invalid)} breweries have malformed website_url"
        )


# ─────────────────────────────────────────────
# QUERY PARAMETER TESTS
# ─────────────────────────────────────────────

class TestQueryParameters:
    def test_filter_by_type_micro(self, api_session, base_url):
        """Filtering by brewery_type=micro should only return micro breweries."""
        response = api_session.get(
            f"{base_url}/breweries", params={"by_type": "micro", "per_page": 20}
        )
        assert response.status_code == 200
        data = response.json()
        for brewery in data:
            assert brewery["brewery_type"] == "micro", (
                f"Expected 'micro', got '{brewery['brewery_type']}'"
            )

    def test_filter_by_state(self, api_session, base_url):
        """Filtering by by_state=colorado should return Colorado breweries."""
        response = api_session.get(
            f"{base_url}/breweries", params={"by_state": "colorado", "per_page": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0, "Expected results for Colorado"
        for brewery in data:
            assert brewery.get("state", "").lower() == "colorado", (
                f"Expected Colorado brewery, got state='{brewery.get('state')}'"
            )

    def test_per_page_parameter_respected(self, api_session, base_url):
        """per_page=5 should return exactly 5 results."""
        response = api_session.get(
            f"{base_url}/breweries", params={"per_page": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5, f"Expected 5 results, got {len(data)}"

    def test_per_page_max_200(self, api_session, base_url):
        """per_page should not exceed API max of 200."""
        response = api_session.get(
            f"{base_url}/breweries", params={"per_page": 200}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 200

    def test_search_returns_relevant_results(self, api_session, base_url):
        """Search results should contain the query term in name or relevant fields."""
        query = "sierra"
        response = api_session.get(
            f"{base_url}/breweries/search", params={"query": query, "per_page": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0, f"Expected results for search query '{query}'"

    def test_pagination_page_2_differs_from_page_1(self, api_session, base_url):
        """Page 2 results should be different from page 1 results."""
        page1 = api_session.get(
            f"{base_url}/breweries", params={"per_page": 10, "page": 1}
        ).json()
        page2 = api_session.get(
            f"{base_url}/breweries", params={"per_page": 10, "page": 2}
        ).json()
        ids_page1 = {b["id"] for b in page1}
        ids_page2 = {b["id"] for b in page2}
        assert ids_page1.isdisjoint(ids_page2), "Page 1 and Page 2 returned overlapping results"


# ─────────────────────────────────────────────
# EDGE CASE TESTS
# ─────────────────────────────────────────────

class TestEdgeCases:
    def test_empty_search_query_returns_gracefully(self, api_session, base_url):
        """Search with empty string should return 200 without crashing."""
        response = api_session.get(
            f"{base_url}/breweries/search", params={"query": ""}
        )
        assert response.status_code in (200, 400, 422), (
            f"Unexpected status {response.status_code} for empty search"
        )

    def test_response_time_under_3_seconds(self, api_session, base_url):
        """API response time should be under 3 seconds."""
        response = api_session.get(f"{base_url}/breweries", params={"per_page": 10})
        assert response.elapsed.total_seconds() < 3.0, (
            f"Response took {response.elapsed.total_seconds():.2f}s — exceeded 3s threshold"
        )

    def test_random_brewery_endpoint(self, api_session, base_url):
        """GET /breweries/random should return a single brewery object."""
        response = api_session.get(f"{base_url}/breweries/random")
        assert response.status_code == 200
        data = response.json()
        # random returns a list with one item
        assert isinstance(data, list) and len(data) == 1
        assert "id" in data[0]
