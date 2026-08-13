"""Normalized public video-detail tools.

The module owns concrete single-video detail behavior for the videos family.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from mcp_server.tools.youtube_common.conventions import safe_upstream_error_message, sanitize_error_details
from mcp_server.tools.youtube_common.channels import ChannelsListToolError, build_channels_list_handler
from mcp_server.tools.youtube_common.playlist_items import PlaylistItemsListToolError, build_playlist_items_list_handler
from mcp_server.tools.youtube_common.search import SearchListToolError, build_search_list_handler
from mcp_server.tools.youtube_common.videos import VideosListToolError, build_videos_list_handler

from mcp_server.tools.youtube_composed.families import get_family

FAMILY_SCAFFOLDING = get_family("videos")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools

VIDEOS_GET_VIDEO_TOOL_NAME = "videos_getVideo"
VIDEOS_GET_VIDEO_CORE_PARTS = ("snippet", "contentDetails")
VIDEOS_GET_VIDEO_SUPPORTED_PARTS = (
    "snippet",
    "contentDetails",
    "statistics",
    "status",
    "topicDetails",
)
VIDEOS_GET_VIDEO_OPTIONAL_PART_FIELDS = {
    "snippet": ("liveBroadcastContent", "defaultLanguage", "defaultAudioLanguage"),
    "contentDetails": ("dimension", "definition", "caption", "licensedContent", "regionRestriction", "projection"),
    "statistics": ("viewCount", "likeCount", "favoriteCount", "commentCount"),
    "status": ("uploadStatus", "privacyStatus", "license", "embeddable", "publicStatsViewable", "madeForKids", "selfDeclaredMadeForKids"),
    "topicDetails": ("topicCategories",),
}
VIDEOS_GET_VIDEO_INPUT_SCHEMA = {
    "type": "object",
    "required": ["videoId"],
    "properties": {
        "videoId": {"type": "string", "minLength": 1},
        "parts": {
            "type": "array",
            "uniqueItems": True,
            "items": {"type": "string", "enum": list(VIDEOS_GET_VIDEO_SUPPORTED_PARTS)},
        },
    },
    "additionalProperties": False,
}

VIDEOS_GET_STATISTICS_TOOL_NAME = "videos_getStatistics"
VIDEOS_GET_STATISTICS_EXPECTED_METRICS = ("viewCount", "likeCount", "commentCount", "favoriteCount")
VIDEOS_GET_STATISTICS_INPUT_SCHEMA = {
    "type": "object",
    "required": ["videoId"],
    "properties": {"videoId": {"type": "string", "minLength": 1}},
    "additionalProperties": False,
}

VIDEOS_SEARCH_VIDEOS_TOOL_NAME = "videos_searchVideos"
VIDEOS_SEARCH_VIDEOS_MAX_RESULTS = 50
VIDEOS_SEARCH_VIDEOS_ORDERS = ("date", "rating", "relevance", "title", "viewCount")
VIDEOS_SEARCH_VIDEOS_SORTS = (
    "relevance",
    "subscribers_asc",
    "subscribers_desc",
    "indie_priority",
    "recent_activity",
)
VIDEOS_SEARCH_VIDEOS_INPUT_SCHEMA = {
    "type": "object",
    "required": ["query"],
    "properties": {
        "query": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 1, "maximum": VIDEOS_SEARCH_VIDEOS_MAX_RESULTS, "default": 10},
        "order": {"type": "string", "enum": list(VIDEOS_SEARCH_VIDEOS_ORDERS)},
        "publishedAfter": {"type": "string", "format": "date-time"},
        "publishedBefore": {"type": "string", "format": "date-time"},
        "channelId": {"type": "string", "minLength": 1},
        "uniqueChannels": {"type": "boolean", "default": False},
        "channelMinSubscribers": {"type": "integer", "minimum": 0},
        "channelMaxSubscribers": {"type": "integer", "minimum": 0},
        "channelLastUploadAfter": {"type": "string", "format": "date-time"},
        "channelLastUploadBefore": {"type": "string", "format": "date-time"},
        "creatorOnly": {"type": "boolean", "default": False},
        "sortBy": {"type": "string", "enum": list(VIDEOS_SEARCH_VIDEOS_SORTS), "default": "relevance"},
    },
    "additionalProperties": False,
}


class VideosGetVideoToolError(ValueError):
    """Represent a safe caller-facing ``videos_getVideo`` failure.

    :param message: Caller-facing explanation of the failure.
    :param category: Stable public failure category.
    :param details: Optional caller-safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the normalized public-tool error.

        :param message: Caller-facing explanation of the failure.
        :param category: Stable public failure category.
        :param details: Candidate diagnostic details to sanitize.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class VideosGetStatisticsToolError(ValueError):
    """Represent a safe caller-facing ``videos_getStatistics`` failure.

    :param message: Caller-facing explanation of the failure.
    :param category: Stable public failure category.
    :param details: Optional caller-safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the normalized public statistics-tool error.

        :param message: Caller-facing explanation of the failure.
        :param category: Stable public failure category.
        :param details: Candidate diagnostic details to sanitize.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class VideosSearchVideosToolError(ValueError):
    """Represent a safe caller-facing ``videos_searchVideos`` failure.

    :param message: Caller-facing explanation of the failure.
    :param category: Stable public failure category.
    :param details: Optional caller-safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the normalized public video-search error.

        :param message: Caller-facing explanation of the failure.
        :param category: Stable public failure category.
        :param details: Candidate diagnostic details to sanitize.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


