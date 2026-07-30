"""Representative non-executing higher-level YouTube contract examples.

Examples in this module prove shared contract coverage across videos, channels,
playlists, and transcripts without invoking lower-layer tools or upstream APIs.
"""

from __future__ import annotations

from typing import Any

from mcp_server.tools.youtube_composed.contracts import ToolContract, ToolFamily
from mcp_server.tools.youtube_composed.conventions import (
    CompositionBoundary,
    HeuristicDisclosure,
    ResponseFieldProvenance,
)


def _field(field_name: str, category: str, source: str, limitations: str = "") -> dict[str, str]:
    """Build representative response-field provenance metadata.

    :param field_name: Public result field name.
    :param category: Provenance category for the field.
    :param source: Lower-layer, normalized, or inferred source.
    :param limitations: Optional caller-facing limitations.
    :return: JSON-compatible field provenance metadata.
    """
    return ResponseFieldProvenance(
        field_name=field_name,
        category=category,
        source=source,
        caller_guidance=f"Interpret {field_name} as {category}.",
        limitations=limitations,
    ).to_metadata()


def _heuristic(name: str, basis: str, limitations: str, applicable_tools: tuple[str, ...]) -> dict[str, Any]:
    """Build representative heuristic disclosure metadata.

    :param name: Heuristic field or signal name.
    :param basis: Signals or evidence used for the heuristic.
    :param limitations: Caller-facing uncertainty notes.
    :param applicable_tools: Planned tools where the heuristic can appear.
    :return: JSON-compatible heuristic disclosure metadata.
    """
    return HeuristicDisclosure(
        name=name,
        basis=basis,
        limitations=limitations,
        applicable_tools=applicable_tools,
        safe_usage_guidance="Use as an approximate aid, not as raw upstream fact.",
    ).to_metadata()


def _contract(
    *,
    tool_name: str,
    family: ToolFamily,
    description: str,
    parameters: tuple[str, ...],
    response_fields: tuple[dict[str, Any], ...],
    composition_kind: str,
    lower_layer_dependencies: tuple[str, ...],
    auth_and_quota_notes: tuple[str, ...],
    partial_result_policy: str,
    error_categories: tuple[str, ...],
    ranking_and_filtering: tuple[str, ...] = (),
    heuristics: tuple[dict[str, Any], ...] = (),
    caveats: tuple[str, ...] = (),
) -> ToolContract:
    """Build a representative non-executing higher-level tool contract.

    :param tool_name: Planned public YouTube tool name.
    :param family: Owning Layer 3 family.
    :param description: Caller-facing summary.
    :param parameters: Shared parameter convention names used by the tool.
    :param response_fields: Representative response provenance fields.
    :param composition_kind: Composition boundary kind.
    :param lower_layer_dependencies: Lower-layer operations referenced.
    :param auth_and_quota_notes: User-visible auth and quota notes.
    :param partial_result_policy: Partial-result behavior.
    :param error_categories: Safe error categories.
    :param ranking_and_filtering: Optional ranking or filtering rules.
    :param heuristics: Optional heuristic disclosure metadata.
    :param caveats: Optional caveat notes.
    :return: Validated representative public YouTube contract.
    """
    return ToolContract(
        tool_name=tool_name,
        family=family,
        description=description,
        parameters=parameters,
        response_fields=response_fields,
        composition_boundary=CompositionBoundary(
            kind=composition_kind,
            lower_layer_dependencies=lower_layer_dependencies,
            quota_behavior="Expose lower-layer and composed quota caveats before invocation.",
            auth_sensitivity="Expose authorization-sensitive dependency behavior when relevant.",
            partial_result_policy=partial_result_policy,
            boundedness="bounded by shared parameter conventions",
            caller_caveats=caveats,
        ).to_metadata(),
        lower_layer_dependencies=lower_layer_dependencies,
        auth_and_quota_notes=auth_and_quota_notes,
        partial_result_policy=partial_result_policy,
        error_categories=error_categories,
        review_evidence=("representative_contract", "yt301_shared_contract"),
        ranking_and_filtering=ranking_and_filtering,
        heuristics=heuristics,
        caveats=caveats,
    )


