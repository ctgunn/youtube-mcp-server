"""Deterministic public-route coverage for the default MCP tool catalog."""

from __future__ import annotations

import socket
import urllib.request
from dataclasses import dataclass

import pytest

from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.transport.http import MCPHTTPTransport


@dataclass(frozen=True)
class CatalogFixture:
    """Describe one safe, deterministic public MCP tool invocation.

    :param tool_name: Public name returned by the discovery route.
    :param arguments: JSON-object arguments sent through the invocation route.
    :param expected_outcome: Expected ``success`` or ``error`` route outcome.
    :param purpose: Reviewable explanation of why the fixture is safe.
    :param expected_error_category: Required safe MCP category for error outcomes.
    """

    tool_name: str
    arguments: dict[str, object]
    expected_outcome: str
    purpose: str
    expected_error_category: str | None = None


def _success(tool_name: str, arguments: dict[str, object], purpose: str) -> CatalogFixture:
    """Create a reviewed success fixture for one default public tool.

    :param tool_name: Public name returned by ``tools/list``.
    :param arguments: Safe object arguments used through ``tools/call``.
    :param purpose: Reason the deterministic local input is safe.
    :return: Success-classified catalog fixture.
    """
    return CatalogFixture(tool_name, arguments, "success", purpose)


def _error(tool_name: str, arguments: dict[str, object], category: str, purpose: str) -> CatalogFixture:
    """Create a reviewed expected-error fixture for one default public tool.

    :param tool_name: Public name returned by ``tools/list``.
    :param arguments: Safe object arguments used through ``tools/call``.
    :param category: Required safe MCP response category.
    :param purpose: Reason the deterministic error input is safe.
    :return: Error-classified catalog fixture.
    """
    return CatalogFixture(tool_name, arguments, "error", purpose, category)


