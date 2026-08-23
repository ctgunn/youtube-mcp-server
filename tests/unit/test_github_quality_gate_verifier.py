"""Unit coverage for read-only GitHub quality-gate verification."""

import importlib.util
import unittest
from pathlib import Path


def _load_verifier_module():
    """Load the standalone governance verifier for direct unit testing.

    :return: Imported verifier module.
    :raises AssertionError: If the verifier cannot be loaded.
    """
    path = Path("scripts/verify_github_quality_gate.py")
    spec = importlib.util.spec_from_file_location("verify_github_quality_gate", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GithubQualityGateVerifierTests(unittest.TestCase):
    """Verify rule and check-result eligibility evaluation."""

    def test_accepts_active_current_github_actions_checks(self) -> None:
        """Accept a complete passing check set for the protected revision.

        :return: ``None`` after asserting an eligible result.
        :raises AssertionError: If valid governance data is rejected.
        """
        verifier = _load_verifier_module()
        result = verifier.evaluate_quality_gate(
            {"enforcement": "active", "requires_pull_requests": True, "requires_up_to_date": True, "bypass_actors": [], "required_checks": ["lint", "typecheck", "tests"]},
            {"head_sha": "abc", "checks": [{"name": name, "head_sha": "abc", "status": "completed", "conclusion": "success", "app": "github-actions"} for name in ("lint", "typecheck", "tests")]},
        )
        self.assertTrue(result["eligible"])

    def test_rejects_missing_or_stale_checks_without_sensitive_details(self) -> None:
        """Reject missing/stale checks and retain only safe remediation details.

        :return: ``None`` after asserting a blocked result.
        :raises AssertionError: If invalid governance data is accepted or leaks values.
        """
        verifier = _load_verifier_module()
        result = verifier.evaluate_quality_gate(
            {"enforcement": "active", "requires_pull_requests": True, "requires_up_to_date": True, "bypass_actors": [], "required_checks": ["lint", "typecheck", "tests"]},
            {"head_sha": "new", "checks": [{"name": "lint", "head_sha": "old", "status": "completed", "conclusion": "success", "app": "github-actions"}]},
        )
        self.assertFalse(result["eligible"])
        self.assertIn("lint", result["blockingChecks"])
        self.assertIn("typecheck", result["blockingChecks"])
        self.assertNotIn("token", str(result).lower())


if __name__ == "__main__":
    unittest.main()