REPRESENTATIVE_TOOL_CONTRACTS: tuple[ToolContract, ...] = (
    _contract(
        tool_name="videos_getVideo",
        family=ToolFamily.VIDEOS,
        description="Return normalized details for one YouTube video.",
        parameters=("videoId", "parts"),
        response_fields=(
            _field("id", "raw_upstream", "videos.list"),
            _field("title", "normalized", "snippet.title"),
        ),
        composition_kind="normalized_retrieval",
        lower_layer_dependencies=("videos.list",),
        auth_and_quota_notes=("Uses videos.list quota and public/private video auth caveats.",),
        partial_result_policy="Return unavailable markers for hidden or missing fields.",
        error_categories=("invalid_parameters", "unavailable_resource", "upstream_failure"),
    ),
    _contract(
        tool_name="videos_searchVideos",
        family=ToolFamily.VIDEOS,
        description="Search videos with optional channel-aware enrichment and ranking.",
        parameters=("query", "maxResults", "order", "channelId", "publishedAfter", "publishedBefore", "sortBy"),
        response_fields=(
            _field("videoId", "raw_upstream", "search.list"),
            _field("channel", "normalized", "channels.list enrichment"),
            _field("rankingScore", "heuristic_inferred", "shared ranking rule", "Approximate ordering signal."),
        ),
        composition_kind="ranked_enrichment",
        lower_layer_dependencies=("search.list", "channels.list"),
        auth_and_quota_notes=("Search quota and optional channel enrichment quota are caller-visible.",),
        partial_result_policy="Return base search results when optional channel enrichment is unavailable.",
        error_categories=("invalid_parameters", "quota_exhaustion", "partial_enrichment_failure"),
        ranking_and_filtering=("sortBy",),
        heuristics=(
            _heuristic(
                "rankingScore",
                "Search rank plus available channel signals.",
                "Approximate and dependent on enrichment availability.",
                ("videos_searchVideos",),
            ),
        ),
    ),
    _contract(
        tool_name="channels_findCreators",
        family=ToolFamily.CHANNELS,
        description="Discover and rank creator channels from search results and channel metadata.",
        parameters=("query", "maxResults", "creatorOnly", "channelMinSubscribers", "channelMaxSubscribers", "sortBy"),
        response_fields=(
            _field("channelId", "raw_upstream", "channels.list"),
            _field("normalizedMetadata", "normalized", "channel resource normalization"),
            _field("creatorSignals", "heuristic_inferred", "creator classification rule", "May produce false positives."),
        ),
        composition_kind="multi_resource_composition",
        lower_layer_dependencies=("search.list", "channels.list"),
        auth_and_quota_notes=("Search plus channel lookup quota must be visible before invocation.",),
        partial_result_policy="Return candidates with missing enrichment markers when channel details are partial.",
        error_categories=("invalid_parameters", "quota_exhaustion", "partial_enrichment_failure"),
        ranking_and_filtering=("creatorOnly", "subscriberBand", "sortBy"),
        heuristics=(
            _heuristic(
                "creatorSignals",
                "Public channel metadata and recent content signals.",
                "Classification is inferred and not an upstream YouTube fact.",
                ("channels_findCreators",),
            ),
        ),
    ),
    _contract(
        tool_name="transcripts_getTranscript",
        family=ToolFamily.TRANSCRIPTS,
        description="Retrieve transcript text for one video in a requested or default language.",
        parameters=("videoId", "language"),
        response_fields=(
            _field("captionTrackId", "raw_upstream", "captions.list"),
            _field("text", "normalized", "captions.download text"),
        ),
        composition_kind="transcript_retrieval",
        lower_layer_dependencies=("captions.list", "captions.download"),
        auth_and_quota_notes=("Official captions may require OAuth-authorized access.",),
        partial_result_policy="Return transcript unavailable when no accessible language track exists.",
        error_categories=("invalid_parameters", "transcript_unavailable", "authorization_sensitive_data"),
        caveats=("Language fallback must be documented before concrete tool implementation.",),
    ),
    _contract(
        tool_name="transcripts_searchTranscript",
        family=ToolFamily.TRANSCRIPTS,
        description="Search transcript text and return matching snippets with timing.",
        parameters=("videoId", "query", "language", "maxMatches"),
        response_fields=(
            _field("matches", "normalized", "transcript text search"),
            _field("matchScore", "heuristic_inferred", "snippet matching rule", "Approximate text relevance."),
        ),
        composition_kind="server_side_filtering",
        lower_layer_dependencies=("captions.list", "captions.download", "in_server_text_search"),
        auth_and_quota_notes=("Transcript retrieval quota and authorization caveats apply before text search.",),
        partial_result_policy="Return no matches when transcript retrieval succeeds but text search finds none.",
        error_categories=("invalid_parameters", "transcript_unavailable", "no_matching_results"),
        ranking_and_filtering=("transcriptMatchLimit",),
        heuristics=(
            _heuristic(
                "matchScore",
                "Text match position and snippet context.",
                "Not a semantic relevance guarantee.",
                ("transcripts_searchTranscript",),
            ),
        ),
    ),
    _contract(
        tool_name="playlists_getPlaylistItems",
        family=ToolFamily.PLAYLISTS,
        description="Return videos contained in one playlist with normalized item summaries.",
        parameters=("playlistId", "maxResults"),
        response_fields=(
            _field("playlistItemId", "raw_upstream", "playlistItems.list"),
            _field("video", "normalized", "playlist item resource normalization"),
        ),
        composition_kind="normalized_retrieval",
        lower_layer_dependencies=("playlistItems.list",),
        auth_and_quota_notes=("Playlist item listing quota and unavailable playlist caveats apply.",),
        partial_result_policy="Return available items with unavailable markers for hidden videos.",
        error_categories=("invalid_parameters", "unavailable_resource", "upstream_failure"),
    ),
    _contract(
        tool_name="playlists_searchItems",
        family=ToolFamily.PLAYLISTS,
        description="Search within playlist items using bounded server-side matching.",
        parameters=("playlistId", "query", "maxResults"),
        response_fields=(
            _field("playlistItemId", "raw_upstream", "playlistItems.list"),
            _field("matchReason", "heuristic_inferred", "playlist item text matching", "Approximate match reason."),
        ),
        composition_kind="server_side_filtering",
        lower_layer_dependencies=("playlistItems.list", "in_server_text_search"),
        auth_and_quota_notes=("Playlist enumeration quota applies before bounded text matching.",),
        partial_result_policy="Return no matches when playlist retrieval succeeds but filtering finds none.",
        error_categories=("invalid_parameters", "no_matching_results", "fan_out_limit_reached"),
        ranking_and_filtering=("sortBy",),
        heuristics=(
            _heuristic(
                "matchReason",
                "Video title, description, or available playlist item text.",
                "Depends on available public item metadata.",
                ("playlists_searchItems",),
            ),
        ),
    ),
    _contract(
        tool_name="playlists_getVideoTranscripts",
        family=ToolFamily.PLAYLISTS,
        description="Retrieve transcripts for videos contained in a playlist with bounded fan-out.",
        parameters=("playlistId", "language", "maxResults"),
        response_fields=(
            _field("playlistItemId", "raw_upstream", "playlistItems.list"),
            _field("transcript", "normalized", "transcript retrieval flow"),
            _field("fanOutSummary", "heuristic_inferred", "bounded fan-out summary", "May omit inaccessible videos."),
        ),
        composition_kind="fan_out",
        lower_layer_dependencies=("playlistItems.list", "captions.list", "captions.download"),
        auth_and_quota_notes=("Playlist and transcript retrieval costs multiply across bounded fan-out.",),
        partial_result_policy="Return per-video transcript status when some videos lack accessible captions.",
        error_categories=("invalid_parameters", "transcript_unavailable", "fan_out_limit_reached"),
        ranking_and_filtering=("fanOutLimit",),
        heuristics=(
            _heuristic(
                "fanOutSummary",
                "Per-video transcript retrieval status.",
                "Summarizes bounded attempts, not full playlist coverage unless all pages are processed.",
                ("playlists_getVideoTranscripts",),
            ),
        ),
    ),
)


def build_representative_tool_descriptor(contract: ToolContract) -> dict[str, Any]:
    """Build an inert descriptor for registration-readiness checks.

    :param contract: Representative Layer 3 tool contract.
    :return: Descriptor containing metadata and a non-executing handler.
    """

    def representative_handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Return representative metadata without executing a public tool.

        :param arguments: Caller-provided representative arguments.
        :return: Non-executing representative result metadata.
        """
        return {
            "representativeOnly": True,
            "concreteToolExecuted": False,
            "toolName": contract.tool_name,
            "arguments": dict(arguments),
        }

    return {
        "name": contract.tool_name,
        "description": contract.description,
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": True},
        "metadata": contract.to_tool_metadata(),
        "handler": representative_handler,
    }
