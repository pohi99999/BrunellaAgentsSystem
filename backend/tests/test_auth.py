import sys
import os
import importlib
from fastapi.testclient import TestClient
import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the module so we can reload it
import app as app_module

def test_auth_disabled():
    """
    Test that if API_KEY is not set, authentication is disabled and requests pass through.
    """
    # Ensure API_KEY is not set
    if "API_KEY" in os.environ:
        del os.environ["API_KEY"]

    importlib.reload(app_module)
    client = TestClient(app_module.app)

    response = client.post("/coder/generate", json={"language": "python", "prompt": "create a fibonacci function"})
    # It will likely be a 500 error as the model is not available, but not 401.
    assert response.status_code != 401

def test_missing_api_key(monkeypatch):
    """
    Test that if API_KEY is set, a missing X-API-Key header results in a 401 error.
    """
    monkeypatch.setenv("API_KEY", "test_api_key")
    importlib.reload(app_module)
    client = TestClient(app_module.app)

    response = client.post("/coder/generate", json={"language": "python", "prompt": "create a fibonacci function"})
    assert response.status_code == 401
    assert response.json() == {"detail": "API key is missing"}

def test_incorrect_api_key(monkeypatch):
    """
    Test that if API_KEY is set, an incorrect X-API-Key header results in a 401 error.
    """
    monkeypatch.setenv("API_KEY", "test_api_key")
    importlib.reload(app_module)
    client = TestClient(app_module.app)

    headers = {"X-API-Key": "incorrect_key"}
    response = client.post("/coder/generate", headers=headers, json={"language": "python", "prompt": "create a fibonacci function"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key"}

def test_valid_api_key(monkeypatch):
    """
    Test that if API_KEY is set, a correct X-API-Key header allows the request to proceed.
    """
    monkeypatch.setenv("API_KEY", "test_api_key")
    importlib.reload(app_module)
    client = TestClient(app_module.app)

    headers = {"X-API-Key": "test_api_key"}
    response = client.post("/coder/generate", headers=headers, json={"language": "python", "prompt": "create a fibonacci function"})
    # Expect a non-401 error. It will likely be 500.
    assert response.status_code != 401
