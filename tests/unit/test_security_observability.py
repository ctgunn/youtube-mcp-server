import io
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.observability import InMemoryObservability


class SecurityObservabilityTests(unittest.TestCase):
    def test_security_decision_event_is_emitted_without_secret_values(self):
        stderr = io.StringIO()
        observability = InMemoryObservability(runtime_stderr=stderr)
        observability.emit_security_decision(
            {
                "requestId": "req-sec-1",
                "path": "/mcp",
                "decision": "denied",
                "decisionCategory": "invalid_credential",
                "clientType": "non_browser",
                "authPresent": True,
                "originPresent": False,
            }
        )
        payload = stderr.getvalue()
        self.assertIn("security.decision", payload)
        self.assertIn("invalid_credential", payload)
        self.assertNotIn("secret-token", payload)


if __name__ == "__main__":
    unittest.main()
