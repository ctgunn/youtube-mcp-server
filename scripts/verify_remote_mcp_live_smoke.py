#!/usr/bin/env python3
"""Run a credential-gated, remote-only MCP read-only live smoke check."""

from __future__ import annotations

import json
import os
import sys
import threading
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.verify_youtube_live import LIVE_SMOKE_ALLOWLIST, LiveSmokeCase

MCP_PROTOCOL_VERSION = "2025-11-25"
MAX_REMOTE_TOOL_CALLS = len(LIVE_SMOKE_ALLOWLIST)
MAX_REMOTE_POSTS = MAX_REMOTE_TOOL_CALLS + 2
HTTP_TIMEOUT_SECONDS = 30.0


@dataclass(frozen=True)
class Layer3LiveSmokeCase:
    """Describe one reviewed public Layer 3 live-smoke invocation.

    :param tool_name: Explicit Layer 3 MCP tool selected for public-read verification.
    :param arguments: Bounded public fixture arguments for the selected tool.
    :param purpose: Reason the selected composed operation is safe to invoke.
    :param expected_fields: Required normalized result fields that prove the intended tool ran.
    """

    tool_name: str
    arguments: Mapping[str, object]
    purpose: str
    expected_fields: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate one bounded Layer 3 public-read case.

        :raises ValueError: If a reviewed case lacks a safe identity, input, or result shape.
        """
        if not isinstance(self.tool_name, str) or not self.tool_name.strip():
            raise ValueError("Layer 3 live smoke tool name is required")
        if not isinstance(self.arguments, Mapping):
            raise ValueError("Layer 3 live smoke arguments must be an object")
        if not isinstance(self.purpose, str) or not self.purpose.strip():
            raise ValueError("Layer 3 live smoke purpose is required")
        if not self.expected_fields or not all(
            isinstance(field, str) and field for field in self.expected_fields
        ):
            raise ValueError("Layer 3 live smoke expected fields are required")


RemoteLiveSmokeCase = LiveSmokeCase | Layer3LiveSmokeCase

LAYER3_REMOTE_LIVE_SMOKE_ALLOWLIST = (
    Layer3LiveSmokeCase(
        tool_name="videos_getVideo",
        arguments={"videoId": "dQw4w9WgXcQ"},
        purpose="Normalized public detail lookup for the documented public video fixture.",
        expected_fields=("videoId", "title"),
    ),
    Layer3LiveSmokeCase(
        tool_name="videos_getStatistics",
        arguments={"videoId": "dQw4w9WgXcQ"},
        purpose="Normalized public statistics lookup for the documented public video fixture.",
        expected_fields=("videoId", "statistics"),
    ),
    Layer3LiveSmokeCase(
        tool_name="channels_getChannel",
        arguments={"channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw"},
        purpose="Normalized public detail lookup for the documented Google Developers channel.",
        expected_fields=("channelId", "normalizedMetadata"),
    ),
    Layer3LiveSmokeCase(
        tool_name="channels_getChannels",
        arguments={
            "channelIds": ["UC_x5XG1OV2P6uZZ5FSM9Ttw"],
            "includeLatestUpload": False,
        },
        purpose="Bounded public batch lookup without optional latest-upload fan-out.",
        expected_fields=("requestedChannelIds", "results", "summary"),
    ),
    Layer3LiveSmokeCase(
        tool_name="channels_getStatistics",
        arguments={"channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw"},
        purpose="Normalized public statistics lookup for the documented Google Developers channel.",
        expected_fields=("channelId", "statistics"),
    ),
    Layer3LiveSmokeCase(
        tool_name="channels_listVideos",
        arguments={"channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw", "maxResults": 1},
        purpose="Bounded public uploads-collection lookup for the documented Google Developers channel.",
        expected_fields=("channelId", "items"),
    ),
    Layer3LiveSmokeCase(
        tool_name="channels_listPlaylists",
        arguments={"channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw", "maxResults": 1},
        purpose="Bounded public playlist lookup for the documented Google Developers channel.",
        expected_fields=("channelId", "items"),
    ),
    Layer3LiveSmokeCase(
        tool_name="playlists_getPlaylist",
        arguments={"playlistId": "UU_x5XG1OV2P6uZZ5FSM9Ttw"},
        purpose="Normalized public uploads-playlist detail lookup for the documented channel fixture.",
        expected_fields=("playlistId", "title"),
    ),
    Layer3LiveSmokeCase(
        tool_name="playlists_getPlaylistItems",
        arguments={"playlistId": "UU_x5XG1OV2P6uZZ5FSM9Ttw", "maxResults": 1},
        purpose="Bounded public uploads-playlist item lookup for the documented channel fixture.",
        expected_fields=("playlistId", "items"),
    ),
    Layer3LiveSmokeCase(
        tool_name="playlists_searchItems",
        arguments={
            "playlistId": "UU_x5XG1OV2P6uZZ5FSM9Ttw",
            "query": "Google",
            "maxResults": 1,
        },
        purpose="Bounded literal phrase search over the documented public uploads playlist.",
        expected_fields=("playlistId", "items", "query"),
    ),
)


class RemoteSmokeError(RuntimeError):
    """Represent a fixed, credential-safe remote smoke failure.

    :param safe_message: Approved operator-facing failure text without diagnostics.
    :param category: Stable credential-safe classification for a failed operation.
    """

    def __init__(
        self, safe_message: str, category: str = "remote_smoke_failure"
    ) -> None:
        """Store the fixed safe failure fields.

        :param safe_message: Approved operator-facing failure text without diagnostics.
        :param category: Stable credential-safe classification for a failed operation.
        """
        super().__init__(safe_message)
        self.safe_message = safe_message
        self.category = category


@dataclass(frozen=True)
class RemoteSmokeSettings:
    """Describe validated operator inputs retained only for one smoke run.

    :param endpoint: Remote public MCP URL with no query, fragment, or user info.
    :param auth_token: Optional bearer token required by the selected endpoint.
    :param auth_required: Whether preflight must require a bearer token.
    """

    endpoint: str
    auth_token: str | None
    auth_required: bool


@dataclass(frozen=True)
class RemoteMCPRequest:
    """Describe one internal remote public-transport request.

    :param endpoint: Validated remote MCP URL used only by the HTTP boundary.
    :param request_id: Safe JSON-RPC request identifier.
    :param method: JSON-RPC MCP method name.
    :param params: Object-shaped JSON-RPC method parameters.
    :param session_id: Optional session continuation value retained in memory only.
    :param protocol_version: Optional negotiated protocol version for continuation.
    :param auth_token: Optional bearer credential retained in memory only.
    """

    endpoint: str
    request_id: str
    method: str
    params: Mapping[str, object]
    session_id: str | None = None
    protocol_version: str | None = None
    auth_token: str | None = None


@dataclass(frozen=True)
class RemoteHTTPResponse:
    """Hold one unreported HTTP response long enough to normalize MCP data.

    :param status_code: HTTP status code returned by the remote endpoint.
    :param headers: Lowercase response headers used only for session/protocol handling.
    :param body: Raw response body retained only in memory for immediate parsing.
    """

    status_code: int
    headers: Mapping[str, str]
    body: str


RemoteRequester = Callable[[RemoteMCPRequest], RemoteHTTPResponse]


def _preflight(values: Mapping[str, str]) -> RemoteSmokeSettings:
    """Validate explicit authorization before constructing a remote request.

    :param values: Candidate environment values for one operator run.
    :return: Validated endpoint and optional bearer settings.
    :raises RemoteSmokeError: If opt-in, endpoint, or declared authentication is invalid.
    """
    if values.get("RUN_REMOTE_MCP_LIVE_SMOKE") != "1":
        raise RemoteSmokeError(
            "set RUN_REMOTE_MCP_LIVE_SMOKE=1 to authorize the remote MCP live smoke check",
            "live_smoke_not_authorized",
        )
    endpoint = str(values.get("REMOTE_MCP_URL") or "").strip()
    if not endpoint:
        raise RemoteSmokeError(
            "REMOTE_MCP_URL is required for the remote MCP live smoke check",
            "remote_endpoint_missing",
        )
    parsed = urlparse(endpoint)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise RemoteSmokeError(
            "REMOTE_MCP_URL must be a valid remote MCP URL without credentials or query data",
            "remote_endpoint_invalid",
        )
    auth_required = values.get("REMOTE_MCP_AUTH_REQUIRED") == "1"
    auth_token = str(values.get("MCP_AUTH_TOKEN") or "").strip() or None
    if auth_required and auth_token is None:
        raise RemoteSmokeError(
            "MCP_AUTH_TOKEN is required for the selected remote MCP endpoint",
            "remote_authentication_missing",
        )
    return RemoteSmokeSettings(
        endpoint=endpoint,
        auth_token=auth_token,
        auth_required=auth_required,
    )


def _request_headers(remote_request: RemoteMCPRequest) -> dict[str, str]:
    """Build required private HTTP headers for one MCP request.

    :param remote_request: In-memory request details for the remote MCP endpoint.
    :return: Request headers; callers must never serialize or report these values.
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if remote_request.auth_token:
        headers["Authorization"] = f"Bearer {remote_request.auth_token}"
    if remote_request.session_id:
        headers["MCP-Session-Id"] = remote_request.session_id
    if remote_request.protocol_version:
        headers["MCP-Protocol-Version"] = remote_request.protocol_version
    return headers


