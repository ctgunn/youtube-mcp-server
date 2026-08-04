"""Retry helpers for internal Layer 1 request execution."""

from __future__ import annotations

from dataclasses import dataclass

from mcp_server.integrations.errors import NormalizedUpstreamError


@dataclass(frozen=True)
class RetryPolicy:
    """Describe retry behavior for the shared executor.

    :param max_attempts: Maximum attempts allowed for one execution.
    :param retryable_statuses: Explicit statuses considered retryable.
    :param initial_backoff_seconds: Delay before the first retry.
    :param max_backoff_seconds: Maximum delay between attempts.
    """

    max_attempts: int = 1
    retryable_statuses: tuple[int, ...] = (429, 500, 502, 503, 504)
    initial_backoff_seconds: float = 0.25
    max_backoff_seconds: float = 2.0

    def __post_init__(self) -> None:
        """Validate retry policy settings."""
        if self.max_attempts <= 0:
            raise ValueError("max_attempts must be greater than zero")
        if self.initial_backoff_seconds < 0 or self.max_backoff_seconds < 0:
            raise ValueError("retry backoff values must not be negative")
        if self.max_backoff_seconds < self.initial_backoff_seconds:
            raise ValueError("max_backoff_seconds must be at least initial_backoff_seconds")

    def should_retry(
        self,
        error: NormalizedUpstreamError,
        attempt_number: int,
        *,
        http_method: str,
    ) -> bool:
        """Return whether the executor should retry after one failure.

        :param error: Normalized upstream error from the failed attempt.
        :param attempt_number: One-based attempt number that just failed.
        :param http_method: Upstream HTTP method for the failed execution.
        :return: Whether a retry should be attempted.
        """
        if attempt_number >= self.max_attempts:
            return False
        if http_method.upper() not in {"GET", "HEAD", "PUT", "DELETE"}:
            return False
        if error.upstream_status in self.retryable_statuses:
            return True
        return error.retryable

    def backoff_seconds(self, attempt_number: int) -> float:
        """Return the bounded exponential delay after a failed attempt.

        :param attempt_number: One-based attempt number that just failed.
        :return: Delay in seconds before a permitted retry.
        """
        if attempt_number <= 0:
            raise ValueError("attempt_number must be greater than zero")
        return min(
            self.max_backoff_seconds,
            self.initial_backoff_seconds * (2 ** (attempt_number - 1)),
        )
