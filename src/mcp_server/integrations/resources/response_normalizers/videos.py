# ruff: noqa: F405
"""Response normalizers for videos resources."""

from __future__ import annotations

import json
from typing import Any

from mcp_server.integrations.executor import RequestExecution
from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _videos_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `videos.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed video-create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    status = body.get("status", {}) if isinstance(body, dict) else {}
    parsed_status = parsed.get("status", {}) if isinstance(parsed.get("status"), dict) else {}
    parsed["part"] = execution.arguments.get("part")
    parsed["uploadMode"] = execution.arguments.get("uploadMode") or "multipart"
    parsed["authPath"] = "oauth_required"
    parsed["title"] = parsed.get("title") or snippet.get("title")
    parsed["privacyStatus"] = parsed.get("privacyStatus") or parsed_status.get("privacyStatus") or status.get(
        "privacyStatus"
    )
    parsed["visibilityCaveat"] = (
        "audit/private-default caveat applies until the caller completes the required review flow"
    )
    return parsed

def _videos_rate_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `videos.rate` response.

    :param execution: Shared request execution details.
    :param payload: Raw payload returned by the upstream response, if any.
    :return: Lightweight rating acknowledgement with stable metadata fields.
    :raises ValueError: If a non-empty upstream response is not a JSON object.
    """
    parsed: dict[str, Any] = {}
    if payload.strip():
        loaded = json.loads(payload)
        if not isinstance(loaded, dict):
            raise ValueError("YouTube Data API responses must decode to an object")
        parsed = loaded

    requested_rating = _stringify_scalar(execution.arguments.get("rating"))
    video_id = _stringify_scalar(execution.arguments.get("id"))
    parsed["videoId"] = parsed.get("videoId") or video_id
    parsed["requestedRating"] = parsed.get("requestedRating") or requested_rating
    parsed["isRated"] = parsed.get("isRated") if "isRated" in parsed else requested_rating != "none"
    parsed["isCleared"] = parsed.get("isCleared") if "isCleared" in parsed else requested_rating == "none"
    parsed["ratingState"] = parsed.get("ratingState") or ("cleared" if requested_rating == "none" else "applied")
    parsed["upstreamBodyState"] = parsed.get("upstreamBodyState") or ("json" if payload.strip() else "empty")
    return parsed

def _videos_get_rating_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `videos.getRating` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed rating lookup payload with stable per-video result fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")

    requested_id = _stringify_scalar(execution.arguments.get("id"))
    requested_video_ids = _split_comma_delimited_ids(requested_id)
    items = parsed.get("items")
    normalized_items: list[dict[str, Any]] = []
    if isinstance(items, list):
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            fallback_video_id = requested_video_ids[index] if index < len(requested_video_ids) else None
            video_id = _stringify_scalar(item.get("videoId")) or fallback_video_id
            rating = _normalized_video_rating_state(item.get("rating"))
            is_unrated = rating == "none"
            normalized_items.append(
                {
                    "videoId": video_id,
                    "rating": rating,
                    "isRated": not is_unrated,
                    "isUnrated": is_unrated,
                }
            )

    parsed["requestedId"] = requested_id
    parsed["authPath"] = "oauth_required"
    parsed["videoRatings"] = normalized_items
    parsed["ratingStateSummary"] = _videos_get_rating_summary(normalized_items)
    return parsed

def _videos_report_abuse_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `videos.reportAbuse` response.

    :param execution: Shared request execution details.
    :param payload: Raw payload returned by the upstream response, if any.
    :return: Lightweight report acknowledgement with stable metadata fields.
    :raises ValueError: If a non-empty upstream response is not a JSON object.
    """
    parsed: dict[str, Any] = {}
    if payload.strip():
        loaded = json.loads(payload)
        if not isinstance(loaded, dict):
            raise ValueError("YouTube Data API responses must decode to an object")
        parsed = loaded

    body = execution.arguments.get("body")
    report_body = body if isinstance(body, dict) else {}
    parsed["isAccepted"] = parsed.get("isAccepted", True)
    parsed["reportedVideoId"] = parsed.get("reportedVideoId") or _stringify_scalar(report_body.get("videoId"))
    parsed["reasonId"] = parsed.get("reasonId") or _stringify_scalar(report_body.get("reasonId"))
    if report_body.get("secondaryReasonId") is not None:
        parsed["secondaryReasonId"] = parsed.get("secondaryReasonId") or _stringify_scalar(
            report_body.get("secondaryReasonId")
        )
    if report_body.get("language") is not None:
        parsed["language"] = parsed.get("language") or _stringify_scalar(report_body.get("language"))
    parsed["hasComments"] = parsed.get("hasComments") if "hasComments" in parsed else bool(report_body.get("comments"))
    parsed["authPath"] = parsed.get("authPath") or "oauth_required"
    parsed["sourceOperation"] = parsed.get("sourceOperation") or execution.metadata.operation_key
    parsed["upstreamBodyState"] = parsed.get("upstreamBodyState") or ("json" if payload.strip() else "empty")
    return parsed

def _videos_delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `videos.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight deletion acknowledgement with stable metadata fields.
    """
    return {
        "videoId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "authPath": "oauth_required",
        "sourceOperation": execution.metadata.operation_key,
        "upstreamBodyState": "empty",
    }

def _videos_update_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `videos.update` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed video update payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    return _update_payload_with_request_fallbacks(execution, payload)

def _videos_list_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `videos.list` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed videos payload with stable selector and auth context.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    selector_name = next(
        (
            selector
            for selector in ("id", "chart", "myRating")
            if selector in execution.arguments and execution.arguments.get(selector) not in (None, "")
        ),
        None,
    )
    parsed["part"] = execution.arguments.get("part")
    parsed["selectedSelector"] = selector_name
    parsed["authPath"] = "oauth_required" if selector_name == "myRating" else "api_key"
    if selector_name:
        parsed[selector_name] = execution.arguments.get(selector_name)
    for field in ("regionCode", "videoCategoryId", "pageToken", "maxResults"):
        if execution.arguments.get(field) not in (None, ""):
            parsed[field] = execution.arguments.get(field)
    return parsed

NORMALIZERS = (
    ResponseNormalizer.context_and_payload(
        family_name="videos",
        operation_key="videos.insert",
        handler=_videos_insert_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="videos",
        operation_key="videos.rate",
        handler=_videos_rate_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="videos",
        operation_key="videos.getRating",
        handler=_videos_get_rating_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="videos",
        operation_key="videos.reportAbuse",
        handler=_videos_report_abuse_payload,
    ),
    ResponseNormalizer.context_only(
        family_name="videos",
        operation_key="videos.delete",
        handler=_videos_delete_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="videos",
        operation_key="videos.update",
        handler=_videos_update_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="videos",
        operation_key="videos.list",
        handler=_videos_list_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_videos_delete_payload",
    "_videos_get_rating_payload",
    "_videos_insert_payload",
    "_videos_list_payload",
    "_videos_rate_payload",
    "_videos_report_abuse_payload",
    "_videos_update_payload",
]