CATALOG_FIXTURES = (
    _success("activities_list", {"part": "snippet", "channelId": "UC_fixture"}, "public local channel selector"),
    _success("captions_delete", {"id": "caption-fixture"}, "local deletion acknowledgment only"),
    _success("captions_download", {"id": "caption-fixture"}, "local safe download descriptor"),
    _error("captions_insert", {"part": "snippet", "body": {"snippet": {"videoId": "video-fixture", "language": "en", "name": "fixture"}}, "media": {}}, "invalid_request", "media-free upload rejection"),
    _success("captions_list", {"part": "snippet", "videoId": "video-fixture"}, "local caption listing"),
    _error("captions_update", {"part": "snippet", "body": {"id": "caption-fixture"}}, "invalid_request", "media-free update rejection"),
    _error("channelBanners_insert", {"media": {}}, "invalid_request", "media-free banner rejection"),
    _success("channels_findCreators", {"query": "fixture"}, "local creator search"),
    _error("channels_getChannel", {"channelId": "fixture"}, "unavailable_resource", "deterministic absent local channel"),
    _success("channels_getChannels", {"channelIds": ["fixture"]}, "local batch channel lookup"),
    _error("channels_getStatistics", {"channelId": "fixture"}, "unavailable_resource", "deterministic absent local statistics"),
    _success("channels_list", {"part": "snippet", "id": "fixture"}, "local channel listing"),
    _error("channels_listPlaylists", {"channelId": "fixture"}, "unavailable_resource", "deterministic absent local playlists"),
    _error("channels_listVideos", {"channelId": "fixture"}, "unavailable_resource", "deterministic absent local videos"),
    _success("channels_searchChannels", {"query": "fixture"}, "local channel search"),
    _success("channels_searchContent", {"channelId": "fixture", "query": "fixture"}, "local channel content search"),
    _error("channels_update", {"part": "brandingSettings", "body": {"id": "fixture"}}, "invalid_request", "incomplete local update body"),
    _success("channelSections_delete", {"id": "section-fixture"}, "local deletion acknowledgment only"),
    _error("channelSections_insert", {"part": "contentDetails", "body": {"snippet": {"type": "singlePlaylist", "channelId": "UC_fixture"}}}, "invalid_request", "safe section without required content reference"),
    _success("channelSections_list", {"part": "snippet", "channelId": "UC_fixture"}, "local section listing"),
    _error("channelSections_update", {"part": "contentDetails", "body": {"id": "section-fixture", "snippet": {"type": "singlePlaylist"}}}, "invalid_request", "safe section update without required content reference"),
    _success("comments_delete", {"id": "comment-fixture"}, "local deletion acknowledgment only"),
    _success("comments_insert", {"part": "snippet", "body": {"snippet": {"parentId": "video-fixture", "textOriginal": "fixture comment"}}}, "local comment creation acknowledgment"),
    _success("comments_list", {"part": "snippet", "id": "comment-fixture"}, "local comment listing"),
    _success("comments_setModerationStatus", {"id": "comment-fixture", "moderationStatus": "heldForReview"}, "local moderation acknowledgment"),
    _success("comments_update", {"part": "snippet", "body": {"id": "comment-fixture", "snippet": {"textOriginal": "fixture comment"}}}, "local comment update acknowledgment"),
    _success("commentThreads_insert", {"part": "snippet", "body": {"snippet": {"channelId": "UC_fixture", "videoId": "video-fixture", "topLevelComment": {"snippet": {"textOriginal": "fixture comment"}}}}}, "local thread creation acknowledgment"),
    _success("commentThreads_list", {"part": "snippet", "videoId": "video-fixture"}, "local thread listing"),
    _error("fetch", {"id": "fixture"}, "unavailable_source", "deterministic absent retrieval document"),
    _error("guideCategories_list", {"part": "snippet", "regionCode": "fixture"}, "invalid_request", "safe invalid local region"),
    _success("i18nLanguages_list", {"part": "snippet"}, "local language reference listing"),
    _success("i18nRegions_list", {"part": "snippet"}, "local region reference listing"),
    _success("members_list", {"part": "snippet", "mode": "all_current"}, "local member listing"),
    _success("membershipsLevels_list", {"part": "snippet"}, "local membership-level listing"),
    _success("playlistImages_delete", {"id": "playlist-image-fixture"}, "local deletion acknowledgment only"),
    _error("playlistImages_insert", {"part": "snippet", "body": {}, "media": {"mimeType": "image/jpeg", "content": "fixture-content"}}, "invalid_request", "incomplete local image metadata"),
    _success("playlistImages_list", {"part": "snippet", "playlistId": "fixture"}, "local playlist-image listing"),
    _error("playlistImages_update", {"part": "snippet", "body": {"id": "playlist-image-fixture", "snippet": {}}, "media": {"mimeType": "image/jpeg", "content": "fixture-content"}}, "invalid_request", "incomplete local image update metadata"),
    _success("playlistItems_delete", {"id": "playlist-item-fixture"}, "local deletion acknowledgment only"),
    _success("playlistItems_insert", {"part": "snippet", "body": {"snippet": {"playlistId": "PL_fixture", "resourceId": {"videoId": "video-fixture"}}}}, "local playlist-item creation acknowledgment"),
    _success("playlistItems_list", {"part": "contentDetails", "playlistId": "PL_fixture"}, "local playlist-item listing"),
    _success("playlistItems_update", {"part": "snippet", "body": {"id": "playlist-item-fixture", "snippet": {"playlistId": "PL_fixture", "resourceId": {"videoId": "video-fixture"}}}}, "local playlist-item update acknowledgment"),
    _success("playlists_delete", {"id": "playlist-fixture"}, "local deletion acknowledgment only"),
    _success("playlists_getPlaylist", {"playlistId": "playlist-fixture"}, "local playlist retrieval"),
    _success("playlists_getPlaylistItems", {"playlistId": "playlist-fixture"}, "local playlist-item retrieval"),
    _success("playlists_getVideoTranscripts", {"playlistId": "playlist-fixture"}, "local playlist transcript retrieval"),
    _success("playlists_insert", {"part": "snippet", "body": {"snippet": {"title": "fixture playlist"}}}, "local playlist creation acknowledgment"),
    _success("playlists_list", {"part": "snippet", "channelId": "fixture"}, "local playlist listing"),
    _success("playlists_searchItems", {"playlistId": "playlist-fixture", "query": "fixture"}, "local playlist-item search"),
    _success("playlists_update", {"part": "snippet", "body": {"id": "playlist-fixture", "snippet": {"title": "fixture playlist"}}}, "local playlist update acknowledgment"),
    _success("search", {"query": "fixture"}, "local retrieval search"),
    _success("search_list", {"part": "snippet", "q": "fixture"}, "local YouTube search listing"),
    _success("server_info", {}, "local server metadata"),
    _success("server_list_tools", {}, "local registry listing"),
    _success("server_ping", {}, "local health response"),
    _success("subscriptions_delete", {"id": "subscription-fixture"}, "local deletion acknowledgment only"),
    _success("subscriptions_insert", {"part": "snippet", "body": {"snippet": {"resourceId": {"channelId": "UC_fixture"}}}}, "local subscription creation acknowledgment"),
    _success("subscriptions_list", {"part": "snippet", "channelId": "fixture"}, "local subscription listing"),
    _success("thumbnails_set", {"videoId": "video-fixture", "media": {"mimeType": "image/jpeg", "content": "fixture-content"}}, "local thumbnail acknowledgment"),
    _success("transcripts_getTimestampedCaptions", {"videoId": "video-fixture"}, "local timestamped caption response"),
    _error("transcripts_getTranscript", {"videoId": "video-fixture"}, "transcript_unavailable", "deterministic unavailable transcript"),
    _success("transcripts_listLanguages", {"videoId": "video-fixture"}, "local transcript language listing"),
    _error("transcripts_searchTranscript", {"videoId": "video-fixture", "query": "fixture"}, "transcript_unavailable", "deterministic unavailable transcript search"),
    _success("videoAbuseReportReasons_list", {"part": "snippet", "hl": "en"}, "local abuse-reason listing"),
    _error("videoCategories_list", {"part": "snippet", "regionCode": "fixture"}, "invalid_request", "safe invalid local region"),
    _success("videos_delete", {"id": "video-fixture"}, "local deletion acknowledgment only"),
    _success("videos_getRating", {"id": "video-fixture"}, "local rating lookup"),
    _success("videos_getStatistics", {"videoId": "video-fixture"}, "local statistics retrieval"),
    _success("videos_getVideo", {"videoId": "video-fixture"}, "local video retrieval"),
    _error("videos_insert", {"part": "snippet", "body": {}, "media": {}}, "invalid_request", "media-free local upload rejection"),
    _success("videos_list", {"part": "snippet", "id": "video-fixture"}, "local video listing"),
    _success("videos_rate", {"id": "video-fixture", "rating": "like"}, "local rating acknowledgment"),
    _success("videos_reportAbuse", {"body": {"videoId": "video-fixture", "reasonId": "reason-fixture"}}, "local report acknowledgment"),
    _success("videos_searchVideos", {"query": "fixture"}, "local video search"),
    _success("videos_update", {"part": "snippet", "body": {"id": "video-fixture", "snippet": {"title": "fixture title"}}}, "local video update acknowledgment"),
    _error("watermarks_set", {"channelId": "UC_fixture", "body": {"timing": {}, "position": {}}, "media": {"mimeType": "image/jpeg", "content": "fixture-content"}}, "invalid_request", "incomplete local watermark metadata"),
    _success("watermarks_unset", {"channelId": "UC_fixture"}, "local watermark removal acknowledgment"),
)


