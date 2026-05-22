# ruff: noqa: F405
"""Response normalizers for playlists resources."""

from __future__ import annotations

import json

from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _playlists_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlists.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    parsed_snippet = parsed.get("snippet", {}) if isinstance(parsed.get("snippet"), dict) else {}
    parsed["part"] = execution.arguments.get("part")
    parsed["title"] = parsed.get("title") or parsed_snippet.get("title") or snippet.get("title")
    return parsed

def _playlists_update_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlists.update` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist update payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    return _update_payload_with_request_fallbacks(execution, payload)

def _playlists_delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `playlists.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight delete result with stable metadata fields.
    """
    return {
        "playlistId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "upstreamBodyState": "empty",
    }

def _playlists_list_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlists.list` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlists list payload with stable selector context.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    selector_name = next(
        (
            selector
            for selector in ("channelId", "id", "mine")
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
        family_name="playlists",
        operation_key="playlists.insert",
        handler=_playlists_insert_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="playlists",
        operation_key="playlists.update",
        handler=_playlists_update_payload,
    ),
    ResponseNormalizer.context_only(
        family_name="playlists",
        operation_key="playlists.delete",
        handler=_playlists_delete_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="playlists",
        operation_key="playlists.list",
        handler=_playlists_list_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_playlists_delete_payload",
    "_playlists_insert_payload",
    "_playlists_list_payload",
    "_playlists_update_payload",
]
