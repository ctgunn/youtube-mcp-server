# ruff: noqa: F405
"""Validation helpers for playlist images resource wrappers."""

from __future__ import annotations

from mcp_server.integrations.contracts import require_mapping_fields
from mcp_server.integrations.resources.constants import *  # noqa: F403
from mcp_server.integrations.resources.validators.base import *  # noqa: F403

def _require_playlist_images_list_arguments(arguments: dict[str, object]) -> None:
    """Validate selector-specific arguments for `playlistImages.list`.

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

def _require_playlist_images_update_body(arguments: dict[str, object]) -> None:
    """Validate the supported `playlistImages.update` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported update rules.
    """
    require_mapping_fields("body", required_keys=("id", "snippet"))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"id", "kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    raw_playlist_image_id = body.get("id")
    if not isinstance(raw_playlist_image_id, str) or not raw_playlist_image_id.strip():
        raise ValueError("body.id is required")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_playlist_id = snippet.get("playlistId")
    if not isinstance(raw_playlist_id, str) or not raw_playlist_id.strip():
        raise ValueError("body.snippet.playlistId is required")

    unsupported_snippet_fields = [field for field in snippet if field not in {"playlistId", "type"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")

def _require_playlist_images_delete_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `playlistImages.delete` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the delete request is incomplete or unsupported.
    """
    raw_playlist_image_id = arguments.get("id")
    if not isinstance(raw_playlist_image_id, str) or not raw_playlist_image_id.strip():
        raise ValueError("id must identify one playlist image")

__all__ = [
    "_require_playlist_images_list_arguments",
    "_require_playlist_images_update_body",
    "_require_playlist_images_delete_arguments",
]
