"""Unit tests for the composed public channel-detail tool."""

import pytest


def _channel_payload():
    """Return one complete public channel fixture.

    :return: Lower-level channel-list payload for composed-tool tests.
    """
    return {
        "items": [
            {
                "id": "UC123",
                "snippet": {
                    "title": "Example Creator",
                    "description": "Public description",
                    "thumbnails": {"default": "https://example.invalid/channel.jpg"},
                    "country": "US",
                    "defaultLanguage": "en",
                    "publishedAt": "2020-01-01T00:00:00Z",
                    "customUrl": "@example",
                },
                "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}},
            }
        ]
    }


def test_channel_details_validates_one_trimmed_identifier_and_rejects_unknown_fields():
    """Require exactly one nonblank public channel identifier."""
    from mcp_server.tools.youtube_composed.channels import ChannelsGetChannelToolError, validate_channels_get_channel_arguments

    assert validate_channels_get_channel_arguments({"channelId": " UC123 "}) == {"channelId": "UC123"}
    for arguments, field in (({}, "channelId"), ({"channelId": " "}, "channelId"), ({"channelId": 3}, "channelId"), ({"channelId": "UC123", "part": "snippet"}, "part")):
        with pytest.raises(ChannelsGetChannelToolError) as exc_info:
            validate_channels_get_channel_arguments(arguments)
        assert exc_info.value.category == "invalid_parameters"
        assert exc_info.value.details["field"] == field


def test_channel_details_normalizes_core_metadata_provenance_and_latest_upload():
    """Return one bounded enriched channel detail from controlled dependencies."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channel_handler

    channel_calls = []
    playlist_calls = []

    def channels(arguments):
        """Record the core lookup and return one public channel.

        :param arguments: Lower-level channel-list arguments.
        :return: One-item public channel result.
        """
        channel_calls.append(arguments)
        return _channel_payload()

    def playlist_items(arguments):
        """Record the uploads lookup and return its latest item.

        :param arguments: Lower-level playlist-items arguments.
        :return: One-item playlist result containing publication time.
        """
        playlist_calls.append(arguments)
        return {"items": [{"contentDetails": {"videoPublishedAt": "2026-03-01T12:00:00Z"}}]}

    result = build_channels_get_channel_handler(channels=channels, playlist_items=playlist_items)({"channelId": " UC123 "})

    assert channel_calls == [{"part": "snippet,contentDetails", "id": "UC123"}]
    assert playlist_calls == [{"part": "contentDetails", "playlistId": "UU123", "maxResults": 1}]
    assert result["channelId"] == "UC123"
    assert result["title"] == "Example Creator"
    assert result["description"] == "Public description"
    assert result["thumbnails"] == {"default": "https://example.invalid/channel.jpg"}
    assert result["normalizedMetadata"] == {
        "country": "US",
        "defaultLanguage": "en",
        "joinedAt": "2020-01-01T00:00:00Z",
        "customUrl": "@example",
        "emailsFound": [],
        "contactLinks": [],
    }
    assert result["latestVideoPublishedAt"] == "2026-03-01T12:00:00Z"
    assert result["enrichment"] == {"status": "complete"}
    assert result["fieldProvenance"]["channelId"] == "raw_upstream"
    assert result["fieldProvenance"]["normalizedMetadata.country"] == "normalized"
    assert result["fieldProvenance"]["latestVideoPublishedAt"] == "normalized"


def test_channel_details_preserves_sparse_public_fields_without_fabrication():
    """Omit unavailable source fields while retaining a successful profile."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channel_handler

    result = build_channels_get_channel_handler(
        channels=lambda _arguments: {"items": [{"id": "UC123", "snippet": {}, "contentDetails": {}}]},
        playlist_items=lambda _arguments: {"items": []},
    )({"channelId": "UC123"})

    assert result["channelId"] == "UC123"
    assert "title" not in result
    assert result["normalizedMetadata"] == {"emailsFound": [], "contactLinks": []}
    assert result["enrichment"] == {"status": "unavailable"}
    assert "latestVideoPublishedAt" not in result


def test_channel_statistics_validates_one_trimmed_identifier_and_normalizes_available_counts():
    """Require one statistics lookup and preserve all reported source counts.

    A reported source zero remains available rather than being mistaken for a
    missing statistic.
    """
    from mcp_server.tools.youtube_composed.channels import (
        ChannelsGetStatisticsToolError,
        build_channels_get_statistics_handler,
        validate_channels_get_statistics_arguments,
    )

    for arguments in (None, {}, {"channelId": " "}, {"channelId": 123}, {"channelId": "UC123", "part": "statistics"}):
        with pytest.raises(ChannelsGetStatisticsToolError) as exc_info:
            validate_channels_get_statistics_arguments(arguments)
        assert exc_info.value.category == "invalid_parameters"

    calls = []

    def channels(arguments):
        """Record one public statistics lookup and return source counts.

        :param arguments: Lower-level channel-list arguments.
        :return: One available channel statistics record.
        """
        calls.append(arguments)
        return {
            "items": [
                {
                    "id": "UC123",
                    "statistics": {"subscriberCount": "1200", "videoCount": "42", "viewCount": "0"},
                }
            ]
        }

    result = build_channels_get_statistics_handler(channels=channels)({"channelId": " UC123 "})

    assert calls == [{"id": "UC123", "part": "statistics"}]
    assert result["channelId"] == "UC123"
    assert result["statistics"] == {
        "subscriberCount": {"state": "available", "value": "1200", "provenance": "source_provided"},
        "videoCount": {"state": "available", "value": "42", "provenance": "source_provided"},
        "viewCount": {"state": "available", "value": "0", "provenance": "source_provided"},
    }


