import pytest
from fastapi.testclient import TestClient
from backend.src.app import app

client = TestClient(app)

def test_app_import():
    """
    Tests if the FastAPI app object can be imported successfully.
    """
    assert app is not None

def test_crew_endpoint_success():
    """
    Tests the /crew endpoint for a successful response.
    """
    response = client.post("/crew", json={"topic": "AI in 2025"})
    assert response.status_code == 200
    # We expect a string response from the crew's kickoff method
    assert isinstance(response.text, str)
    assert len(response.text) > 0