def build_videos_get_video_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for the concrete video-detail tool.

    :return: JSON-compatible public metadata without a representative-only marker.
    """
    return {
        "name": VIDEOS_GET_VIDEO_TOOL_NAME,
        "family": "videos",
        "parameters": ["videoId", "parts"],
        "inputContract": VIDEOS_GET_VIDEO_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "normalized_retrieval",
            "lowerLayerDependencies": ["videos.list"],
            "boundedness": "one video",
            "partialResultPolicy": "Preserve unavailable source fields without inventing values.",
        },
        "lowerLayerDependencies": ["videos.list"],
        "authAndQuotaNotes": ["Uses the videos.list direct lookup path and its one-unit quota behavior."],
        "responseFields": [
            {"fieldName": "videoId", "category": "raw_upstream", "source": "id"},
            {"fieldName": "title", "category": "normalized", "source": "snippet.title"},
            {"fieldName": "description", "category": "normalized", "source": "snippet.description"},
            {"fieldName": "publishedAt", "category": "normalized", "source": "snippet.publishedAt"},
            {"fieldName": "channelId", "category": "normalized", "source": "snippet.channelId"},
            {"fieldName": "channelTitle", "category": "normalized", "source": "snippet.channelTitle"},
            {"fieldName": "duration", "category": "normalized", "source": "contentDetails.duration"},
            {"fieldName": "categoryId", "category": "normalized", "source": "snippet.categoryId"},
            {"fieldName": "tags", "category": "normalized", "source": "snippet.tags"},
            {"fieldName": "thumbnails", "category": "normalized", "source": "snippet.thumbnails"},
        ],
        "optionalPartMappings": {
            part: list(fields) for part, fields in VIDEOS_GET_VIDEO_OPTIONAL_PART_FIELDS.items()
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
            "unavailable_resource": "Use a different accessible video identifier.",
            "authorization_sensitive_data": "Obtain appropriate authorization if applicable.",
            "quota_exhaustion": "Retry after capacity is available.",
            "upstream_failure": "Retry when the source service is available.",
        },
    }


def build_videos_get_statistics_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for the video-statistics tool.

    :return: JSON-compatible public metadata for normalized video statistics.
    """
    return {
        "name": VIDEOS_GET_STATISTICS_TOOL_NAME,
        "family": "videos",
        "parameters": ["videoId"],
        "inputContract": VIDEOS_GET_STATISTICS_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "normalized_retrieval",
            "lowerLayerDependencies": ["videos.list"],
            "boundedness": "one video",
            "partialResultPolicy": "Represent each absent expected metric as unavailable without a numeric value.",
        },
        "lowerLayerDependencies": ["videos.list"],
        "authAndQuotaNotes": ["Uses the videos.list direct lookup path and its one-unit quota behavior."],
        "responseFields": [
            {"fieldName": "videoId", "category": "normalized", "source": "requested videoId"},
            {"fieldName": "statistics.*.value", "category": "raw_upstream", "source": "statistics counts"},
            {"fieldName": "statistics.*.state", "category": "normalized", "source": "source-field availability"},
            {"fieldName": "statistics.*.provenance", "category": "normalized", "source": "result normalization"},
        ],
        "expectedMetrics": list(VIDEOS_GET_STATISTICS_EXPECTED_METRICS),
        "metricAvailability": {
            "available": "A source-provided count, including zero.",
            "unavailable": "The expected source metric was not provided; no numeric value is returned.",
        },
        "sourceCaveats": {
            "favoriteCount": "The source marks this deprecated count as zero when supplied.",
            "dislikeCount": "Excluded because it is owner-sensitive and is not part of this public contract.",
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
            "unavailable_resource": "Use a different accessible video identifier.",
            "authorization_sensitive_data": "Obtain appropriate authorization if applicable.",
            "quota_exhaustion": "Retry after capacity is available.",
            "upstream_failure": "Retry when the source service is available.",
        },
    }


