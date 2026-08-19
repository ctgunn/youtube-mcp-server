"""Concrete channel-family public YouTube tools."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from mcp_server.tools.youtube_common.channels import (
    ChannelsListToolError,
    build_channels_list_handler,
)
from mcp_server.tools.youtube_common.conventions import (
    safe_upstream_error_message,
    sanitize_error_details,
)
from mcp_server.tools.youtube_common.playlist_items import (
    PlaylistItemsListToolError,
    build_playlist_items_list_handler,
)
from mcp_server.tools.youtube_common.playlists import (
    PlaylistsListToolError,
    build_playlists_list_handler,
)
from mcp_server.tools.youtube_common.search import (
    SearchListToolError,
    build_search_list_handler,
)
from mcp_server.tools.youtube_composed.families import get_family

FAMILY_SCAFFOLDING = get_family("channels")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools
CHANNELS_GET_CHANNEL_TOOL_NAME = "channels_getChannel"
CHANNELS_GET_CHANNELS_TOOL_NAME = "channels_getChannels"
CHANNELS_GET_STATISTICS_TOOL_NAME = "channels_getStatistics"
CHANNELS_GET_STATISTICS_EXPECTED_METRICS = ("subscriberCount", "videoCount", "viewCount")
CHANNELS_LIST_VIDEOS_TOOL_NAME = "channels_listVideos"
CHANNELS_LIST_VIDEOS_MAX_RESULTS = 50
CHANNELS_LIST_PLAYLISTS_TOOL_NAME = "channels_listPlaylists"
CHANNELS_LIST_PLAYLISTS_MAX_RESULTS = 50
CHANNELS_SEARCH_CHANNELS_TOOL_NAME = "channels_searchChannels"
CHANNELS_SEARCH_CHANNELS_MAX_RESULTS = 50
CHANNELS_SEARCH_CHANNELS_ORDERS = ("date", "relevance", "title", "videoCount")
CHANNELS_SEARCH_CHANNELS_TYPES = ("any", "show")
CHANNELS_SEARCH_CHANNELS_SORTS = ("relevance", "subscribers_asc", "subscribers_desc", "indie_priority", "recent_activity")
CHANNELS_SEARCH_CONTENT_TOOL_NAME = "channels_searchContent"
CHANNELS_SEARCH_CONTENT_MAX_RESULTS = 50
_BCP47_LANGUAGE_TAG_PATTERN = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
CHANNELS_SEARCH_CHANNELS_INPUT_SCHEMA = {
    "type": "object",
    "required": ["query"],
    "properties": {
        "query": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 1, "maximum": CHANNELS_SEARCH_CHANNELS_MAX_RESULTS, "default": 10},
        "order": {"type": "string", "enum": list(CHANNELS_SEARCH_CHANNELS_ORDERS)},
        "channelType": {"type": "string", "enum": list(CHANNELS_SEARCH_CHANNELS_TYPES)},
        "minSubscribers": {"type": "integer", "minimum": 0},
        "maxSubscribers": {"type": "integer", "minimum": 0},
        "lastUploadAfter": {"type": "string", "format": "date-time"},
        "lastUploadBefore": {"type": "string", "format": "date-time"},
        "creatorOnly": {"type": "boolean", "default": False},
        "sortBy": {"type": "string", "enum": list(CHANNELS_SEARCH_CHANNELS_SORTS), "default": "relevance"},
    },
    "additionalProperties": False,
}
CHANNELS_SEARCH_CONTENT_INPUT_SCHEMA = {
    "type": "object",
    "required": ["channelId", "query"],
    "properties": {
        "channelId": {"type": "string", "minLength": 1},
        "query": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 1, "maximum": CHANNELS_SEARCH_CONTENT_MAX_RESULTS, "default": 10},
        "order": {"type": "string", "enum": ["relevance", "date", "viewCount"], "default": "relevance"},
        "language": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}
CHANNELS_GET_CHANNEL_INPUT_SCHEMA = {
    "type": "object",
    "required": ["channelId"],
    "properties": {"channelId": {"type": "string", "minLength": 1}},
    "additionalProperties": False,
}
CHANNELS_GET_STATISTICS_INPUT_SCHEMA = {
    "type": "object",
    "required": ["channelId"],
    "properties": {"channelId": {"type": "string", "minLength": 1}},
    "additionalProperties": False,
}
CHANNELS_LIST_VIDEOS_INPUT_SCHEMA = {
    "type": "object",
    "required": ["channelId"],
    "properties": {
        "channelId": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 1, "maximum": CHANNELS_LIST_VIDEOS_MAX_RESULTS, "default": 10},
    },
    "additionalProperties": False,
}
CHANNELS_LIST_PLAYLISTS_INPUT_SCHEMA = {
    "type": "object",
    "required": ["channelId"],
    "properties": {
        "channelId": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 1, "maximum": CHANNELS_LIST_PLAYLISTS_MAX_RESULTS, "default": 25},
    },
    "additionalProperties": False,
}
CHANNELS_GET_CHANNELS_SUPPORTED_PARTS = ("snippet", "contentDetails")
CHANNELS_GET_CHANNELS_MAX_IDS = 50
CHANNELS_GET_CHANNELS_INPUT_SCHEMA = {
    "type": "object",
    "required": ["channelIds"],
    "properties": {
        "channelIds": {
            "type": "array",
            "minItems": 1,
            "maxItems": CHANNELS_GET_CHANNELS_MAX_IDS,
            "uniqueItems": True,
            "items": {"type": "string", "minLength": 1},
        },
        "parts": {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True,
            "items": {"type": "string", "enum": list(CHANNELS_GET_CHANNELS_SUPPORTED_PARTS)},
            "default": ["snippet"],
        },
        "includeLatestUpload": {"type": "boolean", "default": True},
    },
    "additionalProperties": False,
}
_EMAIL_PATTERN = re.compile(r"(?<![\w@])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,63}(?![\w@])", re.IGNORECASE)
_URL_PATTERN = re.compile(r"https?://[^\s<>()]+", re.IGNORECASE)
_CREATOR_SIGNAL_TERMS = (("creator", "public_creator_term"), ("artist", "public_artist_term"), ("developer", "public_developer_term"))
_BRAND_SIGNAL_TERMS = (("official", "public_official_term"), ("company", "public_company_term"), ("brand", "public_brand_term"), ("inc", "public_inc_term"))


class ChannelsGetChannelToolError(ValueError):
    """Represent a safe caller-facing channel-detail failure.

    :param message: Caller-safe explanation of the failure.
    :param category: Stable public error category.
    :param details: Candidate diagnostic details to sanitize.
    """

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe public channel-detail error.

        :param message: Caller-safe explanation of the failure.
        :param category: Stable public error category.
        :param details: Candidate diagnostic details to sanitize.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class ChannelsGetChannelsToolError(ChannelsGetChannelToolError):
    """Represent a safe caller-facing batch channel-detail failure."""


class ChannelsGetStatisticsToolError(ChannelsGetChannelToolError):
    """Represent a safe caller-facing channel-statistics failure."""


class ChannelsListVideosToolError(ChannelsGetChannelToolError):
    """Represent a safe caller-facing channel video-listing failure."""


class ChannelsListPlaylistsToolError(ChannelsGetChannelToolError):
    """Represent a safe caller-facing channel playlist-listing failure."""


class ChannelsSearchChannelsToolError(ChannelsGetChannelToolError):
    """Represent a safe caller-facing public channel-search failure."""


class ChannelsSearchContentToolError(ChannelsGetChannelToolError):
    """Represent a safe caller-facing channel-content-search failure."""


def build_channels_get_channel_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for the concrete channel-detail tool.

    :return: JSON-compatible executable tool metadata without a representative marker.
    """
    return {
        "name": CHANNELS_GET_CHANNEL_TOOL_NAME,
        "family": "channels",
        "parameters": ["channelId"],
        "inputContract": CHANNELS_GET_CHANNEL_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "normalized_enrichment",
            "lowerLayerDependencies": ["channels.list", "playlistItems.list"],
            "boundedness": "one channel and at most one playlist item",
            "partialResultPolicy": "Preserve a core profile when latest-video enrichment is unavailable or safely partial.",
        },
        "lowerLayerDependencies": ["channels.list", "playlistItems.list"],
        "authAndQuotaNotes": [
            "Uses the public channel lookup and, when available, one public uploads-playlist item lookup.",
            "Latest-video enrichment is optional and can be unavailable or partial without discarding an available channel profile.",
        ],
        "responseFields": [
            {"fieldName": "channelId", "category": "raw_upstream", "source": "id"},
            {"fieldName": "title", "category": "raw_upstream", "source": "snippet.title"},
            {"fieldName": "description", "category": "raw_upstream", "source": "snippet.description"},
            {"fieldName": "thumbnails", "category": "raw_upstream", "source": "snippet.thumbnails"},
            {"fieldName": "normalizedMetadata.country", "category": "normalized", "source": "snippet.country"},
            {"fieldName": "normalizedMetadata.defaultLanguage", "category": "normalized", "source": "snippet.defaultLanguage"},
            {"fieldName": "normalizedMetadata.joinedAt", "category": "normalized", "source": "snippet.publishedAt"},
            {"fieldName": "normalizedMetadata.customUrl", "category": "normalized", "source": "snippet.customUrl"},
            {"fieldName": "normalizedMetadata.emailsFound", "category": "heuristic_inferred", "source": "public channel material"},
            {"fieldName": "normalizedMetadata.contactLinks", "category": "heuristic_inferred", "source": "public channel material"},
            {"fieldName": "latestVideoPublishedAt", "category": "normalized", "source": "uploads playlist item contentDetails.videoPublishedAt"},
            {"fieldName": "enrichment", "category": "normalized", "source": "bounded latest-video enrichment"},
            {"fieldName": "heuristics.creatorClassification", "category": "heuristic_inferred", "source": "public channel material"},
            {"fieldName": "heuristics.creatorSignals", "category": "heuristic_inferred", "source": "public channel material"},
        ],
        "heuristics": [
            {
                "name": "publicContactExtraction",
                "basis": "Public channel material returned for this request.",
                "limitations": "Contact values are not verified identity, ownership, or permission to contact.",
            },
            {
                "name": "creatorClassification",
                "basis": "Positive public channel metadata signals.",
                "limitations": "Classification is inferred, can be incomplete or incorrect, and is not canonical source truth.",
            },
        ],
        "errorCategories": [
            "invalid_parameters",
            "unavailable_resource",
            "authorization_sensitive_data",
            "quota_exhaustion",
            "upstream_failure",
            "partial_enrichment_failure",
        ],
        "errorGuidance": {
            "invalid_parameters": "Correct the identified request field and retry.",
            "unavailable_resource": "Use a different accessible channel identifier.",
            "authorization_sensitive_data": "Obtain appropriate authorization if applicable.",
            "quota_exhaustion": "Retry after capacity is available.",
            "upstream_failure": "Retry when the source service is available.",
            "partial_enrichment_failure": "Use the returned profile and retry enrichment later when the safe cause category is actionable.",
        },
    }


