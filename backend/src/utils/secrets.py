"""Utilities for retrieving secrets in different environments."""

from __future__ import annotations

import os
from functools import lru_cache

from google.cloud import secretmanager


@lru_cache(maxsize=None)
def get_secret(project_id: str, secret_name: str) -> str:
    """Fetch the latest version of a secret from Secret Manager."""
    if not project_id:
        raise ValueError("project_id must be provided to retrieve secrets")
    if not secret_name:
        raise ValueError("secret_name must be provided to retrieve secrets")

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("utf-8")


@lru_cache(maxsize=1)
def get_gemini_api_key() -> str:
    """Return the Gemini API key based on the current environment."""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment == "production":
        project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError(
                "GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT must be set when ENVIRONMENT=production"
            )
        return get_secret(project_id, "GEMINI_API_KEY")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")
    return api_key
