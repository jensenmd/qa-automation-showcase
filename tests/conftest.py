"""
Shared fixtures for the QA Automation Showcase.
Base URL and reusable session setup for OpenBreweryDB API tests.
"""
import pytest
import requests

BASE_URL = "https://api.openbrewerydb.org/v1"

@pytest.fixture(scope="session")
def api_session():
    """Reusable requests session for all API tests."""
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture(scope="session")
def sample_breweries(api_session, base_url):
    """Fetch a sample dataset once per session for reuse across tests."""
    response = api_session.get(f"{base_url}/breweries", params={"per_page": 50})
    assert response.status_code == 200, "Failed to fetch sample brewery data"
    return response.json()
