import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure we can import from the backend/src module directly
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from src.app import app

client = TestClient(app)

def test_app_import():
    """
    Tests if the FastAPI app object can be imported successfully.
    """
    assert app is not None

def test_health_endpoint():
    """Tests the /health endpoint returns status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
