"""Lightweight in-process metrics + structured event logging (Phase 6)."""

from __future__ import annotations

import threading
from collections import Counter
from typing import Any

from sakoon.core.logging import get_logger

log = get_logger(__name__)

_lock = threading.Lock()
_counters: Counter[str] = Counter()


def emit(event: str, **fields: Any) -> None:
    """Increment a counter and write a structured log line (no secrets)."""
    with _lock:
        _counters[event] += 1
    parts = [f"event={event}"]
    for key, value in fields.items():
        if value is None:
            continue
        # Never log password-like fields
        if "password" in key.lower() or "secret" in key.lower() or "token" in key.lower():
            continue
        parts.append(f"{key}={value}")
    log.info(" ".join(parts))


def snapshot() -> dict[str, int]:
    with _lock:
        return dict(_counters)


def reset_metrics() -> None:
    with _lock:
        _counters.clear()