def test_channel_statistics_distinguishes_hidden_and_unavailable_metrics_without_values():
    """Give source hiddenness precedence and preserve unavailable states."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_statistics_handler

    result = build_channels_get_statistics_handler(
        channels=lambda _arguments: {
            "items": [
                {
                    "id": "UC123",
                    "statistics": {"hiddenSubscriberCount": True, "subscriberCount": "1200", "videoCount": "0"},
                }
            ]
        }
    )({"channelId": "UC123"})

    assert result["statistics"]["subscriberCount"] == {"state": "hidden", "provenance": "normalized"}
    assert "value" not in result["statistics"]["subscriberCount"]
    assert result["statistics"]["videoCount"] == {"state": "available", "value": "0", "provenance": "source_provided"}
    assert result["statistics"]["viewCount"] == {"state": "unavailable", "provenance": "normalized"}
    assert "value" not in result["statistics"]["viewCount"]
    assert "hiddenSubscriberCount" not in str(result)


@pytest.mark.parametrize("statistics", [None, "not-an-object", {"subscriberCount": "not-a-count", "videoCount": -1, "viewCount": False}])
def test_channel_statistics_marks_missing_or_malformed_counts_unavailable(statistics):
    """Avoid fabricating values for missing or malformed source counts.

    :param statistics: Controlled invalid or incomplete source statistics value.
    """
    from mcp_server.tools.youtube_composed.channels import build_channels_get_statistics_handler

    result = build_channels_get_statistics_handler(
        channels=lambda _arguments: {"items": [{"id": "UC123", "statistics": statistics}]}
    )({"channelId": "UC123"})

    for metric in ("subscriberCount", "videoCount", "viewCount"):
        assert result["statistics"][metric] == {"state": "unavailable", "provenance": "normalized"}
        assert "value" not in result["statistics"][metric]


@pytest.mark.parametrize("payload", [{"items": []}, {"items": [None]}, {"items": "not-a-list"}])
def test_channel_statistics_maps_empty_or_malformed_items_to_unavailable(payload):
    """Return one unavailable-resource outcome for unusable item collections.

    :param payload: Controlled lower-level response lacking one usable channel.
    """
    from mcp_server.tools.youtube_composed.channels import ChannelsGetStatisticsToolError, build_channels_get_statistics_handler

    with pytest.raises(ChannelsGetStatisticsToolError) as exc_info:
        build_channels_get_statistics_handler(channels=lambda _arguments: payload)({"channelId": "UC123"})

    assert exc_info.value.category == "unavailable_resource"
    assert exc_info.value.details == {"resource": "channel"}


@pytest.mark.parametrize(
    ("lower_category", "expected_category"),
    [
        ("resource_not_found", "unavailable_resource"),
        ("authorization_failed", "authorization_sensitive_data"),
        ("quota_exhausted", "quota_exhaustion"),
        ("endpoint_unavailable", "upstream_failure"),
    ],
)
def test_channel_statistics_maps_lower_lookup_failures_safely(lower_category, expected_category):
    """Translate source lookup failures without retaining unsafe diagnostics.

    :param lower_category: Lower-level category emitted by the controlled lookup.
    :param expected_category: Required safe public category.
    """
    from mcp_server.tools.youtube_common.channels import ChannelsListToolError
    from mcp_server.tools.youtube_composed.channels import ChannelsGetStatisticsToolError, build_channels_get_statistics_handler

    def failing_channels(_arguments):
        """Raise one controlled lower-layer error with unsafe details.

        :param _arguments: Ignored lower-level request arguments.
        :raises ChannelsListToolError: Always raised to test safe error translation.
        """
        raise ChannelsListToolError(
            "source failure",
            category=lower_category,
            details={"reason": "source failure", "api_key": "hidden", "stack_trace": "hidden"},
        )

    with pytest.raises(ChannelsGetStatisticsToolError) as exc_info:
        build_channels_get_statistics_handler(channels=failing_channels)({"channelId": "UC123"})

    assert exc_info.value.category == expected_category
    assert "hidden" not in str(exc_info.value.details)


def test_channel_details_extracts_only_valid_deduplicated_public_contacts():
    """Normalize public description contacts without reading owner-only fields."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channel_handler

    payload = _channel_payload()
    payload["items"][0]["snippet"]["description"] = (
        "Creator contact HELLO@example.com and hello@example.com; "
        "visit https://example.invalid/contact or ftp://example.invalid; malformed bad@@example"
    )
    payload["items"][0]["ownerEmail"] = "private@example.com"

    result = build_channels_get_channel_handler(
        channels=lambda _arguments: payload,
        playlist_items=lambda _arguments: {"items": []},
    )({"channelId": "UC123"})

    assert result["normalizedMetadata"]["emailsFound"] == ["hello@example.com"]
    assert result["normalizedMetadata"]["contactLinks"] == ["https://example.invalid/contact"]
    assert "private@example.com" not in str(result)
    assert result["fieldProvenance"]["normalizedMetadata.emailsFound"] == "heuristic_inferred"
    assert result["fieldProvenance"]["normalizedMetadata.contactLinks"] == "heuristic_inferred"


@pytest.mark.parametrize(
    ("title", "description", "classification", "signals"),
    [
        ("Creator Sam", "", "creator", ["public_creator_term"]),
        ("Acme", "Official company channel", "brand", ["public_official_term", "public_company_term"]),
        ("Creator Acme", "Official company channel", "unknown", []),
        ("Example", "General public channel", "unknown", []),
    ],
)
def test_channel_details_classifies_only_positive_nonconflicting_public_signals(title, description, classification, signals):
    """Return creator, brand, or unknown from public positive evidence only."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channel_handler

    payload = _channel_payload()
    payload["items"][0]["snippet"]["title"] = title
    payload["items"][0]["snippet"]["description"] = description

    result = build_channels_get_channel_handler(
        channels=lambda _arguments: payload,
        playlist_items=lambda _arguments: {"items": []},
    )({"channelId": "UC123"})

    assert result["heuristics"] == {"creatorClassification": classification, "creatorSignals": signals}
    assert result["fieldProvenance"]["heuristics.creatorClassification"] == "heuristic_inferred"


def test_channel_details_maps_empty_and_failed_core_lookups_to_safe_categories():
    """Distinguish safe whole-request core failures without source diagnostics."""
    from mcp_server.tools.youtube_common.channels import ChannelsListToolError
    from mcp_server.tools.youtube_composed.channels import ChannelsGetChannelToolError, build_channels_get_channel_handler

    unavailable = build_channels_get_channel_handler(
        channels=lambda _arguments: {"items": []},
        playlist_items=lambda _arguments: {"items": []},
    )
    with pytest.raises(ChannelsGetChannelToolError) as exc_info:
        unavailable({"channelId": "UC123"})
    assert exc_info.value.category == "unavailable_resource"
    for lower_category, public_category in (
        ("authentication_failed", "authorization_sensitive_data"),
        ("quota_exhausted", "quota_exhaustion"),
        ("upstream_failure", "upstream_failure"),
    ):
        def failing_channels(_arguments, category=lower_category):
            """Raise a configured lower-level core failure.

            :param _arguments: Ignored lower-level request.
            :param category: Lower-level category to expose to the mapper.
            :raises ChannelsListToolError: Always raised for safe mapping coverage.
            """
            raise ChannelsListToolError("hidden", category=category, details={"api_key": "secret", "raw_body": "hidden"})

        with pytest.raises(ChannelsGetChannelToolError) as exc_info:
            build_channels_get_channel_handler(channels=failing_channels, playlist_items=lambda _arguments: {"items": []})({"channelId": "UC123"})
        assert exc_info.value.category == public_category
        assert "secret" not in str(exc_info.value.details)
        assert "hidden" not in str(exc_info.value.details)


@pytest.mark.parametrize(
    "playlist_payload",
    [
        {"items": []},
        {"items": [{"contentDetails": {}}]},
        {"items": [{"contentDetails": {"videoPublishedAt": "not-a-timestamp"}}]},
    ],
)
def test_channel_details_marks_missing_or_malformed_latest_data_unavailable(playlist_payload):
    """Keep a successful profile when no valid latest publication time exists."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channel_handler

    result = build_channels_get_channel_handler(
        channels=lambda _arguments: _channel_payload(),
        playlist_items=lambda _arguments: playlist_payload,
    )({"channelId": "UC123"})

    assert result["enrichment"] == {"status": "unavailable"}
    assert "latestVideoPublishedAt" not in result


