import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))


class Layer1SearchContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/140-search-list/contracts")

    def test_contract_artifacts_define_search_wrapper_and_auth_guidance(self):
        root = self._feature_contract_root()
        with open(
            os.path.join(root, "layer1-search-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-search-list-auth-refinement-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_refinement_contract = handle.read()

        self.assertIn("quota cost of `100`", wrapper_contract)
        self.assertIn("`part` and `q`", wrapper_contract)
        self.assertIn("stronger authorization", auth_refinement_contract)
        self.assertIn("video-specific refinements", auth_refinement_contract)

    def test_contract_documents_invalid_request_and_empty_result_boundaries(self):
        with open(
            os.path.join(
                self._feature_contract_root(),
                "layer1-search-list-auth-refinement-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_refinement_contract = handle.read()

        self.assertIn("invalid request-shape outcomes must remain reviewable as `invalid_request`", auth_refinement_contract)
        self.assertIn("empty-result success", auth_refinement_contract)
        self.assertIn("normalized upstream search failure", auth_refinement_contract)


if __name__ == "__main__":
    unittest.main()
