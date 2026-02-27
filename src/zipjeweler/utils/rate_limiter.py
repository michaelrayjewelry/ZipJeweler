"""Per-platform rate limiting using tenacity."""

import time
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """Simple per-platform rate limiter tracking timestamps of actions."""

    def __init__(self):
        self._timestamps: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check_and_record(self, platform: str, max_per_hour: int) -> bool:
        """Check if we can perform an action, and record it if so.

        Returns True if the action is allowed, False if rate-limited.
        """
        now = time.time()
        one_hour_ago = now - 3600

        with self._lock:
            # Clean old timestamps
            self._timestamps[platform] = [
                ts for ts in self._timestamps[platform] if ts > one_hour_ago
            ]

            if len(self._timestamps[platform]) >= max_per_hour:
                return False

            self._timestamps[platform].append(now)
            return True

    def wait_if_needed(self, platform: str, min_seconds_between: int) -> None:
        """Wait if the last action was too recent."""
        with self._lock:
            timestamps = self._timestamps.get(platform, [])
            if timestamps:
                elapsed = time.time() - timestamps[-1]
                if elapsed < min_seconds_between:
                    time.sleep(min_seconds_between - elapsed)


# Global rate limiter instance
rate_limiter = RateLimiter()