@pytest.mark.parametrize(
    ("lower_category", "cause_category"),
    [
        ("authentication_failed", "authorization_sensitive_data"),
        ("quota_exhausted", "quota_exhaustion"),
        ("upstream_failure", "upstream_failure"),
    ],
)
def test_channel_details_preserves_profile_on_safe_partial_enrichment_failure(lower_category, cause_category):
    """Return a partial profile when bounded latest enrichment fails."""
    from mcp_server.tools.youtube_common.playlist_items import PlaylistItemsListToolError
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channel_handler

    calls = []

    def playlist_items(arguments):
        """Record one bounded lookup and raise the configured safe error.

        :param arguments: Lower-level playlist-items request.
        :raises PlaylistItemsListToolError: Always raised for partial-result coverage.
        """
        calls.append(arguments)
        raise PlaylistItemsListToolError("hidden", category=lower_category, details={"api_key": "secret", "raw_body": "hidden"})

    result = build_channels_get_channel_handler(channels=lambda _arguments: _channel_payload(), playlist_items=playlist_items)({"channelId": "UC123"})

    assert calls == [{"part": "contentDetails", "playlistId": "UU123", "maxResults": 1}]
    assert result["channelId"] == "UC123"
    assert result["enrichment"] == {
        "status": "partial",
        "category": "partial_enrichment_failure",
        "causeCategory": cause_category,
    }
    assert "latestVideoPublishedAt" not in result
    assert "secret" not in str(result)


def test_batch_channel_details_validate_trimmed_bounded_request_arguments():
    """Require one through fifty distinct batch identifiers and valid options."""
    from mcp_server.tools.youtube_composed.channels import (
        ChannelsGetChannelsToolError,
        validate_channels_get_channels_arguments,
    )

    assert validate_channels_get_channels_arguments({"channelIds": [" UC123 ", "UC456"]}) == {
        "channelIds": ["UC123", "UC456"],
        "parts": ["snippet"],
        "includeLatestUpload": True,
    }
    invalid_arguments = (
        ({}, "channelIds"),
        ({"channelIds": []}, "channelIds"),
        ({"channelIds": [" "]}, "channelIds"),
        ({"channelIds": ["UC123", " UC123 "]}, "channelIds"),
        ({"channelIds": ["UC123"] * 51}, "channelIds"),
        ({"channelIds": ["UC123"], "parts": []}, "parts"),
        ({"channelIds": ["UC123"], "parts": ["unknown"]}, "parts"),
        ({"channelIds": ["UC123"], "includeLatestUpload": "yes"}, "includeLatestUpload"),
        ({"channelIds": ["UC123"], "unexpected": True}, "unexpected"),
    )
    for arguments, field in invalid_arguments:
        with pytest.raises(ChannelsGetChannelsToolError) as exc_info:
            validate_channels_get_channels_arguments(arguments)
        assert exc_info.value.category == "invalid_parameters"
        assert exc_info.value.details["field"] == field


def test_batch_channel_details_uses_one_core_lookup_and_preserves_request_order():
    """Return normalized available items in caller order from one bulk lookup."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channels_handler

    calls = []

    def channels(arguments):
        """Return bulk source items in a different order than requested.

        :param arguments: Lower-level bulk lookup arguments.
        :return: Two public source channel records.
        """
        calls.append(arguments)
        return {
            "items": [
                {"id": "UC456", "snippet": {"title": "Second"}, "contentDetails": {}},
                {"id": "UC123", "snippet": {"title": "First"}, "contentDetails": {}},
            ]
        }

    result = build_channels_get_channels_handler(channels=channels, playlist_items=lambda _arguments: {"items": []})(
        {"channelIds": ["UC123", "UC456"]}
    )

    assert calls == [{"part": "snippet,contentDetails", "id": "UC123,UC456"}]
    assert [item["channelId"] for item in result["results"]] == ["UC123", "UC456"]
    assert [item["outcome"] for item in result["results"]] == [{"status": "success"}, {"status": "success"}]
    assert result["results"][0]["title"] == "First"
    assert result["results"][0]["normalizedMetadata"] == {"emailsFound": [], "contactLinks": []}
    assert result["results"][0]["fieldProvenance"]["title"] == "raw_upstream"
    assert result["summary"] == {"requested": 2, "successful": 2, "unavailable": 0, "partiallyEnriched": 0}


def test_batch_channel_details_applies_parts_and_latest_upload_controls():
    """Select public groups and perform latest enrichment only when enabled."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channels_handler

    payload = {
        "items": [
            {
                "id": "UC123",
                "snippet": {"title": "Example"},
                "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}},
            }
        ]
    }
    playlist_calls = []

    def playlist_items(arguments):
        """Record a bounded latest-upload lookup and return a timestamp.

        :param arguments: Lower-level playlist-items arguments.
        :return: One timestamped uploads-playlist item.
        """
        playlist_calls.append(arguments)
        return {"items": [{"contentDetails": {"videoPublishedAt": "2026-03-01T12:00:00Z"}}]}

    handler = build_channels_get_channels_handler(channels=lambda _arguments: payload, playlist_items=playlist_items)
    default_result = handler({"channelIds": ["UC123"]})
    assert playlist_calls == [{"part": "contentDetails", "playlistId": "UU123", "maxResults": 1}]
    assert default_result["results"][0]["latestVideoPublishedAt"] == "2026-03-01T12:00:00Z"
    assert default_result["results"][0]["enrichment"] == {"status": "complete"}

    playlist_calls.clear()
    selected_result = handler({"channelIds": ["UC123"], "parts": ["contentDetails"], "includeLatestUpload": False})
    item = selected_result["results"][0]
    assert playlist_calls == []
    assert item["contentDetails"] == {"uploadsPlaylistId": "UU123"}
    assert "title" not in item
    assert "normalizedMetadata" not in item
    assert item["enrichment"] == {"status": "not_requested"}
    assert "latestVideoPublishedAt" not in item
    assert "contentDetails.uploadsPlaylistId" in item["fieldProvenance"]


def test_batch_channel_details_preserves_available_items_for_unavailable_and_partial_outcomes():
    """Keep ordered usable items when one ID is absent or enrichment fails."""
    from mcp_server.tools.youtube_common.playlist_items import PlaylistItemsListToolError
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channels_handler

    payload = {
        "items": [
            {
                "id": "UC123",
                "snippet": {"title": "Available"},
                "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}},
            }
        ]
    }

    def playlist_items(_arguments):
        """Raise a sanitized capacity failure for the available item.

        :param _arguments: Ignored lower-level playlist request.
        :raises PlaylistItemsListToolError: Always raised for partial-outcome coverage.
        """
        raise PlaylistItemsListToolError("hidden", category="quota_exhausted", details={"api_key": "secret", "raw_body": "hidden"})

    result = build_channels_get_channels_handler(channels=lambda _arguments: payload, playlist_items=playlist_items)(
        {"channelIds": ["UC123", "UC404"]}
    )

    assert [item["channelId"] for item in result["results"]] == ["UC123", "UC404"]
    assert result["results"][0]["outcome"] == {
        "status": "partial",
        "category": "partial_enrichment_failure",
        "causeCategory": "quota_exhaustion",
    }
    assert result["results"][1]["outcome"] == {"status": "unavailable", "category": "unavailable_resource"}
    assert result["summary"] == {"requested": 2, "successful": 0, "unavailable": 1, "partiallyEnriched": 1}
    assert "secret" not in str(result)


