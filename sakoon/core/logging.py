"""Structured logging setup for Sakoon services."""

from __future__ import annotations

import logging
import sys
from typing import Optional

_CONFIGURED = False


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger once with a concise structured format."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not root.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        root.addHandler(handler)

    # Keep third-party noise down
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    _CONFIGURED = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a named logger; ensures setup_logging has run."""
    if not _CONFIGURED:
        try:
            from sakoon.core.config import get_settings
            setup_logging(get_settings().log_level)
        except Exception:
            setup_logging("INFO")
    return logging.getLogger(name or "sakoon")
