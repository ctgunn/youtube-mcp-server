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
