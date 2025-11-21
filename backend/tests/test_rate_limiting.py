import sys
import os
import time
import importlib
from fastapi.testclient import TestClient
import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the module so we can reload it
import app as app_module

@pytest.fixture
def client(monkeypatch):
    """
    Fixture to create a TestClient with a reloaded app instance for each test.
    This ensures that mocks and environment variables are applied correctly for each test.
    """
    monkeypatch.setenv("API_KEY", "test_api_key")
    importlib.reload(app_module)
    client = TestClient(app_module.app)
    # Reset the limiter state before each test
    app_module.limiter.reset()
    return client

def test_coder_generate_rate_limit(client):
    """
    Test that the /coder/generate endpoint is rate-limited to 10 requests per minute.
    """
    headers = {"X-API-Key": "test_api_key"}

    # The first 10 requests should succeed (or return a non-429 error)
    for _ in range(10):
        response = client.post("/coder/generate", headers=headers, json={"language": "python", "prompt": "create a fibonacci function"})
        assert response.status_code != 429

    # The 11th request should be rate-limited
    response = client.post("/coder/generate", headers=headers, json={"language": "python", "prompt": "create a fibonacci function"})
    assert response.status_code == 429

def test_agent_rate_limit(client):
    """
    Test that the /agent endpoint is rate-limited to 5 requests per minute.
    """
    headers = {"X-API-Key": "test_api_key"}

    # The first 5 requests should succeed
    for i in range(5):
        response = client.post("/agent/test", headers=headers, json={"input": "some message"})
        # We expect a 404 because the test client doesn't actually route to the langgraph server,
        # but the rate limiter should be applied before the 404 is returned.
        assert response.status_code == 404

    # The 6th request should be rate-limited
    response = client.post("/agent/test", headers=headers, json={"input": "some message"})
    assert response.status_code == 429
