"""Red/green hosted-flow tests for production hardening."""

from __future__ import annotations

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import execute_hosted_request


class ProductionHardeningHostedFlowTests(unittest.TestCase):
    """Verify hardening dependency construction preserves base routes."""

    def test_transport_exposes_hardening_dependencies_without_affecting_base_routes(self) -> None:
        """Require explicit hardening dependencies while preserving health/readiness."""
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})

        self.assertTrue(hasattr(app, "hardening"))
        self.assertEqual(app.handle("/health", {}), {"status": "ok"})
        self.assertEqual(app.handle("/ready", {})["status"], "ready")

    def test_over_limit_hosted_tool_call_returns_safe_streamed_error(self) -> None:
        """Reject an exhausted public call before the tool handler can run."""
        app = create_app(
            env={
                "MCP_ENVIRONMENT": "dev",
                "MCP_RATE_LIMIT_ANONYMOUS_REQUESTS_PER_MINUTE": "1",
            }
        )
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        initialize = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers=headers,
            body=json.dumps({"jsonrpc": "2.0", "id": "init", "method": "initialize", "params": {"clientInfo": {"name": "test"}}}).encode(),
        )
        call_headers = {**headers, "MCP-Session-Id": initialize.headers["MCP-Session-Id"]}
        first = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers=call_headers,
            body=json.dumps({"jsonrpc": "2.0", "id": "call-1", "method": "tools/call", "params": {"name": "server_ping", "arguments": {}}}).encode(),
        )
        second = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers=call_headers,
            body=json.dumps({"jsonrpc": "2.0", "id": "call-2", "method": "tools/call", "params": {"name": "server_ping", "arguments": {}}}).encode(),
        )

        self.assertEqual(first.status, 200)
        self.assertEqual(second.status, 200)
        self.assertEqual(second.headers["Retry-After"], "60")
        self.assertIn('"category": "rate_limited"', second.body.decode())

    def test_eligible_fetch_reports_miss_then_hit_without_changing_stream_shape(self) -> None:
        """Expose only safe cache status while retaining normal MCP content."""
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        initialize = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers=headers,
            body=json.dumps({"jsonrpc": "2.0", "id": "init-cache", "method": "initialize", "params": {"clientInfo": {"name": "test"}}}).encode(),
        )
        call_headers = {**headers, "MCP-Session-Id": initialize.headers["MCP-Session-Id"]}
        payload = json.dumps({"jsonrpc": "2.0", "id": "fetch-1", "method": "tools/call", "params": {"name": "fetch", "arguments": {"id": "doc-remote-mcp-001"}}}).encode()
        first = execute_hosted_request(app, method="POST", path="/mcp", headers=call_headers, body=payload)
        second = execute_hosted_request(app, method="POST", path="/mcp", headers=call_headers, body=payload.replace(b"fetch-1", b"fetch-2"))

        self.assertEqual(first.headers["MCP-Cache-Status"], "miss")
        self.assertEqual(second.headers["MCP-Cache-Status"], "hit")
        self.assertIn('"structuredContent"', second.body.decode())


if __name__ == "__main__":
    unittest.main()