def test_batch_channel_details_maps_bulk_core_errors_without_source_diagnostics():
    """Expose safe request-wide failures when the shared core lookup fails."""
    from mcp_server.tools.youtube_common.channels import ChannelsListToolError
    from mcp_server.tools.youtube_composed.channels import ChannelsGetChannelsToolError, build_channels_get_channels_handler

    def failing_channels(_arguments):
        """Raise a lower-level failure containing unsafe diagnostics.

        :param _arguments: Ignored lower-level bulk request.
        :raises ChannelsListToolError: Always raised for safe mapping coverage.
        """
        raise ChannelsListToolError("hidden", category="quota_exhausted", details={"api_key": "secret", "raw_body": "hidden"})

    with pytest.raises(ChannelsGetChannelsToolError) as exc_info:
        build_channels_get_channels_handler(channels=failing_channels)({"channelIds": ["UC123"]})
    assert exc_info.value.category == "quota_exhaustion"
    assert "secret" not in str(exc_info.value.details)
    assert "hidden" not in str(exc_info.value.details)


def test_channel_search_validates_query_and_query_only_options():
    """Normalize the public query-only channel-search request safely."""
    from mcp_server.tools.youtube_composed.channels import ChannelsSearchChannelsToolError, validate_channels_search_channels_arguments

    assert validate_channels_search_channels_arguments({"query": " creator "}) == {
        "query": "creator",
        "maxResults": 10,
        "creatorOnly": False,
        "sortBy": "relevance",
    }
    for arguments, field in (({}, "query"), ({"query": " "}, "query"), ({"query": "creator", "unknown": True}, "unknown")):
        with pytest.raises(ChannelsSearchChannelsToolError) as exc_info:
            validate_channels_search_channels_arguments(arguments)
        assert exc_info.value.category == "invalid_parameters"
        assert exc_info.value.details["field"] == field


def test_channel_search_query_only_normalizes_distinct_candidates_and_preserves_base_context():
    """Return query-only normalized channel candidates without enrichment calls."""
    from mcp_server.tools.youtube_composed.channels import build_channels_search_channels_handler

    calls = []

    def search(arguments):
        """Record the base request and return one duplicate public channel.

        :param arguments: Lower-level search arguments.
        :return: Base channel candidates with a continuation token.
        """
        calls.append(arguments)
        return {
            "items": [
                {"id": {"channelId": "UC1"}, "snippet": {"title": "First", "description": "Public"}},
                {"id": {"channelId": "UC1"}, "snippet": {"title": "Duplicate"}},
                {"id": {"channelId": "UC2"}, "snippet": {"title": "Second"}},
            ],
            "nextPageToken": "NEXT",
        }

    result = build_channels_search_channels_handler(search=search, channels=lambda _arguments: pytest.fail("unexpected enrichment"))(
        {"query": " creator ", "maxResults": 2, "channelType": "show"}
    )

    assert calls == [{"part": "snippet", "q": "creator", "type": "channel", "maxResults": 2, "order": "relevance", "channelType": "show"}]
    assert [item["channelId"] for item in result["items"]] == ["UC1", "UC2"]
    assert result["items"][0]["title"] == "First"
    assert result["appliedInputs"] == {"query": "creator", "maxResults": 2, "channelType": "show", "creatorOnly": False, "sortBy": "relevance"}
    assert result["nextPageToken"] == "NEXT"
    assert result["fieldProvenance"]["channelId"] == "raw_upstream"


def test_channel_search_maps_base_search_failure_without_lower_layer_details():
    """Translate a lower-level base-search failure to the public safe taxonomy."""
    from mcp_server.tools.youtube_common.search import SearchListToolError
    from mcp_server.tools.youtube_composed.channels import ChannelsSearchChannelsToolError, build_channels_search_channels_handler

    def failing_search(_arguments):
        """Raise a lower-level failure containing unsafe details.

        :param _arguments: Ignored base-search request.
        :raises SearchListToolError: Always raised for mapping coverage.
        """
        raise SearchListToolError("hidden", category="quota_exhausted", details={"api_key": "secret"})

    with pytest.raises(ChannelsSearchChannelsToolError) as exc_info:
        build_channels_search_channels_handler(search=failing_search)({"query": "creator"})
    assert exc_info.value.category == "quota_exhaustion"
    assert "secret" not in str(exc_info.value.details)


def test_channel_search_refines_with_bounded_public_channel_and_activity_enrichment():
    """Apply subscriber, activity, and creator filters using public enrichment."""
    from mcp_server.tools.youtube_composed.channels import build_channels_search_channels_handler

    channel_calls = []
    playlist_calls = []

    def search(_arguments):
        """Return three public base candidates.

        :param _arguments: Ignored base-search request.
        :return: Public channel references.
        """
        return {
            "items": [
                {"id": {"channelId": "UC1"}, "snippet": {"title": "Creator Sam"}},
                {"id": {"channelId": "UC2"}, "snippet": {"title": "Small Brand"}},
                {"id": {"channelId": "UC3"}, "snippet": {"title": "Creator Old"}},
            ]
        }

    def channels(arguments):
        """Return public channel metadata for the batched selector.

        :param arguments: Lower-level channels-list request.
        :return: Public channel profile/statistics records.
        """
        channel_calls.append(arguments)
        return {
            "items": [
                {"id": "UC1", "snippet": {"title": "Creator Sam"}, "statistics": {"subscriberCount": "25"}, "contentDetails": {"relatedPlaylists": {"uploads": "UU1"}}},
                {"id": "UC2", "snippet": {"title": "Small Brand"}, "statistics": {"subscriberCount": "10"}, "contentDetails": {"relatedPlaylists": {"uploads": "UU2"}}},
                {"id": "UC3", "snippet": {"title": "Creator Old"}, "statistics": {"subscriberCount": "40"}, "contentDetails": {"relatedPlaylists": {"uploads": "UU3"}}},
            ]
        }

    def playlist_items(arguments):
        """Return per-channel public latest-upload activity.

        :param arguments: Lower-level uploads-playlist request.
        :return: One public publication timestamp.
        """
        playlist_calls.append(arguments)
        timestamp = {"UU1": "2026-02-01T00:00:00Z", "UU2": "2026-02-02T00:00:00Z", "UU3": "2025-01-01T00:00:00Z"}[arguments["playlistId"]]
        return {"items": [{"contentDetails": {"videoPublishedAt": timestamp}}]}

    result = build_channels_search_channels_handler(search=search, channels=channels, playlist_items=playlist_items)(
        {
            "query": "creator",
            "minSubscribers": 20,
            "lastUploadAfter": "2026-01-01T00:00:00Z",
            "creatorOnly": True,
        }
    )

    assert channel_calls == [{"part": "snippet,statistics,contentDetails", "id": "UC1,UC2,UC3"}]
    assert playlist_calls == [
        {"part": "contentDetails", "playlistId": "UU1", "maxResults": 1},
        {"part": "contentDetails", "playlistId": "UU2", "maxResults": 1},
        {"part": "contentDetails", "playlistId": "UU3", "maxResults": 1},
    ]
    assert [item["channelId"] for item in result["items"]] == ["UC1"]
    assert result["items"][0]["statistics"] == {"subscriberCount": "25"}
    assert result["items"][0]["latestVideoPublishedAt"] == "2026-02-01T00:00:00Z"
    assert result["items"][0]["heuristics"]["creatorClassification"] == "creator"


