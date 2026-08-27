"""Loopback integration coverage for the remote MCP live-smoke workflow."""

from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest

from scripts.verify_remote_mcp_live_smoke import (
    HTTP_TIMEOUT_SECONDS,
    LAYER3_REMOTE_LIVE_SMOKE_ALLOWLIST,
    MAX_REMOTE_POSTS,
    MAX_REMOTE_TOOL_CALLS,
    RemoteSmokeError,
    main,
    run_all_remote_live_smoke,
    run_remote_layer2_live_smoke,
    run_remote_layer3_live_smoke,
    run_remote_live_smoke,
)
from scripts.verify_youtube_live import LIVE_SMOKE_ALLOWLIST


class _RemoteResponder(ThreadingHTTPServer):
    """Expose a controlled remote MCP endpoint for deterministic smoke tests.

    :param server_address: Loopback address and ephemeral port for the responder.
    :param handler_class: Request handler type that delegates to this responder.
    """

    def __init__(
        self,
        server_address: tuple[str, int],
        handler_class: type[BaseHTTPRequestHandler],
    ) -> None:
        """Initialize test-private request capture and response mode state.

        :param server_address: Loopback bind address for the temporary server.
        :param handler_class: HTTP handler used for JSON-RPC requests.
        """
        super().__init__(server_address, handler_class)
        self.requests: list[dict[str, Any]] = []
        self.include_secret_error = False
        self.malformed_stream = False
        self.endpoint_mismatch = False
        self.initialize_rejected = False
        self.omit_session = False
        self.empty_catalog = False
        self.http_fail_tool: str | None = None
        self.include_layer3_catalog = False

    def response_for(self, payload: dict[str, Any]) -> tuple[int, dict[str, str], str]:
        """Return a controlled public MCP response for one captured request.

        :param payload: Decoded JSON-RPC payload received from the remote client.
        :return: HTTP status, response headers, and direct JSON or SSE body.
        """
        method = payload["method"]
        request_id = payload["id"]
        if method == "initialize":
            if self.initialize_rejected:
                return (
                    401,
                    {"Content-Type": "application/json"},
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {"code": -32001, "message": "secret auth failure"},
                        }
                    ),
                )
            headers = {
                "Content-Type": "application/json",
                "MCP-Protocol-Version": "2025-11-25",
            }
            if not self.omit_session:
                headers["MCP-Session-Id"] = "test-session-id"
            return (
                200,
                headers,
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2025-11-25",
                            "capabilities": {"tools": {}},
                        },
                    }
                ),
            )
        if method == "tools/list":
            catalog = (
                []
                if self.empty_catalog
                else [
                    {
                        "name": "activities_list",
                        "metadata": {"upstream": {"operationKey": "activities.list"}},
                    },
                    {
                        "name": "commentThreads_list",
                        "metadata": {
                            "upstream": {"operationKey": "commentThreads.list"}
                        },
                    },
                    {
                        "name": "comments_list",
                        "metadata": {"upstream": {"operationKey": "comments.list"}},
                    },
                    {
                        "name": "videos_delete",
                        "metadata": {"upstream": {"operationKey": "videos.delete"}},
                    },
                ]
            )
            if self.include_layer3_catalog:
                catalog.extend(
                    {
                        "name": case.tool_name,
                        "metadata": {"family": "layer3"},
                    }
                    for case in LAYER3_REMOTE_LIVE_SMOKE_ALLOWLIST
                )
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps(
                    {"jsonrpc": "2.0", "id": request_id, "result": {"tools": catalog}}
                ),
            )
        tool_name = payload["params"]["name"]
        if self.http_fail_tool == tool_name:
            return (
                503,
                {"Content-Type": "application/json"},
                json.dumps({"error": "secret body"}),
            )
        if self.malformed_stream:
            return 200, {"Content-Type": "text/event-stream"}, "data: not-json\n\n"
        if self.include_secret_error:
            result: dict[str, Any] = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": "secret-token must never be reported",
                    "data": {
                        "category": "upstream_unavailable",
                        "authorization": "secret-token",
                    },
                },
            }
        elif tool_name in {
            case.tool_name for case in LAYER3_REMOTE_LIVE_SMOKE_ALLOWLIST
        }:
            case = next(
                candidate
                for candidate in LAYER3_REMOTE_LIVE_SMOKE_ALLOWLIST
                if candidate.tool_name == tool_name
            )
            result = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "structuredContent": {
                                field: "safe-fixture" for field in case.expected_fields
                            }
                        }
                    ]
                },
            }
        else:
            endpoint = {
                "activities_list": "activities.list",
                "commentThreads_list": "commentThreads.list",
                "comments_list": "comments.list",
            }[tool_name]
            if self.endpoint_mismatch:
                endpoint = "wrong.endpoint"
            items: list[dict[str, Any]] = [{"id": "safe-fixture-item"}]
            if tool_name == "commentThreads_list":
                items = [{"snippet": {"topLevelComment": {"id": "derived-parent-id"}}}]
            result = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {"structuredContent": {"endpoint": endpoint, "items": items}}
                    ]
                },
            }
        return (
            200,
            {"Content-Type": "text/event-stream"},
            f"event: message\ndata: {json.dumps(result)}\n\n",
        )


