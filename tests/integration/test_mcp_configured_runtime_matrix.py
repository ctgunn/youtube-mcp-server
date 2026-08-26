"""Foundational public-route tests for configured YouTube runtime verification."""

from __future__ import annotations

import socket
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Self
from urllib.parse import urlsplit

import pytest

from mcp_server.app import create_app

GENERIC_TOOL_NAMES = frozenset(
    {"fetch", "search", "server_info", "server_list_tools", "server_ping"}
)
EXPECTED_API_REQUESTS = {
    "activities_list": ("/youtube/v3/activities", "GET"),
    "channels_list": ("/youtube/v3/channels", "GET"),
    "comments_list": ("/youtube/v3/comments", "GET"),
    "commentThreads_list": ("/youtube/v3/commentThreads", "GET"),
    "guideCategories_list": ("/youtube/v3/guideCategories", "GET"),
    "i18nLanguages_list": ("/youtube/v3/i18nLanguages", "GET"),
    "playlistItems_list": ("/youtube/v3/playlistItems", "GET"),
    "playlists_list": ("/youtube/v3/playlists", "GET"),
    "search_list": ("/youtube/v3/search", "GET"),
    "subscriptions_list": ("/youtube/v3/subscriptions", "GET"),
    "videoAbuseReportReasons_list": ("/youtube/v3/videoAbuseReportReasons", "GET"),
    "videoCategories_list": ("/youtube/v3/videoCategories", "GET"),
    "videos_list": ("/youtube/v3/videos", "GET"),
}


@dataclass(frozen=True)
class CapabilityMatrixCase:
    """Describe one reviewable configured-runtime capability verification case.

    :param family: Discovery-derived YouTube family covered by the case.
    :param tool_name: Public MCP tool invoked through the route.
    :param arguments: Safe object arguments that select the capability path.
    :param configured_capability: Credential state used to compose the runtime.
    :param expected_outcome: Reviewed expected capability result.
    :param purpose: Reviewer-facing reason the case is safe and representative.
    """

    family: str
    tool_name: str
    arguments: Mapping[str, object]
    configured_capability: str
    expected_outcome: str
    purpose: str
    expected_error_category: str | None = None

    def __post_init__(self) -> None:
        """Validate the minimum safe fields required by all matrix cases.

        :raises ValueError: If an identity, capability classification, purpose, or
            object-shaped argument mapping is invalid.
        """
        for field_name in (
            "family",
            "tool_name",
            "configured_capability",
            "expected_outcome",
            "purpose",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} is required")
        if not isinstance(self.arguments, Mapping):
            raise ValueError("arguments must be an object mapping")
        if (
            self.expected_outcome == "api_key_executable"
            and self.expected_error_category is not None
        ):
            raise ValueError("successful cases cannot declare an error category")
        if (
            self.expected_outcome != "api_key_executable"
            and not self.expected_error_category
        ):
            raise ValueError("unavailable cases require an error category")


@dataclass(frozen=True)
class ControlledRequestRecord:
    """Store credential-safe evidence of one configured live-runtime request.

    :param family: Discovery-derived family for the selected matrix case.
    :param tool_name: Public MCP tool that constructed the request.
    :param path_shape: Upstream request path without URL query data.
    :param method: Intended upstream HTTP method.
    :param credential_mode: Credential class selected without its value.
    :param timeout_seconds: Bound runtime timeout applied to the request.
    """

    family: str
    tool_name: str
    path_shape: str
    method: str
    credential_mode: str
    timeout_seconds: float


def _safe_request_record(
    matrix_case: CapabilityMatrixCase,
    request: object,
    timeout: object,
) -> ControlledRequestRecord:
    """Derive a non-secret record from an executor-built request.

    :param matrix_case: Case that selected the request's tool and family.
    :param request: Configured executor request object.
    :param timeout: Runtime timeout value supplied to the controlled opener.
    :return: Credential-safe controlled request record.
    :raises AssertionError: If the executor request lacks required safe fields.
    """
    full_url = getattr(request, "full_url", None)
    method = getattr(request, "method", None)
    headers = getattr(request, "headers", None)
    assert isinstance(full_url, str) and full_url, "controlled request URL is required"
    assert isinstance(method, str) and method, "controlled request method is required"
    assert isinstance(headers, Mapping), "controlled request headers are required"
    credential_mode = (
        "oauth" if any(key.lower() == "authorization" for key in headers) else "api_key"
    )
    assert isinstance(timeout, (float, int)) and timeout > 0, (
        "controlled request timeout is required"
    )
    return ControlledRequestRecord(
        family=matrix_case.family,
        tool_name=matrix_case.tool_name,
        path_shape=urlsplit(full_url).path,
        method=method,
        credential_mode=credential_mode,
        timeout_seconds=float(timeout),
    )


