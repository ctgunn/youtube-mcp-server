"""Red/green tests for bounded sustained-degradation incidents."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.config import AlertingSettings
from mcp_server.hardening.alerting import AlertEvaluator


class AlertLifecycleTests(unittest.TestCase):
    """Verify sample thresholds and incident deduplication."""

    def test_error_threshold_opens_one_incident_after_minimum_samples(self) -> None:
        """Avoid low-volume alerts and deduplicate continuing incidents."""
        evaluator = AlertEvaluator(AlertingSettings(enabled=True), clock=lambda: 100.0)
        for _index in range(19):
            self.assertEqual(evaluator.observe("simple_cached", "success", 10), [])
        self.assertEqual(evaluator.observe("simple_cached", "upstream_failure", 10)[0]["state"], "active")
        self.assertEqual(evaluator.observe("simple_cached", "upstream_failure", 10), [])


if __name__ == "__main__":
    unittest.main()