class _RemoteHandler(BaseHTTPRequestHandler):
    """Handle one controlled JSON-RPC request without writing diagnostic output."""

    server: _RemoteResponder

    def do_POST(self) -> None:
        """Capture one public MCP POST and return the responder's planned reply.

        :return: ``None`` after writing the controlled protocol response.
        :raises ValueError: If the client sends non-JSON request data.
        """
        content_length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        self.server.requests.append(
            {
                "method": payload["method"],
                "payload": payload,
                "authorization": self.headers.get("Authorization"),
                "session": self.headers.get("MCP-Session-Id"),
                "protocol": self.headers.get("MCP-Protocol-Version"),
            }
        )
        status, headers, body = self.server.response_for(payload)
        encoded = body.encode("utf-8")
        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, _format: str, *_args: object) -> None:
        """Suppress loopback request logging so test output has no raw headers.

        :param _format: Unused handler log message template.
        :param _args: Unused handler log message arguments.
        :return: ``None`` without emitting the request.
        """


@contextmanager
def _remote_responder() -> Iterator[_RemoteResponder]:
    """Run one temporary loopback server and clean it up after a test.

    :return: Yielded controlled responder with test-private request capture.
    :raises OSError: If the loopback server cannot bind an ephemeral port.
    """
    responder = _RemoteResponder(("127.0.0.1", 0), _RemoteHandler)
    thread = threading.Thread(target=responder.serve_forever, daemon=True)
    thread.start()
    try:
        yield responder
    finally:
        responder.shutdown()
        responder.server_close()
        thread.join()


def _environment(url: str, **overrides: str) -> dict[str, str]:
    """Build authorized remote-smoke environment values for one test.

    :param url: Loopback MCP URL returned by the temporary responder.
    :param overrides: Explicit environment overrides for an edge case.
    :return: Environment mapping with no values emitted by the test itself.
    """
    values = {
        "RUN_REMOTE_MCP_LIVE_SMOKE": "1",
        "REMOTE_MCP_URL": url,
        "MCP_AUTH_TOKEN": "test-mcp-token",
        "REMOTE_MCP_AUTH_REQUIRED": "1",
    }
    values.update(overrides)
    return values


def test_remote_smoke_uses_public_http_session_and_only_discovered_allowlist_entries() -> (
    None
):
    """Require initialize, list, and selected calls through a loopback endpoint.

    :return: ``None`` after validating safe remote selection and report behavior.
    :raises AssertionError: If transport ordering, session continuity, or selection regresses.
    """
    with _remote_responder() as responder:
        url = f"http://127.0.0.1:{responder.server_port}/mcp"
        report = run_remote_live_smoke(_environment(url))

    assert [entry["method"] for entry in responder.requests] == [
        "initialize",
        "tools/list",
        "tools/call",
        "tools/call",
        "tools/call",
    ]
    assert all(
        entry["authorization"] == "Bearer test-mcp-token"
        for entry in responder.requests
    )
    assert [entry["session"] for entry in responder.requests[1:]] == [
        "test-session-id"
    ] * 4
    assert [entry["protocol"] for entry in responder.requests[1:]] == ["2025-11-25"] * 4
    called_names = [
        entry["payload"]["params"]["name"] for entry in responder.requests[2:]
    ]
    assert called_names == ["activities_list", "commentThreads_list", "comments_list"]
    comments_request = responder.requests[-1]["payload"]["params"]["arguments"]
    assert comments_request["parentId"] == "derived-parent-id"
    assert report["status"] == "passed"
    assert [entry["toolName"] for entry in report["selected"]] == called_names
    assert report["excluded"] == ["videos_delete"]
    assert "test-mcp-token" not in repr(report)
    assert "test-session-id" not in repr(report)
    assert "derived-parent-id" not in repr(report)


