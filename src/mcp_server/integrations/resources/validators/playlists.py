# ruff: noqa: F405
"""Validation helpers for playlists resource wrappers."""

from __future__ import annotations

from mcp_server.integrations.contracts import require_mapping_fields
from mcp_server.integrations.resources.constants import *  # noqa: F403
from mcp_server.integrations.resources.validators.base import *  # noqa: F403

def _require_playlists_list_arguments(arguments: dict[str, object]) -> None:
    """Validate selector-specific arguments for `playlists.list`.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If paging fields are supplied for direct ID lookups.
    """
    has_collection_selector = any(
        (
            isinstance(arguments.get("channelId"), str) and bool(str(arguments.get("channelId")).strip()),
            arguments.get("mine") is True,
        )
    )
    has_id_selector = isinstance(arguments.get("id"), str) and bool(str(arguments.get("id")).strip())
    has_paging = any(arguments.get(field) not in (None, "") for field in ("pageToken", "maxResults"))
    if has_paging and not has_collection_selector:
        raise ValueError("paging fields are only supported for channelId or mine lookups")
    if has_id_selector and has_paging:
        raise ValueError("paging fields are only supported for channelId or mine lookups")

def _require_playlists_insert_body(arguments: dict[str, object]) -> None:
    """Validate the supported `playlists.insert` request body.

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

    raw_title = snippet.get("title")
    if not isinstance(raw_title, str) or not raw_title.strip():
        raise ValueError("body.snippet.title is required")

    unsupported_snippet_fields = [field for field in snippet if field not in {"title"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")

def _require_playlists_update_body(arguments: dict[str, object]) -> None:
    """Validate the supported `playlists.update` request body.

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

    raw_playlist_id = body.get("id")
    if not isinstance(raw_playlist_id, str) or not raw_playlist_id.strip():
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

def _require_playlists_delete_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `playlists.delete` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the delete request is incomplete or unsupported.
    """
    raw_playlist_id = arguments.get("id")
    if not isinstance(raw_playlist_id, str) or not raw_playlist_id.strip():
        raise ValueError("id must identify one playlist")

__all__ = [
    "_require_playlists_list_arguments",
    "_require_playlists_insert_body",
    "_require_playlists_update_body",
    "_require_playlists_delete_arguments",
]