def test_channel_search_fails_safely_when_required_enrichment_is_unavailable_for_every_candidate():
    """Reject an unverified filtered collection instead of returning base candidates."""
    from mcp_server.tools.youtube_composed.channels import ChannelsSearchChannelsToolError, build_channels_search_channels_handler

    with pytest.raises(ChannelsSearchChannelsToolError) as exc_info:
        build_channels_search_channels_handler(
            search=lambda _arguments: {"items": [{"id": {"channelId": "UC1"}, "snippet": {"title": "Creator"}}]},
            channels=lambda _arguments: {"items": []},
        )({"query": "creator", "minSubscribers": 1})

    assert exc_info.value.category == "partial_enrichment_failure"
    assert exc_info.value.details == {"excludedCandidateCount": 1, "reasons": ["channel_metadata_unavailable"], "requiredFor": ["minSubscribers"]}


def test_channel_search_applies_documented_rankings_after_filters_with_stable_ties():
    """Rank enriched public channels deterministically after filtering."""
    from mcp_server.tools.youtube_composed.channels import build_channels_search_channels_handler

    def search(_arguments):
        """Return candidates in deterministic base-search order.

        :param _arguments: Ignored base-search request.
        :return: Three public channel references.
        """
        return {
            "items": [
                {"id": {"channelId": "UCH"}, "snippet": {"title": "Large Brand"}},
                {"id": {"channelId": "UCL"}, "snippet": {"title": "Creator Small"}},
                {"id": {"channelId": "UCM"}, "snippet": {"title": "Creator Medium"}},
            ]
        }

    def channels(_arguments):
        """Return ranking metadata for every base candidate.

        :param _arguments: Ignored batched channel request.
        :return: Public profile, statistics, and uploads-playlist data.
        """
        return {
            "items": [
                {"id": "UCH", "snippet": {"title": "Large Brand"}, "statistics": {"subscriberCount": "100"}, "contentDetails": {"relatedPlaylists": {"uploads": "UUH"}}},
                {"id": "UCL", "snippet": {"title": "Creator Small"}, "statistics": {"subscriberCount": "10"}, "contentDetails": {"relatedPlaylists": {"uploads": "UUL"}}},
                {"id": "UCM", "snippet": {"title": "Creator Medium"}, "statistics": {"subscriberCount": "50"}, "contentDetails": {"relatedPlaylists": {"uploads": "UUM"}}},
            ]
        }

    def playlist_items(arguments):
        """Return latest public activity for one uploads playlist.

        :param arguments: Lower-level activity request.
        :return: One activity timestamp.
        """
        timestamp = {"UUH": "2026-01-01T00:00:00Z", "UUL": "2026-03-01T00:00:00Z", "UUM": "2026-02-01T00:00:00Z"}[arguments["playlistId"]]
        return {"items": [{"contentDetails": {"videoPublishedAt": timestamp}}]}

    handler = build_channels_search_channels_handler(search=search, channels=channels, playlist_items=playlist_items)

    expected_orders = {
        "relevance": ["UCH", "UCL", "UCM"],
        "subscribers_asc": ["UCL", "UCM", "UCH"],
        "subscribers_desc": ["UCH", "UCM", "UCL"],
        "indie_priority": ["UCL", "UCM", "UCH"],
        "recent_activity": ["UCL", "UCM", "UCH"],
    }
    for sort_by, expected in expected_orders.items():
        result = handler({"query": "creator", "sortBy": sort_by})
        assert [item["channelId"] for item in result["items"]] == expected

    capped = handler({"query": "creator", "minSubscribers": 20, "sortBy": "subscribers_asc", "maxResults": 1})
    assert [item["channelId"] for item in capped["items"]] == ["UCM"]


def test_creator_discovery_validates_groups_and_samples_matched_videos():
    """Group matching videos by earliest public channel occurrence."""
    from mcp_server.tools.youtube_composed.channels import build_channels_find_creators_handler, validate_channels_find_creators_arguments

    assert validate_channels_find_creators_arguments({"query": " creator "}) == {
        "query": "creator", "maxResults": 10, "creatorOnly": False, "sortBy": "relevance", "sampleVideosPerChannel": 0
    }
    calls = []

    def search(arguments):
        """Record the bounded base request and return duplicate channel videos.

        :param arguments: Lower-level public search request.
        :return: Ordered public video search results.
        """
        calls.append(arguments)
        return {"items": [
            {"id": {"videoId": "v1"}, "snippet": {"channelId": "UC1", "channelTitle": "First", "title": "One", "publishedAt": "2026-01-01T00:00:00Z"}},
            {"id": {"videoId": "v2"}, "snippet": {"channelId": "UC1", "channelTitle": "First", "title": "Two"}},
            {"id": {"videoId": "v3"}, "snippet": {"channelId": "UC2", "channelTitle": "Second", "title": "Three"}},
        ], "nextPageToken": "NEXT"}

    result = build_channels_find_creators_handler(search=search)({"query": "creator", "maxResults": 2, "sampleVideosPerChannel": 2})

    assert calls == [{"part": "snippet", "q": "creator", "type": "video", "maxResults": 50, "order": "relevance"}]
    assert [item["channelId"] for item in result["items"]] == ["UC1", "UC2"]
    assert result["items"][0]["matchedVideoBasis"] == {"count": 2, "firstVideoId": "v1"}
    assert [sample["videoId"] for sample in result["items"][0]["sampleVideos"]] == ["v1", "v2"]
    assert result["nextPageToken"] == "NEXT"


def test_creator_discovery_filters_ranks_and_handles_unavailable_enrichment():
    """Apply public refinement before ranking and sample final candidates."""
    from mcp_server.tools.youtube_composed.channels import ChannelsFindCreatorsToolError, build_channels_find_creators_handler

    def search(_arguments):
        """Return ordered topic-matching video candidates.

        :param _arguments: Ignored lower-layer search request.
        :return: Ordered public video search results.
        """
        return {"items": [
            {"id": {"videoId": "high"}, "snippet": {"channelId": "UCH", "channelTitle": "Brand", "title": "High"}},
            {"id": {"videoId": "low1"}, "snippet": {"channelId": "UCL", "channelTitle": "Creator", "title": "Low one"}},
            {"id": {"videoId": "low2"}, "snippet": {"channelId": "UCL", "channelTitle": "Creator", "title": "Low two"}},
        ]}

    def channels(arguments):
        """Return subscriber and public-profile metadata.

        :param arguments: Batched lower-layer channel request.
        :return: Public channel records.
        """
        assert arguments == {"part": "snippet,statistics,contentDetails", "id": "UCH,UCL"}
        return {"items": [
            {"id": "UCH", "snippet": {"title": "Brand"}, "statistics": {"subscriberCount": "100"}},
            {"id": "UCL", "snippet": {"title": "Creator Sam"}, "statistics": {"subscriberCount": "10"}},
        ]}

    result = build_channels_find_creators_handler(search=search, channels=channels)({
        "query": "creator", "sortBy": "subscribers_asc", "sampleVideosPerChannel": 2
    })
    assert [item["channelId"] for item in result["items"]] == ["UCL", "UCH"]
    assert [sample["videoId"] for sample in result["items"][0]["sampleVideos"]] == ["low1", "low2"]

    with pytest.raises(ChannelsFindCreatorsToolError) as exc_info:
        build_channels_find_creators_handler(search=search, channels=lambda _arguments: {"items": []})({"query": "creator", "channelMinSubscribers": 1})
    assert exc_info.value.category == "partial_enrichment_failure"


