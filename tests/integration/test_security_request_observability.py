import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import execute_hosted_request


class SecurityRequestObservabilityIntegrationTests(unittest.TestCase):
    def test_denied_requests_emit_security_decision_logs(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        app = create_app(
            env={"MCP_ENVIRONMENT": "dev", "MCP_AUTH_TOKEN": "obs-token"},
            runtime_stdout=stdout,
            runtime_stderr=stderr,
        )
        response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            body=b'{"jsonrpc":"2.0","id":"req-obs-init","method":"initialize","params":{"clientInfo":{"name":"client","version":"1.0.0"}}}',
        )
        self.assertEqual(response.status, 401)
        events = [json.loads(line) for line in stderr.getvalue().splitlines()]
        security_event = [event for event in events if event.get("event") == "security.decision"][-1]
        self.assertEqual(security_event["decisionCategory"], "unauthenticated")
        self.assertEqual(security_event["path"], "/mcp")
        self.assertIn("requestId", security_event)


if __name__ == "__main__":
    unittest.main()
