"""Contract coverage for the remote MCP read-only live-smoke client."""

from __future__ import annotations

import json
from typing import ClassVar, Self

import pytest

import scripts.verify_remote_mcp_live_smoke as remote_smoke
from scripts.verify_remote_mcp_live_smoke import (
    LAYER3_REMOTE_LIVE_SMOKE_ALLOWLIST,
    MAX_REMOTE_POSTS,
    MAX_REMOTE_TOOL_CALLS,
    MCP_PROTOCOL_VERSION,
    RemoteHTTPResponse,
    RemoteMCPRequest,
    RemoteSmokeError,
    _parse_protocol_response,
    _preflight,
    _read_sse_response_body,
    _safe_case_result,
    _send_request,
)
from scripts.verify_youtube_live import LIVE_SMOKE_ALLOWLIST


def test_preflight_requires_explicit_enablement_and_remote_url() -> None:
    """Require the remote smoke boundary to fail before constructing requests.

    :return: ``None`` after validating mandatory opt-in inputs.
    :raises AssertionError: If a missing prerequisite is accepted.
    """
    with pytest.raises(RemoteSmokeError, match="RUN_REMOTE_MCP_LIVE_SMOKE"):
        _preflight({"REMOTE_MCP_URL": "https://example.test/mcp"})
    with pytest.raises(RemoteSmokeError, match="REMOTE_MCP_URL"):
        _preflight({"RUN_REMOTE_MCP_LIVE_SMOKE": "1"})


def test_preflight_requires_bearer_material_only_when_declared() -> None:
    """Require declared bearer-protected targets to have a token before I/O.

    :return: ``None`` after checking explicit endpoint authentication intent.
    :raises AssertionError: If a required bearer token is omitted.
    """
    with pytest.raises(RemoteSmokeError, match="MCP_AUTH_TOKEN"):
        _preflight(
            {
                "RUN_REMOTE_MCP_LIVE_SMOKE": "1",
                "REMOTE_MCP_URL": "https://example.test/mcp",
                "REMOTE_MCP_AUTH_REQUIRED": "1",
            }
        )


def test_streamed_tool_response_normalizes_only_matching_json_rpc_event() -> None:
    """Require a streamed call to select its matching JSON-RPC response event.

    :return: ``None`` after parsing the selected event envelope.
    :raises AssertionError: If an unrelated event or raw payload is selected.
    """
    response = RemoteHTTPResponse(
        status_code=200,
        headers={"content-type": "text/event-stream"},
        body=(
            "event: message\n"
            f"data: {json.dumps({'jsonrpc': '2.0', 'id': 'other', 'result': {}})}\n\n"
            "event: message\n"
            f"data: {json.dumps({'jsonrpc': '2.0', 'id': 'call-1', 'result': {'content': []}})}\n\n"
        ),
    )

    assert _parse_protocol_response(response, "call-1") == {
        "jsonrpc": "2.0",
        "id": "call-1",
        "result": {"content": []},
    }


def test_streamed_response_rejects_malformed_or_unmatched_data() -> None:
    """Require malformed streamed data to become a safe protocol failure.

    :return: ``None`` after rejecting an unusable stream.
    :raises AssertionError: If malformed response data is accepted.
    """
    response = RemoteHTTPResponse(
        status_code=200,
        headers={"content-type": "text/event-stream"},
        body="data: not-json\n\n",
    )

    with pytest.raises(RemoteSmokeError, match="valid MCP response"):
        _parse_protocol_response(response, "call-1")


def test_sse_reader_stops_after_the_matching_event_without_waiting_for_close() -> None:
    """Require the HTTP reader to close a persistent stream after the call event.

    :return: ``None`` after selecting the matching event before a later line.
    """

    class _PersistentResponse:
        """Yield planned SSE lines while recording how much of the stream was read."""

        def __init__(self) -> None:
            """Initialize a finite prefix of a simulated persistent event stream."""
            self.lines = iter(
                (
                    b'data: {"jsonrpc": "2.0", "id": "other"}\n',
                    b'data: {"jsonrpc": "2.0", "id": "call-1", "result": {}}\n',
                )
            )
            self.read_count = 0

        def readline(self) -> bytes:
            """Return one planned line and fail if the reader waits for a later line.

            :return: Next simulated SSE line.
            :raises AssertionError: If the client reads past the matching event.
            """
            self.read_count += 1
            if self.read_count > 2:
                raise AssertionError("reader waited for persistent SSE stream closure")
            return next(self.lines)

    response = _PersistentResponse()
    assert _read_sse_response_body(response, "call-1") == (
        'data: {"jsonrpc": "2.0", "id": "call-1", "result": {}}\n\n'
    )
    assert response.read_count == 2