def build_channels_get_statistics_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for the channel-statistics tool.

    :return: JSON-compatible public metadata for normalized channel statistics.
    """
    return {
        "name": CHANNELS_GET_STATISTICS_TOOL_NAME,
        "family": "channels",
        "parameters": ["channelId"],
        "inputContract": CHANNELS_GET_STATISTICS_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "normalized_retrieval",
            "lowerLayerDependencies": ["channels.list"],
            "boundedness": "one channel",
            "partialResultPolicy": "Represent a source-flagged hidden subscriber count and unavailable expected metrics without numeric values.",
        },
        "lowerLayerDependencies": ["channels.list"],
        "authAndQuotaNotes": ["Uses the channels.list direct lookup path and its one-unit quota behavior."],
        "responseFields": [
            {"fieldName": "channelId", "category": "normalized", "source": "requested channelId"},
            {"fieldName": "statistics.*.value", "category": "raw_upstream", "source": "statistics counts"},
            {"fieldName": "statistics.*.state", "category": "normalized", "source": "source count availability and visibility signal"},
            {"fieldName": "statistics.*.provenance", "category": "normalized", "source": "result normalization"},
        ],
        "expectedMetrics": list(CHANNELS_GET_STATISTICS_EXPECTED_METRICS),
        "metricAvailability": {
            "available": "A source-provided count, including zero.",
            "hidden": "A subscriber count marked not publicly visible by the source; no numeric value is returned.",
            "unavailable": "The expected source metric was not provided or was invalid; no numeric value is returned.",
        },
        "sourceCaveats": {
            "subscriberCount": "The source rounds public subscriber counts down to three significant figures.",
            "videoCount": "The source reports public videos only.",
            "viewCount": "The source's current definition includes Shorts starts and replays.",
        },
        "errorCategories": [
            "invalid_parameters",
            "unavailable_resource",
            "authorization_sensitive_data",
            "quota_exhaustion",
            "upstream_failure",
        ],
        "errorGuidance": {
            "invalid_parameters": "Correct the identified request field and retry.",
            "unavailable_resource": "Use a different accessible channel identifier.",
            "authorization_sensitive_data": "Obtain appropriate authorization if applicable.",
            "quota_exhaustion": "Retry after capacity is available.",
            "upstream_failure": "Retry when the source service is available.",
        },
    }


def validate_channels_get_channel_arguments(arguments: dict[str, Any]) -> dict[str, str]:
    """Validate and normalize the public single-channel request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized request containing one stripped channel identifier.
    :raises ChannelsGetChannelToolError: If public input is missing or invalid.
    """
    if not isinstance(arguments, dict):
        raise ChannelsGetChannelToolError(
            "channels_getChannel arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected_fields = set(arguments) - {"channelId"}
    if unexpected_fields:
        raise ChannelsGetChannelToolError(
            "channels_getChannel received an unsupported field",
            category="invalid_parameters",
            details={"field": min(unexpected_fields)},
        )
    channel_id = arguments.get("channelId")
    if not isinstance(channel_id, str) or not channel_id.strip():
        raise ChannelsGetChannelToolError(
            "channels_getChannel requires a non-empty channelId",
            category="invalid_parameters",
            details={"field": "channelId"},
        )
    return {"channelId": channel_id.strip()}


def validate_channels_get_statistics_arguments(arguments: dict[str, Any]) -> dict[str, str]:
    """Validate the required single-channel statistics request input.

    :param arguments: Candidate public tool arguments.
    :return: Normalized request containing one trimmed channel identifier.
    :raises ChannelsGetStatisticsToolError: If the request is missing or invalid.
    """
    if not isinstance(arguments, dict):
        raise ChannelsGetStatisticsToolError(
            "channels_getStatistics arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected_fields = set(arguments) - {"channelId"}
    if unexpected_fields:
        raise ChannelsGetStatisticsToolError(
            "channels_getStatistics received an unsupported field",
            category="invalid_parameters",
            details={"field": min(unexpected_fields)},
        )
    channel_id = arguments.get("channelId")
    if not isinstance(channel_id, str) or not channel_id.strip():
        raise ChannelsGetStatisticsToolError(
            "channels_getStatistics requires a non-empty channelId",
            category="invalid_parameters",
            details={"field": "channelId"},
        )
    return {"channelId": channel_id.strip()}


def validate_channels_list_videos_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one public channel video-listing request.

    :param arguments: Candidate public tool arguments.
    :return: Stripped channel identifier and a bounded whole-number result limit.
    :raises ChannelsListVideosToolError: If a public input is missing, invalid, or unsupported.
    """
    if not isinstance(arguments, dict):
        raise ChannelsListVideosToolError(
            "channels_listVideos arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected_fields = set(arguments) - {"channelId", "maxResults"}
    if unexpected_fields:
        raise ChannelsListVideosToolError(
            "channels_listVideos received an unsupported field",
            category="invalid_parameters",
            details={"field": min(unexpected_fields)},
        )
    channel_id = arguments.get("channelId")
    if not isinstance(channel_id, str) or not channel_id.strip():
        raise ChannelsListVideosToolError(
            "channels_listVideos requires a non-empty channelId",
            category="invalid_parameters",
            details={"field": "channelId"},
        )
    max_results = arguments.get("maxResults", 10)
    if isinstance(max_results, bool) or not isinstance(max_results, int) or not 1 <= max_results <= CHANNELS_LIST_VIDEOS_MAX_RESULTS:
        raise ChannelsListVideosToolError(
            f"maxResults must be an integer from 1 through {CHANNELS_LIST_VIDEOS_MAX_RESULTS}",
            category="invalid_parameters",
            details={"field": "maxResults"},
        )
    return {"channelId": channel_id.strip(), "maxResults": max_results}


def validate_channels_list_playlists_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one public channel playlist-listing request.

    :param arguments: Candidate public tool arguments.
    :return: Stripped channel identifier and bounded whole-number result limit.
    :raises ChannelsListPlaylistsToolError: If a public input is invalid or unsupported.
    """
    if not isinstance(arguments, dict):
        raise ChannelsListPlaylistsToolError("channels_listPlaylists arguments must be an object", category="invalid_parameters", details={"field": "arguments"})
    unexpected_fields = set(arguments) - {"channelId", "maxResults"}
    if unexpected_fields:
        raise ChannelsListPlaylistsToolError("channels_listPlaylists received an unsupported field", category="invalid_parameters", details={"field": min(unexpected_fields)})
    channel_id = arguments.get("channelId")
    if not isinstance(channel_id, str) or not channel_id.strip():
        raise ChannelsListPlaylistsToolError("channels_listPlaylists requires a non-empty channelId", category="invalid_parameters", details={"field": "channelId"})
    max_results = arguments.get("maxResults", 25)
    if isinstance(max_results, bool) or not isinstance(max_results, int) or not 1 <= max_results <= CHANNELS_LIST_PLAYLISTS_MAX_RESULTS:
        raise ChannelsListPlaylistsToolError(f"maxResults must be an integer from 1 through {CHANNELS_LIST_PLAYLISTS_MAX_RESULTS}", category="invalid_parameters", details={"field": "maxResults"})
    return {"channelId": channel_id.strip(), "maxResults": max_results}


def validate_channels_get_channels_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize the public batch channel-detail request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized identifiers, selected parts, and enrichment preference.
    :raises ChannelsGetChannelsToolError: If public input is missing or invalid.
    """
    if not isinstance(arguments, dict):
        raise ChannelsGetChannelsToolError(
            "channels_getChannels arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected_fields = set(arguments) - {"channelIds", "parts", "includeLatestUpload"}
    if unexpected_fields:
        raise ChannelsGetChannelsToolError(
            "channels_getChannels received an unsupported field",
            category="invalid_parameters",
            details={"field": min(unexpected_fields)},
        )
    channel_ids = arguments.get("channelIds")
    if not isinstance(channel_ids, list) or not 1 <= len(channel_ids) <= CHANNELS_GET_CHANNELS_MAX_IDS:
        raise ChannelsGetChannelsToolError(
            "channels_getChannels requires one through fifty channelIds",
            category="invalid_parameters",
            details={"field": "channelIds"},
        )
    normalized_ids: list[str] = []
    for channel_id in channel_ids:
        if not isinstance(channel_id, str) or not channel_id.strip():
            raise ChannelsGetChannelsToolError(
                "channels_getChannels requires non-empty channelIds",
                category="invalid_parameters",
                details={"field": "channelIds"},
            )
        normalized_ids.append(channel_id.strip())
    if len(set(normalized_ids)) != len(normalized_ids):
        raise ChannelsGetChannelsToolError(
            "channels_getChannels requires distinct channelIds",
            category="invalid_parameters",
            details={"field": "channelIds"},
        )
    parts = arguments.get("parts", ["snippet"])
    if (
        not isinstance(parts, list)
        or not parts
        or any(not isinstance(part, str) or part not in CHANNELS_GET_CHANNELS_SUPPORTED_PARTS for part in parts)
        or len(set(parts)) != len(parts)
    ):
        raise ChannelsGetChannelsToolError(
            "channels_getChannels parts must be a distinct supported selection",
            category="invalid_parameters",
            details={"field": "parts"},
        )
    include_latest_upload = arguments.get("includeLatestUpload", True)
    if not isinstance(include_latest_upload, bool):
        raise ChannelsGetChannelsToolError(
            "channels_getChannels includeLatestUpload must be a boolean",
            category="invalid_parameters",
            details={"field": "includeLatestUpload"},
        )
    return {
        "channelIds": normalized_ids,
        "parts": list(parts),
        "includeLatestUpload": include_latest_upload,
    }


def _copy_if_present(result: dict[str, Any], source: dict[str, Any], field: str) -> None:
    """Copy an available source field into a public result using the same name.

    :param result: Result mapping being assembled.
    :param source: Source mapping that may contain the field.
    :param field: Source and public result field name.
    """
    if field in source:
        result[field] = source[field]


def _public_contact_text(snippet: dict[str, Any]) -> str:
    """Return public profile text permitted for contact-value extraction.

    :param snippet: Public source profile metadata.
    :return: Concatenated description and HTTP(S) custom URL text when present.
    """
    values = []
    description = snippet.get("description")
    if isinstance(description, str):
        values.append(description)
    custom_url = snippet.get("customUrl")
    if isinstance(custom_url, str) and custom_url.lower().startswith(("http://", "https://")):
        values.append(custom_url)
    return "\n".join(values)


def _public_contacts(snippet: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Extract deterministic public email and HTTP(S) contact values.

    :param snippet: Public source profile metadata.
    :return: De-duplicated normalized email addresses and contact links.
    """
    text = _public_contact_text(snippet)
    emails: list[str] = []
    email_keys: set[str] = set()
    for match in _EMAIL_PATTERN.finditer(text):
        email = match.group(0).lower()
        if email not in email_keys:
            email_keys.add(email)
            emails.append(email)
    links: list[str] = []
    link_keys: set[str] = set()
    for match in _URL_PATTERN.finditer(text):
        link = match.group(0).rstrip(".,;:!?)]}")
        parsed = urlparse(link)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
            continue
        key = link.lower()
        if key not in link_keys:
            link_keys.add(key)
            links.append(link)
    return emails, links


def _has_term(text: str, term: str) -> bool:
    """Return whether one public classification term appears as a whole word.

    :param text: Lower-cased public profile text.
    :param term: Lower-cased candidate classification term.
    :return: ``True`` when the term appears outside another word.
    """
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) is not None


def _creator_classification(snippet: dict[str, Any]) -> tuple[str, list[str]]:
    """Classify a channel conservatively from positive public profile signals.

    :param snippet: Public source profile metadata.
    :return: ``creator``, ``brand``, or ``unknown`` and safe supporting signals.
    """
    title = snippet.get("title") if isinstance(snippet.get("title"), str) else ""
    description = snippet.get("description") if isinstance(snippet.get("description"), str) else ""
    text = f"{title}\n{description}".lower()
    creator_signals = [signal for term, signal in _CREATOR_SIGNAL_TERMS if _has_term(text, term)]
    brand_signals = [signal for term, signal in _BRAND_SIGNAL_TERMS if _has_term(text, term)]
    if creator_signals and not brand_signals:
        return "creator", creator_signals
    if brand_signals and not creator_signals:
        return "brand", brand_signals
    return "unknown", []


def _normalized_metadata(snippet: dict[str, Any]) -> dict[str, Any]:
    """Build the stable normalized metadata group from public profile values.

    :param snippet: Public source profile metadata.
    :return: Normalized metadata with safely derived public contact collections.
    """
    emails, contact_links = _public_contacts(snippet)
    metadata: dict[str, Any] = {"emailsFound": emails, "contactLinks": contact_links}
    for source_name, result_name in (
        ("country", "country"),
        ("defaultLanguage", "defaultLanguage"),
        ("publishedAt", "joinedAt"),
        ("customUrl", "customUrl"),
    ):
        if source_name in snippet:
            metadata[result_name] = snippet[source_name]
    return metadata


def _uploads_playlist_id(item: dict[str, Any]) -> str | None:
    """Return one usable public uploads-playlist identifier when available.

    :param item: Source channel record containing optional content details.
    :return: Nonblank uploads-playlist identifier, or ``None`` when unavailable.
    """
    content_details = item.get("contentDetails") if isinstance(item.get("contentDetails"), dict) else {}
    related_playlists = content_details.get("relatedPlaylists") if isinstance(content_details.get("relatedPlaylists"), dict) else {}
    uploads = related_playlists.get("uploads")
    return uploads.strip() if isinstance(uploads, str) and uploads.strip() else None


def _latest_video_published_at(payload: dict[str, Any]) -> str | None:
    """Return the latest available publication timestamp from one playlist response.

    :param payload: Lower-level playlist-items result with at most one item requested.
    :return: Timezone-aware publication timestamp, or ``None`` when unavailable or malformed.
    """
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        return None
    content_details = items[0].get("contentDetails") if isinstance(items[0].get("contentDetails"), dict) else {}
    timestamp = content_details.get("videoPublishedAt")
    if not isinstance(timestamp, str) or not timestamp.strip():
        return None
    value = timestamp.strip()
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        return None
    return value if parsed.tzinfo is not None else None


def _field_provenance(result: dict[str, Any]) -> dict[str, str]:
    """Build provenance labels for every currently returned public field path.

    :param result: Channel result before its provenance mapping is attached.
    :return: Public field-path-to-provenance mapping.
    """
    provenance: dict[str, str] = {}
    for field in ("channelId", "title", "description", "thumbnails"):
        if field in result:
            provenance[field] = "raw_upstream"
    metadata = result.get("normalizedMetadata") if isinstance(result.get("normalizedMetadata"), dict) else {}
    for field in ("country", "defaultLanguage", "joinedAt", "customUrl"):
        if field in metadata:
            provenance[f"normalizedMetadata.{field}"] = "normalized"
    provenance["normalizedMetadata.emailsFound"] = "heuristic_inferred"
    provenance["normalizedMetadata.contactLinks"] = "heuristic_inferred"
    if "latestVideoPublishedAt" in result:
        provenance["latestVideoPublishedAt"] = "normalized"
    provenance["enrichment"] = "normalized"
    provenance["heuristics.creatorClassification"] = "heuristic_inferred"
    provenance["heuristics.creatorSignals"] = "heuristic_inferred"
    return provenance


def _normalize_channel_result(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Normalize one available lower-level channel item into a public profile.

    :param payload: Lower-level channel-list result containing one item.
    :return: Public result before latest enrichment and the source channel item.
    :raises ChannelsGetChannelToolError: If no usable channel item is available.
    """
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        raise ChannelsGetChannelToolError(
            "The requested channel is unavailable",
            category="unavailable_resource",
            details={"resource": "channel"},
        )
    item = items[0]
    channel_id = item.get("id")
    if not isinstance(channel_id, str) or not channel_id.strip():
        raise ChannelsGetChannelToolError(
            "The requested channel is unavailable",
            category="unavailable_resource",
            details={"resource": "channel"},
        )
    snippet = item.get("snippet") if isinstance(item.get("snippet"), dict) else {}
    result: dict[str, Any] = {"channelId": channel_id}
    for field in ("title", "description", "thumbnails"):
        _copy_if_present(result, snippet, field)
    result["normalizedMetadata"] = _normalized_metadata(snippet)
    classification, signals = _creator_classification(snippet)
    result["heuristics"] = {"creatorClassification": classification, "creatorSignals": signals}
    return result, item


def _map_channels_list_error(error: ChannelsListToolError) -> ChannelsGetChannelToolError:
    """Translate a lower-level core lookup error to the public taxonomy.

    :param error: Safe lower-level channel-list failure.
    :return: Sanitized public channel-detail error.
    """
    if error.category in {"resource_not_found", "removed"}:
        return ChannelsGetChannelToolError(
            "The requested channel is unavailable",
            category="unavailable_resource",
            details={"resource": "channel"},
        )
    category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
    }.get(error.category, "upstream_failure")
    return ChannelsGetChannelToolError(safe_upstream_error_message(), category=category, details=error.details)


def _channels_get_statistics_lookup_arguments(channel_id: str) -> dict[str, str]:
    """Build the one lower-level lookup for public channel statistics.

    :param channel_id: Validated public channel identifier.
    :return: Direct ``channels.list`` arguments requesting only statistics.
    """
    return {"id": channel_id, "part": "statistics"}


def _source_channel_statistic_value(value: Any) -> str | None:
    """Return a valid non-negative source channel statistic without float conversion.

    :param value: Candidate source statistic value.
    :return: Preserved decimal text for a valid source count, otherwise ``None``.
    """
    if isinstance(value, str) and value.isdecimal():
        return value
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return str(value)
    return None


def _channel_statistic_result(metric: str, source_statistics: dict[str, Any]) -> dict[str, str]:
    """Normalize one expected channel statistic to its public state.

    :param metric: Expected public metric name.
    :param source_statistics: Source statistics mapping for one channel.
    :return: Available, hidden, or unavailable public metric representation.
    """
    if metric == "subscriberCount" and source_statistics.get("hiddenSubscriberCount") is True:
        return {"state": "hidden", "provenance": "normalized"}
    value = _source_channel_statistic_value(source_statistics.get(metric))
    if value is None:
        return {"state": "unavailable", "provenance": "normalized"}
    return {"state": "available", "value": value, "provenance": "source_provided"}


def normalize_channels_get_statistics_result(payload: dict[str, Any], *, channel_id: str) -> dict[str, Any]:
    """Normalize expected source counts for one requested channel.

    :param payload: Lower-level result containing one statistics source item.
    :param channel_id: Validated request identifier associated with the result.
    :return: Stable statistics and availability data for the requested channel.
    :raises ChannelsGetStatisticsToolError: If no source channel item is available.
    """
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        raise ChannelsGetStatisticsToolError(
            "The requested channel is unavailable",
            category="unavailable_resource",
            details={"resource": "channel"},
        )
    item = items[0]
    source_statistics = item.get("statistics") if isinstance(item.get("statistics"), dict) else {}
    statistics = {
        metric: _channel_statistic_result(metric, source_statistics)
        for metric in CHANNELS_GET_STATISTICS_EXPECTED_METRICS
    }
    return {
        "channelId": channel_id,
        "statistics": statistics,
        "fieldProvenance": {
            "statistics.*.value": "source_provided",
            "statistics.*.state": "normalized",
        },
        "sourceCaveats": {
            "subscriberCount": "The source rounds public subscriber counts down to three significant figures.",
            "videoCount": "The source reports public videos only.",
            "viewCount": "The source's current definition includes Shorts starts and replays.",
        },
    }


def _map_channels_list_statistics_error(error: ChannelsListToolError) -> ChannelsGetStatisticsToolError:
    """Translate a lower-level error to a safe public statistics error.

    :param error: Safe lower-level channel lookup error.
    :return: Documented caller-safe channel-statistics error.
    """
    mapped = _map_channels_list_error(error)
    return ChannelsGetStatisticsToolError(str(mapped), category=mapped.category, details=mapped.details)


def build_channels_get_statistics_handler(*, channels=None):
    """Build a callable handler for one normalized channel-statistics lookup.

    :param channels: Optional lower-level channel-list handler override for tests.
    :return: Callable that validates, retrieves, and normalizes one channel.
    """
    selected_channels = channels or build_channels_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated public channel-statistics request.

        :param arguments: Caller-provided public arguments.
        :return: Normalized statistics for the requested available channel.
        :raises ChannelsGetStatisticsToolError: If validation or lookup fails.
        """
        normalized = validate_channels_get_statistics_arguments(arguments)
        try:
            payload = selected_channels(_channels_get_statistics_lookup_arguments(normalized["channelId"]))
        except ChannelsListToolError as exc:
            raise _map_channels_list_statistics_error(exc) from exc
        return normalize_channels_get_statistics_result(payload, channel_id=normalized["channelId"])

    return handler


def build_channels_get_statistics_tool_descriptor(*, channels=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for ``channels_getStatistics``.

    :param channels: Optional lower-level channel-list handler override for tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": CHANNELS_GET_STATISTICS_TOOL_NAME,
        "description": "Return normalized public statistics for one YouTube channel.",
        "inputSchema": CHANNELS_GET_STATISTICS_INPUT_SCHEMA,
        "handler": build_channels_get_statistics_handler(channels=channels),
        "metadata": build_channels_get_statistics_metadata(),
    }


def _channels_list_videos_core_error(error: ChannelsListToolError) -> ChannelsListVideosToolError:
    """Translate one lower-level channel failure for public video listing.

    :param error: Safe lower-level channel-list failure.
    :return: Sanitized channel video-listing error using the public taxonomy.
    """
    mapped = _map_channels_list_error(error)
    return ChannelsListVideosToolError(str(mapped), category=mapped.category, details=mapped.details)


def _channels_list_videos_playlist_error(error: PlaylistItemsListToolError) -> ChannelsListVideosToolError:
    """Translate a required uploads-collection read failure for public listing.

    :param error: Safe lower-level playlist-items failure.
    :return: Sanitized whole-request channel video-listing error.
    """
    if error.category in {"resource_not_found", "removed"}:
        return ChannelsListVideosToolError(
            "The requested channel videos are unavailable",
            category="unavailable_resource",
            details={"resource": "channel"},
        )
    category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
    }.get(error.category, "upstream_failure")
    return ChannelsListVideosToolError(safe_upstream_error_message(), category=category, details=error.details)


def _channel_video_list_result(
    channel_id: str,
    max_results: int,
    items: list[dict[str, Any]],
    *,
    omitted_item_count: int = 0,
) -> dict[str, Any]:
    """Build one stable public channel video-listing result.

    :param channel_id: Normalized requested public channel identifier.
    :param max_results: Validated final result cap.
    :param items: Distinct normalized items in source collection order.
    :param omitted_item_count: Number of unusable source items safely omitted.
    :return: Public result with normalized context and field provenance.
    """
    result: dict[str, Any] = {
        "channelId": channel_id,
        "items": items,
        "returnedCount": len(items),
        "maxResults": max_results,
        "appliedInputs": {"channelId": channel_id, "maxResults": max_results},
        "collectionContext": {
            "source": "channel_uploads_collection",
            "ordering": "source_order_at_request_time",
            "rankingApplied": False,
            "publicContentOnly": True,
            "requestTimeVariability": "collection_can_change",
        },
        "fieldProvenance": _channel_video_list_provenance(items, include_partial_availability=bool(omitted_item_count)),
    }
    if omitted_item_count:
        result["partialAvailability"] = {
            "status": "partial",
            "omittedItemCount": omitted_item_count,
            "reasons": ["unusable_source_item"],
        }
    return result


def _channel_video_list_provenance(
    items: list[dict[str, Any]], *, include_partial_availability: bool = False
) -> dict[str, str]:
    """Build provenance labels for a public channel video-listing result.

    :param items: Normalized public video items in the returned collection.
    :param include_partial_availability: Whether a safe partial-availability value is returned.
    :return: Field-path-to-provenance mapping for source and normalized values.
    """
    provenance = {
        "items.videoId": "raw_upstream",
        "channelId": "normalized",
        "returnedCount": "normalized",
        "maxResults": "normalized",
        "appliedInputs": "normalized",
        "collectionContext": "normalized",
    }
    for field in ("title", "description", "publishedAt", "thumbnails"):
        if any(field in item for item in items):
            provenance[f"items.{field}"] = "raw_upstream"
    if include_partial_availability:
        provenance["partialAvailability"] = "normalized"
    return provenance


def _normalize_channel_video_items(payload: dict[str, Any], max_results: int) -> tuple[list[dict[str, Any]], int]:
    """Normalize, de-duplicate, and cap one uploads-collection response.

    :param payload: Lower-level playlist-items result in source collection order.
    :param max_results: Validated cap applied after first-occurrence de-duplication.
    :return: Distinct public video items and the number of unusable omitted source items.
    """
    source_items = payload.get("items") if isinstance(payload, dict) and isinstance(payload.get("items"), list) else []
    items: list[dict[str, Any]] = []
    seen_video_ids: set[str] = set()
    omitted_item_count = 0
    for source_item in source_items:
        if not isinstance(source_item, dict):
            omitted_item_count += 1
            continue
        snippet = source_item.get("snippet") if isinstance(source_item.get("snippet"), dict) else {}
        content_details = source_item.get("contentDetails") if isinstance(source_item.get("contentDetails"), dict) else {}
        resource_id = snippet.get("resourceId") if isinstance(snippet.get("resourceId"), dict) else {}
        candidate_video_id = resource_id.get("videoId")
        if not isinstance(candidate_video_id, str) or not candidate_video_id.strip():
            candidate_video_id = content_details.get("videoId")
        if not isinstance(candidate_video_id, str) or not candidate_video_id.strip():
            omitted_item_count += 1
            continue
        video_id = candidate_video_id.strip()
        if video_id in seen_video_ids:
            continue
        seen_video_ids.add(video_id)
        item: dict[str, Any] = {"videoId": video_id}
        for field in ("title", "description", "thumbnails"):
            _copy_if_present(item, snippet, field)
        published_at = content_details.get("videoPublishedAt")
        if isinstance(published_at, str) and published_at.strip():
            item["publishedAt"] = published_at.strip()
        items.append(item)
        if len(items) == max_results:
            break
    return items, omitted_item_count


def _channel_uploads_reference(payload: dict[str, Any]) -> str | None:
    """Return the public uploads collection reference from one available channel.

    :param payload: Lower-level channel-list result expected to contain one source channel.
    :return: Nonblank uploads collection reference, or ``None`` when the channel has none.
    :raises ChannelsListVideosToolError: If the requested channel cannot be returned.
    """
    source_items = payload.get("items") if isinstance(payload, dict) and isinstance(payload.get("items"), list) else []
    if not source_items or not isinstance(source_items[0], dict):
        raise ChannelsListVideosToolError(
            "The requested channel is unavailable",
            category="unavailable_resource",
            details={"resource": "channel"},
        )
    channel_id = source_items[0].get("id")
    if not isinstance(channel_id, str) or not channel_id.strip():
        raise ChannelsListVideosToolError(
            "The requested channel is unavailable",
            category="unavailable_resource",
            details={"resource": "channel"},
        )
    return _uploads_playlist_id(source_items[0])


def _partial_enrichment_state(error: PlaylistItemsListToolError) -> dict[str, str]:
    """Build a safe partial state from a post-profile playlist lookup failure.

    :param error: Safe lower-level playlist-items failure.
    :return: Public partial-enrichment status with a safe cause category.
    """
    cause_category = {
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
    }.get(error.category, "upstream_failure")
    return {
        "status": "partial",
        "category": "partial_enrichment_failure",
        "causeCategory": cause_category,
    }


def build_channels_get_channel_handler(*, channels=None, playlist_items=None):
    """Build a callable handler for one normalized and enriched channel lookup.

    :param channels: Optional lower-level channel-list handler override for tests.
    :param playlist_items: Optional lower-level playlist-items handler override for tests.
    :return: Callable public channel-detail handler with complete, unavailable, or partial enrichment.
    """
    selected_channels = channels or build_channels_list_handler()
    selected_playlist_items = playlist_items or build_playlist_items_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated public channel-detail request.

        :param arguments: Caller-provided public arguments.
        :return: Normalized public profile with complete, unavailable, or safely partial enrichment.
        :raises ChannelsGetChannelToolError: If validation or core lookup fails.
        """
        request = validate_channels_get_channel_arguments(arguments)
        try:
            payload = selected_channels({"part": "snippet,contentDetails", "id": request["channelId"]})
        except ChannelsListToolError as exc:
            raise _map_channels_list_error(exc) from exc
        result, item = _normalize_channel_result(payload)
        uploads_playlist_id = _uploads_playlist_id(item)
        if uploads_playlist_id:
            try:
                latest_payload = selected_playlist_items(
                    {"part": "contentDetails", "playlistId": uploads_playlist_id, "maxResults": 1}
                )
            except PlaylistItemsListToolError as exc:
                result["enrichment"] = _partial_enrichment_state(exc)
            else:
                latest_timestamp = _latest_video_published_at(latest_payload)
                if latest_timestamp:
                    result["latestVideoPublishedAt"] = latest_timestamp
                    result["enrichment"] = {"status": "complete"}
                else:
                    result["enrichment"] = {"status": "unavailable"}
        else:
            result["enrichment"] = {"status": "unavailable"}
        result["fieldProvenance"] = _field_provenance(result)
        return result

    return handler


def build_channels_get_channel_tool_descriptor(*, channels=None, playlist_items=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for ``channels_getChannel``.

    :param channels: Optional lower-level channel-list handler override for tests.
    :param playlist_items: Optional lower-level playlist-items handler override for tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": CHANNELS_GET_CHANNEL_TOOL_NAME,
        "description": "Return normalized and enriched details for one YouTube channel.",
        "inputSchema": CHANNELS_GET_CHANNEL_INPUT_SCHEMA,
        "handler": build_channels_get_channel_handler(channels=channels, playlist_items=playlist_items),
        "metadata": build_channels_get_channel_metadata(),
    }


def build_channels_list_videos_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for source-ordered channel video listing.

    :return: JSON-compatible executable tool metadata without a representative marker.
    """
    return {
        "name": CHANNELS_LIST_VIDEOS_TOOL_NAME,
        "family": "channels",
        "parameters": ["channelId", "maxResults"],
        "inputContract": CHANNELS_LIST_VIDEOS_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "source_ordered_collection",
            "lowerLayerDependencies": ["channels.list", "playlistItems.list"],
            "boundedness": "one channel lookup and at most one uploads-collection listing; 1-50 returned distinct items",
            "partialResultPolicy": "A missing uploads reference or successful empty collection returns an empty result; a required collection-read failure is a whole-request error.",
        },
        "lowerLayerDependencies": ["channels.list", "playlistItems.list"],
        "orderingSemantics": {
            "ordering": "Preserves usable uploads-collection source order observed at request time after first-occurrence de-duplication and final cap.",
            "rankingApplied": False,
            "requestTimeVariability": "Later requests can differ when public channel uploads change.",
        },
        "publicContentPolicy": "Only publicly available videos are returned; inaccessible content is omitted.",
        "searchGuidance": "Use a search-oriented tool when keyword matching or relevance-ranked discovery is required.",
        "partialAvailabilityPolicy": {
            "status": "partial",
            "safeAggregateOnly": True,
            "requiredLookupFailure": "whole_request_error",
        },
        "authAndQuotaNotes": [
            "Uses configured public-read capability and does not request owner-scoped data.",
            "The bounded channel and uploads-collection reads consume quota and can fail when capacity is exhausted.",
        ],
        "responseFields": [
            {"fieldName": "items.videoId", "category": "raw_upstream", "source": "snippet.resourceId.videoId or contentDetails.videoId"},
            {"fieldName": "items.title", "category": "raw_upstream", "source": "snippet.title"},
            {"fieldName": "items.description", "category": "raw_upstream", "source": "snippet.description"},
            {"fieldName": "items.publishedAt", "category": "raw_upstream", "source": "contentDetails.videoPublishedAt"},
            {"fieldName": "items.thumbnails", "category": "raw_upstream", "source": "snippet.thumbnails"},
            {"fieldName": "channelId", "category": "normalized", "source": "validated caller input"},
            {"fieldName": "returnedCount", "category": "normalized", "source": "returned distinct item count"},
            {"fieldName": "maxResults", "category": "normalized", "source": "validated caller input"},
            {"fieldName": "appliedInputs", "category": "normalized", "source": "validated caller input"},
            {"fieldName": "collectionContext", "category": "normalized", "source": "source-order contract"},
            {"fieldName": "partialAvailability", "category": "normalized", "source": "safe aggregate known source omissions"},
        ],
        "errorCategories": [
            "invalid_parameters",
            "unavailable_resource",
            "authorization_sensitive_data",
            "quota_exhaustion",
            "upstream_failure",
        ],
        "errorGuidance": {
            "invalid_parameters": "Correct the identified request field and retry.",
            "unavailable_resource": "Use a different accessible channel identifier.",
            "authorization_sensitive_data": "Obtain appropriate public-read capability if applicable.",
            "quota_exhaustion": "Retry after capacity is available.",
            "upstream_failure": "Retry when the source service is available.",
        },
    }


def build_channels_list_videos_handler(*, channels=None, playlist_items=None):
    """Build a callable handler for one bounded source-ordered video listing.

    :param channels: Optional lower-level channel-list handler override for tests.
    :param playlist_items: Optional lower-level playlist-items handler override for tests.
    :return: Callable public channel video-listing handler.
    """
    selected_channels = channels or build_channels_list_handler()
    selected_playlist_items = playlist_items or build_playlist_items_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated public channel video-listing request.

        :param arguments: Caller-provided public arguments.
        :return: Bounded source-ordered public videos and safe collection context.
        :raises ChannelsListVideosToolError: If validation or a required lookup fails.
        """
        request = validate_channels_list_videos_arguments(arguments)
        try:
            channel_payload = selected_channels({"part": "contentDetails", "id": request["channelId"]})
        except ChannelsListToolError as exc:
            raise _channels_list_videos_core_error(exc) from exc
        uploads_playlist_id = _channel_uploads_reference(channel_payload)
        if uploads_playlist_id is None:
            return _channel_video_list_result(request["channelId"], request["maxResults"], [])
        try:
            playlist_payload = selected_playlist_items(
                {"part": "snippet,contentDetails", "playlistId": uploads_playlist_id, "maxResults": request["maxResults"]}
            )
        except PlaylistItemsListToolError as exc:
            raise _channels_list_videos_playlist_error(exc) from exc
        items, omitted_item_count = _normalize_channel_video_items(playlist_payload, request["maxResults"])
        return _channel_video_list_result(
            request["channelId"], request["maxResults"], items, omitted_item_count=omitted_item_count
        )

    return handler


def build_channels_list_videos_tool_descriptor(*, channels=None, playlist_items=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for ``channels_listVideos``.

    :param channels: Optional lower-level channel-list handler override for tests.
    :param playlist_items: Optional lower-level playlist-items handler override for tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": CHANNELS_LIST_VIDEOS_TOOL_NAME,
        "description": "List publicly available videos for one YouTube channel in uploads-collection source order.",
        "inputSchema": CHANNELS_LIST_VIDEOS_INPUT_SCHEMA,
        "handler": build_channels_list_videos_handler(channels=channels, playlist_items=playlist_items),
        "metadata": build_channels_list_videos_metadata(),
    }


def build_channels_list_playlists_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for source-ordered channel playlist listing.

    :return: JSON-compatible executable tool metadata without a representative marker.
    """
    return {
        "name": CHANNELS_LIST_PLAYLISTS_TOOL_NAME,
        "family": "channels",
        "parameters": ["channelId", "maxResults"],
        "inputContract": CHANNELS_LIST_PLAYLISTS_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "source_ordered_collection",
            "lowerLayerDependencies": ["channels.list", "playlists.list"],
            "boundedness": "one channel verification and one channel-scoped playlist listing; 1-50 records",
            "partialResultPolicy": "A verified channel with an empty playlist collection returns an empty result; an unavailable channel is a whole-request error.",
        },
        "lowerLayerDependencies": ["channels.list", "playlists.list"],
        "orderingSemantics": {"ordering": "Preserves usable source playlist order observed at request time.", "rankingApplied": False, "requestTimeVariability": "Later requests can differ when public channel playlists change."},
        "authAndQuotaNotes": ["Uses configured public-read capability and does not request owner-scoped data.", "The bounded channel verification and playlist listing consume quota and can fail when capacity is exhausted."],
        "responseFields": [
            {"fieldName": "items.playlistId", "category": "raw_upstream", "source": "id"},
            {"fieldName": "items.title", "category": "normalized", "source": "snippet.title"},
            {"fieldName": "items.description", "category": "raw_upstream", "source": "snippet.description"},
            {"fieldName": "items.channelId", "category": "raw_upstream", "source": "snippet.channelId"},
            {"fieldName": "items.channelTitle", "category": "raw_upstream", "source": "snippet.channelTitle"},
            {"fieldName": "items.publishedAt", "category": "raw_upstream", "source": "snippet.publishedAt"},
            {"fieldName": "items.thumbnails", "category": "raw_upstream", "source": "snippet.thumbnails"},
            {"fieldName": "items.itemCount", "category": "raw_upstream", "source": "contentDetails.itemCount"},
            {"fieldName": "items.privacyStatus", "category": "raw_upstream", "source": "status.privacyStatus"},
            {"fieldName": "channelId", "category": "normalized", "source": "validated caller input"},
            {"fieldName": "returnedCount", "category": "normalized", "source": "returned record count"},
            {"fieldName": "appliedLimit", "category": "normalized", "source": "validated caller input"},
            {"fieldName": "appliedInputs", "category": "normalized", "source": "validated caller input"},
            {"fieldName": "collectionContext", "category": "normalized", "source": "source-order contract"},
        ],
        "errorCategories": ["invalid_parameters", "unavailable_resource", "authorization_sensitive_data", "quota_exhaustion", "upstream_failure"],
        "errorGuidance": {"invalid_parameters": "Correct the identified request field and retry.", "unavailable_resource": "Use a different accessible channel identifier.", "authorization_sensitive_data": "Obtain appropriate public-read capability if applicable.", "quota_exhaustion": "Retry after capacity is available.", "upstream_failure": "Retry when the source service is available."},
    }


def _channels_list_playlists_error(error: ChannelsListToolError | PlaylistsListToolError) -> ChannelsListPlaylistsToolError:
    """Translate one required lower-layer listing failure to the public taxonomy.

    :param error: Safe lower-layer channel or playlist-listing error.
    :return: Sanitized public channel playlist-listing error.
    """
    if error.category in {"resource_not_found", "removed"}:
        return ChannelsListPlaylistsToolError("The requested channel is unavailable", category="unavailable_resource", details={"resource": "channel"})
    category = {"invalid_request": "invalid_parameters", "authentication_failed": "authorization_sensitive_data", "authorization_failed": "authorization_sensitive_data", "quota_exhausted": "quota_exhaustion"}.get(error.category, "upstream_failure")
    return ChannelsListPlaylistsToolError(safe_upstream_error_message(), category=category, details=error.details)


def _channel_playlist_record(source_item: Any) -> dict[str, Any] | None:
    """Normalize one source playlist record when it has stable identity and title.

    :param source_item: Candidate lower-layer playlist record.
    :return: Normalized public record, or ``None`` when required source values are unusable.
    """
    if not isinstance(source_item, dict):
        return None
    playlist_id = source_item.get("id")
    snippet = source_item.get("snippet") if isinstance(source_item.get("snippet"), dict) else {}
    title = snippet.get("title")
    if not isinstance(playlist_id, str) or not playlist_id.strip() or not isinstance(title, str):
        return None
    result: dict[str, Any] = {"playlistId": playlist_id.strip(), "title": title}
    for field in ("description", "channelId", "channelTitle", "publishedAt", "thumbnails"):
        _copy_if_present(result, snippet, field)
    content_details = source_item.get("contentDetails") if isinstance(source_item.get("contentDetails"), dict) else {}
    status = source_item.get("status") if isinstance(source_item.get("status"), dict) else {}
    _copy_if_present(result, content_details, "itemCount")
    _copy_if_present(result, status, "privacyStatus")
    return result


def _channel_playlist_result(channel_id: str, max_results: int, items: list[dict[str, Any]]) -> dict[str, Any]:
    """Build one stable public channel playlist-listing result.

    :param channel_id: Normalized requested channel identifier.
    :param max_results: Validated source listing limit.
    :param items: Normalized playlist records in source order.
    :return: Public listing with normalized context and field provenance.
    """
    provenance = {"items.playlistId": "raw_upstream", "items.title": "normalized", "channelId": "normalized", "returnedCount": "normalized", "appliedLimit": "normalized", "appliedInputs": "normalized", "collectionContext": "normalized"}
    for field in ("description", "channelId", "channelTitle", "publishedAt", "thumbnails", "itemCount", "privacyStatus"):
        if any(field in item for item in items):
            provenance[f"items.{field}"] = "raw_upstream"
    return {"channelId": channel_id, "items": items, "returnedCount": len(items), "appliedLimit": max_results, "appliedInputs": {"channelId": channel_id, "maxResults": max_results}, "collectionContext": {"source": "channel_playlist_collection", "ordering": "source_order_at_request_time", "rankingApplied": False, "publicContentOnly": True, "stateObservedAtRequest": True}, "fieldProvenance": provenance}


def build_channels_list_playlists_handler(*, channels=None, playlists=None):
    """Build a callable handler for one bounded channel playlist listing.

    :param channels: Optional lower-level channel-list handler override for tests.
    :param playlists: Optional lower-level playlist-list handler override for tests.
    :return: Callable public channel playlist-listing handler.
    """
    selected_channels = channels or build_channels_list_handler()
    selected_playlists = playlists or build_playlists_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Verify one channel and return its normalized ordered playlists.

        :param arguments: Caller-provided public arguments.
        :return: Bounded source-ordered public playlist records.
        :raises ChannelsListPlaylistsToolError: If validation or a required lookup fails.
        """
        request = validate_channels_list_playlists_arguments(arguments)
        try:
            verified = selected_channels({"part": "id", "id": request["channelId"]})
        except ChannelsListToolError as exc:
            raise _channels_list_playlists_error(exc) from exc
        source_channels = verified.get("items") if isinstance(verified, dict) and isinstance(verified.get("items"), list) else []
        if not source_channels or not isinstance(source_channels[0], dict):
            raise ChannelsListPlaylistsToolError("The requested channel is unavailable", category="unavailable_resource", details={"resource": "channel"})
        try:
            payload = selected_playlists({"part": "snippet,contentDetails,status", "channelId": request["channelId"], "maxResults": request["maxResults"]})
        except PlaylistsListToolError as exc:
            raise _channels_list_playlists_error(exc) from exc
        source_items = payload.get("items") if isinstance(payload, dict) and isinstance(payload.get("items"), list) else []
        items = [record for source_item in source_items if (record := _channel_playlist_record(source_item)) is not None]
        return _channel_playlist_result(request["channelId"], request["maxResults"], items)

    return handler


def build_channels_list_playlists_tool_descriptor(*, channels=None, playlists=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for ``channels_listPlaylists``.

    :param channels: Optional lower-level channel-list handler override for tests.
    :param playlists: Optional lower-level playlist-list handler override for tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {"name": CHANNELS_LIST_PLAYLISTS_TOOL_NAME, "description": "List publicly accessible playlists for one YouTube channel in source order.", "inputSchema": CHANNELS_LIST_PLAYLISTS_INPUT_SCHEMA, "handler": build_channels_list_playlists_handler(channels=channels, playlists=playlists), "metadata": build_channels_list_playlists_metadata()}


def build_channels_get_channels_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for the batch channel-detail tool.

    :return: JSON-compatible executable metadata for bounded ordered batch retrieval.
    """
    return {
        "name": CHANNELS_GET_CHANNELS_TOOL_NAME,
        "family": "channels",
        "parameters": ["channelIds", "parts", "includeLatestUpload"],
        "inputContract": CHANNELS_GET_CHANNELS_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "normalized_batch_enrichment",
            "lowerLayerDependencies": ["channels.list", "playlistItems.list"],
            "boundedness": "one channel collection and at most one playlist item per available channel",
            "partialResultPolicy": "Preserve independent items when an identifier is unavailable or optional enrichment is partial.",
        },
        "lowerLayerDependencies": ["channels.list", "playlistItems.list"],
        "responseConvention": {
            "resultKind": "ordered_batch",
            "resultOrdering": "Results preserve channelIds request order.",
            "summaryFields": ["requested", "successful", "unavailable", "partiallyEnriched"],
        },
        "detailSelection": {
            "supported": list(CHANNELS_GET_CHANNELS_SUPPORTED_PARTS),
            "default": ["snippet"],
        },
        "latestUploadEnrichment": {
            "default": True,
            "states": ["complete", "unavailable", "partial", "not_requested"],
        },
        "individualOutcomePolicy": {
            "unavailable": "unavailable_resource",
            "partial": "partial_enrichment_failure",
        },
        "responseFields": [
            {"fieldName": "results.channelId", "category": "raw_upstream", "source": "id"},
            {"fieldName": "results.title", "category": "raw_upstream", "source": "snippet.title"},
            {"fieldName": "results.normalizedMetadata", "category": "normalized", "source": "public profile mappings"},
            {"fieldName": "results.enrichment", "category": "normalized", "source": "bounded latest-upload enrichment"},
            {"fieldName": "results.heuristics", "category": "heuristic_inferred", "source": "public channel material"},
        ],
        "errorCategories": [
            "invalid_parameters",
            "unavailable_resource",
            "authorization_sensitive_data",
            "quota_exhaustion",
            "upstream_failure",
            "partial_enrichment_failure",
        ],
        "errorGuidance": {
            "invalid_parameters": "Correct the identified request field and retry.",
            "unavailable_resource": "Use a different accessible channel identifier.",
            "authorization_sensitive_data": "Obtain appropriate authorization if applicable.",
            "quota_exhaustion": "Retry after capacity is available.",
            "upstream_failure": "Retry when the source service is available.",
            "partial_enrichment_failure": "Use the returned item and retry enrichment later when appropriate.",
        },
    }


def _batch_field_provenance(result: dict[str, Any]) -> dict[str, str]:
    """Build provenance labels only for currently returned batch-item fields.

    :param result: Public batch item before its provenance mapping is attached.
    :return: Field-path-to-provenance mapping for returned public source values.
    """
    provenance: dict[str, str] = {"channelId": "raw_upstream", "enrichment": "normalized"}
    for field in ("title", "description", "thumbnails"):
        if field in result:
            provenance[field] = "raw_upstream"
    metadata = result.get("normalizedMetadata") if isinstance(result.get("normalizedMetadata"), dict) else {}
    for field in ("country", "defaultLanguage", "joinedAt", "customUrl"):
        if field in metadata:
            provenance[f"normalizedMetadata.{field}"] = "normalized"
    if metadata:
        provenance["normalizedMetadata.emailsFound"] = "heuristic_inferred"
        provenance["normalizedMetadata.contactLinks"] = "heuristic_inferred"
    if "heuristics" in result:
        provenance["heuristics.creatorClassification"] = "heuristic_inferred"
        provenance["heuristics.creatorSignals"] = "heuristic_inferred"
    if "latestVideoPublishedAt" in result:
        provenance["latestVideoPublishedAt"] = "normalized"
    content_details = result.get("contentDetails") if isinstance(result.get("contentDetails"), dict) else {}
    if "uploadsPlaylistId" in content_details:
        provenance["contentDetails.uploadsPlaylistId"] = "raw_upstream"
    return provenance


def _normalize_batch_channel_item(item: dict[str, Any], parts: list[str]) -> dict[str, Any] | None:
    """Normalize one available source channel item for its selected public groups.

    :param item: Lower-level channel record with an identifier and public profile fields.
    :param parts: Valid public source-detail groups selected by the caller.
    :return: Successful normalized batch item, or ``None`` for an unusable source record.
    """
    channel_id = item.get("id")
    if not isinstance(channel_id, str) or not channel_id.strip():
        return None
    result: dict[str, Any] = {"channelId": channel_id.strip(), "outcome": {"status": "success"}}
    if "snippet" in parts:
        snippet = item.get("snippet") if isinstance(item.get("snippet"), dict) else {}
        for field in ("title", "description", "thumbnails"):
            _copy_if_present(result, snippet, field)
        result["normalizedMetadata"] = _normalized_metadata(snippet)
        classification, signals = _creator_classification(snippet)
        result["heuristics"] = {"creatorClassification": classification, "creatorSignals": signals}
    if "contentDetails" in parts:
        uploads_playlist_id = _uploads_playlist_id(item)
        if uploads_playlist_id:
            result["contentDetails"] = {"uploadsPlaylistId": uploads_playlist_id}
    return result


def _enrich_batch_channel_item(
    result: dict[str, Any],
    item: dict[str, Any],
    playlist_items,
    include_latest_upload: bool,
) -> None:
    """Attach one bounded latest-upload state to a successful batch item.

    :param result: Successful normalized batch item to enrich in place.
    :param item: Source channel record containing an optional uploads playlist.
    :param playlist_items: Lower-level playlist-item lookup callable.
    :param include_latest_upload: Whether the caller requested latest-upload enrichment.
    :return: ``None`` after adding complete, unavailable, or not-requested enrichment state.
    """
    if not include_latest_upload:
        result["enrichment"] = {"status": "not_requested"}
        result["fieldProvenance"] = _batch_field_provenance(result)
        return
    uploads_playlist_id = _uploads_playlist_id(item)
    if not uploads_playlist_id:
        result["enrichment"] = {"status": "unavailable"}
        result["fieldProvenance"] = _batch_field_provenance(result)
        return
    try:
        latest_payload = playlist_items({"part": "contentDetails", "playlistId": uploads_playlist_id, "maxResults": 1})
    except PlaylistItemsListToolError as exc:
        partial_state = _partial_enrichment_state(exc)
        result["outcome"] = {
            "status": "partial",
            "category": partial_state["category"],
            "causeCategory": partial_state["causeCategory"],
        }
        result["enrichment"] = partial_state
        result["fieldProvenance"] = _batch_field_provenance(result)
        return
    latest_timestamp = _latest_video_published_at(latest_payload)
    if latest_timestamp:
        result["latestVideoPublishedAt"] = latest_timestamp
        result["enrichment"] = {"status": "complete"}
    else:
        result["enrichment"] = {"status": "unavailable"}
    result["fieldProvenance"] = _batch_field_provenance(result)


def _batch_summary(results: list[dict[str, Any]], requested_count: int) -> dict[str, int]:
    """Build the documented partition summary for currently successful batch items.

    :param results: Ordered public batch items.
    :param requested_count: Number of validated identifiers in the request.
    :return: Summary counts for requested, successful, unavailable, and partial items.
    """
    return {
        "requested": requested_count,
        "successful": sum(item.get("outcome", {}).get("status") == "success" for item in results),
        "unavailable": sum(item.get("outcome", {}).get("status") == "unavailable" for item in results),
        "partiallyEnriched": sum(item.get("outcome", {}).get("status") == "partial" for item in results),
    }


def _map_batch_channels_list_error(error: ChannelsListToolError) -> ChannelsGetChannelsToolError:
    """Translate a bulk core lookup error to the batch public taxonomy.

    :param error: Safe lower-level channel-list failure.
    :return: Sanitized public batch channel-detail error.
    """
    mapped = _map_channels_list_error(error)
    return ChannelsGetChannelsToolError(str(mapped), category=mapped.category, details=mapped.details)


def build_channels_get_channels_handler(*, channels=None, playlist_items=None):
    """Build a callable handler for bounded ordered public channel batches.

    :param channels: Optional lower-level channel-list handler override for tests.
    :param playlist_items: Optional lower-level playlist-items handler override for bounded enrichment tests.
    :return: Callable batch channel-detail handler.
    """
    selected_channels = channels or build_channels_list_handler()
    selected_playlist_items = playlist_items or build_playlist_items_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated public batch channel-detail request.

        :param arguments: Caller-provided public batch arguments.
        :return: Ordered normalized channel items and their batch summary.
        :raises ChannelsGetChannelsToolError: If validation or the bulk core lookup fails.
        """
        request = validate_channels_get_channels_arguments(arguments)
        try:
            payload = selected_channels({"part": "snippet,contentDetails", "id": ",".join(request["channelIds"])})
        except ChannelsListToolError as exc:
            raise _map_batch_channels_list_error(exc) from exc
        source_items = payload.get("items") if isinstance(payload, dict) and isinstance(payload.get("items"), list) else []
        by_channel_id = {
            item["id"].strip(): item
            for item in source_items
            if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"].strip()
        }
        results = []
        for channel_id in request["channelIds"]:
            item = by_channel_id.get(channel_id)
            if item is None:
                results.append(
                    {
                        "channelId": channel_id,
                        "outcome": {"status": "unavailable", "category": "unavailable_resource"},
                    }
                )
                continue
            normalized = _normalize_batch_channel_item(item, request["parts"])
            if normalized is None:
                continue
            _enrich_batch_channel_item(normalized, item, selected_playlist_items, request["includeLatestUpload"])
            results.append(normalized)
        return {
            "requestedChannelIds": request["channelIds"],
            "results": results,
            "summary": _batch_summary(results, len(request["channelIds"])),
        }

    return handler


def build_channels_get_channels_tool_descriptor(*, channels=None, playlist_items=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for ``channels_getChannels``.

    :param channels: Optional lower-level channel-list handler override for tests.
    :param playlist_items: Optional lower-level playlist-items handler override for tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": CHANNELS_GET_CHANNELS_TOOL_NAME,
        "description": "Return normalized details for multiple YouTube channels in request order.",
        "inputSchema": CHANNELS_GET_CHANNELS_INPUT_SCHEMA,
        "handler": build_channels_get_channels_handler(channels=channels, playlist_items=playlist_items),
        "metadata": build_channels_get_channels_metadata(),
    }


def _channel_search_timestamp(value: Any, field: str) -> str:
    """Validate one timezone-aware public channel-search timestamp.

    :param value: Candidate timestamp supplied by a caller.
    :param field: Public field name used in a safe validation error.
    :return: Stripped ISO 8601 timestamp with an explicit timezone.
    :raises ChannelsSearchChannelsToolError: If the timestamp is missing, malformed, or timezone-naive.
    """
    if not isinstance(value, str) or not value.strip():
        raise ChannelsSearchChannelsToolError(
            f"{field} must be a non-empty ISO 8601 timestamp",
            category="invalid_parameters",
            details={"field": field},
        )
    normalized = value.strip()
    try:
        parsed = datetime.fromisoformat(normalized[:-1] + "+00:00" if normalized.endswith("Z") else normalized)
    except ValueError as exc:
        raise ChannelsSearchChannelsToolError(
            f"{field} must be an ISO 8601 timestamp with timezone",
            category="invalid_parameters",
            details={"field": field},
        ) from exc
    if parsed.tzinfo is None:
        raise ChannelsSearchChannelsToolError(
            f"{field} must include a timezone",
            category="invalid_parameters",
            details={"field": field},
        )
    return normalized


def validate_channels_search_content_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one public channel-content search request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized required fields with internal default search controls.
    :raises ChannelsSearchContentToolError: If a public field is missing, invalid, or unsupported.
    """
    if not isinstance(arguments, dict):
        raise ChannelsSearchContentToolError(
            "channels_searchContent arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected = set(arguments) - set(CHANNELS_SEARCH_CONTENT_INPUT_SCHEMA["properties"])
    if unexpected:
        raise ChannelsSearchContentToolError(
            "channels_searchContent received an unsupported field",
            category="invalid_parameters",
            details={"field": min(unexpected)},
        )
    normalized: dict[str, Any] = {"maxResults": arguments.get("maxResults", 10), "order": arguments.get("order", "relevance")}
    for field in ("channelId", "query"):
        value = arguments.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ChannelsSearchContentToolError(
                f"channels_searchContent requires a non-empty {field}",
                category="invalid_parameters",
                details={"field": field},
            )
        normalized[field] = value.strip()
    max_results = normalized["maxResults"]
    if isinstance(max_results, bool) or not isinstance(max_results, int) or not 1 <= max_results <= CHANNELS_SEARCH_CONTENT_MAX_RESULTS:
        raise ChannelsSearchContentToolError(
            f"maxResults must be an integer from 1 through {CHANNELS_SEARCH_CONTENT_MAX_RESULTS}",
            category="invalid_parameters",
            details={"field": "maxResults"},
        )
    if normalized["order"] not in ("relevance", "date", "viewCount"):
        raise ChannelsSearchContentToolError(
            "order must use a supported direct-search value",
            category="invalid_parameters",
            details={"field": "order"},
        )
    if "language" in arguments:
        language = arguments["language"]
        if not isinstance(language, str) or not language.strip() or not _BCP47_LANGUAGE_TAG_PATTERN.fullmatch(language.strip()):
            raise ChannelsSearchContentToolError(
                "language must be a valid BCP 47 language tag",
                category="invalid_parameters",
                details={"field": "language"},
            )
        normalized["language"] = language.strip()
    return normalized


def _channels_search_content_base_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Build the one bounded lower-layer request for channel-content search.

    :param arguments: Validated public channel-content search request.
    :return: Lower-layer public video-search arguments constrained to one channel.
    """
    result = {
        "part": "snippet",
        "q": arguments["query"],
        "channelId": arguments["channelId"],
        "type": "video",
        "maxResults": arguments["maxResults"],
        "order": arguments["order"],
    }
    if "language" in arguments:
        result["relevanceLanguage"] = arguments["language"]
    return result


def _normalize_channels_search_content_items(payload: dict[str, Any], channel_id: str, max_results: int) -> tuple[list[dict[str, Any]], int]:
    """Normalize usable public video records from one channel-constrained search.

    :param payload: Lower-layer search payload containing public source items.
    :param channel_id: Requested normalized channel identifier.
    :param max_results: Final public result cap.
    :return: Distinct public video items in source order and a safe omitted-item count.
    """
    source_items = payload.get("items") if isinstance(payload, dict) and isinstance(payload.get("items"), list) else []
    items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    omitted_item_count = 0
    for source_item in source_items:
        if not isinstance(source_item, dict):
            omitted_item_count += 1
            continue
        identifier = source_item.get("id") if isinstance(source_item.get("id"), dict) else {}
        video_id = identifier.get("videoId")
        snippet = source_item.get("snippet") if isinstance(source_item.get("snippet"), dict) else {}
        source_channel_id = snippet.get("channelId")
        if (
            not isinstance(video_id, str)
            or not video_id.strip()
            or not isinstance(source_channel_id, str)
            or source_channel_id.strip() != channel_id
            or video_id.strip() in seen_ids
        ):
            omitted_item_count += 1
            continue
        normalized_video_id = video_id.strip()
        seen_ids.add(normalized_video_id)
        item: dict[str, Any] = {"videoId": normalized_video_id, "contentType": "video"}
        for field in ("title", "description", "publishedAt", "channelId", "channelTitle", "thumbnails"):
            _copy_if_present(item, snippet, field)
        items.append(item)
        if len(items) >= max_results:
            break
    return items, omitted_item_count


def _map_channels_search_content_error(error: SearchListToolError) -> ChannelsSearchContentToolError:
    """Translate a lower-layer search error into the channel-content taxonomy.

    :param error: Safe lower-layer search failure.
    :return: Sanitized public channel-content-search failure.
    """
    category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
        "resource_not_found": "unavailable_resource",
    }.get(error.category, "upstream_failure")
    return ChannelsSearchContentToolError(safe_upstream_error_message(), category=category, details=error.details)


def _channels_search_content_result(arguments: dict[str, Any], items: list[dict[str, Any]], omitted_item_count: int) -> dict[str, Any]:
    """Build one stable direct-search public result collection.

    :param arguments: Validated channel-content search request.
    :param items: Usable requested-channel video items in source order.
    :param omitted_item_count: Safely known count of omitted source records.
    :return: Normalized result collection with direct-search context and provenance.
    """
    result: dict[str, Any] = {
        "channelId": arguments["channelId"],
        "query": arguments["query"],
        "items": items,
        "returnedCount": len(items),
        "maxResults": arguments["maxResults"],
        "appliedInputs": dict(arguments),
        "searchContext": {
            "source": "channel_constrained_public_video_search",
            "matching": "direct_upstream_search",
            "ordering": "upstream_order",
            "order": arguments["order"],
            "rankingApplied": False,
            "enrichmentApplied": False,
            "localFilteringApplied": False,
            "publicContentOnly": True,
            "languageRefinesRelevance": "language" in arguments,
            "requestTimeVariability": "search_results_can_change",
        },
        "fieldProvenance": {
            "items.videoId": "raw_upstream",
            "items.contentType": "normalized",
            "items.title": "raw_upstream",
            "items.description": "raw_upstream",
            "items.publishedAt": "raw_upstream",
            "items.channelId": "raw_upstream",
            "items.channelTitle": "raw_upstream",
            "items.thumbnails": "raw_upstream",
            "channelId": "normalized",
            "query": "normalized",
            "returnedCount": "normalized",
            "maxResults": "normalized",
            "appliedInputs": "normalized",
            "searchContext": "normalized",
        },
    }
    if omitted_item_count:
        result["partialAvailability"] = {
            "status": "partial",
            "omittedItemCount": omitted_item_count,
            "reasons": ["unusable_or_out_of_scope_source_item"],
        }
        result["fieldProvenance"]["partialAvailability"] = "normalized"
    return result


def build_channels_search_content_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for direct channel-content search.

    :return: JSON-compatible executable metadata without a representative marker.
    """
    return {
        "name": CHANNELS_SEARCH_CONTENT_TOOL_NAME,
        "family": "channels",
        "parameters": list(CHANNELS_SEARCH_CONTENT_INPUT_SCHEMA["properties"]),
        "inputContract": CHANNELS_SEARCH_CONTENT_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "direct_search_normalization",
            "lowerLayerDependencies": ["search.list"],
            "boundedness": "one channel-constrained public video search; 1-50 normalized items",
            "partialResultPolicy": "A successful no-match response is empty; unusable source records are disclosed only in safe aggregate form; required search failure is a whole-request error.",
        },
        "lowerLayerDependencies": ["search.list"],
        "publicContentPolicy": "Only publicly available requested-channel videos are returned; inaccessible content is omitted.",
        "directSearchSemantics": {
            "matching": "direct_upstream_search",
            "ordering": "upstream_order",
            "localRankingApplied": False,
            "localEnrichmentApplied": False,
            "localFilteringApplied": False,
        },
        "languageSemantics": {
            "input": "BCP 47 language preference",
            "effect": "relevance_hint_only",
            "guaranteesLanguageMatchedResults": False,
        },
        "authAndQuotaNotes": ["Uses configured public-read capability and does not request owner-scoped data.", "One bounded public search consumes quota and can fail when capacity is exhausted."],
        "responseFields": [
            {"fieldName": "items.videoId", "category": "raw_upstream", "source": "id.videoId"},
            {"fieldName": "items.contentType", "category": "normalized", "source": "fixed public video scope"},
            {"fieldName": "items.title", "category": "raw_upstream", "source": "snippet.title"},
            {"fieldName": "items.description", "category": "raw_upstream", "source": "snippet.description"},
            {"fieldName": "items.publishedAt", "category": "raw_upstream", "source": "snippet.publishedAt"},
            {"fieldName": "items.channelId", "category": "raw_upstream", "source": "snippet.channelId"},
            {"fieldName": "items.channelTitle", "category": "raw_upstream", "source": "snippet.channelTitle"},
            {"fieldName": "items.thumbnails", "category": "raw_upstream", "source": "snippet.thumbnails"},
            {"fieldName": "searchContext", "category": "normalized", "source": "direct-search contract"},
            {"fieldName": "partialAvailability", "category": "normalized", "source": "safe aggregate source omissions"},
        ],
        "errorCategories": ["invalid_parameters", "unavailable_resource", "authorization_sensitive_data", "quota_exhaustion", "upstream_failure"],
        "errorGuidance": {
            "invalid_parameters": "Correct the identified request field and retry.",
            "unavailable_resource": "Use a different accessible channel identifier or retry later.",
            "authorization_sensitive_data": "Obtain applicable public-read capability if available.",
            "quota_exhaustion": "Retry after capacity is available.",
            "upstream_failure": "Retry when the source service is available.",
        },
    }


def build_channels_search_content_handler(*, search=None):
    """Build a callable handler for direct public channel-content search.

    :param search: Optional lower-layer ``search_list`` override for tests.
    :return: Callable bounded direct-search handler.
    """
    selected_search = search or build_search_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated public channel-content search request.

        :param arguments: Caller-provided public tool arguments.
        :return: Normalized public requested-channel video collection.
        :raises ChannelsSearchContentToolError: If validation or the required search fails.
        """
        request = validate_channels_search_content_arguments(arguments)
        try:
            payload = selected_search(_channels_search_content_base_arguments(request))
        except SearchListToolError as exc:
            raise _map_channels_search_content_error(exc) from exc
        items, omitted_item_count = _normalize_channels_search_content_items(payload, request["channelId"], request["maxResults"])
        return _channels_search_content_result(request, items, omitted_item_count)

    return handler


def build_channels_search_content_tool_descriptor(*, search=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for ``channels_searchContent``.

    :param search: Optional lower-layer ``search_list`` override for tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": CHANNELS_SEARCH_CONTENT_TOOL_NAME,
        "description": "Search publicly available video content within one YouTube channel using direct search.",
        "inputSchema": CHANNELS_SEARCH_CONTENT_INPUT_SCHEMA,
        "handler": build_channels_search_content_handler(search=search),
        "metadata": build_channels_search_content_metadata(),
    }


def validate_channels_search_channels_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one public channel-search request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized request with public defaults and only supplied optional filters.
    :raises ChannelsSearchChannelsToolError: If any public field is invalid or unsupported.
    """
    if not isinstance(arguments, dict):
        raise ChannelsSearchChannelsToolError(
            "channels_searchChannels arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected = set(arguments) - set(CHANNELS_SEARCH_CHANNELS_INPUT_SCHEMA["properties"])
    if unexpected:
        raise ChannelsSearchChannelsToolError(
            "channels_searchChannels received an unsupported field",
            category="invalid_parameters",
            details={"field": min(unexpected)},
        )
    query = arguments.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ChannelsSearchChannelsToolError(
            "channels_searchChannels requires a non-empty query",
            category="invalid_parameters",
            details={"field": "query"},
        )
    normalized: dict[str, Any] = {
        "query": query.strip(),
        "maxResults": arguments.get("maxResults", 10),
        "creatorOnly": arguments.get("creatorOnly", False),
        "sortBy": arguments.get("sortBy", "relevance"),
    }
    max_results = normalized["maxResults"]
    if isinstance(max_results, bool) or not isinstance(max_results, int) or not 1 <= max_results <= CHANNELS_SEARCH_CHANNELS_MAX_RESULTS:
        raise ChannelsSearchChannelsToolError(
            "maxResults must be an integer from 1 through 50",
            category="invalid_parameters",
            details={"field": "maxResults"},
        )
    if not isinstance(normalized["creatorOnly"], bool):
        raise ChannelsSearchChannelsToolError(
            "creatorOnly must be a boolean",
            category="invalid_parameters",
            details={"field": "creatorOnly"},
        )
    if normalized["sortBy"] not in CHANNELS_SEARCH_CHANNELS_SORTS:
        raise ChannelsSearchChannelsToolError(
            "sortBy must use a supported ranking value",
            category="invalid_parameters",
            details={"field": "sortBy"},
        )
    for field, allowed in (("order", CHANNELS_SEARCH_CHANNELS_ORDERS), ("channelType", CHANNELS_SEARCH_CHANNELS_TYPES)):
        if field in arguments:
            value = arguments[field]
            if not isinstance(value, str) or value not in allowed:
                raise ChannelsSearchChannelsToolError(
                    f"{field} must use a supported value",
                    category="invalid_parameters",
                    details={"field": field},
                )
            normalized[field] = value
    for field in ("minSubscribers", "maxSubscribers"):
        if field in arguments:
            value = arguments[field]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ChannelsSearchChannelsToolError(
                    f"{field} must be a non-negative integer",
                    category="invalid_parameters",
                    details={"field": field},
                )
            normalized[field] = value
    if normalized.get("minSubscribers") is not None and normalized.get("maxSubscribers") is not None and normalized["minSubscribers"] > normalized["maxSubscribers"]:
        raise ChannelsSearchChannelsToolError(
            "minSubscribers cannot exceed maxSubscribers",
            category="invalid_parameters",
            details={"field": "minSubscribers"},
        )
    for field in ("lastUploadAfter", "lastUploadBefore"):
        if field in arguments:
            normalized[field] = _channel_search_timestamp(arguments[field], field)
    if "lastUploadAfter" in normalized and "lastUploadBefore" in normalized:
        after = datetime.fromisoformat(normalized["lastUploadAfter"])
        before = datetime.fromisoformat(normalized["lastUploadBefore"])
        if after > before:
            raise ChannelsSearchChannelsToolError(
                "lastUploadAfter cannot be later than lastUploadBefore",
                category="invalid_parameters",
                details={"field": "lastUploadAfter"},
            )
    return normalized


def _channel_search_base_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Build the bounded lower-level base request for channel search.

    :param arguments: Validated public channel-search request.
    :return: Lower-level public search arguments restricted to channels.
    """
    result = {
        "part": "snippet",
        "q": arguments["query"],
        "type": "channel",
        "maxResults": arguments["maxResults"],
        "order": arguments.get("order", "relevance"),
    }
    if "channelType" in arguments:
        result["channelType"] = arguments["channelType"]
    return result


def _normalize_channel_search_candidates(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize and de-duplicate base channel-search candidates.

    :param payload: Lower-level search result with public channel references.
    :return: Distinct normalized candidates in earliest base-search order.
    """
    source_items = payload.get("items") if isinstance(payload, dict) and isinstance(payload.get("items"), list) else []
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for position, item in enumerate(source_items):
        if not isinstance(item, dict):
            continue
        identifier = item.get("id") if isinstance(item.get("id"), dict) else {}
        channel_id = identifier.get("channelId")
        if not isinstance(channel_id, str) or not channel_id.strip() or channel_id.strip() in seen:
            continue
        normalized_id = channel_id.strip()
        seen.add(normalized_id)
        snippet = item.get("snippet") if isinstance(item.get("snippet"), dict) else {}
        candidate: dict[str, Any] = {"channelId": normalized_id, "_baseSearchPosition": position}
        for field in ("title", "description", "thumbnails"):
            _copy_if_present(candidate, snippet, field)
        candidates.append(candidate)
    return candidates


def _channel_search_field_provenance(candidates: list[dict[str, Any]]) -> dict[str, str]:
    """Build provenance for public fields returned by channel search.

    :param candidates: Final public candidate collection.
    :return: Public field-path-to-provenance mapping.
    """
    provenance = {"channelId": "raw_upstream"}
    for field in ("title", "description", "thumbnails"):
        if any(field in candidate for candidate in candidates):
            provenance[field] = "raw_upstream"
    if any("normalizedMetadata" in candidate for candidate in candidates):
        provenance["normalizedMetadata"] = "normalized"
    if any("statistics" in candidate for candidate in candidates):
        provenance["statistics.subscriberCount"] = "raw_upstream"
    if any("latestVideoPublishedAt" in candidate for candidate in candidates):
        provenance["latestVideoPublishedAt"] = "normalized"
    if any("heuristics" in candidate for candidate in candidates):
        provenance["heuristics.creatorClassification"] = "heuristic_inferred"
        provenance["heuristics.creatorSignals"] = "heuristic_inferred"
    return provenance


def _map_channel_search_error(error: SearchListToolError) -> ChannelsSearchChannelsToolError:
    """Map a lower-level base-search failure to the Layer 3 public taxonomy.

    :param error: Safe lower-level search failure.
    :return: Sanitized public channel-search error.
    """
    category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
        "resource_not_found": "unavailable_resource",
    }.get(error.category, "upstream_failure")
    return ChannelsSearchChannelsToolError(safe_upstream_error_message(), category=category, details=error.details)


def _channel_search_required_rules(arguments: dict[str, Any]) -> list[str]:
    """Return active rules that require conditional public enrichment.

    :param arguments: Validated public channel-search request.
    :return: Ordered caller-visible names of active enrichment-dependent rules.
    """
    rules = [field for field in ("minSubscribers", "maxSubscribers", "lastUploadAfter", "lastUploadBefore") if field in arguments]
    if arguments["creatorOnly"]:
        rules.append("creatorOnly")
    if arguments["sortBy"] != "relevance":
        rules.append(arguments["sortBy"])
    return rules


def _channel_search_requires_activity(arguments: dict[str, Any]) -> bool:
    """Return whether active rules require a public latest-upload lookup.

    :param arguments: Validated public channel-search request.
    :return: ``True`` when an activity filter or recent-activity rank is active.
    """
    return "lastUploadAfter" in arguments or "lastUploadBefore" in arguments or arguments["sortBy"] == "recent_activity"


def _channel_search_subscriber_count(item: dict[str, Any]) -> tuple[str, int] | None:
    """Return an available public subscriber count in raw and numeric forms.

    :param item: Public lower-level channel item.
    :return: Raw public count and parsed non-negative integer, or ``None`` when unavailable.
    """
    statistics = item.get("statistics") if isinstance(item.get("statistics"), dict) else {}
    raw_count = statistics.get("subscriberCount")
    if not isinstance(raw_count, str) or not raw_count.isdigit():
        return None
    return raw_count, int(raw_count)


def _channel_search_timestamp_matches(timestamp: str, arguments: dict[str, Any]) -> bool:
    """Return whether one activity timestamp satisfies inclusive request bounds.

    :param timestamp: Available timezone-aware public latest-upload timestamp.
    :param arguments: Validated public channel-search request.
    :return: ``True`` when the timestamp is within all supplied inclusive bounds.
    """
    value = datetime.fromisoformat(timestamp)
    if "lastUploadAfter" in arguments and value < datetime.fromisoformat(arguments["lastUploadAfter"]):
        return False
    return "lastUploadBefore" not in arguments or value <= datetime.fromisoformat(arguments["lastUploadBefore"])


def _channel_search_partial_error(excluded_count: int, reasons: list[str], required_for: list[str]) -> ChannelsSearchChannelsToolError:
    """Build the documented safe all-candidates-unavailable enrichment error.

    :param excluded_count: Number of candidates excluded for unavailable required data.
    :param reasons: Safe aggregate unavailable-data categories.
    :param required_for: Active enrichment-dependent filter or ranking names.
    :return: Public partial-enrichment failure without lower-layer diagnostics.
    """
    return ChannelsSearchChannelsToolError(
        "Required public channel enrichment is unavailable",
        category="partial_enrichment_failure",
        details={"excludedCandidateCount": excluded_count, "reasons": reasons, "requiredFor": required_for},
    )


def _rank_channel_search_candidates(candidates: list[dict[str, Any]], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    """Return eligible candidates in the documented deterministic final order.

    :param candidates: Filtered candidates with enrichment required by the selected ranking.
    :param arguments: Validated public channel-search request.
    :return: Candidates sorted by the selected ranking and base-search tie position.
    """
    sort_by = arguments["sortBy"]
    if sort_by == "relevance":
        return sorted(candidates, key=lambda candidate: candidate["_baseSearchPosition"])
    if sort_by == "subscribers_asc":
        return sorted(candidates, key=lambda candidate: (candidate["_subscriberCount"], candidate["_baseSearchPosition"]))
    if sort_by == "subscribers_desc":
        return sorted(candidates, key=lambda candidate: (-candidate["_subscriberCount"], candidate["_baseSearchPosition"]))
    if sort_by == "indie_priority":
        return sorted(
            candidates,
            key=lambda candidate: (
                0 if candidate["heuristics"]["creatorClassification"] == "creator" else 1,
                candidate["_subscriberCount"],
                candidate["_baseSearchPosition"],
            ),
        )
    return sorted(
        candidates,
        key=lambda candidate: (
            -datetime.fromisoformat(candidate["latestVideoPublishedAt"]).timestamp(),
            candidate["_baseSearchPosition"],
        ),
    )


def _enrich_and_filter_channel_search_candidates(candidates: list[dict[str, Any]], arguments: dict[str, Any], channels, playlist_items) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Conditionally enrich and filter base candidates using public channel data.

    :param candidates: Distinct normalized base channel candidates.
    :param arguments: Validated public channel-search request.
    :param channels: Lower-level batched public channel lookup callable.
    :param playlist_items: Lower-level public uploads-playlist lookup callable.
    :return: Eligible enriched candidates and optional safe partial-enrichment summary.
    :raises ChannelsSearchChannelsToolError: If required enrichment is unavailable for every candidate.
    """
    required_for = _channel_search_required_rules(arguments)
    if not required_for:
        return candidates, None
    try:
        payload = channels({"part": "snippet,statistics,contentDetails", "id": ",".join(candidate["channelId"] for candidate in candidates)})
    except ChannelsListToolError as exc:
        mapped = _map_channels_list_error(exc)
        raise ChannelsSearchChannelsToolError(str(mapped), category=mapped.category, details=mapped.details) from exc
    source_items = payload.get("items") if isinstance(payload, dict) and isinstance(payload.get("items"), list) else []
    by_id = {
        item["id"].strip(): item
        for item in source_items
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"].strip()
    }
    eligible: list[dict[str, Any]] = []
    reasons: list[str] = []
    excluded_count = 0
    evaluated_count = 0
    needs_subscriber = "minSubscribers" in arguments or "maxSubscribers" in arguments or arguments["sortBy"] in {"subscribers_asc", "subscribers_desc", "indie_priority"}
    needs_activity = _channel_search_requires_activity(arguments)
    for candidate in candidates:
        source = by_id.get(candidate["channelId"])
        if source is None:
            excluded_count += 1
            if "channel_metadata_unavailable" not in reasons:
                reasons.append("channel_metadata_unavailable")
            continue
        enriched = dict(candidate)
        snippet = source.get("snippet") if isinstance(source.get("snippet"), dict) else {}
        enriched["normalizedMetadata"] = _normalized_metadata(snippet)
        classification, signals = _creator_classification(snippet)
        enriched["heuristics"] = {"creatorClassification": classification, "creatorSignals": signals}
        subscriber = _channel_search_subscriber_count(source)
        if needs_subscriber:
            if subscriber is None:
                excluded_count += 1
                if "subscriber_count_unavailable" not in reasons:
                    reasons.append("subscriber_count_unavailable")
                continue
            raw_count, count = subscriber
            enriched["statistics"] = {"subscriberCount": raw_count}
            enriched["_subscriberCount"] = count
        elif subscriber is not None:
            enriched["statistics"] = {"subscriberCount": subscriber[0]}
        if needs_activity:
            uploads_playlist_id = _uploads_playlist_id(source)
            if uploads_playlist_id is None:
                excluded_count += 1
                if "latest_activity_unavailable" not in reasons:
                    reasons.append("latest_activity_unavailable")
                continue
            try:
                latest_payload = playlist_items({"part": "contentDetails", "playlistId": uploads_playlist_id, "maxResults": 1})
            except PlaylistItemsListToolError:
                excluded_count += 1
                if "latest_activity_unavailable" not in reasons:
                    reasons.append("latest_activity_unavailable")
                continue
            latest_timestamp = _latest_video_published_at(latest_payload)
            if latest_timestamp is None:
                excluded_count += 1
                if "latest_activity_unavailable" not in reasons:
                    reasons.append("latest_activity_unavailable")
                continue
            enriched["latestVideoPublishedAt"] = latest_timestamp
        evaluated_count += 1
        if "minSubscribers" in arguments and enriched["_subscriberCount"] < arguments["minSubscribers"]:
            continue
        if "maxSubscribers" in arguments and enriched["_subscriberCount"] > arguments["maxSubscribers"]:
            continue
        if needs_activity and not _channel_search_timestamp_matches(enriched["latestVideoPublishedAt"], arguments):
            continue
        if arguments["creatorOnly"] and classification != "creator":
            continue
        eligible.append(enriched)
    if candidates and evaluated_count == 0 and excluded_count:
        raise _channel_search_partial_error(excluded_count, reasons, required_for)
    partial = None
    if excluded_count:
        partial = {"status": "partial", "excludedCandidateCount": excluded_count, "reasons": reasons, "requiredFor": required_for}
    return eligible, partial


def build_channels_search_channels_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for concrete public channel search.

    :return: JSON-compatible metadata describing bounded composite search behavior.
    """
    return {
        "name": CHANNELS_SEARCH_CHANNELS_TOOL_NAME,
        "family": "channels",
        "parameters": list(CHANNELS_SEARCH_CHANNELS_INPUT_SCHEMA["properties"]),
        "inputContract": CHANNELS_SEARCH_CHANNELS_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "ranked_enrichment",
            "boundedness": "one base search of at most 50 candidates; enrichment is conditional and bounded per distinct candidate",
            "partialResultPolicy": "Conditional public enrichment excludes candidates whose required data is unavailable and discloses them safely.",
        },
        "lowerLayerDependencies": ["search.list", "channels.list", "playlistItems.list"],
        "continuationPolicy": "Any continuation context belongs to the base-search result and does not paginate the final filtered or ranked collection.",
        "rankingSemantics": {
            "sortBy": list(CHANNELS_SEARCH_CHANNELS_SORTS),
            "filterOrder": "Apply filters before final ranking and result cap.",
            "ties": "Preserve earliest base-search position for every ranking tie.",
        },
        "responseFields": [
            {"fieldName": "channelId", "category": "raw_upstream", "source": "id.channelId"},
            {"fieldName": "title", "category": "raw_upstream", "source": "snippet.title"},
            {"fieldName": "description", "category": "raw_upstream", "source": "snippet.description"},
            {"fieldName": "thumbnails", "category": "raw_upstream", "source": "snippet.thumbnails"},
            {"fieldName": "normalizedMetadata", "category": "normalized", "source": "public channel profile"},
            {"fieldName": "statistics.subscriberCount", "category": "raw_upstream", "source": "statistics.subscriberCount"},
            {"fieldName": "latestVideoPublishedAt", "category": "normalized", "source": "public uploads playlist"},
            {"fieldName": "heuristics.creatorClassification", "category": "heuristic_inferred", "source": "public channel material"},
            {"fieldName": "appliedInputs", "category": "normalized", "source": "validated request"},
            {"fieldName": "partialEnrichment", "category": "normalized", "source": "aggregate enrichment status"},
        ],
        "authAndQuotaNotes": [
            "Uses public configured search capability and does not request owner-scoped data.",
            "Search and conditional public enrichment consume bounded lower-layer quota.",
        ],
        "errorCategories": [
            "invalid_parameters",
            "unavailable_resource",
            "authorization_sensitive_data",
            "quota_exhaustion",
            "upstream_failure",
            "partial_enrichment_failure",
        ],
        "errorGuidance": {
            "invalid_parameters": "Correct the identified request field and retry.",
            "unavailable_resource": "Use a different accessible query or relax the affected refinement.",
            "authorization_sensitive_data": "Use permitted public data or obtain the necessary capability.",
            "quota_exhaustion": "Retry after capacity is available.",
            "upstream_failure": "Retry when the source service is available.",
            "partial_enrichment_failure": "Relax the enrichment-dependent rule or retry when public metadata is available.",
        },
    }


def build_channels_search_channels_handler(*, search=None, channels=None, playlist_items=None):
    """Build the callable public channel-search handler.

    :param search: Optional lower-level search handler override for tests.
    :param channels: Reserved lower-level channel handler for conditional enrichment.
    :param playlist_items: Reserved lower-level playlist handler for conditional activity enrichment.
    :return: Callable that validates, searches, normalizes, and returns public channels.
    """
    selected_search = search or build_search_list_handler()
    selected_channels = channels or build_channels_list_handler()
    selected_playlist_items = playlist_items or build_playlist_items_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated public channel-search request.

        :param arguments: Caller-provided public channel-search arguments.
        :return: Bounded normalized base-search collection with safe context.
        :raises ChannelsSearchChannelsToolError: If validation or base search fails.
        """
        normalized = validate_channels_search_channels_arguments(arguments)
        try:
            payload = selected_search(_channel_search_base_arguments(normalized))
        except SearchListToolError as exc:
            raise _map_channel_search_error(exc) from exc
        candidates = _normalize_channel_search_candidates(payload)
        eligible, partial_enrichment = _enrich_and_filter_channel_search_candidates(
            candidates,
            normalized,
            selected_channels,
            selected_playlist_items,
        )
        ranked = _rank_channel_search_candidates(eligible, normalized)
        public_items = [{key: value for key, value in candidate.items() if not key.startswith("_")} for candidate in ranked]
        result: dict[str, Any] = {
            "items": public_items[: normalized["maxResults"]],
            "appliedInputs": normalized,
            "returnedCount": min(len(public_items), normalized["maxResults"]),
            "maxResults": normalized["maxResults"],
            "fieldProvenance": _channel_search_field_provenance(public_items),
        }
        if partial_enrichment is not None:
            result["partialEnrichment"] = partial_enrichment
        next_page_token = payload.get("nextPageToken") if isinstance(payload, dict) else None
        if isinstance(next_page_token, str) and next_page_token:
            result["nextPageToken"] = next_page_token
        return result

    return handler


def build_channels_search_channels_tool_descriptor(*, search=None, channels=None, playlist_items=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for ``channels_searchChannels``.

    :param search: Optional lower-level search handler override for tests.
    :param channels: Optional lower-level channel handler override for conditional enrichment tests.
    :param playlist_items: Optional lower-level playlist handler override for conditional activity tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": CHANNELS_SEARCH_CHANNELS_TOOL_NAME,
        "description": "Search public YouTube channels with optional public-metadata refinement and ranking.",
        "inputSchema": CHANNELS_SEARCH_CHANNELS_INPUT_SCHEMA,
        "handler": build_channels_search_channels_handler(search=search, channels=channels, playlist_items=playlist_items),
        "metadata": build_channels_search_channels_metadata(),
    }


CHANNELS_FIND_CREATORS_TOOL_NAME = "channels_findCreators"
CHANNELS_FIND_CREATORS_MAX_RESULTS = 50
CHANNELS_FIND_CREATORS_BASE_VIDEO_LIMIT = 50
CHANNELS_FIND_CREATORS_MAX_SAMPLES = 10
CHANNELS_FIND_CREATORS_ORDERS = ("date", "rating", "relevance", "title", "viewCount")
CHANNELS_FIND_CREATORS_SORTS = CHANNELS_SEARCH_CHANNELS_SORTS
CHANNELS_FIND_CREATORS_INPUT_SCHEMA = {
    "type": "object",
    "required": ["query"],
    "properties": {
        "query": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 1, "maximum": CHANNELS_FIND_CREATORS_MAX_RESULTS, "default": 10},
        "order": {"type": "string", "enum": list(CHANNELS_FIND_CREATORS_ORDERS)},
        "videoPublishedAfter": {"type": "string", "format": "date-time"},
        "videoPublishedBefore": {"type": "string", "format": "date-time"},
        "channelMinSubscribers": {"type": "integer", "minimum": 0},
        "channelMaxSubscribers": {"type": "integer", "minimum": 0},
        "channelLastUploadAfter": {"type": "string", "format": "date-time"},
        "channelLastUploadBefore": {"type": "string", "format": "date-time"},
        "creatorOnly": {"type": "boolean", "default": False},
        "sortBy": {"type": "string", "enum": list(CHANNELS_FIND_CREATORS_SORTS), "default": "relevance"},
        "sampleVideosPerChannel": {"type": "integer", "minimum": 0, "maximum": CHANNELS_FIND_CREATORS_MAX_SAMPLES, "default": 0},
    },
    "additionalProperties": False,
}


class ChannelsFindCreatorsToolError(ChannelsGetChannelToolError):
    """Represent a safe caller-facing creator-discovery failure."""


def _creator_timestamp(value: Any, field: str) -> str:
    """Validate a timezone-aware creator-discovery timestamp.

    :param value: Candidate caller-provided timestamp.
    :param field: Public request field name.
    :return: Stripped ISO 8601 timestamp with an explicit timezone.
    :raises ChannelsFindCreatorsToolError: If the value is absent, malformed, or timezone-naive.
    """
    if not isinstance(value, str) or not value.strip():
        raise ChannelsFindCreatorsToolError(f"{field} must be a non-empty ISO 8601 timestamp", category="invalid_parameters", details={"field": field})
    normalized = value.strip()
    try:
        parsed = datetime.fromisoformat(normalized[:-1] + "+00:00" if normalized.endswith("Z") else normalized)
    except ValueError as exc:
        raise ChannelsFindCreatorsToolError(f"{field} must be an ISO 8601 timestamp with timezone", category="invalid_parameters", details={"field": field}) from exc
    if parsed.tzinfo is None:
        raise ChannelsFindCreatorsToolError(f"{field} must include a timezone", category="invalid_parameters", details={"field": field})
    return normalized


def _creator_pair_is_ordered(arguments: dict[str, Any], after_field: str, before_field: str) -> None:
    """Reject a creator-discovery date window with an inverted order.

    :param arguments: Normalized creator-discovery request.
    :param after_field: Inclusive lower-bound field name.
    :param before_field: Inclusive upper-bound field name.
    :return: ``None`` after validating the optional pair.
    :raises ChannelsFindCreatorsToolError: If both values exist and the lower bound is later.
    """
    if after_field in arguments and before_field in arguments:
        after = datetime.fromisoformat(arguments[after_field])
        before = datetime.fromisoformat(arguments[before_field])
        if after > before:
            raise ChannelsFindCreatorsToolError(f"{after_field} cannot be later than {before_field}", category="invalid_parameters", details={"field": after_field})


def validate_channels_find_creators_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one public creator-discovery request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized request with defaults and validated optional filters.
    :raises ChannelsFindCreatorsToolError: If a public field is invalid or unsupported.
    """
    if not isinstance(arguments, dict):
        raise ChannelsFindCreatorsToolError("channels_findCreators arguments must be an object", category="invalid_parameters", details={"field": "arguments"})
    unexpected = set(arguments) - set(CHANNELS_FIND_CREATORS_INPUT_SCHEMA["properties"])
    if unexpected:
        raise ChannelsFindCreatorsToolError("channels_findCreators received an unsupported field", category="invalid_parameters", details={"field": min(unexpected)})
    query = arguments.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ChannelsFindCreatorsToolError("channels_findCreators requires a non-empty query", category="invalid_parameters", details={"field": "query"})
    normalized: dict[str, Any] = {
        "query": query.strip(),
        "maxResults": arguments.get("maxResults", 10),
        "creatorOnly": arguments.get("creatorOnly", False),
        "sortBy": arguments.get("sortBy", "relevance"),
        "sampleVideosPerChannel": arguments.get("sampleVideosPerChannel", 0),
    }
    for field, maximum in (("maxResults", CHANNELS_FIND_CREATORS_MAX_RESULTS), ("sampleVideosPerChannel", CHANNELS_FIND_CREATORS_MAX_SAMPLES)):
        value = normalized[field]
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= maximum or (field == "maxResults" and value == 0):
            minimum = 1 if field == "maxResults" else 0
            raise ChannelsFindCreatorsToolError(f"{field} must be an integer from {minimum} through {maximum}", category="invalid_parameters", details={"field": field})
    if not isinstance(normalized["creatorOnly"], bool):
        raise ChannelsFindCreatorsToolError("creatorOnly must be a boolean", category="invalid_parameters", details={"field": "creatorOnly"})
    if normalized["sortBy"] not in CHANNELS_FIND_CREATORS_SORTS:
        raise ChannelsFindCreatorsToolError("sortBy must use a supported ranking value", category="invalid_parameters", details={"field": "sortBy"})
    if "order" in arguments:
        if not isinstance(arguments["order"], str) or arguments["order"] not in CHANNELS_FIND_CREATORS_ORDERS:
            raise ChannelsFindCreatorsToolError("order must use a supported value", category="invalid_parameters", details={"field": "order"})
        normalized["order"] = arguments["order"]
    for field in ("channelMinSubscribers", "channelMaxSubscribers"):
        if field in arguments:
            value = arguments[field]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ChannelsFindCreatorsToolError(f"{field} must be a non-negative integer", category="invalid_parameters", details={"field": field})
            normalized[field] = value
    if normalized.get("channelMinSubscribers") is not None and normalized.get("channelMaxSubscribers") is not None and normalized["channelMinSubscribers"] > normalized["channelMaxSubscribers"]:
        raise ChannelsFindCreatorsToolError("channelMinSubscribers cannot exceed channelMaxSubscribers", category="invalid_parameters", details={"field": "channelMinSubscribers"})
    for field in ("videoPublishedAfter", "videoPublishedBefore", "channelLastUploadAfter", "channelLastUploadBefore"):
        if field in arguments:
            normalized[field] = _creator_timestamp(arguments[field], field)
    _creator_pair_is_ordered(normalized, "videoPublishedAfter", "videoPublishedBefore")
    _creator_pair_is_ordered(normalized, "channelLastUploadAfter", "channelLastUploadBefore")
    return normalized


def _creator_base_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Build the bounded public video-search request for creator discovery.

    :param arguments: Validated creator-discovery request.
    :return: Lower-layer public video-search arguments bounded independently of final results.
    """
    result = {"part": "snippet", "q": arguments["query"], "type": "video", "maxResults": CHANNELS_FIND_CREATORS_BASE_VIDEO_LIMIT, "order": arguments.get("order", "relevance")}
    for public_name, lower_name in (("videoPublishedAfter", "publishedAfter"), ("videoPublishedBefore", "publishedBefore")):
        if public_name in arguments:
            result[lower_name] = arguments[public_name]
    return result


def _creator_candidates(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize and group public matching videos into distinct channel candidates.

    :param payload: Lower-level public video-search result.
    :return: Candidates ordered by each channel's earliest matched-video position.
    """
    source_items = payload.get("items") if isinstance(payload, dict) and isinstance(payload.get("items"), list) else []
    candidates: list[dict[str, Any]] = []
    by_channel: dict[str, dict[str, Any]] = {}
    for position, item in enumerate(source_items):
        if not isinstance(item, dict):
            continue
        identifier = item.get("id") if isinstance(item.get("id"), dict) else {}
        snippet = item.get("snippet") if isinstance(item.get("snippet"), dict) else {}
        video_id, channel_id = identifier.get("videoId"), snippet.get("channelId")
        if not isinstance(video_id, str) or not video_id.strip() or not isinstance(channel_id, str) or not channel_id.strip():
            continue
        sample: dict[str, Any] = {"videoId": video_id.strip(), "channelId": channel_id.strip()}
        for field in ("title", "publishedAt", "thumbnails"):
            _copy_if_present(sample, snippet, field)
        candidate = by_channel.get(channel_id.strip())
        if candidate is None:
            candidate = {"channelId": channel_id.strip(), "_baseSearchPosition": position, "_matchingVideos": []}
            title = snippet.get("channelTitle") if isinstance(snippet.get("channelTitle"), str) else snippet.get("title")
            if isinstance(title, str):
                candidate["title"] = title
            thumbnails = snippet.get("thumbnails")
            if isinstance(thumbnails, dict):
                candidate["thumbnails"] = thumbnails
            by_channel[channel_id.strip()] = candidate
            candidates.append(candidate)
        candidate["_matchingVideos"].append(sample)
    return candidates


def _creator_required_rules(arguments: dict[str, Any]) -> list[str]:
    """Return active creator rules requiring conditional public enrichment.

    :param arguments: Validated creator-discovery request.
    :return: Ordered active filter and ranking names.
    """
    rules = [field for field in ("channelMinSubscribers", "channelMaxSubscribers", "channelLastUploadAfter", "channelLastUploadBefore") if field in arguments]
    if arguments["creatorOnly"]:
        rules.append("creatorOnly")
    if arguments["sortBy"] != "relevance":
        rules.append(arguments["sortBy"])
    return rules


def _creator_needs_activity(arguments: dict[str, Any]) -> bool:
    """Return whether creator discovery needs latest public upload activity.

    :param arguments: Validated creator-discovery request.
    :return: ``True`` for active activity filters or recent-activity ranking.
    """
    return any(field in arguments for field in ("channelLastUploadAfter", "channelLastUploadBefore")) or arguments["sortBy"] == "recent_activity"


def _creator_activity_matches(timestamp: str, arguments: dict[str, Any]) -> bool:
    """Return whether latest public activity satisfies inclusive request bounds.

    :param timestamp: Available timezone-aware latest-upload timestamp.
    :param arguments: Validated creator-discovery request.
    :return: ``True`` when all selected activity bounds are satisfied.
    """
    value = datetime.fromisoformat(timestamp)
    if "channelLastUploadAfter" in arguments and value < datetime.fromisoformat(arguments["channelLastUploadAfter"]):
        return False
    return "channelLastUploadBefore" not in arguments or value <= datetime.fromisoformat(arguments["channelLastUploadBefore"])


def _creator_enrich_and_filter(candidates: list[dict[str, Any]], arguments: dict[str, Any], channels, playlist_items) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Conditionally enrich and filter video-derived candidates using public channel data.

    :param candidates: Distinct candidates grouped from matching videos.
    :param arguments: Validated creator-discovery request.
    :param channels: Lower-level batched public channel lookup callable.
    :param playlist_items: Lower-level public uploads-playlist lookup callable.
    :return: Eligible candidates and an optional safe partial-enrichment summary.
    :raises ChannelsFindCreatorsToolError: If every candidate cannot be evaluated for an active rule.
    """
    required_for = _creator_required_rules(arguments)
    if not required_for:
        return candidates, None
    try:
        payload = channels({"part": "snippet,statistics,contentDetails", "id": ",".join(candidate["channelId"] for candidate in candidates)})
    except ChannelsListToolError as exc:
        mapped = _map_channels_list_error(exc)
        raise ChannelsFindCreatorsToolError(str(mapped), category=mapped.category, details=mapped.details) from exc
    source_items = payload.get("items") if isinstance(payload, dict) and isinstance(payload.get("items"), list) else []
    by_id = {item["id"].strip(): item for item in source_items if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"].strip()}
    needs_subscriber = any(field in arguments for field in ("channelMinSubscribers", "channelMaxSubscribers")) or arguments["sortBy"] in {"subscribers_asc", "subscribers_desc", "indie_priority"}
    needs_activity = _creator_needs_activity(arguments)
    eligible: list[dict[str, Any]] = []
    reasons: list[str] = []
    excluded = 0
    evaluated = 0
    for candidate in candidates:
        source = by_id.get(candidate["channelId"])
        if source is None:
            excluded += 1
            if "channel_metadata_unavailable" not in reasons:
                reasons.append("channel_metadata_unavailable")
            continue
        enriched = dict(candidate)
        snippet = source.get("snippet") if isinstance(source.get("snippet"), dict) else {}
        enriched["normalizedMetadata"] = _normalized_metadata(snippet)
        classification, signals = _creator_classification(snippet)
        enriched["heuristics"] = {"creatorClassification": classification, "creatorSignals": signals}
        subscriber = _channel_search_subscriber_count(source)
        if needs_subscriber:
            if subscriber is None:
                excluded += 1
                if "subscriber_count_unavailable" not in reasons:
                    reasons.append("subscriber_count_unavailable")
                continue
            enriched["statistics"] = {"subscriberCount": subscriber[0]}
            enriched["_subscriberCount"] = subscriber[1]
        if needs_activity:
            uploads = _uploads_playlist_id(source)
            if uploads is None:
                excluded += 1
                if "latest_activity_unavailable" not in reasons:
                    reasons.append("latest_activity_unavailable")
                continue
            try:
                latest = playlist_items({"part": "contentDetails", "playlistId": uploads, "maxResults": 1})
            except PlaylistItemsListToolError:
                excluded += 1
                if "latest_activity_unavailable" not in reasons:
                    reasons.append("latest_activity_unavailable")
                continue
            timestamp = _latest_video_published_at(latest)
            if timestamp is None:
                excluded += 1
                if "latest_activity_unavailable" not in reasons:
                    reasons.append("latest_activity_unavailable")
                continue
            enriched["latestVideoPublishedAt"] = timestamp
        evaluated += 1
        if "channelMinSubscribers" in arguments and enriched["_subscriberCount"] < arguments["channelMinSubscribers"]:
            continue
        if "channelMaxSubscribers" in arguments and enriched["_subscriberCount"] > arguments["channelMaxSubscribers"]:
            continue
        if needs_activity and not _creator_activity_matches(enriched["latestVideoPublishedAt"], arguments):
            continue
        if arguments["creatorOnly"] and classification != "creator":
            continue
        eligible.append(enriched)
    if candidates and evaluated == 0 and excluded:
        raise ChannelsFindCreatorsToolError("Required public channel enrichment is unavailable", category="partial_enrichment_failure", details={"excludedCandidateCount": excluded, "reasons": reasons, "requiredFor": required_for})
    return eligible, ({"status": "partial", "excludedCandidateCount": excluded, "reasons": reasons, "requiredFor": required_for} if excluded else None)


def _creator_public_item(candidate: dict[str, Any], sample_limit: int) -> dict[str, Any]:
    """Shape one ranked candidate and its bounded matched-video samples.

    :param candidate: Internal ranked candidate with matching video evidence.
    :param sample_limit: Requested per-channel sample cap.
    :return: Public candidate without internal sorting or grouping fields.
    """
    result = {key: value for key, value in candidate.items() if not key.startswith("_")}
    videos = candidate["_matchingVideos"]
    result["matchedVideoBasis"] = {"count": len(videos), "firstVideoId": videos[0]["videoId"]}
    if sample_limit:
        result["sampleVideos"] = videos[:sample_limit]
    return result


def _creator_field_provenance(items: list[dict[str, Any]]) -> dict[str, str]:
    """Build public provenance metadata for creator-discovery results.

    :param items: Final public candidate collection.
    :return: Field-path-to-provenance mapping for returned fields.
    """
    provenance = {"channelId": "raw_upstream", "matchedVideoBasis": "normalized"}
    if any("sampleVideos" in item for item in items):
        provenance["sampleVideos"] = "normalized"
    if any("statistics" in item for item in items):
        provenance["statistics.subscriberCount"] = "raw_upstream"
    if any("latestVideoPublishedAt" in item for item in items):
        provenance["latestVideoPublishedAt"] = "normalized"
    if any("heuristics" in item for item in items):
        provenance["heuristics.creatorClassification"] = "heuristic_inferred"
        provenance["heuristics.creatorSignals"] = "heuristic_inferred"
    return provenance


def build_channels_find_creators_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for concrete creator discovery.

    :return: JSON-compatible metadata for bounded video-derived creator discovery.
    """
    return {
        "name": CHANNELS_FIND_CREATORS_TOOL_NAME,
        "family": "channels",
        "parameters": list(CHANNELS_FIND_CREATORS_INPUT_SCHEMA["properties"]),
        "inputContract": CHANNELS_FIND_CREATORS_INPUT_SCHEMA,
        "compositionBoundary": {"kind": "ranked_enrichment", "boundedness": "one base video search of at most 50 videos; at most 50 distinct channels, one activity lookup per candidate, and 0 through 10 samples per final channel", "partialResultPolicy": "Conditional public enrichment excludes candidates whose required data is unavailable and discloses them safely."},
        "lowerLayerDependencies": ["search.list", "channels.list", "playlistItems.list"],
        "continuationPolicy": "Any continuation context belongs to the bounded base video search and does not paginate the final filtered or ranked creator collection.",
        "rankingSemantics": {"sortBy": list(CHANNELS_FIND_CREATORS_SORTS), "filterOrder": "Apply filters before final ranking and result cap.", "ties": "Preserve earliest base-video position for every ranking tie."},
        "responseFields": [
            {"fieldName": "channelId", "category": "raw_upstream", "source": "matched video snippet.channelId"},
            {"fieldName": "matchedVideoBasis", "category": "normalized", "source": "grouped matching videos"},
            {"fieldName": "sampleVideos", "category": "normalized", "source": "bounded base-video-order samples"},
            {"fieldName": "statistics.subscriberCount", "category": "raw_upstream", "source": "public channel statistics"},
            {"fieldName": "latestVideoPublishedAt", "category": "normalized", "source": "public uploads playlist"},
            {"fieldName": "heuristics.creatorClassification", "category": "heuristic_inferred", "source": "public channel material"},
        ],
        "heuristics": [{"name": "creatorClassification", "basis": "Positive public channel metadata signals.", "limitations": "Classification is inferred, can be incomplete or incorrect, and is not a verified identity, ownership, or independence claim."}],
        "authAndQuotaNotes": ["Uses configured public read capability and no owner-scoped data.", "Base video search and conditional public enrichment have bounded quota impact."],
        "errorCategories": ["invalid_parameters", "unavailable_resource", "authorization_sensitive_data", "quota_exhaustion", "upstream_failure", "partial_enrichment_failure"],
        "errorGuidance": {"invalid_parameters": "Correct the identified request field and retry.", "unavailable_resource": "Use a different accessible query or relax the affected refinement.", "authorization_sensitive_data": "Use permitted public data or obtain the necessary capability.", "quota_exhaustion": "Retry after capacity is available.", "upstream_failure": "Retry when the source service is available.", "partial_enrichment_failure": "Relax the enrichment-dependent rule or retry when public metadata is available."},
    }


def build_channels_find_creators_handler(*, search=None, channels=None, playlist_items=None):
    """Build the callable public creator-discovery handler.

    :param search: Optional lower-level video-search handler override for tests.
    :param channels: Optional lower-level channel handler override for enrichment tests.
    :param playlist_items: Optional lower-level playlist handler override for activity tests.
    :return: Callable that discovers, enriches, ranks, and samples public creator candidates.
    """
    selected_search = search or build_search_list_handler()
    selected_channels = channels or build_channels_list_handler()
    selected_playlist_items = playlist_items or build_playlist_items_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated creator-discovery request.

        :param arguments: Caller-provided public creator-discovery arguments.
        :return: Bounded public creator collection with provenance and safe partial state.
        :raises ChannelsFindCreatorsToolError: If validation, search, or required enrichment fails safely.
        """
        normalized = validate_channels_find_creators_arguments(arguments)
        try:
            payload = selected_search(_creator_base_arguments(normalized))
        except SearchListToolError as exc:
            mapped = _map_channel_search_error(exc)
            raise ChannelsFindCreatorsToolError(str(mapped), category=mapped.category, details=mapped.details) from exc
        eligible, partial = _creator_enrich_and_filter(_creator_candidates(payload), normalized, selected_channels, selected_playlist_items)
        ranked = _rank_channel_search_candidates(eligible, normalized)
        items = [_creator_public_item(candidate, normalized["sampleVideosPerChannel"]) for candidate in ranked[: normalized["maxResults"]]]
        result: dict[str, Any] = {"items": items, "appliedInputs": normalized, "returnedCount": len(items), "maxResults": normalized["maxResults"], "fieldProvenance": _creator_field_provenance(items)}
        if partial is not None:
            result["partialEnrichment"] = partial
        token = payload.get("nextPageToken") if isinstance(payload, dict) else None
        if isinstance(token, str) and token:
            result["nextPageToken"] = token
        return result

    return handler


def build_channels_find_creators_tool_descriptor(*, search=None, channels=None, playlist_items=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for ``channels_findCreators``.

    :param search: Optional lower-level video-search handler override for tests.
    :param channels: Optional lower-level channel handler override for enrichment tests.
    :param playlist_items: Optional lower-level playlist handler override for activity tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {"name": CHANNELS_FIND_CREATORS_TOOL_NAME, "description": "Discover public creator channels from matching videos with optional enrichment, ranking, and samples.", "inputSchema": CHANNELS_FIND_CREATORS_INPUT_SCHEMA, "handler": build_channels_find_creators_handler(search=search, channels=channels, playlist_items=playlist_items), "metadata": build_channels_find_creators_metadata()}
