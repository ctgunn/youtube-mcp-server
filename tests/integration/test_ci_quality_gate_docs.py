"""Integration coverage for the OPS-401 operator runbook."""

import unittest
from pathlib import Path


class CiQualityGateDocumentationTests(unittest.TestCase):
    """Require one reproducible local and hosted release procedure."""

    def test_guides_document_clean_checkout_quality_and_release_evidence(self) -> None:
        """Require documented installation, quality, safety, and evidence boundaries.

        :return: ``None`` after validating the operator runbook content.
        :raises AssertionError: If a required procedure or safe evidence term is absent.
        """
        content = "\n".join(
            (
                Path("docs/engineering.md").read_text(),
                Path("docs/hosted-deployment.md").read_text(),
            )
        )
        for required_text in (
            "python -m pip install -e '.[dev]'",
            "make lint",
            "make typecheck",
            "make test",
            "make quality",
            "clean checkout",
            "local",
            "hosted",
            "safe preflight",
            "full commit SHA",
            "immutable image digest",
            "deployment record",
            "verification",
            "must never",
        ):
            self.assertIn(required_text, content)

    def test_readme_documents_deterministic_catalog_verification_boundary(self) -> None:
        """Require focused tool-catalog and separate live-verification guidance.

        :return: ``None`` after validating README command-boundary content.
        :raises AssertionError: If the README omits required operator guidance.
        """
        content = Path("README.md").read_text()
        for required_text in (
            "make test-tools",
            "make test-runtime",
            "make test-live-smoke",
            "make test",
            "live smoke",
            "credential",
            "quota",
            "upstream",
        ):
            self.assertIn(required_text, content)

    def test_live_smoke_is_not_part_of_ordinary_quality_or_hosted_gates(self) -> None:
        """Require manual live-smoke execution to remain outside normal automation.

        :return: ``None`` after checking Make and workflow execution boundaries.
        """
        makefile = Path("Makefile").read_text()
        quality_workflow = Path(".github/workflows/quality.yml").read_text()
        hosted_workflow = Path(".github/workflows/hosted-deploy.yml").read_text()
        self.assertIn("test-runtime:", makefile)
        self.assertIn("test-live-smoke:", makefile)
        self.assertIn(".env.local", makefile)
        self.assertIn(".env", makefile)
        self.assertNotIn("test-live-smoke: test", makefile)
        self.assertNotIn("test-live-smoke: quality", makefile)
        self.assertNotIn("RUN_YOUTUBE_LIVE_SMOKE", quality_workflow)
        self.assertNotIn("RUN_YOUTUBE_LIVE_SMOKE", hosted_workflow)


if __name__ == "__main__":
    unittest.main()