def _send_request(remote_request: RemoteMCPRequest) -> RemoteHTTPResponse:
    """POST one JSON-RPC request to the configured remote MCP endpoint.

    :param remote_request: Validated request to send through the public transport.
    :return: Unreported response retained only for immediate protocol parsing.
    :raises RemoteSmokeError: If the HTTP request cannot complete safely.
    """
    payload = {
        "jsonrpc": "2.0",
        "id": remote_request.request_id,
        "method": remote_request.method,
        "params": dict(remote_request.params),
    }
    encoded = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        remote_request.endpoint,
        data=encoded,
        headers=_request_headers(remote_request),
        method="POST",
    )
    try:
        with request.urlopen(
            http_request, timeout=HTTP_TIMEOUT_SECONDS
        ) as http_response:
            headers = {
                name.lower(): value for name, value in http_response.headers.items()
            }
            deadline = threading.Timer(HTTP_TIMEOUT_SECONDS, http_response.close)
            deadline.daemon = True
            deadline.start()
            try:
                if (
                    "text/event-stream"
                    in str(headers.get("content-type") or "").lower()
                ):
                    body = _read_sse_response_body(
                        http_response, remote_request.request_id
                    )
                else:
                    body = http_response.read().decode("utf-8")
            except (OSError, TimeoutError, ValueError) as exc:
                if deadline.finished.is_set():
                    raise RemoteSmokeError(
                        "remote MCP request timed out", "remote_timeout"
                    ) from exc
                raise
            finally:
                deadline.cancel()
            return RemoteHTTPResponse(
                status_code=http_response.status,
                headers=headers,
                body=body,
            )
    except error.HTTPError as exc:
        return RemoteHTTPResponse(
            status_code=exc.code,
            headers={name.lower(): value for name, value in exc.headers.items()},
            body=exc.read().decode("utf-8"),
        )
    except TimeoutError as exc:
        raise RemoteSmokeError(
            "remote MCP request timed out", "remote_timeout"
        ) from exc
    except error.URLError as exc:
        raise RemoteSmokeError(
            "remote MCP request could not be completed", "remote_transport_failure"
        ) from exc
    except OSError as exc:
        raise RemoteSmokeError(
            "remote MCP request could not be completed", "remote_transport_failure"
        ) from exc


