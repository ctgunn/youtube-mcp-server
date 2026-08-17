"""Contract tests for the public normalized playlist-detail tool."""


def test_playlist_details_metadata_is_concrete_and_exposes_one_input_schema():
    """Require executable discovery metadata for one playlist detail lookup.

    :return: ``None`` after validating the concrete descriptor shape.
    """
    from mcp_server.tools.youtube_composed.playlists import build_playlists_get_playlist_tool_descriptor

    descriptor = build_playlists_get_playlist_tool_descriptor()
    metadata = descriptor["metadata"]

    assert descriptor["name"] == "playlists_getPlaylist"
    assert descriptor["inputSchema"] == {
        "type": "object",
        "required": ["playlistId"],
        "properties": {"playlistId": {"type": "string", "minLength": 1}},
        "additionalProperties": False,
    }
    assert metadata["compositionBoundary"]["kind"] == "normalized_retrieval"
    assert metadata["lowerLayerDependencies"] == ["playlists.list"]
    assert "representativeOnly" not in metadata


def test_playlist_details_contract_documents_fields_provenance_and_scope():
    """Require caller-visible field interpretation and playlist-item guidance.

    :return: ``None`` after validating response metadata.
    """
    from mcp_server.tools.youtube_composed.playlists import build_playlists_get_playlist_metadata

    metadata = build_playlists_get_playlist_metadata()
    fields = {field["fieldName"]: field for field in metadata["responseFields"]}

    assert set(fields) >= {
        "playlistId",
        "title",
        "description",
        "channelId",
        "channelTitle",
        "publishedAt",
        "thumbnails",
        "privacyStatus",
        "itemCount",
        "fieldProvenance",
        "contentScope",
    }
    assert fields["playlistId"]["category"] == "raw_upstream"
    assert fields["title"]["category"] == "normalized"
    assert metadata["compositionBoundary"]["boundedness"] == "one playlist; one lookup"
    assert metadata["contentScope"]["playlistItemsIncluded"] is False
    assert metadata["contentScope"]["playlistItemsTool"] == "playlists_getPlaylistItems"
    assert metadata["stateVariability"] == "Public metadata is observed at request time and may change later."


def test_playlist_details_contract_documents_safe_categories_without_unsafe_metadata():
    """Require every public error category and safe caller guidance.

    :return: ``None`` after validating safe discovery metadata.
    """
    from mcp_server.tools.youtube_composed.playlists import build_playlists_get_playlist_metadata

    metadata = build_playlists_get_playlist_metadata()

    assert metadata["errorCategories"] == [
        "invalid_parameters",
        "unavailable_resource",
        "authorization_sensitive_data",
        "quota_exhaustion",
        "upstream_failure",
    ]
    assert metadata["errorGuidance"]["unavailable_resource"] == "Use a different accessible playlist identifier."
    assert "representativeOnly" not in metadata
    assert "token" not in str(metadata).lower()
    assert "stack" not in str(metadata).lower()


def test_playlist_items_contract_is_concrete_and_documents_bounded_source_ordered_results():
    """Require executable discovery metadata for bounded playlist item retrieval.

    :return: ``None`` after validating the public descriptor and metadata.
    """
    from mcp_server.tools.youtube_composed.playlists import build_playlists_get_playlist_items_tool_descriptor

    descriptor = build_playlists_get_playlist_items_tool_descriptor()
    metadata = descriptor["metadata"]

    assert descriptor["name"] == "playlists_getPlaylistItems"
    assert descriptor["inputSchema"] == {
        "type": "object",
        "required": ["playlistId"],
        "properties": {
            "playlistId": {"type": "string", "minLength": 1},
            "maxResults": {"type": "integer", "minimum": 1, "maximum": 50, "default": 25},
        },
        "additionalProperties": False,
    }
    assert metadata["compositionBoundary"]["kind"] == "source_ordered_collection"
    assert metadata["lowerLayerDependencies"] == ["playlistItems.list"]
    assert metadata["compositionBoundary"]["boundedness"] == "one playlist; one listing; 1-50 items"
    assert metadata["collectionPolicy"]["paginationTraversed"] is False
    assert metadata["collectionPolicy"]["emptyResult"] == "successful_empty_collection"
    assert metadata["collectionPolicy"]["unavailableEntry"] == "retain_and_mark_unavailable"
    assert "representativeOnly" not in metadata


