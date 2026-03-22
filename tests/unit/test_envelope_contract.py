import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.protocol.envelope import error_response, error_response_for_category, success_response
from mcp_server.protocol.methods import route_mcp_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class EnvelopeContractTests(unittest.TestCase):
    def test_success_response_shape(self):
        response = success_response({"ok": True}, request_id="req-1")
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "req-1")
        self.assertEqual(response["result"], {"ok": True})
        self.assertNotIn("success", response)
        self.assertNotIn("data", response)
        self.assertNotIn("meta", response)

    def test_error_response_shape_and_sanitization(self):
        message = "RuntimeError: boom\nTraceback (most recent call last)"
        response = error_response(-32603, message, request_id="req-2", details={"k": "v"})
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "req-2")
        self.assertEqual(response["error"]["code"], -32603)
        self.assertIn("boom", response["error"]["message"])
        self.assertNotIn("Traceback", response["error"]["message"])
        self.assertEqual(response["error"]["data"], {"k": "v"})

    def test_error_response_allows_tool_detail_payload(self):
        response = error_response_for_category(
            "unknown_tool",
            "Tool not found.",
            request_id="req-3",
            details={"toolName": "missing"},
        )
        self.assertEqual(response["error"]["code"], -32001)
        self.assertEqual(response["error"]["data"], {"category": "unknown_tool", "toolName": "missing"})

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

    def test_error_response_always_contains_code_message_data_keys(self):
        response = error_response(-32602, "bad request")
        self.assertEqual(set(response["error"].keys()), {"code", "message", "data"})
        self.assertIsNone(response["error"]["data"])

    def test_baseline_tool_responses_use_mcp_protocol_shape(self):
        dispatcher = InMemoryToolDispatcher()
        success = route_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": "req-4",
                "method": "tools/call",
                "params": {"name": "server_ping", "arguments": {}},
            },
            dispatcher,
        )
        failure = route_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": "req-5",
                "method": "tools/call",
                "params": {"name": "missing", "arguments": {}},
            },
            dispatcher,
        )

        self.assertEqual(success["jsonrpc"], "2.0")
        self.assertEqual(success["id"], "req-4")
        self.assertIn("result", success)
        content = success["result"]["content"]
        self.assertEqual(content[0]["type"], "text")
        payload = json.loads(content[0]["text"])
        self.assertEqual(payload["status"], "ok")

        self.assertEqual(failure["jsonrpc"], "2.0")
        self.assertEqual(failure["id"], "req-5")
        self.assertIn("error", failure)
        self.assertEqual(failure["error"]["code"], -32001)
        self.assertEqual(failure["error"]["data"]["category"], "unknown_tool")


if __name__ == "__main__":
    unittest.main()
