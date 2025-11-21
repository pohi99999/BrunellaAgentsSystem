import logging.config
import os

def get_logging_config(stream=None):
    """
    Returns the logging configuration dictionary.

    Args:
        stream: The stream to use for the console handler. Defaults to stdout.
    """
    if stream is None:
        stream = "ext://sys.stdout"

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
            },
            "simple": {
                "format": "%(levelname)s: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json" if os.getenv("ENVIRONMENT") == "production" else "simple",
                "stream": stream,
            }
        },
        "loggers": {
            "root": {
                "level": "DEBUG" if os.getenv("ENVIRONMENT") == "development" else "INFO",
                "handlers": ["console"],
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

def setup_logging(stream=None):
    """
    Sets up the logging configuration for the application.
    """
    logging.config.dictConfig(get_logging_config(stream))