def validate_videos_get_video_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate the required core video-details request input.

    :param arguments: Candidate public tool arguments.
    :return: Normalized request containing one video identifier and selected parts.
    :raises VideosGetVideoToolError: If the identifier is missing or invalid.
    """
    if not isinstance(arguments, dict):
        raise VideosGetVideoToolError(
            "videos_getVideo arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected_fields = set(arguments) - {"videoId", "parts"}
    if unexpected_fields:
        raise VideosGetVideoToolError(
            "videos_getVideo received an unsupported field",
            category="invalid_parameters",
            details={"field": sorted(unexpected_fields)[0]},
        )
    video_id = arguments.get("videoId")
    if not isinstance(video_id, str) or not video_id.strip():
        raise VideosGetVideoToolError(
            "videos_getVideo requires a non-empty videoId",
            category="invalid_parameters",
            details={"field": "videoId"},
        )
    parts = arguments.get("parts", [])
    if not isinstance(parts, list) or any(not isinstance(part, str) for part in parts):
        raise VideosGetVideoToolError(
            "parts must be an array of supported text values",
            category="invalid_parameters",
            details={"field": "parts"},
        )
    if len(parts) != len(set(parts)) or any(part not in VIDEOS_GET_VIDEO_SUPPORTED_PARTS for part in parts):
        raise VideosGetVideoToolError(
            "parts contains an unsupported or duplicate value",
            category="invalid_parameters",
            details={"field": "parts"},
        )
    return {"videoId": video_id.strip(), "parts": tuple(parts)}


def validate_videos_get_statistics_arguments(arguments: dict[str, Any]) -> dict[str, str]:
    """Validate the required single-video statistics request input.

    :param arguments: Candidate public tool arguments.
    :return: Normalized request containing one trimmed video identifier.
    :raises VideosGetStatisticsToolError: If the request is missing or invalid.
    """
    if not isinstance(arguments, dict):
        raise VideosGetStatisticsToolError(
            "videos_getStatistics arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected_fields = set(arguments) - {"videoId"}
    if unexpected_fields:
        raise VideosGetStatisticsToolError(
            "videos_getStatistics received an unsupported field",
            category="invalid_parameters",
            details={"field": sorted(unexpected_fields)[0]},
        )
    video_id = arguments.get("videoId")
    if not isinstance(video_id, str) or not video_id.strip():
        raise VideosGetStatisticsToolError(
            "videos_getStatistics requires a non-empty videoId",
            category="invalid_parameters",
            details={"field": "videoId"},
        )
    return {"videoId": video_id.strip()}


def _lookup_arguments(video_id: str, requested_parts: tuple[str, ...]) -> dict[str, str]:
    """Build the lower-level request required for default video fields.

    :param video_id: Validated public video identifier.
    :param requested_parts: Valid optional groups selected by the caller.
    :return: Direct-lookup arguments for the existing video list capability.
    """
    selected_parts = list(VIDEOS_GET_VIDEO_CORE_PARTS)
    selected_parts.extend(part for part in requested_parts if part not in selected_parts)
    return {"id": video_id, "part": ",".join(selected_parts)}


def _copy_if_present(result: dict[str, Any], source: dict[str, Any], source_name: str, result_name: str) -> None:
    """Copy one available source value to the normalized result.

    :param result: Result mapping being assembled.
    :param source: Source mapping containing the candidate value.
    :param source_name: Source field name.
    :param result_name: Public normalized field name.
    """
    if source_name in source:
        result[result_name] = source[source_name]


def _optional_group(item: dict[str, Any], part: str) -> dict[str, Any]:
    """Return available fields for one requested optional source group.

    :param item: Source video item.
    :param part: Valid requested source group name.
    :return: Available fields from the selected group.
    """
    source = item.get(part) if isinstance(item.get(part), dict) else {}
    return {field: source[field] for field in VIDEOS_GET_VIDEO_OPTIONAL_PART_FIELDS[part] if field in source}


def normalize_videos_get_video_result(
    payload: dict[str, Any],
    *,
    requested_parts: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Normalize the first available lower-level video item.

    :param payload: Lower-level result containing an ``items`` collection.
    :param requested_parts: Valid optional groups selected by the caller.
    :return: Stable default and requested optional detail fields for one video.
    :raises VideosGetVideoToolError: If no video item is available.
    """
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        raise VideosGetVideoToolError(
            "The requested video is unavailable",
            category="unavailable_resource",
            details={"resource": "video"},
        )
    item = items[0]
    snippet = item.get("snippet") if isinstance(item.get("snippet"), dict) else {}
    content_details = item.get("contentDetails") if isinstance(item.get("contentDetails"), dict) else {}
    result: dict[str, Any] = {}
    _copy_if_present(result, item, "id", "videoId")
    for field in ("title", "description", "publishedAt", "channelId", "channelTitle", "categoryId", "tags", "thumbnails"):
        _copy_if_present(result, snippet, field, field)
    _copy_if_present(result, content_details, "duration", "duration")
    for part in requested_parts:
        group = _optional_group(item, part)
        if group:
            result[part] = group
    return result


def _public_videos_list_error_parts(error: VideosListToolError) -> tuple[str, str, dict[str, Any]]:
    """Return safe public error fields for one lower-level video-list failure.

    :param error: Safe lower-level video lookup error.
    :return: Public category, message, and diagnostic details for one failure.
    """
    if error.category in {"resource_not_found", "removed"}:
        return "unavailable_resource", "The requested video is unavailable", {"resource": "video"}
    public_category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
    }.get(error.category, "upstream_failure")
    return public_category, safe_upstream_error_message(), error.details


def _map_videos_list_error(error: VideosListToolError) -> VideosGetVideoToolError:
    """Translate one lower-level error to a safe public video-detail error.

    :param error: Safe lower-level video lookup error.
    :return: Public error with the documented category and safe details.
    """
    category, message, details = _public_videos_list_error_parts(error)
    return VideosGetVideoToolError(message, category=category, details=details)


def build_videos_get_video_handler(*, lookup=None):
    """Build a callable handler for one normalized video lookup.

    :param lookup: Optional lower-level lookup override for tests.
    :return: Callable that validates, retrieves, and normalizes one video.
    """
    selected_lookup = lookup or build_videos_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated video-detail request.

        :param arguments: Caller-provided public arguments.
        :return: Normalized default detail result for one available video.
        :raises VideosGetVideoToolError: If validation or lookup normalization fails.
        """
        normalized = validate_videos_get_video_arguments(arguments)
        try:
            payload = selected_lookup(_lookup_arguments(normalized["videoId"], normalized["parts"]))
        except VideosListToolError as exc:
            raise _map_videos_list_error(exc) from exc
        return normalize_videos_get_video_result(payload, requested_parts=normalized["parts"])

    return handler


def build_videos_get_video_tool_descriptor(*, lookup=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for ``videos_getVideo``.

    :param lookup: Optional lower-level lookup override for tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": VIDEOS_GET_VIDEO_TOOL_NAME,
        "description": "Return normalized details for one YouTube video.",
        "inputSchema": VIDEOS_GET_VIDEO_INPUT_SCHEMA,
        "handler": build_videos_get_video_handler(lookup=lookup),
        "metadata": build_videos_get_video_metadata(),
    }


def _videos_get_statistics_lookup_arguments(video_id: str) -> dict[str, str]:
    """Build the one lower-level lookup for public video statistics.

    :param video_id: Validated public video identifier.
    :return: Direct ``videos.list`` arguments requesting only statistics.
    """
    return {"id": video_id, "part": "statistics"}


def _source_statistic_value(value: Any) -> str | None:
    """Return a valid non-negative source statistic without float conversion.

    :param value: Candidate source statistic value.
    :return: Preserved decimal text for a valid source count, otherwise ``None``.
    """
    if isinstance(value, str) and value.isdecimal():
        return value
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return str(value)
    return None


def normalize_videos_get_statistics_result(payload: dict[str, Any], *, video_id: str) -> dict[str, Any]:
    """Normalize expected source counts for one requested video.

    :param payload: Lower-level result containing one statistics source item.
    :param video_id: Validated request identifier associated with the result.
    :return: Stable statistics and availability data for the requested video.
    :raises VideosGetStatisticsToolError: If no source video item is available.
    """
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        raise VideosGetStatisticsToolError(
            "The requested video is unavailable",
            category="unavailable_resource",
            details={"resource": "video"},
        )
    item = items[0]
    source_statistics = item.get("statistics") if isinstance(item.get("statistics"), dict) else {}
    statistics: dict[str, dict[str, str]] = {}
    for metric in VIDEOS_GET_STATISTICS_EXPECTED_METRICS:
        value = _source_statistic_value(source_statistics.get(metric))
        if value is None:
            statistics[metric] = {"state": "unavailable", "provenance": "normalized"}
        else:
            statistics[metric] = {"state": "available", "value": value, "provenance": "source_provided"}
    return {
        "videoId": video_id,
        "statistics": statistics,
        "fieldProvenance": {
            "statistics.*.value": "source_provided",
            "statistics.*.state": "normalized",
        },
        "sourceCaveats": {
            "favoriteCount": "The source marks this deprecated count as zero when supplied.",
        },
    }


def _map_videos_list_statistics_error(error: VideosListToolError) -> VideosGetStatisticsToolError:
    """Translate a lower-level error to a safe public statistics error.

    :param error: Safe lower-level video lookup error.
    :return: Documented caller-safe statistics-tool error.
    """
    category, message, details = _public_videos_list_error_parts(error)
    return VideosGetStatisticsToolError(message, category=category, details=details)


def build_videos_get_statistics_handler(*, lookup=None):
    """Build a callable handler for one normalized video-statistics lookup.

    :param lookup: Optional lower-level lookup override for tests.
    :return: Callable that validates, retrieves, and normalizes one video.
    """
    selected_lookup = lookup or build_videos_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated public video-statistics request.

        :param arguments: Caller-provided public arguments.
        :return: Normalized statistics for the requested available video.
        :raises VideosGetStatisticsToolError: If validation or lookup fails.
        """
        normalized = validate_videos_get_statistics_arguments(arguments)
        try:
            payload = selected_lookup(_videos_get_statistics_lookup_arguments(normalized["videoId"]))
        except VideosListToolError as exc:
            raise _map_videos_list_statistics_error(exc) from exc
        return normalize_videos_get_statistics_result(payload, video_id=normalized["videoId"])

    return handler


