import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.security import (
    HostedSecuritySettings,
    browser_preflight_headers,
    evaluate_credential,
    evaluate_browser_preflight,
    evaluate_origin,
    evaluate_security_request,
    parse_requested_headers,
)


class HostedSecurityPolicyTests(unittest.TestCase):
    def setUp(self):
        self.settings = HostedSecuritySettings(
            auth_required=True,
            auth_token="secret-token",
            allowed_origins=("http://localhost:3000",),
            allow_originless_clients=True,
        )

    def test_origin_allowlist_and_originless_clients(self):
        browser = evaluate_origin({"origin": "http://localhost:3000"}, self.settings)
        self.assertEqual(browser.match_result, "allowed")

        non_browser = evaluate_origin({}, self.settings)
        self.assertEqual(non_browser.match_result, "exempt")
        self.assertEqual(non_browser.client_type, "non_browser")

    def test_malformed_and_denied_origin(self):
        malformed = evaluate_origin({"origin": "bad-origin"}, self.settings)
        self.assertEqual(malformed.reason_code, "malformed_origin")

        denied = evaluate_origin({"origin": "https://evil.example"}, self.settings)
        self.assertEqual(denied.match_result, "denied")
        self.assertEqual(denied.reason_code, "origin_not_allowed")

    def test_credential_evaluation(self):
        missing = evaluate_credential({}, self.settings, environment="dev")
        self.assertEqual(missing.token_state, "missing")

        malformed = evaluate_credential({"authorization": "Token nope"}, self.settings, environment="dev")
        self.assertEqual(malformed.token_state, "malformed")

        invalid = evaluate_credential({"authorization": "Bearer wrong"}, self.settings, environment="dev")
        self.assertEqual(invalid.token_state, "invalid")

        valid = evaluate_credential({"authorization": "Bearer secret-token"}, self.settings, environment="dev")
        self.assertEqual(valid.token_state, "valid")

    def test_security_decision_categories(self):
        origin_denied = evaluate_security_request(
            {"origin": "https://evil.example", "authorization": "Bearer secret-token"},
            self.settings,
            path="/mcp",
            request_id="req-1",
            environment="dev",
        )
        self.assertEqual(origin_denied.decision_category, "origin_denied")
        self.assertFalse(origin_denied.tool_execution_allowed)

        unauthenticated = evaluate_security_request(
            {},
            self.settings,
            path="/mcp",
            request_id="req-2",
            environment="dev",
        )
        self.assertEqual(unauthenticated.decision_category, "unauthenticated")

        accepted = evaluate_security_request(
            {"authorization": "Bearer secret-token"},
            self.settings,
            path="/mcp",
            request_id="req-3",
            environment="dev",
        )
        self.assertEqual(accepted.decision_category, "accepted")
        self.assertTrue(accepted.tool_execution_allowed)

    def test_requested_headers_are_normalized_and_deduplicated(self):
        self.assertEqual(
            parse_requested_headers(" Authorization, Content-Type, authorization , MCP-Session-Id "),
            ("authorization", "content-type", "mcp-session-id"),
        )

    def test_browser_preflight_allows_supported_origin_method_and_headers(self):
        evaluation = evaluate_browser_preflight(
            path="/mcp",
            request_headers={
                "origin": "http://localhost:3000",
                "access-control-request-method": "POST",
                "access-control-request-headers": "authorization, content-type",
            },
            settings=self.settings,
        )
        self.assertEqual(evaluation.decision_category, "approved")
        self.assertEqual(evaluation.status_code, 204)
        headers = browser_preflight_headers(evaluation, self.settings)
        self.assertEqual(headers["Access-Control-Allow-Origin"], "http://localhost:3000")
        self.assertIn("POST", headers["Access-Control-Allow-Methods"])
        self.assertIn("authorization", headers["Access-Control-Allow-Headers"].lower())

    def test_browser_preflight_rejects_unsupported_headers(self):
        evaluation = evaluate_browser_preflight(
            path="/mcp",
            request_headers={
                "origin": "http://localhost:3000",
                "access-control-request-method": "POST",
                "access-control-request-headers": "x-custom-header",
            },
            settings=self.settings,
        )
        self.assertEqual(evaluation.decision_category, "unsupported_browser_headers")
        self.assertEqual(evaluation.status_code, 400)


if __name__ == "__main__":
    unittest.main()