def _fail_network(*_args: object, **_kwargs: object) -> None:
    """Fail a test when the deterministic suite attempts outbound network access.

    :param _args: Positional arguments sent to an outbound networking API.
    :param _kwargs: Keyword arguments sent to an outbound networking API.
    :return: This function never returns.
    :raises AssertionError: Always, because catalog verification must remain offline.
    """
    raise AssertionError("catalog verification must not make an outbound request")


@pytest.fixture(autouse=True)
def _block_outbound_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Block socket and urllib network access for every catalog verification test.

    :param monkeypatch: Pytest patch manager used to install deterministic guards.
    :return: ``None`` after the guards are installed for the test lifetime.
    :raises AssertionError: Via the patched networking functions if code attempts I/O.
    """
    monkeypatch.setattr(socket, "create_connection", _fail_network)
    monkeypatch.setattr(urllib.request, "urlopen", _fail_network)


def _build_catalog_transport() -> MCPHTTPTransport:
    """Build the credential-free in-process transport used by this verification suite.

    :return: Public MCP transport backed by the default local dispatcher only.
    :raises AssertionError: If a test later attempts blocked outbound network access.
    """
    return MCPHTTPTransport(dispatcher=InMemoryToolDispatcher())


def _route_request(transport: MCPHTTPTransport, request_id: str, method: str, params: dict[str, object]) -> dict[str, object]:
    """Send one JSON-RPC request through the public MCP transport route.

    :param transport: In-process public MCP transport under test.
    :param request_id: Unique request identifier for test diagnostics.
    :param method: Public MCP method name.
    :param params: Object parameters for the MCP method.
    :return: JSON-RPC response envelope returned by ``/mcp``.
    """
    return transport.handle("/mcp", {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})


def _discover_default_tools() -> list[dict[str, object]]:
    """Discover the default catalog through ``tools/list`` rather than a copied name list.

    :return: Non-empty public tool descriptors in their route-provided order.
    :raises AssertionError: If the route returns a malformed, empty, or duplicate catalog.
    """
    response = _route_request(_build_catalog_transport(), "catalog-list", "tools/list", {})
    assert "error" not in response
    result = response.get("result")
    assert isinstance(result, dict)
    tools = result.get("tools")
    assert isinstance(tools, list) and tools
    names = [tool.get("name") for tool in tools if isinstance(tool, dict)]
    assert len(names) == len(tools)
    assert all(isinstance(name, str) and name.strip() for name in names)
    assert len(set(names)) == len(names)
    return tools


def _fixture_index(fixtures: tuple[CatalogFixture, ...]) -> dict[str, CatalogFixture]:
    """Validate fixture records and return their unique public-name index.

    :param fixtures: Candidate reviewable fixture records.
    :return: Mapping from public tool name to exactly one fixture.
    :raises AssertionError: If a fixture is malformed, duplicated, or lacks a safe outcome declaration.
    """
    index: dict[str, CatalogFixture] = {}
    for fixture in fixtures:
        assert fixture.tool_name and fixture.tool_name.strip(), "fixture tool name is required"
        assert isinstance(fixture.arguments, dict), f"{fixture.tool_name}: fixture arguments must be an object"
        assert fixture.purpose.strip(), f"{fixture.tool_name}: fixture purpose is required"
        assert fixture.expected_outcome in {"success", "error"}, f"{fixture.tool_name}: invalid fixture outcome"
        if fixture.expected_outcome == "error":
            assert fixture.expected_error_category, f"{fixture.tool_name}: expected-error category is required"
        else:
            assert fixture.expected_error_category is None, f"{fixture.tool_name}: success fixture cannot declare an error category"
        assert fixture.tool_name not in index, f"duplicate fixture: {fixture.tool_name}"
        index[fixture.tool_name] = fixture
    return index


def _assert_fixture_coverage(descriptors: list[dict[str, object]], fixtures: tuple[CatalogFixture, ...]) -> dict[str, CatalogFixture]:
    """Require exact bidirectional coverage between public discovery and fixtures.

    :param descriptors: Public descriptors returned by the current ``tools/list`` response.
    :param fixtures: Candidate test-owned fixture records.
    :return: Validated mapping from each discovered tool name to its fixture.
    :raises AssertionError: If fixture names are missing from or stale against discovery.
    """
    index = _fixture_index(fixtures)
    discovered = {str(descriptor["name"]) for descriptor in descriptors}
    fixture_names = set(index)
    missing = sorted(discovered - fixture_names)
    stale = sorted(fixture_names - discovered)
    assert not missing, f"missing fixtures: {', '.join(missing)}"
    assert not stale, f"stale fixtures: {', '.join(stale)}"
    return index


def _assert_fixture_outcome(descriptor: dict[str, object], fixture: CatalogFixture) -> None:
    """Invoke one fixture through ``tools/call`` and assert its declared MCP outcome.

    :param descriptor: Discovered public descriptor associated with the fixture.
    :param fixture: Safe invocation input and expected result classification.
    :return: ``None`` after route-level result validation.
    :raises AssertionError: If the response does not match the fixture or public contract.
    """
    response = _route_request(
        _build_catalog_transport(),
        f"catalog-call-{fixture.tool_name}",
        "tools/call",
        {"name": fixture.tool_name, "arguments": fixture.arguments},
    )
    if fixture.expected_outcome == "error":
        error = response.get("error")
        assert isinstance(error, dict), f"{fixture.tool_name}: expected MCP error envelope"
        details = error.get("data")
        assert isinstance(details, dict), f"{fixture.tool_name}: expected MCP error details"
        assert details.get("category") == fixture.expected_error_category, f"{fixture.tool_name}: unexpected error category"
        return

    assert "error" not in response, f"{fixture.tool_name}: unexpected MCP error envelope"
    result = response.get("result")
    assert isinstance(result, dict), f"{fixture.tool_name}: result envelope is required"
    assert result.get("isError") is False, f"{fixture.tool_name}: expected non-error MCP result"
    content = result.get("content")
    assert isinstance(content, list) and content, f"{fixture.tool_name}: nonempty content is required"
    first_content = content[0]
    assert isinstance(first_content, dict), f"{fixture.tool_name}: content item is required"
    structured_content = first_content.get("structuredContent")
    assert isinstance(structured_content, (dict, list)), f"{fixture.tool_name}: structured content is required"
    if isinstance(structured_content, dict) and "endpoint" in structured_content:
        metadata = descriptor.get("metadata")
        upstream = metadata.get("upstream") if isinstance(metadata, dict) else None
        operation_key = upstream.get("operationKey") if isinstance(upstream, dict) else None
        if operation_key is not None:
            assert structured_content["endpoint"] == operation_key, f"{fixture.tool_name}: endpoint metadata mismatch"


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Generate one individually reported invocation case per discovered public tool.

    :param metafunc: Pytest collection context for the target test function.
    :return: ``None`` after parametrizing discovery-derived catalog cases.
    :raises AssertionError: If discovery cannot provide valid public tool descriptors.
    """
    if "catalog_case" not in metafunc.fixturenames:
        return
    descriptors = _discover_default_tools()
    fixture_index = _fixture_index(CATALOG_FIXTURES)
    cases = [(descriptor, fixture_index.get(str(descriptor["name"]))) for descriptor in descriptors]
    metafunc.parametrize("catalog_case", cases, ids=[str(descriptor["name"]) for descriptor, _fixture in cases])


