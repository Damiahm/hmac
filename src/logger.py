"""Simple logger setup without leaking secrets."""

from __future__ import annotations

import logging

from src.config import get_config


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Return configured logger.

    Uses log level from config; avoids propagating secrets.
    """
    config = get_config()
    logging.basicConfig(
        level=config.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    return logging.getLogger(name)
