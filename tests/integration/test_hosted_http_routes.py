import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import build_asgi_app, execute_hosted_request
from mcp_server.transport.session_store import reset_memory_session_store_registry


class HostedHTTPRoutesIntegrationTests(unittest.TestCase):
    def tearDown(self):
        reset_memory_session_store_registry()

    def _runtime_transport(self):
        hosted_app = build_asgi_app(validate_startup=False)
        return getattr(hosted_app, "transport", getattr(getattr(hosted_app, "state", None), "transport", None))

    def _initialize_session(self, app):
        response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-init-routes",
                    "method": "initialize",
                    "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
                }
            ).encode("utf-8"),
        )
        self.assertEqual(response.status, 200)
        return response.headers["MCP-Session-Id"]

    def test_health_and_ready_use_expected_hosted_statuses(self):
        ready_app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        ready = execute_hosted_request(ready_app, method="GET", path="/ready")
        self.assertEqual(ready.status, 200)
        self.assertEqual(ready.headers["Content-Type"], "application/json")
        self.assertEqual(ready.payload["status"], "ready")

        not_ready_app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        not_ready = execute_hosted_request(not_ready_app, method="GET", path="/ready")
        self.assertEqual(not_ready.status, 503)
        self.assertEqual(not_ready.headers["Content-Type"], "application/json")
        self.assertEqual(not_ready.payload["status"], "not_ready")

        liveness = execute_hosted_request(ready_app, method="GET", path="/health")
        self.assertEqual(liveness.status, 200)
        self.assertEqual(liveness.payload, {"status": "ok"})

    def test_mcp_rejects_malformed_json_and_unsupported_media_type(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})

        malformed = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            body=b'{"id":"req-bad"',
        )
        self.assertEqual(malformed.status, 400)
        self.assertEqual(malformed.payload["error"]["code"], -32600)
        self.assertEqual(malformed.payload["error"]["data"]["category"], "invalid_json")

        unsupported_media_type = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "text/plain", "Accept": "application/json, text/event-stream"},
            body=b"plain-text",
        )
        self.assertEqual(unsupported_media_type.status, 415)
        self.assertEqual(unsupported_media_type.payload["error"]["code"], -32602)
        self.assertEqual(unsupported_media_type.payload["error"]["data"]["category"], "unsupported_media_type")

    def test_unsupported_method_and_unknown_path_use_distinct_statuses(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})

        wrong_method = execute_hosted_request(app, method="DELETE", path="/mcp")
        self.assertEqual(wrong_method.status, 405)
        self.assertEqual(wrong_method.payload["error"]["code"], -32601)
        self.assertEqual(wrong_method.payload["error"]["data"]["category"], "method_not_allowed")

        missing_path = execute_hosted_request(app, method="GET", path="/missing")
        self.assertEqual(missing_path.status, 404)
        self.assertEqual(missing_path.payload["error"]["code"], -32001)
        self.assertEqual(missing_path.payload["error"]["data"]["category"], "path_not_found")

    def test_hosted_mcp_initialize_and_session_list_use_json_protocol_result(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        session_id = self._initialize_session(app)
        response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=json.dumps({"jsonrpc": "2.0", "id": "req-hosted-1", "method": "tools/list", "params": {}}).encode("utf-8"),
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.payload["jsonrpc"], "2.0")
        self.assertIsInstance(response.payload["result"]["tools"], list)
        self.assertIn("inputSchema", response.payload["result"]["tools"][0])

    def test_hosted_tool_call_returns_structured_content(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        session_id = self._initialize_session(app)
        response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-hosted-call",
                    "method": "tools/call",
                    "params": {"name": "server_ping", "arguments": {}},
                }
            ).encode("utf-8"),
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers["Content-Type"], "text/event-stream")
        self.assertIn('"structuredContent"', response.body.decode("utf-8"))

    def test_hosted_search_and_fetch_routes_return_streamed_structured_content(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        session_id = self._initialize_session(app)

        list_response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=b'{"jsonrpc":"2.0","id":"req-hosted-list","method":"tools/list","params":{}}',
        )
        self.assertEqual(list_response.status, 200)
        list_payload = list_response.payload["result"]["tools"]
        fetch_tool = [tool for tool in list_payload if tool["name"] == "fetch"][0]
        self.assertIn("oneOf", fetch_tool["inputSchema"])

        search_response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-hosted-search",
                    "method": "tools/call",
                    "params": {"name": "search", "arguments": {"query": "remote MCP research", "pageSize": 1}},
                }
            ).encode("utf-8"),
        )
        search_body = search_response.body.decode("utf-8")
        self.assertEqual(search_response.status, 200)
        self.assertIn('"resourceId": "res_remote_mcp_001"', search_body)

        fetch_response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-hosted-fetch",
                    "method": "tools/call",
                    "params": {"name": "fetch", "arguments": {"resourceId": "res_remote_mcp_001"}},
                }
            ).encode("utf-8"),
        )
        fetch_body = fetch_response.body.decode("utf-8")
        self.assertEqual(fetch_response.status, 200)
        self.assertIn('"retrievalStatus": "complete"', fetch_body)

        fetch_by_uri_response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-hosted-fetch-uri",
                    "method": "tools/call",
                    "params": {"name": "fetch", "arguments": {"uri": "https://example.com/remote-mcp-research"}},
                }
            ).encode("utf-8"),
        )
        self.assertEqual(fetch_by_uri_response.status, 200)
        self.assertIn('"resourceId": "res_remote_mcp_001"', fetch_by_uri_response.body.decode("utf-8"))

    def test_migrated_runtime_transport_preserves_mcp_route_execution(self):
        transport = self._runtime_transport()
        response = execute_hosted_request(
            transport,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-asgi-routes-init",
                    "method": "initialize",
                    "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
                }
            ).encode("utf-8"),
        )
        self.assertEqual(response.status, 200)
        self.assertIn("MCP-Session-Id", response.headers)

    def test_invalid_session_response_remains_distinct_from_tool_errors(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": "missing-session",
            },
            body=b'{"jsonrpc":"2.0","id":"req-missing-session","method":"tools/list","params":{}}',
        )
        self.assertEqual(response.status, 404)
        self.assertEqual(response.payload["error"]["code"], -32001)
        self.assertEqual(response.payload["error"]["data"]["category"], "session_not_found")

    def test_browser_preflight_is_supported_for_mcp(self):
        app = create_app(
            env={
                "MCP_ENVIRONMENT": "dev",
                "MCP_AUTH_TOKEN": "routes-token",
                "MCP_ALLOWED_ORIGINS": "http://localhost:3000",
            }
        )
        response = execute_hosted_request(
            app,
            method="OPTIONS",
            path="/mcp",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization, content-type",
            },
        )
        self.assertEqual(response.status, 204)
        self.assertEqual(response.body, b"")
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://localhost:3000")


if __name__ == "__main__":
    unittest.main()