def _read_sse_response_body(http_response: Any, request_id: str) -> str:
    """Read only the matching MCP event instead of waiting for an SSE stream to close.

    :param http_response: Open HTTP response that yields byte lines from an SSE body.
    :param request_id: JSON-RPC response identifier required for the current call.
    :return: Minimal SSE data body containing the matching event, or all malformed data.
    :raises RemoteSmokeError: If the event stream cannot be read within the HTTP bound.
    """
    try:
        while True:
            raw_line = http_response.readline()
            if not raw_line:
                return ""
            line = raw_line.decode("utf-8")
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if not data:
                continue
            try:
                candidate = json.loads(data)
            except (TypeError, ValueError, json.JSONDecodeError):
                return f"data: {data}\n\n"
            if isinstance(candidate, dict) and str(candidate.get("id")) == request_id:
                return f"data: {data}\n\n"
    except (OSError, TimeoutError) as exc:
        raise RemoteSmokeError(
            "remote MCP request timed out", "remote_timeout"
        ) from exc


def _http_failure_category(status_code: int) -> str:
    """Map an HTTP failure status to a stable safe category.

    :param status_code: HTTP status returned by the remote endpoint.
    :return: Credential-safe category without response text or headers.
    """
    if status_code in {401, 403}:
        return "remote_authentication_failed"
    if status_code == 404:
        return "remote_session_or_endpoint_missing"
    return "remote_http_failure"


