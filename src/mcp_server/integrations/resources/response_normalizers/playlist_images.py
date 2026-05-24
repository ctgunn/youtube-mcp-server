# ruff: noqa: F405
"""Response normalizers for playlist images resources."""

from __future__ import annotations

import json

from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _playlist_images_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlistImages.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist-image create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    parsed["part"] = execution.arguments.get("part")
    parsed["playlistId"] = parsed.get("playlistId") or snippet.get("playlistId")
    return parsed

def _playlist_images_update_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlistImages.update` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist-image update payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    parsed["part"] = execution.arguments.get("part")
    parsed["playlistId"] = parsed.get("playlistId") or snippet.get("playlistId")
    return parsed

def _playlist_images_delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `playlistImages.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight delete result with stable metadata fields.
    """
    return {
        "playlistImageId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "upstreamBodyState": "empty",
    }

def _playlist_images_list_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlistImages.list` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist-images list payload with stable selector context.
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
        family_name="playlist_images",
        operation_key="playlistImages.insert",
        handler=_playlist_images_insert_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="playlist_images",
        operation_key="playlistImages.update",
        handler=_playlist_images_update_payload,
    ),
    ResponseNormalizer.context_only(
        family_name="playlist_images",
        operation_key="playlistImages.delete",
        handler=_playlist_images_delete_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="playlist_images",
        operation_key="playlistImages.list",
        handler=_playlist_images_list_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_playlist_images_delete_payload",
    "_playlist_images_insert_payload",
    "_playlist_images_list_payload",
    "_playlist_images_update_payload",
]
