
import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_coder_generate_with_valid_key():
    with patch.dict(os.environ, {"API_KEY": "test-key"}):
        # We need to mock the coder chain to avoid actual LLM calls
        with patch("src.app.coder_chain") as mock_coder_chain:
            mock_coder_chain.invoke.return_value = "def factorial(n): pass"
            response = client.post(
                "/coder/generate",
                headers={"X-API-Key": "test-key"},
                json={"language": "python", "prompt": "create a factorial function"},
            )
            assert response.status_code == 200
            assert "code" in response.json()


def test_coder_generate_with_invalid_key():
    with patch.dict(os.environ, {"API_KEY": "test-key"}):
        response = client.post(
            "/coder/generate",
            headers={"X-API-Key": "invalid-key"},
            json={"language": "python", "prompt": "create a factorial function"},
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid API Key"}


def test_coder_generate_with_missing_key():
    with patch.dict(os.environ, {"API_KEY": "test-key"}):
        response = client.post(
            "/coder/generate",
            json={"language": "python", "prompt": "create a factorial function"},
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Missing API Key"}


def test_coder_generate_with_auth_disabled():
    with patch.dict(os.environ, {}, clear=True):
        with patch("src.app.coder_chain") as mock_coder_chain:
            mock_coder_chain.invoke.return_value = "def factorial(n): pass"
            response = client.post(
                "/coder/generate",
                json={"language": "python", "prompt": "create a factorial function"},
            )
            assert response.status_code == 200
            assert "code" in response.json()


def test_health_check_is_public():
    with patch.dict(os.environ, {"API_KEY": "test-key"}):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