def test_remote_layer3_smoke_uses_only_its_reviewed_composed_allowlist() -> None:
    """Require Layer 3 live smoke to select only its fixed public-read cases.

    :return: ``None`` after checking Layer 3 catalog selection and result validation.
    :raises AssertionError: If an unapproved or malformed composed result is accepted.
    """
    with _remote_responder() as responder:
        responder.include_layer3_catalog = True
        url = f"http://127.0.0.1:{responder.server_port}/mcp"
        report = run_remote_layer3_live_smoke(_environment(url))

    selected_names = [case.tool_name for case in LAYER3_REMOTE_LIVE_SMOKE_ALLOWLIST]
    called_names = [
        entry["payload"]["params"]["name"] for entry in responder.requests[2:]
    ]
    assert called_names == selected_names
    assert [entry["toolName"] for entry in report["selected"]] == selected_names
    assert all(entry["outcome"] == "success" for entry in report["selected"])
    assert report["toolCallLimit"] == len(LAYER3_REMOTE_LIVE_SMOKE_ALLOWLIST)
    assert report["requestLimit"] == len(LAYER3_REMOTE_LIVE_SMOKE_ALLOWLIST) + 2


def test_aggregate_remote_smoke_runs_each_layer_in_its_own_bounded_session() -> None:
    """Require the aggregate workflow to retain Layer 2 and Layer 3 isolation.

    :return: ``None`` after checking separate session starts and aggregate status.
    :raises AssertionError: If the suites share a request bound or lose one layer.
    """
    with _remote_responder() as responder:
        responder.include_layer3_catalog = True
        url = f"http://127.0.0.1:{responder.server_port}/mcp"
        report = run_all_remote_live_smoke(_environment(url))

    assert report["status"] == "passed"
    assert report["layer2"]["toolCallLimit"] == MAX_REMOTE_TOOL_CALLS
    assert report["layer3"]["toolCallLimit"] == len(LAYER3_REMOTE_LIVE_SMOKE_ALLOWLIST)
    assert [entry["method"] for entry in responder.requests].count("initialize") == 2
    assert [entry["method"] for entry in responder.requests].count("tools/list") == 2
    assert len(responder.requests) == 2 + 3 + 2 + len(
        LAYER3_REMOTE_LIVE_SMOKE_ALLOWLIST
    )


def test_layer2_alias_matches_the_original_remote_live_smoke() -> None:
    """Require the named Layer 2 command path to preserve prior selection behavior.

    :return: ``None`` after comparing the original and explicit Layer 2 reports.
    """
    with _remote_responder() as responder:
        url = f"http://127.0.0.1:{responder.server_port}/mcp"
        report = run_remote_layer2_live_smoke(_environment(url))

    assert report["toolCallLimit"] == MAX_REMOTE_TOOL_CALLS
    assert [entry["toolName"] for entry in report["selected"]] == [
        "activities_list",
        "commentThreads_list",
        "comments_list",
    ]


def test_remote_smoke_fails_closed_before_network_for_missing_prerequisites() -> None:
    """Require missing authorization inputs to prevent any requester call.

    :return: ``None`` after confirming preflight blocks the injected requester.
    :raises AssertionError: If an unauthorized run reaches the requester.
    """
    calls: list[object] = []

    def requester(_request: object) -> object:
        """Record an unexpected remote request made despite failed preflight.

        :param _request: Candidate request passed by the smoke workflow.
        :return: No response because this callback must not be reached.
        """
        calls.append(_request)
        raise AssertionError("requester must not be called")

    with pytest.raises(RuntimeError, match="RUN_REMOTE_MCP_LIVE_SMOKE"):
        run_remote_live_smoke(
            {"REMOTE_MCP_URL": "http://example.test/mcp"}, requester=requester
        )
    with pytest.raises(RuntimeError, match="MCP_AUTH_TOKEN"):
        run_remote_live_smoke(
            {
                "RUN_REMOTE_MCP_LIVE_SMOKE": "1",
                "REMOTE_MCP_URL": "http://example.test/mcp",
                "REMOTE_MCP_AUTH_REQUIRED": "1",
            },
            requester=requester,
        )
    assert calls == []


