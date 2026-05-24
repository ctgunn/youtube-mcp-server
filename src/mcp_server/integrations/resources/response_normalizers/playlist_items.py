# ruff: noqa: F405
"""Response normalizers for playlist items resources."""

from __future__ import annotations

import json

from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _playlist_items_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlistItems.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist-item create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    resource_id = snippet.get("resourceId", {}) if isinstance(snippet, dict) else {}
    parsed_snippet = parsed.get("snippet", {}) if isinstance(parsed.get("snippet"), dict) else {}
    parsed_resource_id = (
        parsed_snippet.get("resourceId", {}) if isinstance(parsed_snippet.get("resourceId"), dict) else {}
    )
    parsed["part"] = execution.arguments.get("part")
    parsed["playlistId"] = parsed.get("playlistId") or parsed_snippet.get("playlistId") or snippet.get("playlistId")
    parsed["videoId"] = (
        parsed.get("videoId")
        or parsed_resource_id.get("videoId")
        or resource_id.get("videoId")
    )
    return parsed

def _playlist_items_update_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlistItems.update` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist-item update payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    resource_id = snippet.get("resourceId", {}) if isinstance(snippet, dict) else {}
    parsed_snippet = parsed.get("snippet", {}) if isinstance(parsed.get("snippet"), dict) else {}
    parsed_resource_id = (
        parsed_snippet.get("resourceId", {}) if isinstance(parsed_snippet.get("resourceId"), dict) else {}
    )
    parsed["part"] = execution.arguments.get("part")
    parsed["playlistItemId"] = parsed.get("playlistItemId") or parsed.get("id") or (body.get("id") if isinstance(body, dict) else None)
    parsed["playlistId"] = parsed.get("playlistId") or parsed_snippet.get("playlistId") or snippet.get("playlistId")
    parsed["videoId"] = (
        parsed.get("videoId")
        or parsed_resource_id.get("videoId")
        or resource_id.get("videoId")
    )
    return parsed

def _playlist_items_delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `playlistItems.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight delete result with stable metadata fields.
    """
    return {
        "playlistItemId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "upstreamBodyState": "empty",
    }

def _playlist_items_list_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlistItems.list` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist-items list payload with stable selector context.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    selector_name = next(
        (
            selector
            for selector in ("playlistId", "id")
            if selector in execution.arguments and execution.arguments.get(selector) not in (None, "")
        ),
        None,
    )
    parsed["part"] = execution.arguments.get("part")
    parsed["selectorName"] = selector_name
    parsed["selectorValue"] = execution.arguments.get(selector_name) if selector_name else None
    return parsed

NORMALIZERS = (
    ResponseNormalizer.context_and_payload(
        family_name="playlist_items",
        operation_key="playlistItems.insert",
        handler=_playlist_items_insert_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="playlist_items",
        operation_key="playlistItems.update",
        handler=_playlist_items_update_payload,
    ),
    ResponseNormalizer.context_only(
        family_name="playlist_items",
        operation_key="playlistItems.delete",
        handler=_playlist_items_delete_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="playlist_items",
        operation_key="playlistItems.list",
        handler=_playlist_items_list_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_playlist_items_delete_payload",
    "_playlist_items_insert_payload",
    "_playlist_items_list_payload",
    "_playlist_items_update_payload",
]
