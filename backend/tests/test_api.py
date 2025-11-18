from fastapi.testclient import TestClient

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