def build_videos_get_statistics_tool_descriptor(*, lookup=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for ``videos_getStatistics``.

    :param lookup: Optional lower-level lookup override for tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": VIDEOS_GET_STATISTICS_TOOL_NAME,
        "description": "Return normalized public statistics for one YouTube video.",
        "inputSchema": VIDEOS_GET_STATISTICS_INPUT_SCHEMA,
        "handler": build_videos_get_statistics_handler(lookup=lookup),
        "metadata": build_videos_get_statistics_metadata(),
    }


def _required_search_text(arguments: dict[str, Any], field: str) -> str:
    """Return one required non-blank public video-search text value.

    :param arguments: Candidate public video-search arguments.
    :param field: Required text field to read.
    :return: Stripped text value.
    :raises VideosSearchVideosToolError: If the field is missing or blank.
    """
    value = arguments.get(field)
    if not isinstance(value, str) or not value.strip():
        raise VideosSearchVideosToolError(
            f"videos_searchVideos requires a non-empty {field}",
            category="invalid_parameters",
            details={"field": field},
        )
    return value.strip()


def _parse_search_timestamp(value: str, field: str) -> datetime:
    """Validate one timezone-aware ISO 8601 public timestamp.

    :param value: Candidate timestamp text.
    :param field: Public field name used for safe error details.
    :return: Parsed timezone-aware timestamp.
    :raises VideosSearchVideosToolError: If the timestamp is invalid or lacks a timezone.
    """
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise VideosSearchVideosToolError(
            f"{field} must be an ISO 8601 timestamp with a timezone",
            category="invalid_parameters",
            details={"field": field},
        ) from exc
    if parsed.tzinfo is None:
        raise VideosSearchVideosToolError(
            f"{field} must include a timezone",
            category="invalid_parameters",
            details={"field": field},
        )
    return parsed


def _optional_search_timestamp(arguments: dict[str, Any], field: str) -> datetime | None:
    """Validate one optional public timestamp while preserving request text.

    :param arguments: Candidate public video-search arguments.
    :param field: Optional public timestamp field to inspect.
    :return: Parsed timestamp when supplied, otherwise ``None``.
    :raises VideosSearchVideosToolError: If a supplied value is invalid.
    """
    if field not in arguments:
        return None
    value = arguments[field]
    if not isinstance(value, str) or not value.strip():
        raise VideosSearchVideosToolError(
            f"{field} must be a non-empty ISO 8601 timestamp",
            category="invalid_parameters",
            details={"field": field},
        )
    arguments[field] = value.strip()
    return _parse_search_timestamp(arguments[field], field)


def _validate_optional_boolean(arguments: dict[str, Any], field: str, default: bool) -> bool:
    """Validate one optional boolean public video-search argument.

    :param arguments: Candidate public video-search arguments.
    :param field: Boolean field to inspect.
    :param default: Value applied when the field is omitted.
    :return: Valid boolean value.
    :raises VideosSearchVideosToolError: If a supplied value is not boolean.
    """
    value = arguments.get(field, default)
    if not isinstance(value, bool):
        raise VideosSearchVideosToolError(
            f"{field} must be a boolean",
            category="invalid_parameters",
            details={"field": field},
        )
    return value