def test_channels_list_videos_validates_public_request_and_lists_distinct_uploads_in_source_order():
    """Validate and execute one bounded source-ordered channel video listing."""
    from mcp_server.tools.youtube_composed.channels import (
        ChannelsListVideosToolError,
        build_channels_list_videos_handler,
        validate_channels_list_videos_arguments,
    )

    assert validate_channels_list_videos_arguments({"channelId": " UC123 "}) == {"channelId": "UC123", "maxResults": 10}
    assert validate_channels_list_videos_arguments({"channelId": "UC123", "maxResults": 3}) == {"channelId": "UC123", "maxResults": 3}
    for arguments, field in (
        ({}, "channelId"),
        ({"channelId": " "}, "channelId"),
        ({"channelId": "UC123", "maxResults": True}, "maxResults"),
        ({"channelId": "UC123", "maxResults": 1.5}, "maxResults"),
        ({"channelId": "UC123", "maxResults": 0}, "maxResults"),
        ({"channelId": "UC123", "maxResults": 51}, "maxResults"),
        ({"channelId": "UC123", "unexpected": "value"}, "unexpected"),
    ):
        with pytest.raises(ChannelsListVideosToolError) as exc_info:
            validate_channels_list_videos_arguments(arguments)
        assert exc_info.value.category == "invalid_parameters"
        assert exc_info.value.details == {"field": field}

    channel_calls = []
    playlist_calls = []

    def channels(arguments):
        """Record one channel lookup and return its public uploads reference.

        :param arguments: Lower-level public channel-list request.
        :return: One source channel with an uploads collection reference.
        """
        channel_calls.append(arguments)
        return {"items": [{"id": "UC123", "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}}}]}

    def playlist_items(arguments):
        """Record one bounded collection read with duplicate and unusable items.

        :param arguments: Lower-level public playlist-item request.
        :return: Source items in public uploads-collection order.
        """
        playlist_calls.append(arguments)
        return {
            "items": [
                {
                    "snippet": {
                        "resourceId": {"videoId": "v1"},
                        "title": "First",
                        "description": "First description",
                        "thumbnails": {"medium": "https://example.invalid/first"},
                    },
                    "contentDetails": {"videoPublishedAt": "2026-03-01T00:00:00Z"},
                },
                {"snippet": {"resourceId": {"videoId": "v1"}, "title": "Duplicate"}},
                {"snippet": {"title": "Unusable"}},
                {"snippet": {"resourceId": {"videoId": "v2"}, "title": "Second"}},
                {"snippet": {"resourceId": {"videoId": "v3"}, "title": "Third"}},
            ]
        }

    result = build_channels_list_videos_handler(channels=channels, playlist_items=playlist_items)(
        {"channelId": " UC123 ", "maxResults": 3}
    )

    assert channel_calls == [{"part": "contentDetails", "id": "UC123"}]
    assert playlist_calls == [{"part": "snippet,contentDetails", "playlistId": "UU123", "maxResults": 3}]
    assert result["channelId"] == "UC123"
    assert [item["videoId"] for item in result["items"]] == ["v1", "v2", "v3"]
    assert result["items"][0] == {
        "videoId": "v1",
        "title": "First",
        "description": "First description",
        "thumbnails": {"medium": "https://example.invalid/first"},
        "publishedAt": "2026-03-01T00:00:00Z",
    }
    assert result["returnedCount"] == 3
    assert result["maxResults"] == 3


def test_channels_list_videos_returns_successful_empty_collections_without_extra_reads():
    """Keep absent uploads references and empty public collections successful."""
    from mcp_server.tools.youtube_composed.channels import build_channels_list_videos_handler

    playlist_calls = []
    no_uploads = build_channels_list_videos_handler(
        channels=lambda _arguments: {"items": [{"id": "UC123", "contentDetails": {}}]},
        playlist_items=lambda arguments: playlist_calls.append(arguments),
    )({"channelId": "UC123"})
    assert no_uploads["items"] == []
    assert no_uploads["returnedCount"] == 0
    assert playlist_calls == []

    empty_collection = build_channels_list_videos_handler(
        channels=lambda _arguments: {"items": [{"id": "UC123", "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}}}]},
        playlist_items=lambda _arguments: {"items": []},
    )({"channelId": "UC123", "maxResults": 1})
    assert empty_collection["items"] == []
    assert empty_collection["returnedCount"] == 0


def test_channels_list_videos_result_context_discloses_public_source_order_without_ranking():
    """Expose caller-visible ordering and public-content context on results."""
    from mcp_server.tools.youtube_composed.channels import build_channels_list_videos_handler

    result = build_channels_list_videos_handler(
        channels=lambda _arguments: {"items": [{"id": "UC123", "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}}}]},
        playlist_items=lambda _arguments: {"items": [{"snippet": {"resourceId": {"videoId": "v1"}, "title": "First"}}]},
    )({"channelId": "UC123"})

    assert result["appliedInputs"] == {"channelId": "UC123", "maxResults": 10}
    assert result["collectionContext"] == {
        "source": "channel_uploads_collection",
        "ordering": "source_order_at_request_time",
        "rankingApplied": False,
        "publicContentOnly": True,
        "requestTimeVariability": "collection_can_change",
    }
    assert result["fieldProvenance"]["items.videoId"] == "raw_upstream"
    assert result["fieldProvenance"]["collectionContext"] == "normalized"


def test_channels_list_videos_maps_required_lookup_failures_and_discloses_safe_source_omissions():
    """Keep unavailable, source failures, and malformed items safe to callers."""
    from mcp_server.tools.youtube_common.channels import ChannelsListToolError
    from mcp_server.tools.youtube_common.playlist_items import PlaylistItemsListToolError
    from mcp_server.tools.youtube_composed.channels import ChannelsListVideosToolError, build_channels_list_videos_handler

    with pytest.raises(ChannelsListVideosToolError) as core_error:
        build_channels_list_videos_handler(
            channels=lambda _arguments: {"items": []}, playlist_items=lambda _arguments: {"items": []}
        )({"channelId": "UC404"})
    assert core_error.value.category == "unavailable_resource"
    assert core_error.value.details == {"resource": "channel"}

    def quota_limited_channels(_arguments):
        """Raise a lower-level capacity error with unsafe diagnostic content.

        :param _arguments: Ignored lower-level channel-list request.
        :raises ChannelsListToolError: Always raised for safe mapping coverage.
        """
        raise ChannelsListToolError("quota", category="quota_exhausted", details={"api_key": "hidden", "raw_body": "hidden"})

    with pytest.raises(ChannelsListVideosToolError) as quota_error:
        build_channels_list_videos_handler(channels=quota_limited_channels, playlist_items=lambda _arguments: {"items": []})({"channelId": "UC123"})
    assert quota_error.value.category == "quota_exhaustion"
    assert quota_error.value.details == {}

    def unavailable_playlist(_arguments):
        """Raise a required uploads-collection access failure with unsafe details.

        :param _arguments: Ignored lower-level playlist-item request.
        :raises PlaylistItemsListToolError: Always raised for safe mapping coverage.
        """
        raise PlaylistItemsListToolError("denied", category="authentication_failed", details={"api_key": "hidden", "raw_body": "hidden"})

    with pytest.raises(ChannelsListVideosToolError) as playlist_error:
        build_channels_list_videos_handler(
            channels=lambda _arguments: {"items": [{"id": "UC123", "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}}}]},
            playlist_items=unavailable_playlist,
        )({"channelId": "UC123"})
    assert playlist_error.value.category == "authorization_sensitive_data"
    assert playlist_error.value.details == {}

    partial = build_channels_list_videos_handler(
        channels=lambda _arguments: {"items": [{"id": "UC123", "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}}}]},
        playlist_items=lambda _arguments: {"items": [{"snippet": {"title": "Hidden", "api_key": "hidden"}}, {"snippet": {"resourceId": {"videoId": "v1"}, "title": "Visible"}}]},
    )({"channelId": "UC123"})
    assert partial["items"] == [{"videoId": "v1", "title": "Visible"}]
    assert partial["partialAvailability"] == {"status": "partial", "omittedItemCount": 1, "reasons": ["unusable_source_item"]}
    assert partial["fieldProvenance"]["partialAvailability"] == "normalized"
    assert "hidden" not in str(partial)


def test_channels_list_playlists_validates_and_normalizes_a_verified_channel_listing():
    """Validate, verify, and normalize a bounded channel playlist listing.

    :return: ``None`` after asserting the public listing contract.
    """
    from mcp_server.tools.youtube_composed.channels import (
        ChannelsListPlaylistsToolError,
        build_channels_list_playlists_handler,
        validate_channels_list_playlists_arguments,
    )

    assert validate_channels_list_playlists_arguments({"channelId": " UC123 "}) == {"channelId": "UC123", "maxResults": 25}
    for arguments, field in (({}, "channelId"), ({"channelId": " "}, "channelId"), ({"channelId": "UC123", "maxResults": 0}, "maxResults"), ({"channelId": "UC123", "maxResults": 51}, "maxResults"), ({"channelId": "UC123", "maxResults": True}, "maxResults"), ({"channelId": "UC123", "pageToken": "next"}, "pageToken")):
        with pytest.raises(ChannelsListPlaylistsToolError) as error:
            validate_channels_list_playlists_arguments(arguments)
        assert error.value.details == {"field": field}

    calls = []
    def channels(arguments):
        """Record the one public channel verification.

        :param arguments: Lower-level channel-list arguments.
        :return: One verified public channel.
        """
        calls.append(("channels", arguments))
        return {"items": [{"id": "UC123"}]}
    def playlists(arguments):
        """Record the one ordered public playlist listing.

        :param arguments: Lower-level playlist-list arguments.
        :return: Ordered playlist source records.
        """
        calls.append(("playlists", arguments))
        return {"items": [{"id": "PL1", "snippet": {"title": "First", "description": "One"}, "contentDetails": {"itemCount": 2}, "status": {"privacyStatus": "public"}}, {"id": "PL2", "snippet": {"title": "Second"}}, {"id": "PL3", "snippet": {}}]}

    result = build_channels_list_playlists_handler(channels=channels, playlists=playlists)({"channelId": " UC123 ", "maxResults": 2})
    assert calls == [("channels", {"part": "id", "id": "UC123"}), ("playlists", {"part": "snippet,contentDetails,status", "channelId": "UC123", "maxResults": 2})]
    assert result["items"] == [{"playlistId": "PL1", "title": "First", "description": "One", "itemCount": 2, "privacyStatus": "public"}, {"playlistId": "PL2", "title": "Second"}]
    assert result["returnedCount"] == 2
    assert result["appliedLimit"] == 2
    assert result["collectionContext"]["ordering"] == "source_order_at_request_time"
    assert result["collectionContext"]["rankingApplied"] is False
    assert result["fieldProvenance"]["items.playlistId"] == "raw_upstream"


def test_channels_list_playlists_keeps_empty_unavailable_and_failures_distinct():
    """Keep successful emptiness and sanitized failures caller-distinguishable.

    :return: ``None`` after asserting safe listing outcomes.
    """
    from mcp_server.tools.youtube_common.playlists import PlaylistsListToolError
    from mcp_server.tools.youtube_composed.channels import ChannelsListPlaylistsToolError, build_channels_list_playlists_handler

    empty = build_channels_list_playlists_handler(channels=lambda _arguments: {"items": [{"id": "UC123"}]}, playlists=lambda _arguments: {"items": []})({"channelId": "UC123"})
    assert empty["items"] == []
    with pytest.raises(ChannelsListPlaylistsToolError) as unavailable:
        build_channels_list_playlists_handler(channels=lambda _arguments: {"items": []}, playlists=lambda _arguments: {"items": []})({"channelId": "UC404"})
    assert unavailable.value.category == "unavailable_resource"
    def denied(_arguments):
        """Raise an access failure with unsafe lower-layer details.

        :param _arguments: Ignored lower-layer playlist-list arguments.
        :raises PlaylistsListToolError: Always raised for safe mapping coverage.
        """
        raise PlaylistsListToolError("hidden", category="authorization_failed", details={"api_key": "hidden"})
    with pytest.raises(ChannelsListPlaylistsToolError) as restricted:
        build_channels_list_playlists_handler(channels=lambda _arguments: {"items": [{"id": "UC123"}]}, playlists=denied)({"channelId": "UC123"})
    assert restricted.value.category == "authorization_sensitive_data"
    assert "hidden" not in str(restricted.value.details)


def test_channels_search_content_validates_and_normalizes_one_direct_channel_search():
    """Execute one direct public video search scoped to the requested channel.

    The fixture includes duplicate, malformed, and mismatched source records to
    prove that only safely usable requested-channel items are returned.
    """
    from mcp_server.tools.youtube_composed.channels import (
        ChannelsSearchContentToolError,
        build_channels_search_content_handler,
        validate_channels_search_content_arguments,
    )

    assert validate_channels_search_content_arguments({"channelId": " UC123 ", "query": " release notes "}) == {
        "channelId": "UC123",
        "query": "release notes",
        "maxResults": 10,
        "order": "relevance",
    }
    for arguments, field in (
        (None, "arguments"),
        ({}, "channelId"),
        ({"channelId": "UC123"}, "query"),
        ({"channelId": " ", "query": "release"}, "channelId"),
        ({"channelId": "UC123", "query": " ", "unexpected": True}, "unexpected"),
    ):
        with pytest.raises(ChannelsSearchContentToolError) as error:
            validate_channels_search_content_arguments(arguments)
        assert error.value.category == "invalid_parameters"
        assert error.value.details == {"field": field}

    calls = []

    def search(arguments):
        """Record the direct lower-layer request and return controlled records.

        :param arguments: Lower-layer public search request.
        :return: Ordered source records including unusable candidates.
        """
        calls.append(arguments)
        return {
            "items": [
                {
                    "id": {"videoId": "v1"},
                    "snippet": {
                        "channelId": "UC123",
                        "channelTitle": "Example",
                        "title": "First",
                        "description": "Public description",
                        "publishedAt": "2026-01-01T00:00:00Z",
                        "thumbnails": {"medium": "https://example.invalid/first"},
                    },
                },
                {"id": {"videoId": "v1"}, "snippet": {"channelId": "UC123", "title": "Duplicate"}},
                {"id": {"videoId": "v2"}, "snippet": {"channelId": "UC999", "title": "Mismatched"}},
                {"id": {}, "snippet": {"channelId": "UC123", "title": "Unusable"}},
            ]
        }

    result = build_channels_search_content_handler(search=search)({"channelId": " UC123 ", "query": " release notes "})

    assert calls == [{"part": "snippet", "q": "release notes", "channelId": "UC123", "type": "video", "maxResults": 10, "order": "relevance"}]
    assert result["items"] == [{"videoId": "v1", "contentType": "video", "title": "First", "description": "Public description", "publishedAt": "2026-01-01T00:00:00Z", "channelId": "UC123", "channelTitle": "Example", "thumbnails": {"medium": "https://example.invalid/first"}}]
    assert result["returnedCount"] == 1
    assert result["appliedInputs"] == {"channelId": "UC123", "query": "release notes", "maxResults": 10, "order": "relevance"}
    assert result["searchContext"]["matching"] == "direct_upstream_search"
    assert result["searchContext"]["rankingApplied"] is False
    assert result["partialAvailability"] == {"status": "partial", "omittedItemCount": 3, "reasons": ["unusable_or_out_of_scope_source_item"]}
    assert result["fieldProvenance"]["items.videoId"] == "raw_upstream"
    assert result["fieldProvenance"]["searchContext"] == "normalized"


def test_channels_search_content_returns_empty_and_maps_safe_lower_layer_errors():
    """Keep empty success distinct from sanitized required-search failures."""
    from mcp_server.tools.youtube_common.search import SearchListToolError
    from mcp_server.tools.youtube_composed.channels import ChannelsSearchContentToolError, build_channels_search_content_handler

    empty = build_channels_search_content_handler(search=lambda _arguments: {"items": []})({"channelId": "UC123", "query": "absent"})
    assert empty["items"] == []
    assert empty["returnedCount"] == 0
    assert empty["channelId"] == "UC123"

    def quota_limited(_arguments):
        """Raise a lower-layer quota error with unsafe diagnostic details.

        :param _arguments: Ignored lower-layer search request.
        :raises SearchListToolError: Always raised for safe mapping coverage.
        """
        raise SearchListToolError("quota", category="quota_exhausted", details={"api_key": "hidden", "raw_body": "hidden"})

    with pytest.raises(ChannelsSearchContentToolError) as error:
        build_channels_search_content_handler(search=quota_limited)({"channelId": "UC123", "query": "release"})
    assert error.value.category == "quota_exhaustion"
    assert error.value.details == {}


def test_channels_search_content_applies_bounded_limits_and_direct_source_ordering():
    """Validate result controls and forward them without local ranking."""
    from mcp_server.tools.youtube_composed.channels import (
        ChannelsSearchContentToolError,
        build_channels_search_content_handler,
        validate_channels_search_content_arguments,
    )

    assert validate_channels_search_content_arguments({"channelId": "UC123", "query": "topic", "maxResults": 1, "order": "date"}) == {
        "channelId": "UC123",
        "query": "topic",
        "maxResults": 1,
        "order": "date",
    }
    for arguments, field in (
        ({"channelId": "UC123", "query": "topic", "maxResults": True}, "maxResults"),
        ({"channelId": "UC123", "query": "topic", "maxResults": 0}, "maxResults"),
        ({"channelId": "UC123", "query": "topic", "maxResults": 51}, "maxResults"),
        ({"channelId": "UC123", "query": "topic", "order": "title"}, "order"),
    ):
        with pytest.raises(ChannelsSearchContentToolError) as error:
            validate_channels_search_content_arguments(arguments)
        assert error.value.details == {"field": field}

    calls = []

    def search(arguments):
        """Record explicit controls and return more records than the final cap.

        :param arguments: Lower-layer public channel-video search request.
        :return: Ordered matching public video records.
        """
        calls.append(arguments)
        return {"items": [
            {"id": {"videoId": "v1"}, "snippet": {"channelId": "UC123", "title": "First"}},
            {"id": {"videoId": "v2"}, "snippet": {"channelId": "UC123", "title": "Second"}},
        ]}

    result = build_channels_search_content_handler(search=search)({"channelId": "UC123", "query": "topic", "maxResults": 1, "order": "viewCount"})
    assert calls == [{"part": "snippet", "q": "topic", "channelId": "UC123", "type": "video", "maxResults": 1, "order": "viewCount"}]
    assert [item["videoId"] for item in result["items"]] == ["v1"]
    assert result["searchContext"]["order"] == "viewCount"
    assert result["searchContext"]["ordering"] == "upstream_order"
    assert result["searchContext"]["rankingApplied"] is False


def test_channels_search_content_validates_and_forwards_language_as_relevance_hint():
    """Forward only a valid optional language preference to the source search."""
    from mcp_server.tools.youtube_composed.channels import (
        ChannelsSearchContentToolError,
        build_channels_search_content_handler,
        validate_channels_search_content_arguments,
    )

    assert validate_channels_search_content_arguments({"channelId": "UC123", "query": "topic", "language": " en-US "}) == {
        "channelId": "UC123",
        "query": "topic",
        "maxResults": 10,
        "order": "relevance",
        "language": "en-US",
    }
    for language in ("", " ", "english", "en_US", 3):
        with pytest.raises(ChannelsSearchContentToolError) as error:
            validate_channels_search_content_arguments({"channelId": "UC123", "query": "topic", "language": language})
        assert error.value.category == "invalid_parameters"
        assert error.value.details == {"field": "language"}

    calls = []

    def search(arguments):
        """Record the relevance hint without imposing a content-language filter.

        :param arguments: Lower-layer public channel-video search request.
        :return: Empty public source result.
        """
        calls.append(arguments)
        return {"items": []}

    result = build_channels_search_content_handler(search=search)({"channelId": "UC123", "query": "topic", "language": "en-US"})
    assert calls == [{"part": "snippet", "q": "topic", "channelId": "UC123", "type": "video", "maxResults": 10, "order": "relevance", "relevanceLanguage": "en-US"}]
    assert result["appliedInputs"]["language"] == "en-US"
    assert result["searchContext"]["languageRefinesRelevance"] is True
