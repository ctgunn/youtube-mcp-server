"""Contract coverage for OPS-401 guarded release automation."""

from __future__ import annotations

import unittest
from pathlib import Path


class CiReleaseGuardContractTests(unittest.TestCase):
    """Require both supported release paths to use the OPS-401 gate."""

    def test_release_workflows_use_canonical_quality_and_safe_provenance(self) -> None:
        """Require quality, revision, digest, and provenance markers in both paths.

        :return: ``None`` after inspecting the checked-in workflow contracts.
        :raises AssertionError: If a deployment path omits a required release guard.
        """
        for workflow_path in (Path("cloudbuild.yaml"), Path(".github/workflows/hosted-deploy.yml")):
            content = workflow_path.read_text()
            for required_text in (
                "make quality",
                "resolve-source-revision",
                "validate-bootstrap-prerequisites",
                "sha256:",
                "release-provenance.json",
                "SOURCE_REVISION",
                "PREFLIGHT_STATUS",
            ):
                self.assertIn(required_text, content, workflow_path)

    def test_release_workflows_gate_later_stages_in_order(self) -> None:
        """Require source resolution, preflight, quality, image, deploy ordering.

        :return: ``None`` after verifying failure-safe stage order.
        :raises AssertionError: If an image or deployment stage can precede a gate.
        """
        ordered_markers = (
            "resolve-source-revision",
            "validate-bootstrap-prerequisites",
            "quality-gate",
            "build-image",
            "deploy-hosted-revision",
        )
        for workflow_path in (Path("cloudbuild.yaml"), Path(".github/workflows/hosted-deploy.yml")):
            content = workflow_path.read_text()
            positions = [content.index(marker) for marker in ordered_markers]
            self.assertEqual(positions, sorted(positions), workflow_path)

    def test_preflight_does_not_receive_runtime_secret_values(self) -> None:
        """Keep runtime credential values out of the preflight environment.

        :return: ``None`` after checking the safe preflight boundary.
        :raises AssertionError: If a preflight stage injects a runtime secret value.
        """
        for workflow_path in (Path("cloudbuild.yaml"), Path(".github/workflows/hosted-deploy.yml")):
            content = workflow_path.read_text()
            preflight = content.split("validate-bootstrap-prerequisites", maxsplit=1)[1].split(
                "quality-gate", maxsplit=1
            )[0]
            self.assertNotIn("YOUTUBE_API_KEY", preflight, workflow_path)
            self.assertNotIn("MCP_AUTH_TOKEN", preflight, workflow_path)
