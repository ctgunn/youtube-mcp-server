"""Normalized upstream error shapes for Layer 1 execution."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizedUpstreamError(RuntimeError):
    """Represent one normalized upstream failure.

    :param message: Failure message safe for internal consumers.
    :param category: Stable internal failure category.
    :param retryable: Whether the failure can be retried safely.
    :param upstream_status: Optional preserved upstream status.
    :param details: Optional structured details safe for logs and tests.
    """

    message: str
    category: str
    retryable: bool
    upstream_status: int | None = None
    details: dict[str, object] | None = None

    def __post_init__(self) -> None:
        """Initialize the runtime error state for exception consumers."""
        RuntimeError.__init__(self, self.message)


def normalize_upstream_error(
    error: Exception,
    *,
    category: str | None = None,
    status_code: int | None = None,
    retryable: bool | None = None,
    details: dict[str, object] | None = None,
) -> NormalizedUpstreamError:
    """Normalize an arbitrary upstream exception into the shared error model.

    :param error: Upstream exception to normalize.
    :param category: Explicit failure category override.
    :param status_code: Optional upstream status for the failure.
    :param retryable: Optional retryability override.
    :param details: Optional structured details safe for logs and tests.
    :return: Normalized upstream error instance.
    """
        # Determine category from explicit values first, then status/message heuristics.
    lowered = str(error).lower()
    normalized_category = category
    if normalized_category is None:
        if status_code in {401, 403}:
            normalized_category = "auth"
        elif status_code == 404:
            normalized_category = "not_found"
        elif status_code == 429:
            normalized_category = "rate_limit"
        elif status_code in {500, 502, 503, 504} or "timeout" in lowered or "tempor" in lowered:
            normalized_category = "transient"
        else:
            normalized_category = "upstream_service"

    normalized_retryable = retryable
    if normalized_retryable is None:
        normalized_retryable = normalized_category in {"rate_limit", "transient"}

    return NormalizedUpstreamError(
        message=str(error),
        category=normalized_category,
        retryable=normalized_retryable,
        upstream_status=status_code,
        details=details or {},
    )
