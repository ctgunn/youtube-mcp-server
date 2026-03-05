import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.protocol.envelope import error_response, success_response
from mcp_server.protocol.methods import route_mcp_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class EnvelopeContractTests(unittest.TestCase):
    def test_success_response_shape(self):
        response = success_response({"ok": True}, request_id="req-1")
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], {"ok": True})
        self.assertEqual(response["meta"]["requestId"], "req-1")
        self.assertIsNone(response["error"])

    def test_error_response_shape_and_sanitization(self):
        message = "RuntimeError: boom\nTraceback (most recent call last)"
        response = error_response(
            "INTERNAL_ERROR", message, request_id="req-2", details={"k": "v"}
        )
        self.assertFalse(response["success"])
        self.assertIsNone(response["data"])
        self.assertEqual(response["meta"]["requestId"], "req-2")
        self.assertEqual(response["error"]["code"], "INTERNAL_ERROR")
        self.assertIn("boom", response["error"]["message"])
        self.assertNotIn("Traceback", response["error"]["message"])
        self.assertEqual(response["error"]["details"], {"k": "v"})

    def test_error_response_allows_tool_detail_payload(self):
        response = error_response(
            "RESOURCE_NOT_FOUND",
            "Tool not found.",
            request_id="req-3",
            details={"toolName": "missing"},
        )
        self.assertEqual(response["error"]["details"], {"toolName": "missing"})

    def test_error_response_does_not_expose_secret_values(self):
        response = error_response(
            "CONFIG_VALIDATION_ERROR",
            "missing required secret",
            request_id="req-secret",
            details={"profile": "prod", "failures": [{"key": "YOUTUBE_API_KEY", "reason": "missing required secret"}]},
        )
        rendered = str(response)
        self.assertIn("YOUTUBE_API_KEY", rendered)
        self.assertNotIn("secret-value", rendered)

    def test_error_response_always_contains_code_message_details_keys(self):
        response = error_response("INVALID_ARGUMENT", "bad request")
        self.assertEqual(set(response["error"].keys()), {"code", "message", "details"})
        self.assertIsNone(response["error"]["details"])

    def test_baseline_tool_responses_keep_envelope_shape(self):
        dispatcher = InMemoryToolDispatcher()
        success = route_mcp_request(
            {
                "id": "req-4",
                "method": "tools/call",
                "params": {"toolName": "server_ping", "arguments": {}},
            },
            dispatcher,
        )
        failure = route_mcp_request(
            {
                "id": "req-5",
                "method": "tools/call",
                "params": {"toolName": "missing", "arguments": {}},
            },
            dispatcher,
        )

        self.assertTrue(success["success"])
        self.assertIn("data", success)
        self.assertIn("meta", success)
        self.assertIn("error", success)
        self.assertIsNone(success["error"])

        self.assertFalse(failure["success"])
        self.assertIsNone(failure["data"])
        self.assertIn("meta", failure)
        self.assertIn("error", failure)


if __name__ == "__main__":
    unittest.main()