def test_sse_reader_ignores_an_empty_stream_primer_before_the_response() -> None:
    """Require the client to skip the valid empty event that starts a stream.

    :return: ``None`` after selecting the later JSON-RPC event.
    """

    class _PrimedResponse:
        """Yield the same empty primer and response sequence as the hosted route."""

        def __init__(self) -> None:
            """Initialize the finite simulated hosted event sequence."""
            self.lines = iter(
                (
                    b"id: stream:1\n",
                    b"data: \n",
                    b"\n",
                    b"id: stream:2\n",
                    b'data: {"jsonrpc": "2.0", "id": "call-1", "result": {}}\n',
                )
            )

        def readline(self) -> bytes:
            """Return one simulated server-sent event line.

            :return: Next encoded SSE line.
            """
            return next(self.lines)

    assert _read_sse_response_body(_PrimedResponse(), "call-1") == (
        'data: {"jsonrpc": "2.0", "id": "call-1", "result": {}}\n\n'
    )


def test_request_reader_cancels_its_absolute_deadline_after_a_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure persistent transports receive a full-request deadline guard.

    :param monkeypatch: Pytest patch helper used to replace HTTP and timer boundaries.
    :return: ``None`` after validating the deadline lifecycle.
    """

    class _Response:
        """Provide a finite non-streaming response for the HTTP context boundary."""

        status = 200
        headers: ClassVar[dict[str, str]] = {"content-type": "application/json"}

        def __enter__(self) -> Self:
            """Enter the synthetic HTTP context.

            :return: This response instance.
            """
            return self

        def __exit__(self, *_: object) -> None:
            """Exit the synthetic HTTP context.

            :return: ``None``.
            """

        def close(self) -> None:
            """Accept a timeout-driven close request.

            :return: ``None``.
            """

        def read(self) -> bytes:
            """Return a successful JSON-RPC payload.

            :return: Encoded JSON-RPC response.
            """
            return b'{"jsonrpc": "2.0", "id": "call-1", "result": {}}'

    class _Timer:
        """Record deadline lifecycle operations without starting a background thread."""

        instances: ClassVar[list[Self]] = []

        def __init__(self, _: float, __: object) -> None:
            """Initialize an unexpired synthetic timer.

            :param _: Requested deadline duration.
            :param __: Requested timeout action.
            """
            self.daemon = False
            self.started = False
            self.cancelled = False
            self.finished = type("_Finished", (), {"is_set": lambda self: False})()
            self.instances.append(self)

        def start(self) -> None:
            """Record that the deadline became active.

            :return: ``None``.
            """
            self.started = True

        def cancel(self) -> None:
            """Record that the deadline was cancelled after the response.

            :return: ``None``.
            """
            self.cancelled = True

    monkeypatch.setattr(
        remote_smoke.request, "urlopen", lambda *_args, **_kwargs: _Response()
    )
    monkeypatch.setattr(remote_smoke.threading, "Timer", _Timer)

    result = _send_request(
        RemoteMCPRequest(
            endpoint="https://example.test/mcp",
            request_id="call-1",
            method="tools/list",
            params={},
        )
    )

    assert result.status_code == 200
    assert len(_Timer.instances) == 1
    assert _Timer.instances[0].daemon is True
    assert _Timer.instances[0].started is True
    assert _Timer.instances[0].cancelled is True


def test_protocol_constant_uses_the_supported_streamable_version() -> None:
    """Keep remote initialization on the hosted transport's supported version.

    :return: ``None`` after checking the fixed MCP protocol version.
    """
    assert MCP_PROTOCOL_VERSION == "2025-11-25"


def test_explicit_allowlist_and_bounds_reject_discovered_name_inference() -> None:
    """Require fixed review membership rather than read-like name inference.

    :return: ``None`` after checking the canonical list and run limits.
    """
    approved_names = {case.tool_name for case in LIVE_SMOKE_ALLOWLIST}
    assert "videos_delete" not in approved_names
    assert MAX_REMOTE_TOOL_CALLS == len(LIVE_SMOKE_ALLOWLIST)
    assert MAX_REMOTE_POSTS == MAX_REMOTE_TOOL_CALLS + 2


def test_layer3_allowlist_is_fixed_to_bounded_api_key_public_reads() -> None:
    """Require the Layer 3 suite to exclude OAuth captions and search fan-out.

    :return: ``None`` after checking the reviewed immediate public-read subset.
    """
    approved_names = {case.tool_name for case in LAYER3_REMOTE_LIVE_SMOKE_ALLOWLIST}

    assert len(LAYER3_REMOTE_LIVE_SMOKE_ALLOWLIST) == 10
    assert "transcripts_getTranscript" not in approved_names
    assert "playlists_getVideoTranscripts" not in approved_names
    assert "channels_findCreators" not in approved_names
    assert "videos_getVideo" in approved_names
    assert "playlists_searchItems" in approved_names


def test_successful_result_must_agree_with_discovered_operation_identity() -> None:
    """Require discovered upstream metadata to match a selected result endpoint.

    :return: ``None`` after classifying an identity mismatch safely.
    """
    case = LIVE_SMOKE_ALLOWLIST[0]
    envelope = {
        "jsonrpc": "2.0",
        "id": "call",
        "result": {
            "content": [
                {"structuredContent": {"endpoint": case.expected_endpoint, "items": []}}
            ]
        },
    }

    assert (
        _safe_case_result(case, envelope, case.expected_endpoint)["outcome"]
        == "success"
    )
    assert _safe_case_result(case, envelope, "wrong.operation") == {
        "toolName": case.tool_name,
        "outcome": "actionable_failure",
        "category": "unexpected_endpoint",
    }