def validate_videos_search_videos_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize a public ``videos_searchVideos`` request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized request suitable for lower-layer composition.
    :raises VideosSearchVideosToolError: If the request contains invalid fields,
        values, bounds, or timestamp windows.
    """
    if not isinstance(arguments, dict):
        raise VideosSearchVideosToolError(
            "videos_searchVideos arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    supported_fields = set(VIDEOS_SEARCH_VIDEOS_INPUT_SCHEMA["properties"])
    unexpected_fields = set(arguments) - supported_fields
    if unexpected_fields:
        raise VideosSearchVideosToolError(
            "videos_searchVideos received an unsupported field",
            category="invalid_parameters",
            details={"field": sorted(unexpected_fields)[0]},
        )

    source = dict(arguments)
    normalized: dict[str, Any] = {
        "query": _required_search_text(source, "query"),
        "maxResults": source.get("maxResults", 10),
        "order": source.get("order", "relevance"),
        "uniqueChannels": _validate_optional_boolean(source, "uniqueChannels", False),
        "creatorOnly": _validate_optional_boolean(source, "creatorOnly", False),
        "sortBy": source.get("sortBy", "relevance"),
    }
    max_results = normalized["maxResults"]
    if isinstance(max_results, bool) or not isinstance(max_results, int) or not 1 <= max_results <= VIDEOS_SEARCH_VIDEOS_MAX_RESULTS:
        raise VideosSearchVideosToolError(
            "maxResults must be an integer from 1 through 50",
            category="invalid_parameters",
            details={"field": "maxResults"},
        )
    if normalized["order"] not in VIDEOS_SEARCH_VIDEOS_ORDERS:
        raise VideosSearchVideosToolError(
            "order must be a supported base-search value",
            category="invalid_parameters",
            details={"field": "order"},
        )
    if normalized["sortBy"] not in VIDEOS_SEARCH_VIDEOS_SORTS:
        raise VideosSearchVideosToolError(
            "sortBy must be a supported ranking value",
            category="invalid_parameters",
            details={"field": "sortBy"},
        )
    if "channelId" in source:
        normalized["channelId"] = _required_search_text(source, "channelId")

    published_after = _optional_search_timestamp(source, "publishedAfter")
    published_before = _optional_search_timestamp(source, "publishedBefore")
    for field in ("publishedAfter", "publishedBefore"):
        if field in source:
            normalized[field] = source[field]
    if published_after and published_before and published_after > published_before:
        raise VideosSearchVideosToolError(
            "publishedAfter cannot be later than publishedBefore",
            category="invalid_parameters",
            details={"field": "publishedAfter"},
        )
    for field in ("channelMinSubscribers", "channelMaxSubscribers"):
        if field not in source:
            continue
        value = source[field]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise VideosSearchVideosToolError(
                f"{field} must be a non-negative integer",
                category="invalid_parameters",
                details={"field": field},
            )
        normalized[field] = value
    minimum = normalized.get("channelMinSubscribers")
    maximum = normalized.get("channelMaxSubscribers")
    if minimum is not None and maximum is not None and minimum > maximum:
        raise VideosSearchVideosToolError(
            "channelMinSubscribers cannot exceed channelMaxSubscribers",
            category="invalid_parameters",
            details={"field": "channelMinSubscribers"},
        )
    latest_after = _optional_search_timestamp(source, "channelLastUploadAfter")
    latest_before = _optional_search_timestamp(source, "channelLastUploadBefore")
    for field in ("channelLastUploadAfter", "channelLastUploadBefore"):
        if field in source:
            normalized[field] = source[field]
    if latest_after and latest_before and latest_after > latest_before:
        raise VideosSearchVideosToolError(
            "channelLastUploadAfter cannot be later than channelLastUploadBefore",
            category="invalid_parameters",
            details={"field": "channelLastUploadAfter"},
        )
    return normalized


def _build_base_search_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Build the lower-layer video-only search request for one normalized input.

    :param arguments: Validated public video-search arguments.
    :return: Compatible Layer 2 ``search_list`` arguments.
    """
    result = {
        "part": "snippet",
        "q": arguments["query"],
        "type": "video",
        "maxResults": arguments["maxResults"],
        "order": arguments["order"],
    }
    for field in ("publishedAfter", "publishedBefore", "channelId"):
        if field in arguments:
            result[field] = arguments[field]
    return result


