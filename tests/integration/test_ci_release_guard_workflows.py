"""Workflow-shape integration coverage for guarded OPS-401 releases."""

from __future__ import annotations

import unittest
from pathlib import Path


class CiReleaseGuardWorkflowTests(unittest.TestCase):
    """Verify release workflow paths preserve one immutable release identity."""

    def test_both_workflows_pass_provenance_to_deploy_and_upload_it(self) -> None:
        """Require the digest-qualified release record to flow through deployment.

        :return: ``None`` after checking release evidence handoff markers.
        :raises AssertionError: If a workflow omits deploy provenance evidence.
        """
        for workflow_path in (Path("cloudbuild.yaml"), Path(".github/workflows/hosted-deploy.yml")):
            content = workflow_path.read_text()
            self.assertIn("IMAGE_REFERENCE", content, workflow_path)
            self.assertIn("RELEASE_PROVENANCE_FILE", content, workflow_path)
            self.assertIn("artifacts/release-provenance.json", content, workflow_path)

    def test_failing_gate_has_no_image_stage_before_it(self) -> None:
        """Require each workflow to place image publication after all blockers.

        :return: ``None`` after validating gate-before-image ordering.
        :raises AssertionError: If a build stage can run before quality validation.
        """
        for workflow_path in (Path("cloudbuild.yaml"), Path(".github/workflows/hosted-deploy.yml")):
            content = workflow_path.read_text()
            gate_end = content.index("quality-gate")
            image_start = content.index("build-image")
            self.assertLess(gate_end, image_start, workflow_path)
