import sys
import os
import logging
import json
from io import StringIO
import pytest
import importlib

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/utils')))

# Import the module so we can reload it
import logging_config

@pytest.fixture
def stream():
    """
    Fixture to create a StringIO stream.
    """
    return StringIO()

def test_development_logging(monkeypatch, stream):
    """
    Test that logging is in simple format in development mode.
    """
    monkeypatch.setenv("ENVIRONMENT", "development")
    importlib.reload(logging_config)
    logging_config.setup_logging(stream)

    logger = logging.getLogger("test_logger")
    logger.info("This is an info message.")

    log_output = stream.getvalue()
    assert "INFO: This is an info message." in log_output

def test_production_logging(monkeypatch, stream):
    """
    Test that logging is in JSON format in production mode.
    """
    monkeypatch.setenv("ENVIRONMENT", "production")
    importlib.reload(logging_config)
    logging_config.setup_logging(stream)

    logger = logging.getLogger("test_logger")
    logger.warning("This is a warning message.")

    log_output = stream.getvalue()
    log_json = json.loads(log_output)

    assert log_json["levelname"] == "WARNING"
    assert log_json["message"] == "This is a warning message."
