import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app


class MCPRequestFlowIntegrationTests(unittest.TestCase):
    def test_initialize_list_call_sequence(self):
        app = create_app()

        init_payload = {
            "id": "req-i1",
            "method": "initialize",
            "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
        }
        init_resp = app.handle("/mcp", init_payload)
        self.assertTrue(init_resp["success"])

        list_payload = {"id": "req-i2", "method": "tools/list", "params": {}}
        list_resp = app.handle("/mcp", list_payload)
        self.assertTrue(list_resp["success"])
        names = [tool["name"] for tool in list_resp["data"]]
        self.assertIn("server_ping", names)

        call_payload = {
            "id": "req-i3",
            "method": "tools/call",
            "params": {"toolName": "server_ping", "arguments": {}},
        }
        call_resp = app.handle("/mcp", call_payload)
        self.assertTrue(call_resp["success"])
        self.assertEqual(call_resp["data"]["result"]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
