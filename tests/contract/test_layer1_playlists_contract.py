import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import build_playlists_insert_wrapper


class Layer1PlaylistsContractTests(unittest.TestCase):
    def _insert_contract_root(self) -> str:
        return os.path.abspath("specs/137-playlists-insert/contracts")

    def test_contract_artifacts_define_wrapper_and_auth_write_guidance_for_insert(self):
        root = self._insert_contract_root()
        with open(
            os.path.join(root, "layer1-playlists-insert-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-playlists-insert-auth-write-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("quota cost of `50`", wrapper_contract)
        self.assertIn("authorized access", wrapper_contract)
        self.assertIn("body` metadata payload", wrapper_contract)
        self.assertIn("OAuth-backed access", auth_write_contract)
        self.assertIn("playlist title", auth_write_contract)
        self.assertIn("optional playlist attributes", auth_write_contract)
        self.assertIn("invalid_request", auth_write_contract)

    def test_playlists_insert_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_playlists_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlists")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "playlists.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("part=snippet", review_surface["notes"])
        self.assertIn("body.snippet.description", review_surface["notes"])

    def test_contract_documents_write_boundaries_and_failure_rules(self):
        with open(
            os.path.join(
                self._insert_contract_root(),
                "layer1-playlists-insert-auth-write-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("unsupported writable parts", auth_write_contract)
        self.assertIn("required playlist title", auth_write_contract)
        self.assertIn("optional playlist attributes", auth_write_contract)
        self.assertIn("upstream create failures", auth_write_contract)
        self.assertIn("description", auth_write_contract)
        self.assertIn("localization", auth_write_contract)
