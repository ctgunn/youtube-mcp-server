"""Unit coverage for safe OPS-401 release provenance."""

from __future__ import annotations

import unittest

from mcp_server.deploy import (
    ReleaseProvenance,
    serialize_release_provenance,
    validate_release_provenance,
)


class CiReleaseProvenanceTests(unittest.TestCase):
    """Exercise release eligibility and safe evidence serialization."""

    def _provenance(self, **overrides: object) -> ReleaseProvenance:
        """Build a valid provenance record with optional field overrides.

        :param overrides: Replacement values for the valid baseline fields.
        :return: A release-provenance record for an isolated assertion.
        """
        values: dict[str, object] = {
            "source_revision": "a" * 40,
            "image_reference": "us-docker.pkg.dev/example/apps/server@sha256:" + "b" * 64,
            "target_environment": "staging",
            "quality_statuses": {"lint": "pass", "typecheck": "pass", "tests": "pass"},
            "preflight_status": "pass",
        }
        values.update(overrides)
        return ReleaseProvenance(**values)  # type: ignore[arg-type]

    def test_valid_provenance_is_eligible_and_contains_no_secret_values(self) -> None:
        """Accept passing SHA/digest evidence and serialize only safe fields.

        :return: ``None`` after asserting the public evidence shape.
        """
        provenance = self._provenance()
        self.assertEqual(validate_release_provenance(provenance), ())
        payload = serialize_release_provenance(provenance)
        self.assertEqual(payload["qualityStatuses"], {"lint": "pass", "typecheck": "pass", "tests": "pass"})
        self.assertNotIn("secret", str(payload).lower())

    def test_bad_quality_sha_digest_or_preflight_blocks_release(self) -> None:
        """Reject each condition that could detach a release from validated source.

        :return: ``None`` after asserting all invalid conditions are reported.
        """
        failures = validate_release_provenance(
            self._provenance(
                source_revision="not-a-sha",
                image_reference="us-docker.pkg.dev/example/apps/server:mutable",
                quality_statuses={"lint": "pass", "typecheck": "cancelled", "tests": "missing"},
                preflight_status="fail",
            )
        )
        self.assertTrue(any("source_revision" in failure for failure in failures))
        self.assertTrue(any("image_reference" in failure for failure in failures))
        self.assertTrue(any("typecheck" in failure for failure in failures))
        self.assertTrue(any("tests" in failure for failure in failures))
        self.assertTrue(any("preflight" in failure for failure in failures))

