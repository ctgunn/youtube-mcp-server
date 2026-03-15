import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.transport.http import HostedRequestClassification, classify_hosted_request, hosted_status_code


class HostedHTTPSemanticsUnitTests(unittest.TestCase):
    def test_ready_classification_and_status_mapping(self):
        classification = classify_hosted_request(method="GET", path="/ready")
        self.assertEqual(
            classification,
            HostedRequestClassification(
                path_class="ready",
                method_class="supported",
                media_type_class="not_applicable",
                body_class="ignored",
                outcome_class="success",
            ),
        )
        self.assertEqual(
            hosted_status_code(classification, {"status": "ready", "checks": {"configuration": "pass"}}),
            200,
        )
        self.assertEqual(
            hosted_status_code(
                classification,
                {"status": "not_ready", "checks": {"configuration": "fail"}, "reason": {"code": "X"}},
            ),
            503,
        )

    def test_mcp_content_type_and_body_validation_classification(self):
        malformed = classify_hosted_request(
            method="POST",
            path="/mcp",
            content_type="application/json",
            body_present=True,
            body_valid=False,
        )
        self.assertEqual(malformed.outcome_class, "bad_request")
        self.assertEqual(hosted_status_code(malformed), 400)

        valid = classify_hosted_request(
            method="POST",
            path="/mcp",
            content_type="application/json; charset=utf-8",
            body_present=True,
            body_valid=True,
        )
        self.assertEqual(valid.media_type_class, "supported")
        self.assertEqual(hosted_status_code(valid, {"success": True}), 200)

        invalid_media_type = classify_hosted_request(
            method="POST",
            path="/mcp",
            content_type="text/plain",
            body_present=True,
            body_valid=True,
        )
        self.assertEqual(invalid_media_type.outcome_class, "unsupported_media_type")
        self.assertEqual(hosted_status_code(invalid_media_type), 415)

    def test_method_not_allowed_and_not_found_are_distinct(self):
        method_not_allowed = classify_hosted_request(method="POST", path="/health")
        self.assertEqual(method_not_allowed.outcome_class, "method_not_allowed")
        self.assertEqual(hosted_status_code(method_not_allowed), 405)

        not_found = classify_hosted_request(method="GET", path="/missing")
        self.assertEqual(not_found.outcome_class, "not_found")
        self.assertEqual(hosted_status_code(not_found), 404)


if __name__ == "__main__":
    unittest.main()