def test_playlist_items_contract_documents_provenance_limits_and_safe_categories():
    """Require caller-visible field, limit, availability, and error semantics.

    :return: ``None`` after validating safe public metadata.
    """
    from mcp_server.tools.youtube_composed.playlists import build_playlists_get_playlist_items_metadata

    metadata = build_playlists_get_playlist_items_metadata()
    fields = {field["fieldName"]: field for field in metadata["responseFields"]}

    assert fields["items.playlistItemId"]["category"] == "raw_upstream"
    assert fields["items.availabilityState"]["category"] == "normalized"
    assert fields["isLimited"]["category"] == "normalized"
    assert metadata["limitPolicy"] == {"default": 25, "minimum": 1, "maximum": 50, "continuationInputAccepted": False}
    assert metadata["errorCategories"] == [
        "invalid_parameters",
        "unavailable_resource",
        "authorization_sensitive_data",
        "quota_exhaustion",
        "upstream_failure",
    ]
    assert metadata["errorGuidance"]["unavailable_resource"] == "Use a different accessible playlist identifier."
    assert "token" not in str(metadata).lower()
    assert "stack" not in str(metadata).lower()


def test_playlist_search_contract_is_concrete_and_documents_composite_bounded_search():
    """Require discovery metadata for the bounded playlist-item search tool.

    :return: ``None`` after validating strict inputs, coverage, matching, and safe errors.
    """
    from mcp_server.tools.youtube_composed.playlists import build_playlists_search_items_tool_descriptor

    descriptor = build_playlists_search_items_tool_descriptor()
    metadata = descriptor["metadata"]
    fields = {field["fieldName"]: field for field in metadata["responseFields"]}

    assert descriptor["name"] == "playlists_searchItems"
    assert descriptor["inputSchema"] == {
        "type": "object",
        "required": ["playlistId", "query"],
        "properties": {
            "playlistId": {"type": "string", "minLength": 1},
            "query": {"type": "string", "minLength": 1},
            "maxResults": {"type": "integer", "minimum": 1, "maximum": 50, "default": 25},
        },
        "additionalProperties": False,
    }
    assert metadata["compositionBoundary"]["kind"] == "bounded_playlist_item_literal_search"
    assert metadata["compositionBoundary"]["boundedness"] == "one playlist lookup; up to 10 item pages; at most 500 inspected entries; 1-50 returned matches"
    assert metadata["lowerLayerDependencies"] == ["playlists.list", "playlistItems.list", "in_server_literal_search"]
    assert metadata["limitPolicy"] == {"default": 25, "minimum": 1, "maximum": 50, "continuationInputAccepted": False}
    assert metadata["searchPolicy"]["matching"] == "case_insensitive_literal_phrase"
    assert metadata["searchPolicy"]["searchableFields"] == ["title", "description", "channelTitle", "videoId"]
    assert metadata["searchPolicy"]["paginationTraversed"] is True
    assert metadata["searchPolicy"]["maximumInspectedEntries"] == 500
    assert fields["items.matchingFields"]["category"] == "normalized"
    assert fields["searchCoverage"]["category"] == "normalized"
    assert metadata["errorCategories"] == [
        "invalid_parameters",
        "unavailable_resource",
        "authorization_sensitive_data",
        "quota_exhaustion",
        "upstream_failure",
    ]
    assert "representativeOnly" not in metadata
    assert "token" not in str(metadata).lower()