def test_default_catalog_is_discovered_through_public_route() -> None:
    """Require catalog discovery through the public MCP request route.

    :return: ``None`` after asserting the public discovery response.
    """
    assert _discover_default_tools()


def test_catalog_fixture_registry_is_complete() -> None:
    """Require the reviewed registry to cover the current public catalog exactly.

    :return: ``None`` after validating no missing or stale fixture names exist.
    """
    assert _assert_fixture_coverage(_discover_default_tools(), CATALOG_FIXTURES)


def test_fixture_validation_rejects_missing_stale_duplicate_and_malformed_records() -> None:
    """Reject representative catalog fixture-governance failures before invocation.

    :return: ``None`` after asserting safe fixture validation failures.
    """
    descriptors = [{"name": "one"}]
    valid = _success("one", {}, "valid local fixture")
    with pytest.raises(AssertionError, match="missing fixtures: one"):
        _assert_fixture_coverage(descriptors, ())
    with pytest.raises(AssertionError, match="stale fixtures: two"):
        _assert_fixture_coverage(descriptors, (valid, _success("two", {}, "stale local fixture")))
    with pytest.raises(AssertionError, match="duplicate fixture: one"):
        _fixture_index((valid, valid))
    with pytest.raises(AssertionError, match="fixture arguments must be an object"):
        _fixture_index((CatalogFixture("one", "not-an-object", "success", "malformed fixture"),))  # type: ignore[arg-type]