def _validate_controlled_records(records: tuple[object, ...] | list[object]) -> None:
    """Reject raw or secret-bearing data from controlled request evidence.

    :param records: Candidate controlled request records for one matrix call.
    :return: ``None`` after proving all records use the safe record type.
    :raises AssertionError: If a record is raw, malformed, or contains unsafe text.
    """
    unsafe_markers = ("matrix-sentinel", "authorization", "token", "key=", "?", "body")
    for record in records:
        assert isinstance(record, ControlledRequestRecord), (
            "unsafe controlled request record"
        )
        rendered = repr(record).lower()
        assert not any(marker in rendered for marker in unsafe_markers), (
            "unsafe controlled request record"
        )


MATRIX_CASES = (
    CapabilityMatrixCase(
        "activities",
        "activities_list",
        {"part": "snippet", "channelId": "UC_fixture"},
        "api_key",
        "api_key_executable",
        "public activity selector",
    ),
    CapabilityMatrixCase(
        "activities",
        "activities_list",
        {"part": "snippet", "channelId": "UC_fixture"},
        "api_key_missing",
        "unavailable",
        "missing API-key capability",
        "authentication_failed",
    ),
    CapabilityMatrixCase(
        "captions",
        "captions_list",
        {"part": "snippet", "videoId": "video-fixture"},
        "oauth_missing",
        "oauth_required",
        "OAuth-protected caption listing",
        "authentication_failed",
    ),
    CapabilityMatrixCase(
        "channelBanners",
        "channelBanners_insert",
        {"media": {"mimeType": "image/png", "content": "fixture"}},
        "oauth_missing",
        "oauth_required",
        "OAuth-protected banner upload boundary",
        "authentication_failed",
    ),
    CapabilityMatrixCase(
        "channels",
        "channels_list",
        {"part": "snippet", "id": "UC_fixture"},
        "api_key",
        "api_key_executable",
        "public channel selector",
    ),
    CapabilityMatrixCase(
        "channel_sections",
        "channelSections_delete",
        {"id": "section-fixture"},
        "oauth_missing",
        "oauth_required",
        "OAuth-protected channel section boundary",
        "authentication_failed",
    ),
    CapabilityMatrixCase(
        "comments",
        "comments_list",
        {"part": "snippet", "id": "comment-fixture"},
        "api_key",
        "api_key_executable",
        "public comment identifier selector",
    ),
    CapabilityMatrixCase(
        "comment_threads",
        "commentThreads_list",
        {"part": "snippet", "videoId": "video-fixture"},
        "api_key",
        "api_key_executable",
        "public video comment-thread selector",
    ),
    CapabilityMatrixCase(
        "guide_categories",
        "guideCategories_list",
        {"part": "snippet", "regionCode": "US"},
        "api_key",
        "api_key_executable",
        "public region selector",
    ),
    CapabilityMatrixCase(
        "localization",
        "i18nLanguages_list",
        {"part": "snippet"},
        "api_key",
        "api_key_executable",
        "public language reference",
    ),
    CapabilityMatrixCase(
        "members",
        "members_list",
        {"part": "snippet", "mode": "all_current"},
        "oauth_missing",
        "oauth_required",
        "OAuth-protected members listing",
        "authentication_failed",
    ),
    CapabilityMatrixCase(
        "memberships_levels",
        "membershipsLevels_list",
        {"part": "snippet"},
        "oauth_missing",
        "oauth_required",
        "OAuth-protected memberships listing",
        "authentication_failed",
    ),
    CapabilityMatrixCase(
        "playlist_images",
        "playlistImages_list",
        {"part": "snippet", "playlistId": "playlist-fixture"},
        "oauth_missing",
        "oauth_required",
        "OAuth-protected playlist image listing",
        "authentication_failed",
    ),
    CapabilityMatrixCase(
        "playlist_items",
        "playlistItems_list",
        {"part": "snippet", "playlistId": "playlist-fixture"},
        "api_key",
        "api_key_executable",
        "public playlist item selector",
    ),
    CapabilityMatrixCase(
        "playlists",
        "playlists_list",
        {"part": "snippet", "channelId": "UC_fixture"},
        "api_key",
        "api_key_executable",
        "public playlist selector",
    ),
    CapabilityMatrixCase(
        "search",
        "search_list",
        {"part": "snippet", "q": "fixture"},
        "api_key",
        "api_key_executable",
        "public search selector",
    ),
    CapabilityMatrixCase(
        "subscriptions",
        "subscriptions_list",
        {"part": "snippet", "channelId": "UC_fixture"},
        "api_key",
        "api_key_executable",
        "public subscription selector",
    ),
    CapabilityMatrixCase(
        "thumbnails",
        "thumbnails_set",
        {
            "videoId": "video-fixture",
            "media": {"mimeType": "image/png", "content": "fixture"},
        },
        "oauth_missing",
        "oauth_required",
        "OAuth-protected thumbnail boundary",
        "authentication_failed",
    ),
    CapabilityMatrixCase(
        "transcripts",
        "transcripts_getTranscript",
        {"videoId": "video-fixture"},
        "oauth_missing",
        "oauth_required",
        "OAuth-protected transcript boundary",
        "authorization_sensitive_data",
    ),
    CapabilityMatrixCase(
        "video_abuse_report_reasons",
        "videoAbuseReportReasons_list",
        {"part": "snippet", "hl": "en"},
        "oauth_missing",
        "oauth_required",
        "OAuth-protected abuse-reason reference",
        "authentication_failed",
    ),
    CapabilityMatrixCase(
        "video_categories",
        "videoCategories_list",
        {"part": "snippet", "regionCode": "US"},
        "api_key",
        "api_key_executable",
        "public category reference",
    ),
    CapabilityMatrixCase(
        "videos",
        "videos_list",
        {"part": "snippet", "id": "video-fixture"},
        "api_key",
        "api_key_executable",
        "public video selector",
    ),
    CapabilityMatrixCase(
        "watermarks",
        "watermarks_unset",
        {"channelId": "UC_fixture"},
        "oauth_missing",
        "oauth_required",
        "OAuth-protected watermark boundary",
        "authentication_failed",
    ),
)