def _parse_protocol_response(
    response: RemoteHTTPResponse, request_id: str
) -> dict[str, object]:
    """Normalize direct JSON or streamed JSON-RPC output for one request.

    :param response: Immediate raw HTTP response retained only for parsing.
    :param request_id: Expected JSON-RPC identifier for the response envelope.
    :return: Matching JSON-RPC envelope with no HTTP headers or raw body included.
    :raises RemoteSmokeError: If the endpoint returns an unusable response.
    """
    if response.status_code >= 400:
        raise RemoteSmokeError(
            "remote MCP request returned an HTTP failure",
            _http_failure_category(response.status_code),
        )
    content_type = str(response.headers.get("content-type") or "").lower()
    candidates: list[object] = []
    try:
        if "text/event-stream" in content_type:
            for line in response.body.splitlines():
                if not line.startswith("data:"):
                    continue
                candidates.append(json.loads(line[5:].strip()))
        else:
            candidates.append(json.loads(response.body))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RemoteSmokeError(
            "remote MCP response did not contain a valid MCP response",
            "remote_protocol_failure",
        ) from exc
    for candidate in candidates:
        if isinstance(candidate, dict) and str(candidate.get("id")) == request_id:
            return candidate
    raise RemoteSmokeError(
        "remote MCP response did not contain a valid MCP response",
        "remote_protocol_failure",
    )


def _initialize_params() -> dict[str, object]:
    """Build safe client initialization parameters for the public MCP route.

    :return: Fixed JSON-RPC initialization object with no operator data.
    """
    return {
        "protocolVersion": MCP_PROTOCOL_VERSION,
        "clientInfo": {"name": "youtube-mcp-remote-live-smoke", "version": "1.0"},
        "capabilities": {},
    }


def _require_successful_initialize(envelope: Mapping[str, object]) -> None:
    """Require a successful initialize response before session continuation.

    :param envelope: Parsed initialization JSON-RPC envelope.
    :return: ``None`` after validating the declared initialization result.
    :raises RemoteSmokeError: If the remote endpoint rejects initialization.
    """
    result = envelope.get("result")
    if (
        "error" in envelope
        or not isinstance(result, Mapping)
        or "capabilities" not in result
    ):
        raise RemoteSmokeError(
            "remote MCP initialization failed", "remote_initialize_failed"
        )


def _discover_tools(envelope: Mapping[str, object]) -> dict[str, str | None]:
    """Extract unique tool names and optional upstream identities from discovery.

    :param envelope: Parsed JSON-RPC `tools/list` response envelope.
    :return: Mapping of discovered names to optional upstream operation keys.
    :raises RemoteSmokeError: If remote discovery is unavailable or malformed.
    """
    result = envelope.get("result")
    tools = result.get("tools") if isinstance(result, Mapping) else None
    if "error" in envelope or not isinstance(tools, list):
        raise RemoteSmokeError(
            "remote MCP catalog discovery failed", "remote_discovery_failed"
        )
    discovered: dict[str, str | None] = {}
    for tool in tools:
        if not isinstance(tool, Mapping):
            raise RemoteSmokeError(
                "remote MCP catalog discovery failed", "remote_discovery_failed"
            )
        name = tool.get("name")
        if not isinstance(name, str) or not name or name in discovered:
            raise RemoteSmokeError(
                "remote MCP catalog discovery failed", "remote_discovery_failed"
            )
        metadata = tool.get("metadata")
        upstream = metadata.get("upstream") if isinstance(metadata, Mapping) else None
        operation_key = (
            upstream.get("operationKey") if isinstance(upstream, Mapping) else None
        )
        discovered[name] = (
            operation_key if isinstance(operation_key, str) and operation_key else None
        )
    if not discovered:
        raise RemoteSmokeError(
            "remote MCP catalog discovery failed", "remote_discovery_failed"
        )
    return discovered


def _comment_parent_id(envelope: Mapping[str, object]) -> str:
    """Read one approved public comment parent identifier without reporting it.

    :param envelope: Successful source-tool response retained only in memory.
    :return: Bounded public parent identifier for the approved comments fixture.
    :raises RemoteSmokeError: If the source fixture has no usable public comment.
    """
    result = envelope.get("result")
    content = result.get("content") if isinstance(result, Mapping) else None
    first_content = content[0] if isinstance(content, list) and content else None
    structured = (
        first_content.get("structuredContent")
        if isinstance(first_content, Mapping)
        else None
    )
    items = structured.get("items") if isinstance(structured, Mapping) else None
    first_item = items[0] if isinstance(items, list) and items else None
    snippet = first_item.get("snippet") if isinstance(first_item, Mapping) else None
    top_comment = (
        snippet.get("topLevelComment") if isinstance(snippet, Mapping) else None
    )
    parent_id = top_comment.get("id") if isinstance(top_comment, Mapping) else None
    if not isinstance(parent_id, str) or not parent_id:
        raise RemoteSmokeError(
            "approved public fixture source is unavailable",
            "fixture_source_unavailable",
        )
    return parent_id


