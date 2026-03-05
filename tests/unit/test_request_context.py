import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.observability import build_request_context, classify_endpoint


class RequestContextUnitTests(unittest.TestCase):
    def test_uses_payload_request_id_when_present(self):
        context = build_request_context(
            "/mcp",
            {
                "id": "req-abc",
                "method": "tools/call",
                "params": {"toolName": "server_ping", "arguments": {}},
            },
        )
        self.assertEqual(context.request_id, "req-abc")
        self.assertEqual(context.method_name, "tools/call")
        self.assertEqual(context.tool_name, "server_ping")

    def test_generates_request_id_when_missing(self):
        context = build_request_context("/healthz", {})
        self.assertTrue(context.request_id.startswith("req-"))
        self.assertEqual(context.path, "/healthz")

    def test_classify_endpoint(self):
        self.assertEqual(classify_endpoint("/healthz"), "/healthz")
        self.assertEqual(classify_endpoint("/readyz"), "/readyz")
        self.assertEqual(classify_endpoint("/mcp"), "/mcp")
        self.assertEqual(classify_endpoint("/unknown"), "not_found")


if __name__ == "__main__":
    unittest.main()
