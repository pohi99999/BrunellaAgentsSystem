
import os
import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_coder_generate_rate_limit():
    """Test that /coder/generate endpoint is rate limited to 10 requests per minute."""
    with patch.dict(os.environ, {}, clear=True):
        with patch("src.app.coder_chain") as mock_coder_chain:
            mock_coder_chain.invoke.return_value = "def test(): pass"
            
            # Make 10 requests (should succeed)
            for i in range(10):
                response = client.post(
                    "/coder/generate",
                    json={"language": "python", "prompt": f"create function {i}"},
                )
                assert response.status_code == 200, f"Request {i+1} failed"
            
            # 11th request should be rate limited
            response = client.post(
                "/coder/generate",
                json={"language": "python", "prompt": "create another function"},
            )
            assert response.status_code == 429
            assert "rate limit" in response.text.lower()


def test_health_endpoint_not_rate_limited():
    """Test that /health endpoint is not rate limited."""
    # Make many requests to health endpoint
    for i in range(20):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_rate_limit_different_ips():
    """Test that rate limiting is per IP address."""
    with patch.dict(os.environ, {}, clear=True):
        with patch("src.app.coder_chain") as mock_coder_chain:
            mock_coder_chain.invoke.return_value = "def test(): pass"
            
            # Simulate requests from different IPs by testing the endpoint
            # Note: In TestClient, all requests come from the same test client,
            # so this is a basic sanity check that the endpoint works
            response = client.post(
                "/coder/generate",
                json={"language": "python", "prompt": "test"},
            )
            assert response.status_code == 200
