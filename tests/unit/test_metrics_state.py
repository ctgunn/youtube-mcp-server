import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.observability import InMemoryObservability, RequestContext


class MetricsStateUnitTests(unittest.TestCase):
    def test_count_and_latency_summary_for_endpoint(self):
        obs = InMemoryObservability()
        context = RequestContext(request_id="req-1", path="/healthz")

        obs.record(context=context, outcome="success", latency_ms=10)
        obs.record(context=context, outcome="success", latency_ms=20)
        obs.record(context=context, outcome="error", latency_ms=30)

        self.assertEqual(obs.count_for("/healthz", "success"), 2)
        self.assertEqual(obs.count_for("/healthz", "error"), 1)

        snapshot = obs.snapshot()
        self.assertEqual(snapshot["counts"]["/healthz"]["success"], 2)
        self.assertEqual(snapshot["counts"]["/healthz"]["error"], 1)
        self.assertGreaterEqual(snapshot["latency"]["byEndpoint"]["/healthz"]["p95"], 20)

    def test_tool_dimension_latency(self):
        obs = InMemoryObservability()
        context = RequestContext(
            request_id="req-2",
            path="/mcp",
            method_name="tools/call",
            tool_name="server_ping",
        )

        obs.record(context=context, outcome="success", latency_ms=15)
        obs.record(context=context, outcome="success", latency_ms=25)

        snapshot = obs.snapshot()
        self.assertIn("server_ping", snapshot["latency"]["byTool"])
        self.assertEqual(snapshot["latency"]["byTool"]["server_ping"]["count"], 2)


if __name__ == "__main__":
    unittest.main()
