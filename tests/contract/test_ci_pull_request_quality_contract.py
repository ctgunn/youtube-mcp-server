"""Contract coverage for the pull-request quality workflow."""

import unittest
from pathlib import Path


class PullRequestQualityWorkflowContractTests(unittest.TestCase):
    """Require the checked-in workflow shape that supports protected PRs."""

    def test_workflow_exposes_three_unprivileged_quality_checks(self) -> None:
        """Require the exact PR trigger, job names, and canonical commands.

        :return: ``None`` after validating the workflow contract.
        :raises AssertionError: If a required PR quality-gate property is absent.
        """
        content = Path(".github/workflows/quality.yml").read_text()

        self.assertIn("pull_request:", content)
        self.assertIn("branches: [main]", content)
        self.assertIn("contents: read", content)
        for job_name, command in (("lint:", "make lint"), ("typecheck:", "make typecheck"), ("tests:", "make test")):
            self.assertIn(job_name, content)
            self.assertIn(f"name: {job_name[:-1]}", content)
            self.assertIn(command, content)
        self.assertNotIn("pull_request_target", content)
        self.assertNotIn("secrets.", content)
        self.assertNotIn("paths:", content)


if __name__ == "__main__":
    unittest.main()
