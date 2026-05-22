# ruff: noqa: F405
"""Validation helpers for videos resource wrappers."""

from __future__ import annotations

from mcp_server.integrations.contracts import require_mapping_fields
from mcp_server.integrations.resources.constants import *  # noqa: F403
from mcp_server.integrations.resources.validators.base import *  # noqa: F403

def _require_videos_list_arguments(arguments: dict[str, object]) -> None:
    """Validate selector-specific arguments for `videos.list`.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If unsupported refinements are supplied for the selector path.
    """
    has_id_selector = isinstance(arguments.get("id"), str) and bool(str(arguments.get("id")).strip())
    has_chart_selector = isinstance(arguments.get("chart"), str) and bool(str(arguments.get("chart")).strip())
    has_rating_selector = isinstance(arguments.get("myRating"), str) and bool(str(arguments.get("myRating")).strip())
    has_collection_selector = has_chart_selector or has_rating_selector
    has_paging = any(arguments.get(field) not in (None, "") for field in ("pageToken", "maxResults"))
    if has_paging and not has_collection_selector:
        raise ValueError("paging fields are only supported for chart or myRating lookups")
    if has_id_selector and has_paging:
        raise ValueError("paging fields are only supported for chart or myRating lookups")

    has_chart_refinements = any(
        arguments.get(field) not in (None, "")
        for field in ("regionCode", "videoCategoryId")
    )
    if has_chart_refinements and not has_chart_selector:
        raise ValueError("chart-only refinements require chart lookup")

def _require_videos_insert_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `videos.insert` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If metadata, media, or upload-mode details are incomplete.
    """
    require_mapping_fields("body", required_keys=("snippet",))(arguments)
    require_mapping_fields("media", required_keys=("mimeType", "content"))(arguments)
    upload_mode = arguments.get("uploadMode")
    if upload_mode in (None, ""):
        return
    if not isinstance(upload_mode, str) or upload_mode not in _VIDEOS_INSERT_UPLOAD_MODES:
        raise ValueError("uploadMode must be multipart or resumable")

def _require_videos_update_body(arguments: dict[str, object]) -> None:
    """Validate the supported `videos.update` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported update rules.
    """
    part = str(arguments.get("part", "")).strip()
    if part != "snippet":
        raise ValueError("unsupported writable part: only snippet is supported")

    require_mapping_fields("body", required_keys=("id", "snippet"))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"id", "kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    raw_video_id = body.get("id")
    if not isinstance(raw_video_id, str) or not raw_video_id.strip():
        raise ValueError("body.id is required")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_title = snippet.get("title")
    if not isinstance(raw_title, str) or not raw_title.strip():
        raise ValueError("body.snippet.title is required")

    unsupported_snippet_fields = [field for field in snippet if field not in {"title"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")

def _require_videos_rate_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `videos.rate` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request arguments do not match supported rating rules.
    """
    raw_video_id = arguments.get("id")
    if not isinstance(raw_video_id, str) or not raw_video_id.strip():
        raise ValueError("id is required")

    raw_rating = arguments.get("rating")
    if not isinstance(raw_rating, str) or not raw_rating.strip():
        raise ValueError("rating is required")

    rating = raw_rating.strip()
    if rating not in {"like", "dislike", "none"}:
        raise ValueError(f"unsupported rating: {rating}")

def _validated_videos_get_rating_ids(raw_value: object) -> tuple[str, ...]:
    """Return validated video identifiers for `videos.getRating`.

    :param raw_value: Candidate `id` value from wrapper arguments.
    :return: Normalized ordered video identifiers without duplicates.
    :raises ValueError: If the identifier field is empty, malformed, or duplicated.
    """
    if not isinstance(raw_value, str):
        raise ValueError("id must identify one or more videos")

    normalized_ids: list[str] = []
    for raw_identifier in raw_value.split(","):
        identifier = raw_identifier.strip()
        if not identifier:
            raise ValueError("id must identify one or more videos")
        if identifier in normalized_ids:
            raise ValueError("duplicate video identifiers are unsupported")
        normalized_ids.append(identifier)
    if not normalized_ids:
        raise ValueError("id must identify one or more videos")
    if len(normalized_ids) > 50:
        raise ValueError("id may include at most 50 video identifiers")
    return tuple(normalized_ids)

def _require_videos_get_rating_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `videos.getRating` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request arguments do not match supported lookup rules.
    """
    _validated_videos_get_rating_ids(arguments.get("id"))

def _require_videos_report_abuse_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `videos.reportAbuse` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the report body is missing required fields or uses
        unsupported payload fields.
    """
    require_mapping_fields("body", required_keys=("videoId", "reasonId"))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    for field in body:
        if field not in _VIDEOS_REPORT_ABUSE_BODY_FIELDS:
            raise ValueError(f"body.{field} is unsupported")

def _require_videos_delete_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `videos.delete` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the target identifier is malformed or unsupported
        delete modifiers are supplied.
    """
    raw_video_id = arguments.get("id")
    if not isinstance(raw_video_id, str) or not raw_video_id.strip():
        raise ValueError("id must identify one video")

__all__ = [
    "_require_videos_list_arguments",
    "_require_videos_insert_arguments",
    "_require_videos_update_body",
    "_require_videos_rate_arguments",
    "_validated_videos_get_rating_ids",
    "_require_videos_get_rating_arguments",
    "_require_videos_report_abuse_arguments",
    "_require_videos_delete_arguments",
]
