"""Implement bounded public-tool admission policy state."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from threading import RLock
from time import time

from mcp_server.config import RateLimitSettings


@dataclass(frozen=True)
class AdmissionDecision:
    """Describe one safe admission outcome.

    :param accepted: Whether dispatcher execution may begin.
    :param retry_after_seconds: Positive retry delay when rejected.
    :param caller_class: Bounded caller category used for metrics.
    """

    accepted: bool
    retry_after_seconds: int | None
    caller_class: str


class RateLimiter:
    """Apply an in-process rolling-window admission policy.

    The in-memory behavior is used for local development and deterministic
    tests. Hosted deployments may replace this component with a shared store
    without changing the caller-facing decision contract.
    """

    def __init__(self, settings: RateLimitSettings, clock: Callable[[], float] = time) -> None:
        """Initialize empty rolling windows for the supplied policy.

        :param settings: Validated admission policy settings.
        :param clock: Injectable wall-clock source for deterministic tests.
        """
        self._settings = settings
        self._clock = clock
        self._windows: dict[str, deque[float]] = {}
        self._lock = RLock()

    def admit(self, key: str, *, identified: bool) -> AdmissionDecision:
        """Admit or reject one valid public tool invocation.

        :param key: Internal non-secret caller bucket key.
        :param identified: Whether the key represents a validated caller.
        :return: Safe decision with retry delay only when rejected.
        """
        now = self._clock()
        caller_class = "identified" if identified else "anonymous"
        limit = self._settings.identified_requests_per_minute if identified else self._settings.anonymous_requests_per_minute
        bucket_key = f"{caller_class}:{key}"
        with self._lock:
            window = self._windows.setdefault(bucket_key, deque())
            cutoff = now - self._settings.window_seconds
            while window and window[0] <= cutoff:
                window.popleft()
            if len(window) >= limit:
                retry_after = max(1, int(window[0] + self._settings.window_seconds - now + 0.999))
                return AdmissionDecision(False, retry_after, caller_class)
            window.append(now)
        return AdmissionDecision(True, None, caller_class)
