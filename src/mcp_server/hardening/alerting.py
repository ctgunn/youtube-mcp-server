"""Evaluate bounded application-level production alert state."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from time import time

from mcp_server.config import AlertingSettings


@dataclass(frozen=True)
class OperationalSample:
    """Represent one bounded eligible public tool observation.

    :param observed_at: Evaluation timestamp.
    :param tool_class: Finite latency class.
    :param outcome: Finite public outcome category.
    :param latency_ms: Non-negative observed request latency.
    """

    observed_at: float
    tool_class: str
    outcome: str
    latency_ms: float


class AlertEvaluator:
    """Track small rolling windows and emit deduplicated incident state."""

    def __init__(self, settings: AlertingSettings, clock: Callable[[], float] = time) -> None:
        """Initialize the evaluator with no retained samples or incidents.

        :param settings: Validated alerting configuration.
        :param clock: Injectable clock used by deterministic tests.
        """
        self._settings = settings
        self._clock = clock
        self._samples: deque[OperationalSample] = deque()
        self._active: set[str] = set()

    def observe(self, tool_class: str, outcome: str, latency_ms: float) -> list[dict[str, str | float | int]]:
        """Record an eligible tool result and return newly opened incidents.

        :param tool_class: Finite simple/cached or transcript-heavy class.
        :param outcome: Finite safe request outcome class.
        :param latency_ms: Measured request latency in milliseconds.
        :return: Newly active incident payloads; continuing incidents are omitted.
        """
        if not self._settings.enabled:
            return []
        now = self._clock()
        self._samples.append(OperationalSample(now, tool_class, outcome, max(float(latency_ms), 0.0)))
        while self._samples and self._samples[0].observed_at <= now - 600:
            self._samples.popleft()
        if len(self._samples) < self._settings.minimum_sample_count:
            return []
        events: list[dict[str, str | float | int]] = []
        failures = sum(sample.outcome in {"service_failure", "upstream_failure", "capacity_rejection"} for sample in self._samples)
        if failures * 100 >= len(self._samples) * self._settings.error_rate_percent:
            events.extend(self._activate("sustained_error_rate", failures * 100 / len(self._samples)))
        for class_name, threshold, condition in (
            ("simple_cached", 3000.0, "simple_latency"),
            ("transcript_heavy", 8000.0, "transcript_latency"),
        ):
            values = sorted(sample.latency_ms for sample in self._samples if sample.tool_class == class_name)
            if len(values) >= self._settings.minimum_sample_count:
                p95 = values[round((len(values) - 1) * 0.95)]
                if p95 > threshold:
                    events.extend(self._activate(condition, p95))
        return events

    def _activate(self, condition: str, observed_value: float) -> list[dict[str, str | float | int]]:
        """Open a condition once and suppress duplicate active notifications.

        :param condition: Finite incident condition name.
        :param observed_value: Safe threshold measurement.
        :return: One active event for a newly opened condition.
        """
        if condition in self._active:
            return []
        self._active.add(condition)
        return [{"condition": condition, "state": "active", "observedValue": round(observed_value, 3)}]
