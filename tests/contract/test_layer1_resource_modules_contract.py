import os
import sys
import unittest
import importlib.util

sys.path.insert(0, os.path.abspath("src"))


FEATURE_ROOT = os.path.abspath("specs/156-layer1-resource-modules")
REQUIRED_FAMILIES = (
    "activities",
    "captions",
    "channel_banners",
    "channels",
    "channel_sections",
    "comments",
    "comment_threads",
    "guide_categories",
    "localization",
    "members",
    "memberships_levels",
    "playlist_images",
    "playlist_items",
    "playlists",
    "search",
    "subscriptions",
    "thumbnails",
    "video_abuse_report_reasons",
    "video_categories",
    "videos",
    "watermarks",
)


class Layer1ResourceModulesContractTests(unittest.TestCase):
    def _read_contract(self, name: str) -> str:
        path = os.path.join(FEATURE_ROOT, "contracts", name)
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()

    def test_resource_family_contract_documents_compatibility_and_scope(self):
        contract = self._read_contract("layer1-resource-family-compatibility-contract.md")

        self.assertIn("mcp_server.integrations", contract)
        self.assertIn("mcp_server.integrations.wrappers", contract)
        self.assertIn("mcp_server.integrations.youtube", contract)
        self.assertIn("YT-103 through YT-155", contract)
        self.assertIn("does not introduce a public MCP tool", contract)

    def test_resource_family_contract_lists_required_families(self):
        contract = self._read_contract("layer1-resource-family-compatibility-contract.md")

        for family in REQUIRED_FAMILIES:
            self.assertIn(f"`{family}`", contract)

    def test_response_dispatch_contract_documents_explicit_dispatch(self):
        contract = self._read_contract("layer1-response-normalizer-dispatch-contract.md")

        self.assertIn("operation-key to response-normalizer registration", contract.lower())
        self.assertIn("execution context only", contract)
        self.assertIn("payload only", contract)
        self.assertIn("both execution context and payload", contract)
        self.assertIn("generic JSON object parsing", contract)

    def test_required_resource_family_modules_exist(self):
        for family in REQUIRED_FAMILIES:
            spec = importlib.util.find_spec(f"mcp_server.integrations.resources.{family}")
            self.assertIsNotNone(spec, f"missing resource-family module for {family}")

    def test_default_registry_covers_required_family_inventory(self):
        from mcp_server.integrations import resources

        self.assertEqual(resources.REQUIRED_RESOURCE_FAMILIES, REQUIRED_FAMILIES)
        self.assertEqual(set(resources.DEFAULT_FAMILY_BUILDER_REGISTRY), set(REQUIRED_FAMILIES))
        for family in REQUIRED_FAMILIES:
            self.assertGreater(
                len(resources.DEFAULT_FAMILY_BUILDER_REGISTRY[family]),
                0,
                f"missing builders for {family}",
            )


if __name__ == "__main__":
    unittest.main()
