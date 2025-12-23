import logging
import os
from unittest.mock import patch

import pytest

from src.utils.logging_config import (
    get_log_level,
    is_production,
    get_logging_config,
    setup_logging,
    get_logger,
)


def test_get_log_level_default():
    """Test that default log level is INFO."""
    with patch.dict(os.environ, {}, clear=True):
        assert get_log_level() == logging.INFO


def test_get_log_level_from_env():
    """Test that log level is read from environment variable."""
    with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
        assert get_log_level() == logging.DEBUG
    
    with patch.dict(os.environ, {"LOG_LEVEL": "WARNING"}):
        assert get_log_level() == logging.WARNING
    
    with patch.dict(os.environ, {"LOG_LEVEL": "ERROR"}):
        assert get_log_level() == logging.ERROR


def test_get_log_level_case_insensitive():
    """Test that log level is case insensitive."""
    with patch.dict(os.environ, {"LOG_LEVEL": "debug"}):
        assert get_log_level() == logging.DEBUG
    
    with patch.dict(os.environ, {"LOG_LEVEL": "WaRnInG"}):
        assert get_log_level() == logging.WARNING


def test_is_production_default():
    """Test that default environment is development."""
    with patch.dict(os.environ, {}, clear=True):
        assert is_production() is False


def test_is_production_from_env():
    """Test that production mode is detected from environment."""
    with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
        assert is_production() is True
    
    with patch.dict(os.environ, {"ENVIRONMENT": "PRODUCTION"}):
        assert is_production() is True
    
    with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
        assert is_production() is False


def test_get_logging_config_structure():
    """Test that logging config has required structure."""
    config = get_logging_config()
    
    # Check basic structure
    assert "version" in config
    assert config["version"] == 1
    assert "formatters" in config
    assert "handlers" in config
    assert "loggers" in config
    assert "root" in config
    
    # Check formatters
    assert "simple" in config["formatters"]
    assert "detailed" in config["formatters"]
    
    # Check handlers
    assert "console" in config["handlers"]
    
    # Check key loggers
    assert "src" in config["loggers"]
    assert "src.utils.middleware" in config["loggers"]
    assert "src.utils.prompt_validator" in config["loggers"]


def test_get_logging_config_security_loggers():
    """Test that security-related loggers have appropriate levels."""
    config = get_logging_config()
    
    # Security loggers should be at least WARNING
    middleware_level = config["loggers"]["src.utils.middleware"]["level"]
    validator_level = config["loggers"]["src.utils.prompt_validator"]["level"]
    
    assert middleware_level >= logging.WARNING
    assert validator_level >= logging.WARNING


def test_get_logging_config_development():
    """Test logging config in development mode."""
    with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
        config = get_logging_config()
        
        # In development, should use detailed formatter
        assert config["handlers"]["console"]["formatter"] == "detailed"


def test_get_logging_config_production():
    """Test logging config in production mode."""
    with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
        config = get_logging_config()
        
        # In production, should use simple formatter
        assert config["handlers"]["console"]["formatter"] == "simple"


def test_setup_logging():
    """Test that setup_logging configures logging without errors."""
    # This should not raise any exceptions
    setup_logging()
    
    # Verify that logging is configured
    logger = logging.getLogger("src")
    assert logger is not None


def test_get_logger():
    """Test that get_logger returns a logger instance."""
    logger = get_logger("test.module")
    
    assert logger is not None
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test.module"


def test_logging_config_reduces_noise():
    """Test that third-party loggers have reduced verbosity."""
    config = get_logging_config()
    
    # LangChain/LangGraph should be WARNING or higher
    assert config["loggers"]["langchain"]["level"] == logging.WARNING
    assert config["loggers"]["langgraph"]["level"] == logging.WARNING
