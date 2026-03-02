import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.protocol.envelope import error_response, success_response


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


if __name__ == "__main__":
    unittest.main()
