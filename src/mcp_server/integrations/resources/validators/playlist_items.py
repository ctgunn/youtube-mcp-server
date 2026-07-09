# ruff: noqa: F405
"""Validation helpers for playlist items resource wrappers."""

from __future__ import annotations

from mcp_server.integrations.contracts import require_mapping_fields
from mcp_server.integrations.resources.constants import *  # noqa: F403
from mcp_server.integrations.resources.validators.base import *  # noqa: F403

def _require_playlist_items_list_arguments(arguments: dict[str, object]) -> None:
    """Validate selector-specific arguments for `playlistItems.list`.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If paging fields are supplied for non-playlist lookups.
    """
    has_playlist_selector = isinstance(arguments.get("playlistId"), str) and bool(
        str(arguments.get("playlistId")).strip()
    )
    has_id_selector = isinstance(arguments.get("id"), str) and bool(str(arguments.get("id")).strip())
    has_paging = any(arguments.get(field) not in (None, "") for field in ("pageToken", "maxResults"))
    if has_paging and not has_playlist_selector:
        raise ValueError("paging fields are only supported for playlistId lookups")
    if has_id_selector and has_paging:
        raise ValueError("paging fields are only supported for playlistId lookups")

def _require_playlist_items_insert_body(arguments: dict[str, object]) -> None:
    """Validate the supported `playlistItems.insert` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported create rules.
    """
    part = str(arguments.get("part", "")).strip()
    if part != "snippet":
        raise ValueError("unsupported writable part: only snippet is supported")

    require_mapping_fields("body", required_keys=("snippet",))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_playlist_id = snippet.get("playlistId")
    if not isinstance(raw_playlist_id, str) or not raw_playlist_id.strip():
        raise ValueError("body.snippet.playlistId is required")

    resource_id = snippet.get("resourceId")
    if not isinstance(resource_id, dict):
        raise ValueError("body.snippet.resourceId is required")

    raw_video_id = resource_id.get("videoId")
    if not isinstance(raw_video_id, str) or not raw_video_id.strip():
        raise ValueError("body.snippet.resourceId.videoId is required")

    resource_kind = resource_id.get("kind")
    if resource_kind not in (None, "", "youtube#video"):
        raise ValueError("body.snippet.resourceId.kind must be youtube#video when provided")

    position = snippet.get("position")
    if position is not None and (isinstance(position, bool) or not isinstance(position, int) or position < 0):
        raise ValueError("body.snippet.position must be a non-negative integer when provided")

    unsupported_snippet_fields = [field for field in snippet if field not in {"playlistId", "position", "resourceId"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")

    unsupported_resource_fields = [field for field in resource_id if field not in {"kind", "videoId"}]
    if unsupported_resource_fields:
        raise ValueError(
            f"body.snippet.resourceId.{unsupported_resource_fields[0]} is read-only or unsupported"
        )

def _require_playlist_items_update_body(arguments: dict[str, object]) -> None:
    """Validate the supported `playlistItems.update` request body.

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

    raw_playlist_item_id = body.get("id")
    if not isinstance(raw_playlist_item_id, str) or not raw_playlist_item_id.strip():
        raise ValueError("body.id is required")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_playlist_id = snippet.get("playlistId")
    if not isinstance(raw_playlist_id, str) or not raw_playlist_id.strip():
        raise ValueError("body.snippet.playlistId is required")

    resource_id = snippet.get("resourceId")
    if not isinstance(resource_id, dict):
        raise ValueError("body.snippet.resourceId is required")

    raw_video_id = resource_id.get("videoId")
    if not isinstance(raw_video_id, str) or not raw_video_id.strip():
        raise ValueError("body.snippet.resourceId.videoId is required")

    resource_kind = resource_id.get("kind")
    if resource_kind not in (None, "", "youtube#video"):
        raise ValueError("body.snippet.resourceId.kind must be youtube#video when provided")

    unsupported_snippet_fields = [field for field in snippet if field not in {"playlistId", "resourceId"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")

    unsupported_resource_fields = [field for field in resource_id if field not in {"kind", "videoId"}]
    if unsupported_resource_fields:
        raise ValueError(
            f"body.snippet.resourceId.{unsupported_resource_fields[0]} is read-only or unsupported"
        )

def _require_playlist_items_delete_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `playlistItems.delete` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the delete request is incomplete or unsupported.
    """
    raw_playlist_item_id = arguments.get("id")
    if not isinstance(raw_playlist_item_id, str) or not raw_playlist_item_id.strip():
        raise ValueError("id must identify one playlist item")

__all__ = [
    "_require_playlist_items_list_arguments",
    "_require_playlist_items_insert_body",
    "_require_playlist_items_update_body",
    "_require_playlist_items_delete_arguments",
]