def test_expected_error_fixture_requires_its_documented_category() -> None:
    """Reject a fixture whose observed public error category differs from its declaration.

    :return: ``None`` after proving expected-error category comparison is enforced.
    """
    descriptor = next(tool for tool in _discover_default_tools() if tool["name"] == "fetch")
    wrong_fixture = _error("fetch", {"id": "fixture"}, "invalid_request", "intentional category mismatch")
    with pytest.raises(AssertionError, match="unexpected error category"):
        _assert_fixture_outcome(descriptor, wrong_fixture)


def test_catalog_fixture_execution_requires_no_live_runtime() -> None:
    """Prove the catalog transport has no configured YouTube runtime dependency.

    :return: ``None`` after asserting the deterministic transport configuration.
    """
    transport = _build_catalog_transport()
    assert transport.youtube_runtime_settings is None
    assert transport.runtime_settings is None


def test_discovered_tool_fixture_invokes_the_public_route(catalog_case: tuple[dict[str, object], CatalogFixture | None]) -> None:
    """Invoke one discovery-derived default tool through the public MCP call route.

    :param catalog_case: Public descriptor and its required safe fixture.
    :return: ``None`` after validating the declared route outcome.
    :raises AssertionError: If discovery yields an uncovered tool or the route contract fails.
    """
    descriptor, fixture = catalog_case
    tool_name = str(descriptor["name"])
    assert fixture is not None, f"missing fixture: {tool_name}"
    _assert_fixture_outcome(descriptor, fixture)