def _normalize_video_search_candidate(item: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize one available lower-layer video-search item.

    :param item: Near-raw Layer 2 search item.
    :return: Stable public video candidate, or ``None`` when no video ID exists.
    """
    identifier = item.get("id") if isinstance(item.get("id"), dict) else {}
    video_id = identifier.get("videoId")
    if not isinstance(video_id, str) or not video_id:
        return None
    snippet = item.get("snippet") if isinstance(item.get("snippet"), dict) else {}
    candidate: dict[str, Any] = {"videoId": video_id}
    for field in ("title", "description", "publishedAt", "channelId", "channelTitle", "thumbnails"):
        if field in snippet:
            candidate[field] = snippet[field]
    return candidate


def _map_video_search_error(error: SearchListToolError) -> VideosSearchVideosToolError:
    """Translate a lower-layer search failure to the public Layer 3 taxonomy.

    :param error: Safe lower-layer search failure.
    :return: Sanitized public video-search error.
    """
    category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
        "resource_not_found": "unavailable_resource",
    }.get(error.category, "upstream_failure")
    return VideosSearchVideosToolError(
        safe_upstream_error_message(),
        category=category,
        details=error.details,
    )


def _map_channel_search_error(error: ChannelsListToolError) -> VideosSearchVideosToolError:
    """Translate a lower-layer channel failure to the public Layer 3 taxonomy.

    :param error: Safe lower-layer channel lookup failure.
    :return: Sanitized public video-search error.
    """
    category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
        "resource_not_found": "unavailable_resource",
    }.get(error.category, "upstream_failure")
    return VideosSearchVideosToolError(
        safe_upstream_error_message(),
        category=category,
        details=error.details,
    )


def _required_channel_rules(arguments: dict[str, Any]) -> list[str]:
    """Return active public rules that require channel enrichment.

    :param arguments: Validated public video-search arguments.
    :return: Ordered active metadata-dependent filter and ranking rule names.
    """
    fields = [
        "channelMinSubscribers",
        "channelMaxSubscribers",
        "channelLastUploadAfter",
        "channelLastUploadBefore",
    ]
    active = [field for field in fields if field in arguments]
    if arguments["creatorOnly"]:
        active.append("creatorOnly")
    if arguments["sortBy"] in {"subscribers_asc", "subscribers_desc", "indie_priority", "recent_activity"}:
        active.append(arguments["sortBy"])
    return active


def _requires_latest_activity(arguments: dict[str, Any]) -> bool:
    """Return whether active rules need derived latest public activity.

    :param arguments: Validated public video-search arguments.
    :return: ``True`` when latest-upload enrichment is required.
    """
    return any(field in arguments for field in ("channelLastUploadAfter", "channelLastUploadBefore")) or arguments["sortBy"] == "recent_activity"


def _creator_classification(channel: dict[str, Any]) -> tuple[str, list[str]]:
    """Classify a channel conservatively from positive public metadata signals.

    :param channel: Near-raw public channel item.
    :return: Classification and safe positive signal names; classification is
        ``creator`` only when documented public creator terms are present.
    """
    snippet = channel.get("snippet") if isinstance(channel.get("snippet"), dict) else {}
    text = " ".join(str(snippet.get(field, "")) for field in ("title", "description")).lower()
    terms = ("creator", "artist", "musician", "filmmaker", "photographer", "educator", "developer")
    signals = [f"public_{term}_term" for term in terms if term in text]
    return ("creator", signals) if signals else ("unknown", [])


def _channel_metadata_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index available public channel metadata by channel identifier.

    :param payload: Near-raw Layer 2 channel-list result.
    :return: Mapping of non-empty channel identifiers to source channel items.
    """
    items = payload.get("items") if isinstance(payload, dict) else []
    return {item["id"]: item for item in items if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"]}


def _subscriber_count(channel: dict[str, Any]) -> int | None:
    """Return one available non-negative public channel subscriber count.

    :param channel: Near-raw public channel item.
    :return: Parsed subscriber count, or ``None`` when hidden or invalid.
    """
    statistics = channel.get("statistics") if isinstance(channel.get("statistics"), dict) else {}
    value = statistics.get("subscriberCount")
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def _timestamp_matches(value: str, after: str | None, before: str | None) -> bool:
    """Return whether one available timestamp is inside inclusive public bounds.

    :param value: Available timezone-aware timestamp text.
    :param after: Optional inclusive lower boundary.
    :param before: Optional inclusive upper boundary.
    :return: ``True`` when the timestamp is within every supplied boundary.
    """
    parsed = _parse_search_timestamp(value, "latestVideoPublishedAt")
    return (after is None or parsed >= _parse_search_timestamp(after, "channelLastUploadAfter")) and (
        before is None or parsed <= _parse_search_timestamp(before, "channelLastUploadBefore")
    )


def _latest_upload_from_playlist(channel: dict[str, Any], playlist_items) -> str | None:
    """Return the latest upload timestamp from one public uploads playlist.

    :param channel: Near-raw public channel item containing uploads metadata.
    :param playlist_items: Lower-layer playlist-items list callable.
    :return: Latest available video publication timestamp, or ``None``.
    """
    content_details = channel.get("contentDetails") if isinstance(channel.get("contentDetails"), dict) else {}
    related_playlists = content_details.get("relatedPlaylists") if isinstance(content_details.get("relatedPlaylists"), dict) else {}
    uploads_id = related_playlists.get("uploads")
    if not isinstance(uploads_id, str) or not uploads_id:
        return None
    try:
        payload = playlist_items({"part": "contentDetails", "playlistId": uploads_id, "maxResults": 1})
    except PlaylistItemsListToolError:
        return None
    items = payload.get("items") if isinstance(payload, dict) else []
    if not items or not isinstance(items[0], dict):
        return None
    content_details = items[0].get("contentDetails") if isinstance(items[0].get("contentDetails"), dict) else {}
    value = content_details.get("videoPublishedAt")
    return value if isinstance(value, str) and value else None


def _unique_channel_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep the first candidate for each distinct available channel identifier.

    :param candidates: Ordered eligible public video candidates.
    :return: Ordered candidates with at most one item per channel.
    """
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for candidate in candidates:
        channel_id = candidate.get("channelId")
        if not isinstance(channel_id, str) or not channel_id or channel_id in seen:
            continue
        seen.add(channel_id)
        unique.append(candidate)
    return unique


def _rank_video_search_candidates(candidates: list[dict[str, Any]], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    """Return eligible candidates in the requested stable public ranking order.

    :param candidates: Filtered candidates enriched with required ranking values.
    :param arguments: Validated public video-search arguments.
    :return: Candidates ordered by ``sortBy`` and then base-search position.
    """
    sort_by = arguments["sortBy"]

    def key(candidate: dict[str, Any]) -> tuple[Any, ...]:
        """Build the stable key for one already-qualified candidate.

        :param candidate: Eligible normalized candidate with internal base position.
        :return: Comparable selected-ranking key followed by base position.
        """
        base_position = candidate.get("_baseSearchPosition", 0)
        channel = candidate.get("channel") if isinstance(candidate.get("channel"), dict) else {}
        subscriber_count = int(channel["subscriberCount"]) if "subscriberCount" in channel else 0
        if sort_by == "subscribers_asc":
            return (subscriber_count, base_position)
        if sort_by == "subscribers_desc":
            return (-subscriber_count, base_position)
        if sort_by == "indie_priority":
            return (0 if channel.get("creatorClassification") == "creator" else 1, subscriber_count, base_position)
        if sort_by == "recent_activity":
            latest = _parse_search_timestamp(channel["latestVideoPublishedAt"], "latestVideoPublishedAt")
            return (-latest.timestamp(), base_position)
        return (base_position,)

    return sorted(candidates, key=key)


def _enrich_and_filter_video_candidates(
    candidates: list[dict[str, Any]],
    arguments: dict[str, Any],
    *,
    channels,
    latest_activity,
    playlist_items,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Conditionally enrich and filter base candidates for active channel rules.

    :param candidates: Ordered normalized base video candidates.
    :param arguments: Validated public video-search arguments.
    :param channels: Injected lower-layer channel lookup callable.
    :param latest_activity: Optional injected latest-activity lookup callable.
    :param playlist_items: Lower-layer uploads-playlist lookup callable.
    :return: Eligible candidates and optional safe partial-enrichment summary.
    :raises VideosSearchVideosToolError: If all candidates needing active
        enrichment cannot be evaluated or a lower-layer call fails.
    """
    required_rules = _required_channel_rules(arguments)
    if not required_rules:
        return candidates, None
    channel_ids = list(dict.fromkeys(candidate.get("channelId") for candidate in candidates if isinstance(candidate.get("channelId"), str) and candidate["channelId"]))
    if not channel_ids:
        raise VideosSearchVideosToolError(
            "Required channel enrichment is unavailable",
            category="partial_enrichment_failure",
            details={"requiredFor": required_rules},
        )
    try:
        channel_payload = channels({"part": "snippet,statistics,contentDetails", "id": ",".join(channel_ids)})
    except ChannelsListToolError as exc:
        mapped = _map_channel_search_error(exc)
        raise VideosSearchVideosToolError(
            str(mapped),
            category="partial_enrichment_failure",
            details={"requiredFor": required_rules},
        ) from exc
    channel_by_id = _channel_metadata_by_id(channel_payload)
    qualified: list[dict[str, Any]] = []
    excluded = 0
    reasons: set[str] = set()
    needs_latest = _requires_latest_activity(arguments)
    needs_subscriber_count = any(
        field in arguments for field in ("channelMinSubscribers", "channelMaxSubscribers")
    ) or arguments["sortBy"] in {"subscribers_asc", "subscribers_desc", "indie_priority"}
    for candidate in candidates:
        channel_id = candidate.get("channelId")
        channel = channel_by_id.get(channel_id) if isinstance(channel_id, str) else None
        if channel is None:
            excluded += 1
            reasons.add("channel_metadata_unavailable")
            continue
        subscriber_count = _subscriber_count(channel)
        classification, signals = _creator_classification(channel)
        channel_result: dict[str, Any] = {}
        statistics = channel.get("statistics") if isinstance(channel.get("statistics"), dict) else {}
        if subscriber_count is not None:
            channel_result["subscriberCount"] = statistics["subscriberCount"]
        if classification == "creator":
            channel_result["creatorClassification"] = classification
            channel_result["creatorSignals"] = signals
        elif arguments["creatorOnly"]:
            continue
        if needs_subscriber_count and subscriber_count is None:
            excluded += 1
            reasons.add("subscriber_count_unavailable")
            continue
        if "channelMinSubscribers" in arguments and (subscriber_count is None or subscriber_count < arguments["channelMinSubscribers"]):
            if subscriber_count is None:
                excluded += 1
                reasons.add("subscriber_count_unavailable")
            continue
        if "channelMaxSubscribers" in arguments and (subscriber_count is None or subscriber_count > arguments["channelMaxSubscribers"]):
            if subscriber_count is None:
                excluded += 1
                reasons.add("subscriber_count_unavailable")
            continue
        if needs_latest:
            latest = latest_activity(channel_id) if latest_activity is not None else _latest_upload_from_playlist(channel, playlist_items)
            if not isinstance(latest, str) or not latest:
                excluded += 1
                reasons.add("latest_activity_unavailable")
                continue
            if not _timestamp_matches(latest, arguments.get("channelLastUploadAfter"), arguments.get("channelLastUploadBefore")):
                continue
            channel_result["latestVideoPublishedAt"] = latest
        if channel_result:
            candidate = dict(candidate)
            candidate["channel"] = channel_result
        qualified.append(candidate)
    if candidates and not qualified and excluded == len(candidates):
        raise VideosSearchVideosToolError(
            "Required channel enrichment is unavailable",
            category="partial_enrichment_failure",
            details={"requiredFor": required_rules},
        )
    partial = None
    if excluded:
        partial = {
            "status": "partial",
            "excludedCandidateCount": excluded,
            "reasons": sorted(reasons),
            "requiredFor": required_rules,
        }
    return qualified, partial


def _search_field_provenance() -> dict[str, str]:
    """Return public field provenance for the base query-only result shape.

    :return: Field-to-provenance mapping for stable video-search results.
    """
    return {
        "videoId": "raw_upstream",
        "title": "normalized",
        "description": "normalized",
        "publishedAt": "normalized",
        "channelId": "normalized",
        "channelTitle": "normalized",
        "thumbnails": "normalized",
        "channel.subscriberCount": "raw_upstream",
        "channel.latestVideoPublishedAt": "normalized",
        "channel.creatorClassification": "heuristic_inferred",
    }


def _build_video_search_result(
    payload: dict[str, Any],
    arguments: dict[str, Any],
    *,
    candidates: list[dict[str, Any]] | None = None,
    partial_enrichment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Shape the bounded query-only public video-search result.

    :param payload: Near-raw Layer 2 base-search result.
    :param arguments: Validated public video-search arguments.
    :param candidates: Optional filtered candidates replacing base candidates.
    :param partial_enrichment: Optional safe partial-enrichment summary.
    :return: Stable result collection with applied inputs and provenance.
    """
    raw_items = payload.get("items") if isinstance(payload, dict) else []
    normalized_candidates = [candidate for item in raw_items if isinstance(item, dict) if (candidate := _normalize_video_search_candidate(item))]
    final_candidates = candidates if candidates is not None else normalized_candidates
    public_candidates = [{key: value for key, value in candidate.items() if not key.startswith("_")} for candidate in final_candidates]
    result: dict[str, Any] = {
        "items": public_candidates[: arguments["maxResults"]],
        "appliedInputs": dict(arguments),
        "returnedCount": min(len(public_candidates), arguments["maxResults"]),
        "maxResults": arguments["maxResults"],
        "fieldProvenance": _search_field_provenance(),
    }
    next_page_token = payload.get("nextPageToken") if isinstance(payload, dict) else None
    if isinstance(next_page_token, str) and next_page_token:
        result["nextPageToken"] = next_page_token
    if partial_enrichment is not None:
        result["partialEnrichment"] = partial_enrichment
    return result


def build_videos_search_videos_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for the concrete video-search tool.

    :return: JSON-compatible public metadata without a representative-only marker.
    """
    return {
        "name": VIDEOS_SEARCH_VIDEOS_TOOL_NAME,
        "family": "videos",
        "parameters": list(VIDEOS_SEARCH_VIDEOS_INPUT_SCHEMA["properties"]),
        "inputContract": VIDEOS_SEARCH_VIDEOS_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "ranked_enrichment",
            "lowerLayerDependencies": ["search.list", "channels.list", "playlistItems.list"],
            "boundedness": "Final results and conditional enrichment candidates are capped at maxResults (1-50).",
            "partialResultPolicy": "Candidates missing data needed by an active channel rule are excluded with safe partial-enrichment disclosure.",
        },
        "lowerLayerDependencies": ["search.list", "channels.list", "playlistItems.list"],
        "authAndQuotaNotes": [
            "Uses public search, channel lookup, and uploads-playlist capability.",
            "Channel-aware filters and activity ranking can add bounded lower-layer requests.",
        ],
        "responseFields": [
            {"fieldName": field, "category": category, "source": "documented public video-search result"}
            for field, category in _search_field_provenance().items()
        ],
        "rankingAndFiltering": ["uniqueChannels", "creatorOnly", "subscriberBand", "latestUpload", "sortBy"],
        "rankingSemantics": {
            "sortBy": list(VIDEOS_SEARCH_VIDEOS_SORTS),
            "ties": "Every tie preserves base-search position.",
            "deduplication": "Apply uniqueChannels after final ranking.",
            "unavailableData": "Candidates missing data required by a selected non-relevance ranking are excluded with safe partial-enrichment disclosure.",
        },
        "heuristics": [
            {
                "name": "creatorClassification",
                "basis": "Available public channel metadata.",
                "limitations": "Classification is inferred and can be incomplete or incorrect.",
            }
        ],
        "errorCategories": [
            "invalid_parameters",
            "unavailable_resource",
            "authorization_sensitive_data",
            "quota_exhaustion",
            "upstream_failure",
            "partial_enrichment_failure",
            "unsupported_filter_or_sort",
        ],
        "errorGuidance": {
            "invalid_parameters": "Correct the identified request field and retry.",
            "unavailable_resource": "Use a different accessible query or channel constraint.",
            "authorization_sensitive_data": "Use permitted public data or obtain the necessary capability.",
            "quota_exhaustion": "Retry after capacity is available.",
            "upstream_failure": "Retry when the source service is available.",
            "partial_enrichment_failure": "Relax the enrichment-dependent rule or retry when metadata is available.",
            "unsupported_filter_or_sort": "Use a documented supported value or combination.",
        },
    }


def build_videos_search_videos_handler(*, search=None, channels=None, latest_activity=None, playlist_items=None):
    """Build a callable handler for query-only public video search.

    :param search: Optional lower-layer ``search_list`` override for tests.
    :param channels: Optional lower-layer ``channels_list`` override for tests.
    :param latest_activity: Optional channel-ID-to-timestamp override for tests.
    :param playlist_items: Optional lower-layer uploads-playlist override for tests.
    :return: Callable that validates, retrieves, and normalizes video-search results.
    """
    selected_search = search or build_search_list_handler()
    selected_channels = channels or build_channels_list_handler()
    selected_playlist_items = playlist_items or build_playlist_items_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated query-only public video search.

        :param arguments: Caller-provided public video-search arguments.
        :return: Stable bounded public video-search collection.
        :raises VideosSearchVideosToolError: If validation or base search fails.
        """
        normalized = validate_videos_search_videos_arguments(arguments)
        try:
            payload = selected_search(_build_base_search_arguments(normalized))
        except SearchListToolError as exc:
            raise _map_video_search_error(exc) from exc
        raw_items = payload.get("items") if isinstance(payload, dict) else []
        candidates = [
            {**candidate, "_baseSearchPosition": position}
            for position, item in enumerate(raw_items)
            if isinstance(item, dict) and (candidate := _normalize_video_search_candidate(item))
        ]
        eligible, partial = _enrich_and_filter_video_candidates(
            candidates,
            normalized,
            channels=selected_channels,
            latest_activity=latest_activity,
            playlist_items=selected_playlist_items,
        )
        ranked = _rank_video_search_candidates(eligible, normalized)
        if normalized["uniqueChannels"]:
            ranked = _unique_channel_candidates(ranked)
        return _build_video_search_result(payload, normalized, candidates=ranked, partial_enrichment=partial)

    return handler


def build_videos_search_videos_tool_descriptor(*, search=None, channels=None, latest_activity=None, playlist_items=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for ``videos_searchVideos``.

    :param search: Optional lower-layer ``search_list`` override for tests.
    :param channels: Optional lower-layer ``channels_list`` override for tests.
    :param latest_activity: Optional channel-ID-to-timestamp override for tests.
    :param playlist_items: Optional lower-layer uploads-playlist override for tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": VIDEOS_SEARCH_VIDEOS_TOOL_NAME,
        "description": "Search public YouTube videos with optional channel-aware refinement and ranking.",
        "inputSchema": VIDEOS_SEARCH_VIDEOS_INPUT_SCHEMA,
        "handler": build_videos_search_videos_handler(
            search=search,
            channels=channels,
            latest_activity=latest_activity,
            playlist_items=playlist_items,
        ),
        "metadata": build_videos_search_videos_metadata(),
    }