def _case_arguments(
    case: RemoteLiveSmokeCase, prior_responses: Mapping[str, Mapping[str, object]]
) -> dict[str, object]:
    """Build one reviewed call input without exposing fixture-derived values.

    :param case: Explicit reviewed allowlist entry selected from discovery.
    :param prior_responses: Earlier selected response envelopes retained only in memory.
    :return: Object arguments for the selected public MCP call.
    :raises RemoteSmokeError: If an approved dependent fixture cannot be used safely.
    """
    arguments = dict(case.arguments)
    if not isinstance(case, LiveSmokeCase) or case.fixture_source_tool is None:
        return arguments
    source = prior_responses.get(case.fixture_source_tool)
    if source is None or case.tool_name != "comments_list":
        raise RemoteSmokeError(
            "approved public fixture source is unavailable",
            "fixture_source_unavailable",
        )
    arguments["parentId"] = _comment_parent_id(source)
    return arguments


def _safe_case_result(
    case: RemoteLiveSmokeCase,
    envelope: Mapping[str, object],
    discovered_operation_key: str | None,
) -> dict[str, object]:
    """Classify one selected tool response without copying remote payload content.

    :param case: Reviewed allowlist entry used for the remote call.
    :param envelope: Parsed JSON-RPC envelope retained only for immediate classification.
    :param discovered_operation_key: Optional upstream identity published at discovery.
    :return: Credential-safe terminal per-tool report entry.
    """
    error_payload = envelope.get("error")
    if isinstance(error_payload, Mapping):
        details = error_payload.get("data")
        category = details.get("category") if isinstance(details, Mapping) else None
        return {
            "toolName": case.tool_name,
            "outcome": "safe_availability_error",
            "category": category
            if isinstance(category, str) and category
            else "remote_tool_error",
        }
    result = envelope.get("result")
    content = result.get("content") if isinstance(result, Mapping) else None
    first_content = content[0] if isinstance(content, list) and content else None
    structured = (
        first_content.get("structuredContent")
        if isinstance(first_content, Mapping)
        else None
    )
    if not isinstance(structured, Mapping):
        return {
            "toolName": case.tool_name,
            "outcome": "actionable_failure",
            "category": "remote_result_invalid",
        }
    if isinstance(case, Layer3LiveSmokeCase):
        if any(field not in structured for field in case.expected_fields):
            return {
                "toolName": case.tool_name,
                "outcome": "actionable_failure",
                "category": "remote_result_invalid",
            }
        layer3_report: dict[str, object] = {
            "toolName": case.tool_name,
            "outcome": "success",
            "resultType": "normalized",
        }
        items = structured.get("items")
        if isinstance(items, list):
            layer3_report["itemCount"] = len(items)
        return layer3_report
    endpoint = structured.get("endpoint")
    if endpoint != case.expected_endpoint or (
        discovered_operation_key is not None and endpoint != discovered_operation_key
    ):
        return {
            "toolName": case.tool_name,
            "outcome": "actionable_failure",
            "category": "unexpected_endpoint",
        }
    report: dict[str, object] = {
        "toolName": case.tool_name,
        "outcome": "success",
        "endpoint": endpoint,
    }
    items = structured.get("items")
    if isinstance(items, list):
        report["itemCount"] = len(items)
    return report


def _failure_result(case: RemoteLiveSmokeCase, category: str) -> dict[str, object]:
    """Create one safe actionable-failure report without exception details.

    :param case: Selected reviewed allowlist entry that did not complete.
    :param category: Stable safe failure category.
    :return: Credential-safe terminal report for the selected tool.
    """
    return {
        "toolName": case.tool_name,
        "outcome": "actionable_failure",
        "category": category,
    }


def _safe_console_line(result: Mapping[str, object]) -> str:
    """Format one selected result as a compact credential-safe terminal line.

    :param result: Selected-tool evidence returned by :func:`run_remote_live_smoke`.
    :return: One operator-facing line with only safe tool evidence.
    """
    tool_name = result.get("toolName")
    outcome = result.get("outcome")
    if not isinstance(tool_name, str) or not isinstance(outcome, str):
        return "  FAIL  unknown tool  category=remote_smoke_failure"
    if outcome == "success":
        endpoint = result.get("endpoint")
        item_count = result.get("itemCount")
        fields = [f"  PASS  {tool_name}"]
        if isinstance(endpoint, str) and endpoint:
            fields.append(f"endpoint={endpoint}")
        result_type = result.get("resultType")
        if isinstance(result_type, str) and result_type:
            fields.append(f"result={result_type}")
        if isinstance(item_count, int) and item_count >= 0:
            fields.append(f"items={item_count}")
        return "  |  ".join(fields)
    category = result.get("category")
    safe_category = (
        category if isinstance(category, str) and category else "remote_smoke_failure"
    )
    return f"  FAIL  {tool_name}  |  outcome={outcome}  |  category={safe_category}"