class _FakeHTTPResponse:
    """Provide the minimal controlled response interface used by the live executor."""

    def __init__(self, payload: bytes = b'{"items": []}') -> None:
        """Store deterministic JSON payload bytes for a controlled request.

        :param payload: JSON response bytes returned by :meth:`read`.
        """
        self._payload = payload

    def read(self) -> bytes:
        """Return the deterministic controlled response payload.

        :return: JSON response bytes.
        """
        return self._payload

    def __enter__(self) -> Self:
        """Enter the response context without acquiring external resources.

        :return: This controlled response.
        """
        return self

    def __exit__(self, *_args: object) -> bool:
        """Exit the response context without suppressing external exceptions.

        :param _args: Context-manager exception arguments, if any.
        :return: ``False`` so exceptions are not suppressed.
        """
        return False


def _fail_network(*_args: object, **_kwargs: object) -> None:
    """Fail when the deterministic configured-runtime matrix attempts network I/O.

    :param _args: Positional values sent to a blocked network API.
    :param _kwargs: Keyword values sent to a blocked network API.
    :return: This function never returns.
    :raises AssertionError: Always, because the matrix must remain offline.
    """
    raise AssertionError("configured-runtime matrix must not make an outbound request")


def _block_outbound_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Install deterministic guards for socket and URL-opening network paths.

    :param monkeypatch: Pytest patch manager used to install safety guards.
    :return: ``None`` after guards apply for the test lifetime.
    """
    monkeypatch.setattr(socket, "create_connection", _fail_network)
    monkeypatch.setattr(urllib.request, "urlopen", _fail_network)


def _configured_transport() -> tuple[Any, list[object]]:
    """Build the configured in-process MCP transport for matrix verification.

    :return: Public transport and a controlled-opener record list.
    """
    records: list[object] = []

    def controlled_opener(request: object, timeout: object) -> _FakeHTTPResponse:
        """Record a controlled request without performing network I/O.

        :param request: Request object built by the configured live runtime.
        :param timeout: Configured request timeout value.
        :return: Deterministic JSON response used by the executor.
        """
        records.append((request, timeout))
        return _FakeHTTPResponse()

    transport = create_app(
        env={
            "MCP_ENVIRONMENT": "dev",
            "YOUTUBE_API_KEY": "matrix-sentinel-api-key",
            "YOUTUBE_OAUTH_TOKEN": "matrix-sentinel-oauth-token",
        },
        youtube_opener=controlled_opener,
    )
    return transport, records


def _configured_transport_for(
    matrix_case: CapabilityMatrixCase,
) -> tuple[Any, list[object]]:
    """Build one configured transport using a matrix case's credential state.

    :param matrix_case: Reviewed case that declares available runtime capability.
    :return: Public transport and controlled-opener records for the case.
    """
    records: list[object] = []

    def controlled_opener(request: object, timeout: object) -> _FakeHTTPResponse:
        """Capture configured request construction without sending a request.

        :param request: Request object created by the configured live executor.
        :param timeout: Timeout selected by the runtime.
        :return: Deterministic JSON response for the configured executor.
        """
        records.append(_safe_request_record(matrix_case, request, timeout))
        return _FakeHTTPResponse(
            b'{"items": [{"id": "matrix-item", "snippet": {"title": "Matrix"}}]}'
        )

    environment = {"MCP_ENVIRONMENT": "dev"}
    if matrix_case.configured_capability == "api_key":
        environment["YOUTUBE_API_KEY"] = "matrix-sentinel-api-key"
    elif matrix_case.configured_capability == "oauth":
        environment["YOUTUBE_OAUTH_TOKEN"] = "matrix-sentinel-oauth-token"
    elif (
        matrix_case.configured_capability != "api_key_missing"
        and matrix_case.configured_capability != "oauth_missing"
    ):
        raise ValueError(
            f"unknown configured capability: {matrix_case.configured_capability}"
        )
    return create_app(env=environment, youtube_opener=controlled_opener), records


def _assert_family_coverage(
    discovered_families: set[str], cases: tuple[CapabilityMatrixCase, ...]
) -> None:
    """Require exact coverage between discovered families and matrix cases.

    :param discovered_families: Family names returned by public MCP discovery.
    :param cases: Reviewed matrix cases expected to cover those families.
    :return: ``None`` after validating no missing or stale family names exist.
    :raises AssertionError: If discovery and matrix family names differ.
    """
    matrix_families = {case.family for case in cases}
    missing = sorted(discovered_families - matrix_families)
    stale = sorted(matrix_families - discovered_families)
    assert not missing, f"missing matrix families: {', '.join(missing)}"
    assert not stale, f"stale matrix families: {', '.join(stale)}"


def _assert_capability_outcome(
    matrix_case: CapabilityMatrixCase,
    response: dict[str, object],
    records: list[object],
) -> None:
    """Validate one public-route result against its reviewed capability case.

    :param matrix_case: Reviewed expected capability classification.
    :param response: JSON-RPC response returned through ``/mcp``.
    :param records: Controlled opener records created by this invocation.
    :return: ``None`` after checking success or safe unavailable outcome.
    :raises AssertionError: If the response or request count violates the case.
    """
    if matrix_case.expected_outcome == "api_key_executable":
        assert "error" not in response, f"{matrix_case.family}: unexpected MCP error"
        result = response.get("result")
        assert isinstance(result, dict), (
            f"{matrix_case.family}: result envelope is required"
        )
        assert result.get("isError") is False, (
            f"{matrix_case.family}: expected non-error result"
        )
        content = result.get("content")
        assert isinstance(content, list) and content, (
            f"{matrix_case.family}: structured content is required"
        )
        assert len(records) >= 1, (
            f"{matrix_case.family}: configured request was not constructed"
        )
        return

    error = response.get("error")
    assert isinstance(error, dict), f"{matrix_case.family}: expected safe MCP error"
    details = error.get("data")
    assert isinstance(details, dict), (
        f"{matrix_case.family}: expected safe MCP error details"
    )
    assert details.get("category") == matrix_case.expected_error_category, (
        f"{matrix_case.family}: unexpected capability category"
    )
    assert not records, (
        f"{matrix_case.family}: unavailable capability must not construct a request"
    )


def _assert_live_runtime_boundary(
    matrix_case: CapabilityMatrixCase,
    response: dict[str, object],
    records: tuple[object, ...] | list[object],
) -> None:
    """Prove an executable MCP case used the bounded live runtime safely.

    :param matrix_case: Executable API-key case under verification.
    :param response: Public MCP response returned by the configured invocation.
    :param records: Sanitized controlled request evidence for the invocation.
    :return: ``None`` after checking configured response and request evidence.
    :raises AssertionError: If fallback data, unsafe diagnostics, or request drift occurs.
    """
    rendered_response = repr(response).lower()
    assert "representative" not in rendered_response, (
        "configured result must not contain representative fallback data"
    )
    assert "matrix-sentinel" not in rendered_response, (
        "configured result must not expose sentinel credentials"
    )
    result = response.get("result")
    assert isinstance(result, dict) and result.get("isError") is False, (
        "configured success result is required"
    )
    content = result.get("content")
    assert isinstance(content, list) and content, (
        "configured structured content is required"
    )
    assert len(records) == 1, (
        f"{matrix_case.family}: expected one bounded configured request"
    )
    _validate_controlled_records(records)
    record = records[0]
    assert isinstance(record, ControlledRequestRecord)
    expected_path, expected_method = EXPECTED_API_REQUESTS[matrix_case.tool_name]
    assert record.family == matrix_case.family
    assert record.tool_name == matrix_case.tool_name
    assert record.path_shape == expected_path
    assert record.method == expected_method
    assert record.credential_mode == "api_key"
    assert record.timeout_seconds > 0


def _route_request(
    transport: Any, request_id: str, method: str, params: dict[str, object]
) -> dict[str, object]:
    """Send one JSON-RPC request through the public MCP route.

    :param transport: In-process MCP transport under test.
    :param request_id: Unique request identity for test diagnostics.
    :param method: Public MCP method to invoke.
    :param params: Object-shaped JSON-RPC parameters.
    :return: JSON-RPC response envelope returned by ``/mcp``.
    """
    response = transport.handle(
        "/mcp", {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
    )
    assert isinstance(response, dict)
    return response


def _discovered_matrix_scope() -> tuple[set[str], set[str]]:
    """Discover YouTube families and explicit generic-tool exclusions through MCP.

    :return: The non-empty discovered YouTube-family set and generic tool names.
    :raises AssertionError: If discovery is malformed or a generic tool is absent.
    """
    transport, _records = _configured_transport()
    response = _route_request(transport, "matrix-scope", "tools/list", {})
    result = response.get("result")
    assert isinstance(result, dict)
    descriptors = result.get("tools")
    assert isinstance(descriptors, list) and descriptors
    families: set[str] = set()
    excluded: set[str] = set()
    for descriptor in descriptors:
        assert isinstance(descriptor, dict)
        name = descriptor.get("name")
        assert isinstance(name, str) and name
        metadata = descriptor.get("metadata")
        metadata = metadata if isinstance(metadata, dict) else {}
        family = metadata.get("resourceFamily", metadata.get("family"))
        if isinstance(family, str) and family:
            families.add(family)
        elif name in GENERIC_TOOL_NAMES:
            excluded.add(name)
        else:
            raise AssertionError(
                f"{name}: descriptor lacks a configured YouTube family"
            )
    assert families
    assert excluded == GENERIC_TOOL_NAMES
    return families, excluded


def test_matrix_case_requires_reviewable_fields() -> None:
    """Require the planned matrix case record before capability tests can run.

    :return: ``None`` after validating the planned record contract.
    """
    case = CapabilityMatrixCase(
        family="activities",
        tool_name="activities_list",
        arguments={"part": "snippet", "channelId": "UC_fixture"},
        configured_capability="api_key",
        expected_outcome="api_key_executable",
        purpose="public activity selector",
    )
    assert case.family == "activities"


def test_discovery_separates_youtube_families_from_generic_tools() -> None:
    """Require discovery-derived family and generic-tool classification.

    :return: ``None`` after validating the planned discovery classification.
    """
    families, excluded = _discovered_matrix_scope()
    assert "activities" in families
    assert {
        "server_ping",
        "server_info",
        "server_list_tools",
        "search",
        "fetch",
    } <= excluded


def test_matrix_transport_uses_public_routes_and_blocks_network() -> None:
    """Require a configured public-route transport with outbound I/O guards.

    :return: ``None`` after validating planned route and network boundaries.
    """
    transport, records = _configured_transport()
    response = _route_request(transport, "matrix-discovery", "tools/list", {})
    assert "error" not in response
    assert records == []


def test_unplanned_network_is_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    """Require socket and URL-opening guards for deterministic matrix tests.

    :param monkeypatch: Pytest patch manager used to exercise the safety guard.
    :return: ``None`` after proving both outbound paths fail safely.
    """
    _block_outbound_network(monkeypatch)
    with pytest.raises(
        AssertionError,
        match="configured-runtime matrix must not make an outbound request",
    ):
        socket.create_connection(("example.invalid", 443))
    with pytest.raises(
        AssertionError,
        match="configured-runtime matrix must not make an outbound request",
    ):
        urllib.request.urlopen("https://example.invalid")


@pytest.fixture(autouse=True)
def _guard_matrix_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Block unplanned network I/O for every configured-runtime matrix case.

    :param monkeypatch: Pytest patch manager used to install safety guards.
    :return: ``None`` after guards apply for the test lifetime.
    """
    _block_outbound_network(monkeypatch)


