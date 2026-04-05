"""Retry helpers for internal Layer 1 request execution."""

from __future__ import annotations

from dataclasses import dataclass

from mcp_server.integrations.errors import NormalizedUpstreamError


@dataclass(frozen=True)
class RetryPolicy:
    """Describe retry behavior for the shared executor.

    :param max_attempts: Maximum attempts allowed for one execution.
    :param retryable_statuses: Explicit statuses considered retryable.
    """

    max_attempts: int = 1
    retryable_statuses: tuple[int, ...] = (429, 500, 502, 503, 504)

    def __post_init__(self) -> None:
        """Validate retry policy settings."""
        if self.max_attempts <= 0:
            raise ValueError("max_attempts must be greater than zero")

    def should_retry(self, error: NormalizedUpstreamError, attempt_number: int) -> bool:
        """Return whether the executor should retry after one failure.

        :param error: Normalized upstream error from the failed attempt.
        :param attempt_number: One-based attempt number that just failed.
        :return: Whether a retry should be attempted.
        """
        if attempt_number >= self.max_attempts:
            return False
        if error.upstream_status in self.retryable_statuses:
            return True
        return error.retryable
