"""
Unit tests for secrets management utility.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

from utils.secrets import get_secret, get_gemini_api_key


class TestGetSecret:
    """Tests for get_secret function."""

    @patch("utils.secrets.secretmanager.SecretManagerServiceClient")
    def test_get_secret_retrieves_from_secret_manager(self, mock_sm_client):
        """Test that get_secret correctly calls Secret Manager."""
        # Mock Secret Manager client
        mock_client_instance = MagicMock()
        mock_sm_client.return_value = mock_client_instance

        # Mock access_secret_version response
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "secret-value-123"
        mock_client_instance.access_secret_version.return_value = mock_response

        result = get_secret("my-project", "MY_SECRET")

        assert result == "secret-value-123"
        mock_client_instance.access_secret_version.assert_called_once()
        call_args = mock_client_instance.access_secret_version.call_args
        assert "projects/my-project/secrets/MY_SECRET/versions/latest" in str(call_args)

    def test_get_secret_raises_on_empty_project_id(self):
        """Test that get_secret raises ValueError for empty project_id."""
        with pytest.raises(ValueError, match="project_id must be provided"):
            get_secret("", "MY_SECRET")

    def test_get_secret_raises_on_empty_secret_name(self):
        """Test that get_secret raises ValueError for empty secret_name."""
        with pytest.raises(ValueError, match="secret_name must be provided"):
            get_secret("my-project", "")


class TestGetGeminiApiKey:
    """Tests for get_gemini_api_key function."""

    @patch.dict(os.environ, {"ENVIRONMENT": "development", "GEMINI_API_KEY": "test-dev-key"}, clear=True)
    def test_development_mode_returns_env_var(self):
        """Test that in development mode, API key comes from environment variable."""
        # Clear cache from previous tests
        get_gemini_api_key.cache_clear()
        result = get_gemini_api_key()
        assert result == "test-dev-key"

    @patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True)
    def test_development_mode_missing_key_raises_error(self):
        """Test that missing key in development raises ValueError."""
        get_gemini_api_key.cache_clear()
        with pytest.raises(ValueError, match="GEMINI_API_KEY is not set"):
            get_gemini_api_key()

    @patch.dict(os.environ, {"ENVIRONMENT": "production", "GCP_PROJECT_ID": "my-project"}, clear=True)
    @patch("utils.secrets.get_secret")
    def test_production_mode_uses_secret_manager(self, mock_get_secret):
        """Test that production mode calls get_secret with correct parameters."""
        get_gemini_api_key.cache_clear()
        mock_get_secret.return_value = "prod-secret-value"

        result = get_gemini_api_key()

        assert result == "prod-secret-value"
        mock_get_secret.assert_called_once_with("my-project", "GEMINI_API_KEY")

    @patch.dict(os.environ, {}, clear=True)
    def test_no_environment_set_defaults_to_development(self):
        """Test that without ENVIRONMENT variable, defaults to development behavior."""
        get_gemini_api_key.cache_clear()
        # Should raise because GEMINI_API_KEY is also not set
        with pytest.raises(ValueError, match="GEMINI_API_KEY is not set"):
            get_gemini_api_key()

    @patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True)
    def test_production_without_gcp_project_id_raises_error(self):
        """Test production mode behavior when GCP_PROJECT_ID is missing."""
        get_gemini_api_key.cache_clear()
        with pytest.raises(ValueError, match="GCP_PROJECT_ID.*must be set"):
            get_gemini_api_key()

    @patch.dict(os.environ, {"ENVIRONMENT": "production", "GOOGLE_CLOUD_PROJECT": "alt-project"}, clear=True)
    @patch("utils.secrets.get_secret")
    def test_production_uses_google_cloud_project_fallback(self, mock_get_secret):
        """Test that GOOGLE_CLOUD_PROJECT is used as fallback for GCP_PROJECT_ID."""
        get_gemini_api_key.cache_clear()
        mock_get_secret.return_value = "prod-key-alt"

        result = get_gemini_api_key()

        mock_get_secret.assert_called_once_with("alt-project", "GEMINI_API_KEY")
        assert result == "prod-key-alt"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