def test_matrix_cases_cover_discovered_youtube_families_exactly() -> None:
    """Require reviewed matrix cases for every current YouTube family.

    :return: ``None`` after comparing discovery to reviewed matrix records.
    """
    families, _excluded = _discovered_matrix_scope()
    matrix_families = {case.family for case in MATRIX_CASES}
    assert matrix_families == families


@pytest.mark.parametrize(
    "matrix_case",
    MATRIX_CASES,
    ids=lambda case: f"{case.family}-{case.expected_outcome}",
)
def test_matrix_case_reports_its_documented_capability(
    matrix_case: CapabilityMatrixCase,
) -> None:
    """Require public-route capability outcomes for every reviewed matrix case.

    :param matrix_case: Reviewed matrix case selected for one YouTube family.
    :return: ``None`` after validating the documented MCP outcome.
    """
    transport, records = _configured_transport_for(matrix_case)
    response = _route_request(
        transport,
        f"matrix-{matrix_case.tool_name}-{matrix_case.expected_outcome}",
        "tools/call",
        {"name": matrix_case.tool_name, "arguments": dict(matrix_case.arguments)},
    )
    _assert_capability_outcome(matrix_case, response, records)


def test_matrix_coverage_rejects_missing_and_stale_families() -> None:
    """Require actionable failure messages for drift between discovery and cases.

    :return: ``None`` after proving family coverage failures are explicit.
    """
    with pytest.raises(AssertionError, match="missing matrix families: activities"):
        _assert_family_coverage({"activities"}, ())
    stale_case = CapabilityMatrixCase(
        family="stale",
        tool_name="server_ping",
        arguments={},
        configured_capability="api_key",
        expected_outcome="api_key_executable",
        purpose="stale coverage test",
    )
    with pytest.raises(AssertionError, match="stale matrix families: stale"):
        _assert_family_coverage(set(), (stale_case,))


