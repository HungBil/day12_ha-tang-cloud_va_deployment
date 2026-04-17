"""Sliding-window rate limiter (in-memory)."""
import time
from collections import defaultdict, deque

from fastapi import HTTPException

from app.config import settings

# Per-key sliding window: key → deque of timestamps
_rate_windows: dict[str, deque] = defaultdict(deque)


def check_rate_limit(key: str) -> None:
    """
    Sliding-window rate limiter.
    Raises 429 if the key exceeds rate_limit_per_minute requests within 60s.
    """
    now = time.time()
    window = _rate_windows[key]

    # Remove timestamps older than 60 seconds
    while window and window[0] < now - 60:
        window.popleft()

    if len(window) >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
            headers={"Retry-After": "60"},
        )

    window.append(now)