def _print_report(
    report: Mapping[str, object], stream: Any, title: str = "Remote MCP live smoke"
) -> None:
    """Print a concise human-readable summary without raw remote payloads.

    :param report: Credential-safe report returned by :func:`run_remote_live_smoke`.
    :param stream: Text stream that receives the terminal report.
    :param title: Safe suite label displayed at the top of the terminal report.
    :return: ``None`` after writing selected evidence and aggregate bounds.
    """
    selected = report.get("selected")
    excluded = report.get("excluded")
    selected_results = selected if isinstance(selected, list) else []
    excluded_names = excluded if isinstance(excluded, list) else []
    successful_count = sum(
        1
        for result in selected_results
        if isinstance(result, Mapping) and result.get("outcome") == "success"
    )
    status = report.get("status")
    heading = "PASS" if status == "passed" else "COMPLETED WITH SAFE ERRORS"

    print(f"{title}: {heading}", file=stream)
    print(file=stream)
    print("Approved public-read tools", file=stream)
    for result in selected_results:
        if isinstance(result, Mapping):
            print(_safe_console_line(result), file=stream)
    print(file=stream)
    print("Summary", file=stream)
    print(
        f"  Passed: {successful_count}/{len(selected_results)} approved tool(s)",
        file=stream,
    )
    print(
        f"  Excluded: {len(excluded_names)} non-approved tool(s) (not invoked)",
        file=stream,
    )
    request_count = report.get("requestCount")
    request_limit = report.get("requestLimit")
    if isinstance(request_count, int) and isinstance(request_limit, int):
        print(f"  Requests: {request_count}/{request_limit} allowed", file=stream)


