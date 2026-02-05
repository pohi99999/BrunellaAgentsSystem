"""Centralized logging configuration for the Brunella Agent System."""

import logging
import logging.config
import os
import sys
from typing import Any


def get_log_level() -> int:
    """Get the log level from environment variable."""
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    return getattr(logging, level_name, logging.INFO)


def is_production() -> bool:
    """Check if we're running in production mode."""
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def get_logging_config() -> dict[str, Any]:
    """
    Get the logging configuration dictionary.
    
    Returns structured JSON logging in production, simple format in development.
    """
    log_level = get_log_level()
    
    # Base configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(levelname)s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "detailed" if not is_production() else "simple",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            # Application loggers
            "src": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            # Security-related logger (always WARNING or higher)
            "src.utils.middleware": {
                "level": max(logging.WARNING, log_level),
                "handlers": ["console"],
                "propagate": False,
            },
            "src.utils.prompt_validator": {
                "level": max(logging.WARNING, log_level),
                "handlers": ["console"],
                "propagate": False,
            },
            # LangChain/LangGraph loggers (reduce noise)
            "langchain": {
                "level": logging.WARNING,
                "handlers": ["console"],
                "propagate": False,
            },
            "langgraph": {
                "level": logging.WARNING,
                "handlers": ["console"],
                "propagate": False,
            },
            # FastAPI/Uvicorn
            "uvicorn": {
                "level": logging.INFO,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": logging.INFO if not is_production() else logging.WARNING,
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }
    
    return config


def setup_logging() -> None:
    """
    Configure logging for the application.
    
    Should be called once at application startup.
    """
    config = get_logging_config()
    logging.config.dictConfig(config)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    env = "production" if is_production() else "development"
    logger.info(
        "Logging configured for %s environment with level %s",
        env,
        logging.getLevelName(get_log_level()),
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: The name of the logger (typically __name__)
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)
