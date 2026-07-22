"""In-process sliding-window rate limiter (Phase 6)."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    retry_after_sec: float
    remaining: int


class SlidingWindowRateLimiter:
    """Thread-safe per-key limiter: max `limit` events per `window_sec`."""

    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, limit: int, window_sec: float) -> RateLimitResult:
        if limit <= 0:
            return RateLimitResult(True, 0.0, 0)

        now = time.monotonic()
        cutoff = now - window_sec
        with self._lock:
            q = self._events[key]
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= limit:
                retry = max(0.0, window_sec - (now - q[0]))
                return RateLimitResult(False, retry, 0)
            q.append(now)
            return RateLimitResult(True, 0.0, max(0, limit - len(q)))

    def reset(self, key: str | None = None) -> None:
        with self._lock:
            if key is None:
                self._events.clear()
            elif key in self._events:
                del self._events[key]


# Process-wide limiter (shared across Streamlit sessions in one container)
_limiter = SlidingWindowRateLimiter()


def get_limiter() -> SlidingWindowRateLimiter:
    return _limiter


def allow_chat(user_key: str, limit: int | None = None, window_sec: float | None = None) -> RateLimitResult:
    from sakoon.core.config import get_settings

    s = get_settings()
    return _limiter.check(
        f"chat:{user_key}",
        limit if limit is not None else s.rate_limit_chat_per_min,
        window_sec if window_sec is not None else 60.0,
    )


def allow_auth(identity_key: str, limit: int | None = None, window_sec: float | None = None) -> RateLimitResult:
    from sakoon.core.config import get_settings

    s = get_settings()
    return _limiter.check(
        f"auth:{identity_key}",
        limit if limit is not None else s.rate_limit_auth_per_min,
        window_sec if window_sec is not None else 60.0,
    )
