"""Security contracts for OPS-401 quality and release automation."""

from __future__ import annotations

import unittest
from pathlib import Path


class CiQualityGateSecurityContractTests(unittest.TestCase):
    """Keep pull-request and release gating free of secret-bearing evidence."""

    def test_pull_request_quality_workflow_has_no_deployment_credentials(self) -> None:
        """Keep untrusted pull-request validation separate from deployment identity.

        :return: ``None`` after validating the PR workflow's narrow privilege scope.
        :raises AssertionError: If the PR workflow gains deployment credentials.
        """
        workflow = Path(".github/workflows/quality.yml").read_text()
        for forbidden_text in (
            "secrets.",
            "id-token: write",
            "google-github-actions/auth",
            "gcloud",
            "docker push",
        ):
            self.assertNotIn(forbidden_text, workflow)

    def test_release_preflight_and_provenance_avoid_runtime_secret_values(self) -> None:
        """Keep secret values out of preflight and public release evidence.

        :return: ``None`` after checking safe boundaries in both release workflows.
        :raises AssertionError: If a preflight accepts a runtime secret value.
        """
        for workflow_path in (Path("cloudbuild.yaml"), Path(".github/workflows/hosted-deploy.yml")):
            content = workflow_path.read_text()
            preflight = content.split("validate-bootstrap-prerequisites", maxsplit=1)[1].split(
                "quality-gate", maxsplit=1
            )[0]
            self.assertNotIn("YOUTUBE_API_KEY", preflight, workflow_path)
            self.assertNotIn("MCP_AUTH_TOKEN", preflight, workflow_path)
            provenance = content.split("record-release-provenance", maxsplit=1)[-1].split(
                "deploy-hosted-revision", maxsplit=1
            )[0]
            self.assertNotIn("MCP_AUTH_TOKEN", provenance, workflow_path)
            self.assertNotIn("YOUTUBE_API_KEY", provenance, workflow_path)
