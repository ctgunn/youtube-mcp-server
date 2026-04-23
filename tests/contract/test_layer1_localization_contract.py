import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import (
    build_i18n_languages_list_wrapper,
    build_i18n_regions_list_wrapper,
)


class Layer1LocalizationContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/124-i18n-languages-list/contracts")

    def _region_feature_contract_root(self) -> str:
        return os.path.abspath("specs/125-i18n-regions-list/contracts")

    def test_contract_artifacts_define_wrapper_and_localization_guidance(self):
        root = self._feature_contract_root()
        with open(
            os.path.join(root, "layer1-i18n-languages-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-i18n-languages-list-localization-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            localization_contract = handle.read()

        self.assertIn("quota cost (`1`)", wrapper_contract)
        self.assertIn("`part` plus `hl`", wrapper_contract)
        self.assertIn("localization lookup", localization_contract.lower())
        self.assertIn("successful empty results", localization_contract.lower())

    def test_i18n_languages_list_wrapper_review_surface_exposes_identity_quota_and_lookup_notes(self):
        review_surface = build_i18n_languages_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "i18nLanguages")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "i18nLanguages.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part", "hl"))
        self.assertEqual(review_surface["lifecycleState"], "active")

    def test_contract_documents_request_boundaries_and_invalid_request_rules(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-i18n-languages-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()

        self.assertIn("`part` and `hl` are required", wrapper_contract)
        self.assertIn("undocumented modifiers", wrapper_contract)
        self.assertIn("silently rewritten", wrapper_contract)

    def test_contract_documents_empty_result_and_invalid_request_rules(self):
        with open(
            os.path.join(
                self._feature_contract_root(),
                "layer1-i18n-languages-list-localization-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            localization_contract = handle.read()

        self.assertIn("successful empty results", localization_contract.lower())
        self.assertIn("invalid requests", localization_contract.lower())
        self.assertIn("missing `part` or `hl`", localization_contract)

    def test_region_contract_artifacts_define_wrapper_and_region_guidance(self):
        root = self._region_feature_contract_root()
        with open(
            os.path.join(root, "layer1-i18n-regions-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-i18n-regions-list-region-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            region_contract = handle.read()

        self.assertIn("quota cost (`1`)", wrapper_contract)
        self.assertIn("`part` plus `hl`", wrapper_contract)
        self.assertIn("region lookup", region_contract.lower())
        self.assertIn("empty-result", region_contract.lower())

    def test_i18n_regions_list_wrapper_review_surface_exposes_identity_quota_and_lookup_notes(self):
        review_surface = build_i18n_regions_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "i18nRegions")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "i18nRegions.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part", "hl"))
        self.assertEqual(review_surface["lifecycleState"], "active")

    def test_region_contract_documents_request_boundaries_and_invalid_request_rules(self):
        with open(
            os.path.join(
                self._region_feature_contract_root(),
                "layer1-i18n-regions-list-wrapper-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()

        self.assertIn("`part` and `hl` are required", wrapper_contract)
        self.assertIn("undocumented modifiers", wrapper_contract)
        self.assertIn("silently rewritten", wrapper_contract)

    def test_region_contract_documents_reviewable_lookup_guidance(self):
        with open(
            os.path.join(
                self._region_feature_contract_root(),
                "layer1-i18n-regions-list-region-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            region_contract = handle.read()

        self.assertIn("api-key access", region_contract.lower())
        self.assertIn("`part` plus `hl`", region_contract)
        self.assertIn("downstream callers", region_contract.lower())
