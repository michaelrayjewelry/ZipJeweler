"""Retry utilities with exponential backoff."""

from tenacity import retry, stop_after_attempt, wait_exponential


def with_retry(max_attempts: int = 3, min_wait: int = 1, max_wait: int = 30):
    """Decorator for retrying functions with exponential backoff."""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        reraise=True,
    )
