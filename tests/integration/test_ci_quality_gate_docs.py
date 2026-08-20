"""Integration coverage for the OPS-401 operator runbook."""

import unittest
from pathlib import Path


class CiQualityGateDocumentationTests(unittest.TestCase):
    """Require one reproducible local and hosted release procedure."""

    def test_readme_documents_clean_checkout_quality_and_release_evidence(self) -> None:
        """Require documented installation, quality, safety, and evidence boundaries.

        :return: ``None`` after validating the operator runbook content.
        :raises AssertionError: If a required procedure or safe evidence term is absent.
        """
        content = Path("README.md").read_text()
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


if __name__ == "__main__":
    unittest.main()
