"""Workflow-shape integration coverage for guarded OPS-401 releases."""

from __future__ import annotations

import unittest
from pathlib import Path


class CiReleaseGuardWorkflowTests(unittest.TestCase):
    """Verify release workflow paths preserve one immutable release identity."""

    def test_hosted_workflow_passes_provenance_to_deploy_and_uploads_it(self) -> None:
        """Require the digest-qualified release record to flow through deployment.

        :return: ``None`` after checking release evidence handoff markers.
        :raises AssertionError: If a workflow omits deploy provenance evidence.
        """
        workflow_path = Path(".github/workflows/hosted-deploy.yml")
        content = workflow_path.read_text()
        self.assertIn("IMAGE_REFERENCE", content, workflow_path)
        self.assertIn("RELEASE_PROVENANCE_FILE", content, workflow_path)
        self.assertIn("artifacts/release-provenance.json", content, workflow_path)

    def test_failing_gate_has_no_image_stage_before_it(self) -> None:
        """Require the hosted workflow to place image publication after blockers.

        :return: ``None`` after validating gate-before-image ordering.
        :raises AssertionError: If a build stage can run before quality validation.
        """
        workflow_path = Path(".github/workflows/hosted-deploy.yml")
        content = workflow_path.read_text()
        gate_end = content.index("quality-gate")
        image_start = content.index("build-image")
        self.assertLess(gate_end, image_start, workflow_path)

    def test_hosted_workflow_targets_the_configured_registry_region(self) -> None:
        """Require the hosted release path to derive its registry hostname from region.

        :return: ``None`` after checking registry-host configuration.
        :raises AssertionError: If a workflow targets a different registry location.
        """
        workflow_path = Path(".github/workflows/hosted-deploy.yml")
        content = workflow_path.read_text()
        self.assertIn("${GCP_REGION}-docker.pkg.dev", content, workflow_path)
        self.assertNotIn("us-docker.pkg.dev", content, workflow_path)

    def test_hosted_deploy_installs_terraform_before_invoking_it(self) -> None:
        """Require the fallback runner to provision Terraform before its use.

        :return: ``None`` after validating Terraform setup ordering.
        :raises AssertionError: If the workflow invokes Terraform without setup.
        """
        workflow_path = Path(".github/workflows/hosted-deploy.yml")
        content = workflow_path.read_text()
        setup_start = content.index("hashicorp/setup-terraform@v3")
        init_start = content.index("terraform -chdir=infrastructure/gcp init")
        self.assertLess(setup_start, init_start, workflow_path)

    def test_hosted_deploy_uses_remote_state_and_a_dedicated_deployer(self) -> None:
        """Require GitHub deployment to use remote state and a non-runtime identity.

        :return: ``None`` after checking state and identity handoff markers.
        :raises AssertionError: If state or identity handling can cause unsafe drift.
        """
        workflow_path = Path(".github/workflows/hosted-deploy.yml")
        content = workflow_path.read_text()
        versions = Path("infrastructure/gcp/versions.tf").read_text()

        self.assertIn("GCP_TERRAFORM_STATE_BUCKET", content)
        self.assertIn('backend-config="bucket=${GCP_TERRAFORM_STATE_BUCKET}"', content)
        self.assertIn('backend "gcs" {}', versions)
        self.assertIn("GCP_DEPLOYER_SERVICE_ACCOUNT", content)
        self.assertIn("service_account: ${{ secrets.GCP_DEPLOYER_SERVICE_ACCOUNT }}", content)
        self.assertNotIn("SERVICE_ACCOUNT_EMAIL: ${{ secrets.GCP_SERVICE_ACCOUNT }}", content)
