"""Logging."""

import json
import logging
import os

_initted = False


class JsonFormatter(logging.Formatter):
    """Simple structured logging."""

    def format(self, record):
        """Log message formatter."""
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
        }
        return json.dumps(log_record)


def init():
    """Initialize logging."""
    # Flyte calls this multiple times, resulting in duplicate handlers, hence the guard.
    global _initted
    if _initted:
        return
    _initted = True

    level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.propagate = False

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

    logger.warning("Initialized logger.")