def run_remote_live_smoke(
    environment: Mapping[str, str] | None = None,
    *,
    requester: RemoteRequester = _send_request,
    allowlist: tuple[RemoteLiveSmokeCase, ...] = LIVE_SMOKE_ALLOWLIST,
) -> dict[str, object]:
    """Run the authorized allowlist through a running remote MCP endpoint.

    :param environment: Optional operator environment mapping, primarily for tests.
    :param requester: Injectable public HTTP requester used by deterministic tests.
    :param allowlist: Reviewed fixed public-read cases for the selected manual suite.
    :return: Credential-safe selected/excluded report and bounded request counts.
    :raises RemoteSmokeError: If preflight, initialization, or discovery cannot proceed.
    """
    values = dict(os.environ if environment is None else environment)
    settings = _preflight(values)
    if not allowlist:
        raise RemoteSmokeError(
            "remote MCP smoke allowlist is empty", "remote_allowlist_empty"
        )
    max_remote_tool_calls = len(allowlist)
    max_remote_posts = max_remote_tool_calls + 2
    request_count = 0

    def submit(
        request_id: str,
        method: str,
        params: Mapping[str, object],
        *,
        session_id: str | None = None,
        protocol_version: str | None = None,
    ) -> tuple[RemoteHTTPResponse, dict[str, object]]:
        """Send one bounded remote request and normalize its MCP envelope.

        :param request_id: Safe JSON-RPC identifier for one request.
        :param method: Public MCP method to call.
        :param params: Object-shaped method parameters.
        :param session_id: Optional retained remote continuation identifier.
        :param protocol_version: Optional retained negotiated protocol version.
        :return: Immediate HTTP response and parsed JSON-RPC response envelope.
        :raises RemoteSmokeError: If request bounds or remote protocol handling fail.
        """
        nonlocal request_count
        if request_count >= max_remote_posts:
            raise RemoteSmokeError(
                "remote MCP smoke request bound reached", "bound_reached"
            )
        request_count += 1
        response = requester(
            RemoteMCPRequest(
                endpoint=settings.endpoint,
                request_id=request_id,
                method=method,
                params=params,
                session_id=session_id,
                protocol_version=protocol_version,
                auth_token=settings.auth_token,
            )
        )
        if not isinstance(response, RemoteHTTPResponse):
            raise RemoteSmokeError(
                "remote MCP requester returned an invalid response",
                "remote_protocol_failure",
            )
        return response, _parse_protocol_response(response, request_id)

    initialize_response, initialize = submit(
        "remote-live-smoke-initialize", "initialize", _initialize_params()
    )
    _require_successful_initialize(initialize)
    initialize_result = initialize.get("result")
    session_id = (
        str(initialize_response.headers.get("mcp-session-id") or "").strip() or None
    )
    protocol_version = (
        str(initialize_response.headers.get("mcp-protocol-version") or "").strip()
        or None
    )
    if isinstance(initialize_result, Mapping):
        protocol_candidate = initialize_result.get("protocolVersion")
        if (
            protocol_version is None
            and isinstance(protocol_candidate, str)
            and protocol_candidate
        ):
            protocol_version = protocol_candidate
    if session_id is None:
        raise RemoteSmokeError(
            "remote MCP initialization did not provide a usable session",
            "remote_session_missing",
        )
    if protocol_version is None:
        raise RemoteSmokeError(
            "remote MCP initialization did not provide a usable protocol version",
            "remote_protocol_failure",
        )

    _, discovery = submit(
        "remote-live-smoke-list",
        "tools/list",
        {},
        session_id=session_id,
        protocol_version=protocol_version,
    )
    discovered = _discover_tools(discovery)
    selected_cases = tuple(case for case in allowlist if case.tool_name in discovered)
    if not selected_cases:
        raise RemoteSmokeError(
            "remote MCP catalog contains no approved live smoke tools",
            "remote_allowlist_empty",
        )
    selected_names = {case.tool_name for case in selected_cases}
    excluded = sorted(name for name in discovered if name not in selected_names)
    selected_results: list[dict[str, object]] = []
    prior_responses: dict[str, Mapping[str, object]] = {}
    tool_call_count = 0
    for case in selected_cases:
        if (
            tool_call_count >= max_remote_tool_calls
            or request_count >= max_remote_posts
        ):
            selected_results.append(
                {
                    "toolName": case.tool_name,
                    "outcome": "bound_reached",
                    "category": "bound_reached",
                }
            )
            continue
        try:
            arguments = _case_arguments(case, prior_responses)
            _, envelope = submit(
                f"remote-live-smoke-call-{case.tool_name}",
                "tools/call",
                {"name": case.tool_name, "arguments": arguments},
                session_id=session_id,
                protocol_version=protocol_version,
            )
            tool_call_count += 1
            prior_responses[case.tool_name] = envelope
            selected_results.append(
                _safe_case_result(case, envelope, discovered[case.tool_name])
            )
        except RemoteSmokeError as exc:
            selected_results.append(_failure_result(case, exc.category))

    return {
        "status": "passed"
        if all(result.get("outcome") == "success" for result in selected_results)
        else "completed_with_safe_errors",
        "selected": selected_results,
        "excluded": excluded,
        "requestCount": request_count,
        "requestLimit": max_remote_posts,
        "toolCallCount": tool_call_count,
        "toolCallLimit": max_remote_tool_calls,
    }


def run_remote_layer3_live_smoke(
    environment: Mapping[str, str] | None = None,
    *,
    requester: RemoteRequester = _send_request,
) -> dict[str, object]:
    """Run only the reviewed API-key-compatible Layer 3 public-read cases.

    :param environment: Optional operator environment mapping, primarily for tests.
    :param requester: Injectable public HTTP requester used by deterministic tests.
    :return: Credential-safe selected/excluded Layer 3 report with bounded counts.
    :raises RemoteSmokeError: If preflight, discovery, or a required protocol step fails.
    """
    return run_remote_live_smoke(
        environment,
        requester=requester,
        allowlist=LAYER3_REMOTE_LIVE_SMOKE_ALLOWLIST,
    )


def run_remote_layer2_live_smoke(
    environment: Mapping[str, str] | None = None,
    *,
    requester: RemoteRequester = _send_request,
) -> dict[str, object]:
    """Run only the reviewed Layer 2 API-key public-read cases.

    :param environment: Optional operator environment mapping, primarily for tests.
    :param requester: Injectable public HTTP requester used by deterministic tests.
    :return: Credential-safe selected/excluded Layer 2 report with bounded counts.
    :raises RemoteSmokeError: If preflight, discovery, or a required protocol step fails.
    """
    return run_remote_live_smoke(environment, requester=requester)


def run_all_remote_live_smoke(
    environment: Mapping[str, str] | None = None,
    *,
    requester: RemoteRequester = _send_request,
) -> dict[str, object]:
    """Run Layer 2 and Layer 3 smoke suites in separate bounded sessions.

    :param environment: Optional operator environment mapping, primarily for tests.
    :param requester: Injectable public HTTP requester used by deterministic tests.
    :return: Aggregate credential-safe reports for both independently bounded suites.
    :raises RemoteSmokeError: If a shared preflight or required protocol step fails.
    """
    layer2 = run_remote_layer2_live_smoke(environment, requester=requester)
    layer3 = run_remote_layer3_live_smoke(environment, requester=requester)
    return {
        "status": "passed"
        if layer2.get("status") == "passed" and layer3.get("status") == "passed"
        else "completed_with_safe_errors",
        "layer2": layer2,
        "layer3": layer3,
    }