def test_remote_smoke_redacts_secret_bearing_error_content() -> None:
    """Require remote error payloads to be classified without copied secrets.

    :return: ``None`` after inspecting the safe per-tool report.
    :raises AssertionError: If responder secrets reach operator evidence.
    """
    with _remote_responder() as responder:
        responder.include_secret_error = True
        url = f"http://127.0.0.1:{responder.server_port}/mcp"
        report = run_remote_live_smoke(_environment(url))

    assert report["status"] == "completed_with_safe_errors"
    assert report["selected"][0] == {
        "toolName": "activities_list",
        "outcome": "safe_availability_error",
        "category": "upstream_unavailable",
    }
    assert "secret-token" not in repr(report)
    assert "test-mcp-token" not in repr(report)


def test_remote_smoke_reports_endpoint_mismatch_without_raw_response() -> None:
    """Require a discovered/result endpoint disagreement to fail safely.

    :return: ``None`` after classifying endpoint drift without response capture.
    :raises AssertionError: If endpoint disagreement is accepted as success.
    """
    with _remote_responder() as responder:
        responder.endpoint_mismatch = True
        url = f"http://127.0.0.1:{responder.server_port}/mcp"
        report = run_remote_live_smoke(_environment(url))

    assert report["selected"][0] == {
        "toolName": "activities_list",
        "outcome": "actionable_failure",
        "category": "unexpected_endpoint",
    }
    assert "wrong.endpoint" not in repr(report)


def test_remote_smoke_handles_rejected_or_sessionless_initialization_safely() -> None:
    """Require initialization failures to stop before discovery without diagnostics.

    :return: ``None`` after checking rejected and sessionless initialization paths.
    :raises AssertionError: If the client continues without a usable session.
    """
    with _remote_responder() as responder:
        responder.initialize_rejected = True
        url = f"http://127.0.0.1:{responder.server_port}/mcp"
        with pytest.raises(RemoteSmokeError, match="HTTP failure") as rejected:
            run_remote_live_smoke(_environment(url))
    assert rejected.value.category == "remote_authentication_failed"
    assert len(responder.requests) == 1
    assert "secret" not in str(rejected.value)

    with _remote_responder() as responder:
        responder.omit_session = True
        url = f"http://127.0.0.1:{responder.server_port}/mcp"
        with pytest.raises(RemoteSmokeError, match="usable session") as sessionless:
            run_remote_live_smoke(_environment(url))
    assert sessionless.value.category == "remote_session_missing"
    assert len(responder.requests) == 1


def test_remote_smoke_rejects_empty_catalog_and_classifies_per_tool_http_failure() -> (
    None
):
    """Require discovery and tool failures to have separate safe outcomes.

    :return: ``None`` after checking empty-catalog and HTTP-failure behavior.
    :raises AssertionError: If unsafe transport details reach a report.
    """
    with _remote_responder() as responder:
        responder.empty_catalog = True
        url = f"http://127.0.0.1:{responder.server_port}/mcp"
        with pytest.raises(
            RemoteSmokeError, match="catalog discovery"
        ) as empty_catalog:
            run_remote_live_smoke(_environment(url))
    assert empty_catalog.value.category == "remote_discovery_failed"
    assert "test-mcp-token" not in str(empty_catalog.value)

    with _remote_responder() as responder:
        responder.http_fail_tool = "activities_list"
        url = f"http://127.0.0.1:{responder.server_port}/mcp"
        report = run_remote_live_smoke(_environment(url))
    assert report["selected"][0] == {
        "toolName": "activities_list",
        "outcome": "actionable_failure",
        "category": "remote_http_failure",
    }
    assert "secret body" not in repr(report)