@pytest.mark.parametrize(
    "matrix_case",
    tuple(
        case for case in MATRIX_CASES if case.expected_outcome == "api_key_executable"
    ),
    ids=lambda case: f"{case.family}-live-boundary",
)
def test_executable_cases_record_a_bounded_sanitized_live_request(
    matrix_case: CapabilityMatrixCase,
) -> None:
    """Require safe controlled-request proof for each executable family case.

    :param matrix_case: API-key executable case selected for live-boundary proof.
    :return: ``None`` after validating sanitized bounded request evidence.
    """
    transport, records = _configured_transport_for(matrix_case)
    response = _route_request(
        transport,
        f"matrix-live-boundary-{matrix_case.tool_name}",
        "tools/call",
        {"name": matrix_case.tool_name, "arguments": dict(matrix_case.arguments)},
    )
    _assert_live_runtime_boundary(matrix_case, response, records)


def test_live_boundary_rejects_representative_data_and_secret_bearing_records() -> None:
    """Require configured results and records to exclude fallback and secret data.

    :return: ``None`` after proving unsafe result and record variants are rejected.
    """
    matrix_case = next(
        case
        for case in MATRIX_CASES
        if case.family == "activities" and case.expected_outcome == "api_key_executable"
    )
    with pytest.raises(AssertionError, match="representative"):
        _assert_live_runtime_boundary(
            matrix_case,
            {
                "result": {
                    "content": [{"structuredContent": {"source": "representative"}}]
                }
            },
            (),
        )
    with pytest.raises(AssertionError, match="unsafe controlled request record"):
        _validate_controlled_records(
            ("matrix-sentinel-api-key",),
        )