def _success_count(report: Mapping[str, object]) -> tuple[int, int]:
    """Return successful and selected counts from one credential-safe report.

    :param report: Report returned by a bounded Layer 2 or Layer 3 suite.
    :return: Successful count followed by selected-tool count.
    """
    selected = report.get("selected")
    selected_results = selected if isinstance(selected, list) else []
    successful_count = sum(
        1
        for result in selected_results
        if isinstance(result, Mapping) and result.get("outcome") == "success"
    )
    return successful_count, len(selected_results)


def _print_combined_report(report: Mapping[str, object], stream: Any) -> None:
    """Print two suite reports followed by one aggregate bounded summary.

    :param report: Aggregate report returned by :func:`run_all_remote_live_smoke`.
    :param stream: Text stream that receives the terminal report.
    :return: ``None`` after writing both suite reports and their combined counts.
    """
    layer2 = report.get("layer2")
    layer3 = report.get("layer3")
    if not isinstance(layer2, Mapping) or not isinstance(layer3, Mapping):
        print("Remote MCP live smoke: COMPLETED WITH SAFE ERRORS", file=stream)
        print("Reason: remote_smoke_failure", file=stream)
        return
    _print_report(layer2, stream, "Remote MCP Layer 2 live smoke")
    print(file=stream)
    _print_report(layer3, stream, "Remote MCP Layer 3 live smoke")
    layer2_success, layer2_total = _success_count(layer2)
    layer3_success, layer3_total = _success_count(layer3)
    layer2_requests = layer2.get("requestCount")
    layer2_limit = layer2.get("requestLimit")
    layer3_requests = layer3.get("requestCount")
    layer3_limit = layer3.get("requestLimit")
    print(file=stream)
    print("Combined summary", file=stream)
    print(
        f"  Passed: {layer2_success + layer3_success}/{layer2_total + layer3_total} approved tool(s)",
        file=stream,
    )
    if all(
        isinstance(value, int)
        for value in (layer2_requests, layer2_limit, layer3_requests, layer3_limit)
    ):
        print(
            f"  Requests: {layer2_requests + layer3_requests}/{layer2_limit + layer3_limit} allowed",
            file=stream,
        )


def main(arguments: list[str] | None = None) -> int:
    """Run remote smoke and emit only human-readable credential-safe evidence.

    :param arguments: Optional command arguments, supplied by tests or the shell.
    :return: Process exit code for the manual operator command.
    """
    selected_arguments = [] if arguments is None else arguments
    title = "Remote MCP live smoke"
    if selected_arguments == ["--layer3"]:
        title = "Remote MCP Layer 3 live smoke"
    elif selected_arguments == ["--layer2"]:
        title = "Remote MCP Layer 2 live smoke"
    elif selected_arguments == ["--all"]:
        title = "Remote MCP live smoke"
    elif selected_arguments not in ([], ["--layer2"]):
        print("Remote MCP live smoke: FAILED", file=sys.stderr)
        print("Reason: remote_smoke_failure", file=sys.stderr)
        return 1
    try:
        if selected_arguments == ["--all"]:
            combined_report = run_all_remote_live_smoke()
            output = (
                sys.stdout if combined_report.get("status") == "passed" else sys.stderr
            )
            _print_combined_report(combined_report, output)
            return 0 if combined_report.get("status") == "passed" else 1
        report = (
            run_remote_layer3_live_smoke()
            if selected_arguments == ["--layer3"]
            else (
                run_remote_layer2_live_smoke()
                if selected_arguments == ["--layer2"]
                else run_remote_live_smoke()
            )
        )
    except RemoteSmokeError as exc:
        print(f"{title}: FAILED", file=sys.stderr)
        print(f"Reason: {exc.category}", file=sys.stderr)
        return 1
    except Exception:  # noqa: BLE001 - final CLI boundary must not reveal diagnostics.
        print(f"{title}: FAILED", file=sys.stderr)
        print("Reason: remote_smoke_failure", file=sys.stderr)
        return 1
    output = sys.stdout if report.get("status") == "passed" else sys.stderr
    _print_report(report, output, title)
    return 0 if report.get("status") == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
