"""Normalized public video-detail tools.

The module owns concrete single-video detail behavior for the videos family.
"""

from __future__ import annotations

from typing import Any

from mcp_server.tools.youtube_common.conventions import sanitize_error_details
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


def _map_videos_list_error(error: VideosListToolError) -> VideosGetVideoToolError:
    """Translate one lower-level error to a safe public video-detail error.

    :param error: Safe lower-level video lookup error.
    :return: Public error with the documented category and safe details.
    """
    category = error.category
    if category in {"resource_not_found", "removed"}:
        return VideosGetVideoToolError(
            "The requested video is unavailable",
            category="unavailable_resource",
            details={"resource": "video"},
        )
    public_category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
    }.get(category, "upstream_failure")
    return VideosGetVideoToolError(str(error), category=public_category, details=error.details)


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
