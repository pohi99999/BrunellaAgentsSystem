import pytest
from fastapi.testclient import TestClient
from backend.src.app import app

client = TestClient(app)

def test_app_import():
    """
    Tests if the FastAPI app object can be imported successfully.
    """
    assert app is not None

