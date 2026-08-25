"""Red/green tests for public MCP admission policy."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.config import RateLimitSettings
from mcp_server.hardening.rate_limit import RateLimiter


class RateLimitPolicyTests(unittest.TestCase):
    """Verify isolated rolling admission behavior."""

    def test_identified_and_anonymous_limits_are_independent(self) -> None:
        """Reject only the caller class that exhausts its configured allowance."""
        limiter = RateLimiter(
            RateLimitSettings(
                identified_requests_per_minute=2,
                anonymous_requests_per_minute=1,
                window_seconds=60,
            ),
            clock=lambda: 100.0,
        )

        self.assertTrue(limiter.admit("identified:one", identified=True).accepted)
        self.assertTrue(limiter.admit("identified:one", identified=True).accepted)
        rejected = limiter.admit("identified:one", identified=True)
        self.assertFalse(rejected.accepted)
        self.assertGreater(rejected.retry_after_seconds, 0)
        self.assertTrue(limiter.admit("identified:two", identified=True).accepted)
        self.assertTrue(limiter.admit("anonymous", identified=False).accepted)
        self.assertFalse(limiter.admit("anonymous", identified=False).accepted)


if __name__ == "__main__":
    unittest.main()
