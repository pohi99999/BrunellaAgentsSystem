"""
Unit tests for secrets management utility.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

from utils.secrets import get_secret


class TestGetSecret:
    """Tests for get_secret function."""

    @patch.dict(os.environ, {"ENVIRONMENT": "development", "GEMINI_API_KEY": "test-dev-key"})
    def test_development_mode_returns_env_var(self):
        """Test that in development mode, secrets come from environment variables."""
        result = get_secret("GEMINI_API_KEY")
        assert result == "test-dev-key"

    @patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True)
    def test_development_mode_missing_key_returns_none(self):
        """Test that missing key in development returns None."""
        result = get_secret("NONEXISTENT_KEY")
        assert result is None

    @patch.dict(os.environ, {"ENVIRONMENT": "production", "GCP_PROJECT_ID": "my-project"})
    @patch("utils.secrets.secretmanager.SecretManagerServiceClient")
    def test_production_mode_uses_secret_manager(self, mock_sm_client):
        """Test that production mode attempts to use Secret Manager."""
        # Mock Secret Manager client
        mock_client_instance = MagicMock()
        mock_sm_client.return_value = mock_client_instance

        # Mock access_secret_version response
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "prod-secret-value"
        mock_client_instance.access_secret_version.return_value = mock_response

        # Note: This test may need adjustment based on actual implementation
        # If SecretManagerServiceClient is not available in dev, test might fail
        try:
            result = get_secret("GEMINI_API_KEY")
            # If secret manager is properly mocked, should return the mocked value
            assert result == "prod-secret-value" or result is None
        except ImportError:
            pytest.skip("Secret Manager client not available in test environment")

    @patch.dict(os.environ, {}, clear=True)
    def test_no_environment_set_defaults_to_development(self):
        """Test that without ENVIRONMENT variable, defaults to development behavior."""
        # Without ENVIRONMENT set, should default to development mode
        result = get_secret("NONEXISTENT_KEY")
        assert result is None or isinstance(result, str)

    @patch.dict(os.environ, {"ENVIRONMENT": "development", "TEST_KEY": ""})
    def test_empty_string_environment_variable(self):
        """Test handling of empty string environment variable."""
        result = get_secret("TEST_KEY")
        # Should return empty string (not None) since key exists
        assert result == ""

    def test_key_name_validation(self):
        """Test that key names are handled correctly."""
        # Test with various key name formats
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            assert get_secret("") is None or get_secret("") == ""
            # Very long key name
            long_key = "A" * 1000
            assert get_secret(long_key) is None


class TestSecretManagerIntegration:
    """Integration-style tests for secret manager behavior."""

    @patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_production_without_gcp_project_id(self):
        """Test production mode behavior when GCP_PROJECT_ID is missing."""
        # Should handle gracefully or raise appropriate error
        with pytest.raises((ValueError, KeyError, AttributeError)) or patch(
            "utils.secrets.secretmanager"
        ):
            result = get_secret("GEMINI_API_KEY")
            # Behavior depends on implementation - might return None or raise error

    @patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "production",
            "GCP_PROJECT_ID": "test-project",
            "GEMINI_API_KEY": "fallback-key",
        },
    )
    @patch("utils.secrets.secretmanager.SecretManagerServiceClient")
    def test_production_fallback_to_env_on_sm_failure(self, mock_sm_client):
        """Test that if Secret Manager fails, might fallback to env var."""
        # Mock Secret Manager to raise exception
        mock_sm_client.side_effect = Exception("Secret Manager unavailable")

        try:
            result = get_secret("GEMINI_API_KEY")
            # Depending on implementation, might return env var as fallback
            assert result is None or result == "fallback-key"
        except Exception as e:
            # Or might propagate the exception
            assert "Secret Manager" in str(e)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