def test_remote_smoke_rejects_malformed_stream_without_leaking_content() -> None:
    """Require malformed streamed calls to become fixed safe tool failures.

    :return: ``None`` after classifying malformed events without response text.
    :raises AssertionError: If a malformed stream becomes a raw exception/report.
    """
    with _remote_responder() as responder:
        responder.malformed_stream = True
        url = f"http://127.0.0.1:{responder.server_port}/mcp"
        report = run_remote_live_smoke(_environment(url))

    assert report["selected"][0] == {
        "toolName": "activities_list",
        "outcome": "actionable_failure",
        "category": "remote_protocol_failure",
    }
    assert "not-json" not in repr(report)


def test_main_emits_only_safe_category_when_a_remote_error_contains_secret_text(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Require the final CLI boundary to discard exception text before output.

    :param monkeypatch: Pytest patch manager used to replace run execution.
    :param capsys: Output capture used to inspect the CLI boundary.
    :return: ``None`` after checking credential-safe CLI failure output.
    """

    def raise_secret_error() -> dict[str, object]:
        """Raise a deliberately secret-bearing error for final-boundary coverage.

        :return: No report because this helper always raises.
        :raises RemoteSmokeError: Fixed safe category with unsafe internal text.
        """
        raise RemoteSmokeError("secret-token must not print", "remote_timeout")

    monkeypatch.setattr(
        "scripts.verify_remote_mcp_live_smoke.run_remote_live_smoke", raise_secret_error
    )
    assert main() == 1
    output = capsys.readouterr().err
    assert output == "Remote MCP live smoke: FAILED\nReason: remote_timeout\n"
    assert "secret-token" not in output


def test_main_formats_compact_selected_and_excluded_tool_summary(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Require terminal output to summarize safe evidence without a raw JSON dump.

    :param monkeypatch: Pytest patch helper used to replace remote execution.
    :param capsys: Pytest output capture fixture used to inspect the console report.
    :return: ``None`` after checking formatted success and safe-error reports.
    """

    def successful_report() -> dict[str, object]:
        """Return a representative credential-safe successful report.

        :return: One selected success, one excluded tool, and bounded counts.
        """
        return {
            "status": "passed",
            "selected": [
                {
                    "toolName": "channels_list",
                    "outcome": "success",
                    "endpoint": "channels.list",
                    "itemCount": 1,
                }
            ],
            "excluded": ["videos_delete"],
            "requestCount": 3,
            "requestLimit": 14,
        }

    monkeypatch.setattr(
        "scripts.verify_remote_mcp_live_smoke.run_remote_live_smoke", successful_report
    )
    assert main() == 0
    output = capsys.readouterr().out
    assert "Remote MCP live smoke: PASS" in output
    assert "PASS  channels_list  |  endpoint=channels.list  |  items=1" in output
    assert "Passed: 1/1 approved tool(s)" in output
    assert "Excluded: 1 non-approved tool(s) (not invoked)" in output
    assert "Requests: 3/14 allowed" in output
    assert "videos_delete" not in output

    def safe_error_report() -> dict[str, object]:
        """Return a representative safe per-tool failure report.

        :return: One selected failure with an approved safe category.
        """
        return {
            "status": "completed_with_safe_errors",
            "selected": [
                {
                    "toolName": "channels_list",
                    "outcome": "actionable_failure",
                    "category": "remote_timeout",
                }
            ],
            "excluded": [],
            "requestCount": 3,
            "requestLimit": 14,
        }

    monkeypatch.setattr(
        "scripts.verify_remote_mcp_live_smoke.run_remote_live_smoke", safe_error_report
    )
    assert main() == 1
    error_output = capsys.readouterr().err
    assert "Remote MCP live smoke: COMPLETED WITH SAFE ERRORS" in error_output
    assert (
        "FAIL  channels_list  |  outcome=actionable_failure  |  category=remote_timeout"
        in error_output
    )


def test_remote_smoke_constants_reuse_the_reviewed_local_allowlist_limit() -> None:
    """Keep remote selection bounded by the reviewed canonical local allowlist.

    :return: ``None`` after validating the remote request limits.
    """
    assert len(LIVE_SMOKE_ALLOWLIST) == MAX_REMOTE_TOOL_CALLS
    assert MAX_REMOTE_POSTS == MAX_REMOTE_TOOL_CALLS + 2
    assert HTTP_TIMEOUT_SECONDS == 30.0
