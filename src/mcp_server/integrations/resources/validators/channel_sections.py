# ruff: noqa: F405
"""Validation helpers for channel sections resource wrappers."""

from __future__ import annotations

from mcp_server.integrations.contracts import require_mapping_fields
from mcp_server.integrations.resources.constants import *  # noqa: F403
from mcp_server.integrations.resources.validators.base import *  # noqa: F403

def _validate_channel_sections_body(
    arguments: dict[str, object],
    *,
    require_existing_id: bool,
) -> None:
    """Validate the supported channel-sections write request body.

    :param arguments: Wrapper arguments to validate.
    :param require_existing_id: Whether the request body must identify an existing section.
    :raises ValueError: If the request body does not match supported section rules.
    """
    require_mapping_fields("body", required_keys=("snippet",))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    supported_body_fields = {"snippet", "contentDetails"}
    if require_existing_id:
        supported_body_fields = {"id", *supported_body_fields}
    unsupported_fields = [field for field in body if field not in supported_body_fields]
    if unsupported_fields:
        raise ValueError(f"body.{unsupported_fields[0]} is read-only or unsupported")

    if require_existing_id:
        raw_id = body.get("id")
        if not isinstance(raw_id, str) or not raw_id.strip():
            raise ValueError("body.id is required")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_type = snippet.get("type")
    if not isinstance(raw_type, str) or not raw_type.strip():
        raise ValueError("body.snippet.type is required")
    section_type = raw_type.strip()

    raw_channel_id = snippet.get("channelId")
    if not isinstance(raw_channel_id, str) or not raw_channel_id.strip():
        raise ValueError("body.snippet.channelId is required")

    title = snippet.get("title")
    if section_type in _CHANNEL_SECTIONS_TITLE_REQUIRED_TYPES:
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"{section_type} requires body.snippet.title")

    content_details = body.get("contentDetails")
    if section_type in _CHANNEL_SECTIONS_PLAYLIST_TYPES:
        if not isinstance(content_details, dict):
            raise ValueError("body.contentDetails.playlists is required")
        if content_details.get("channels") not in (None, [], ()):
            raise ValueError(f"{section_type} does not accept body.contentDetails.channels")
        playlist_ids = _validated_reference_values(
            content_details.get("playlists"),
            reference_label="playlist",
            required_message="body.contentDetails.playlists is required",
            duplicate_message="duplicate playlist references are unsupported",
        )
        if section_type == "singlePlaylist" and len(playlist_ids) != 1:
            raise ValueError("singlePlaylist requires exactly one playlist id")
        return

    if section_type in _CHANNEL_SECTIONS_CHANNEL_TYPES:
        if not isinstance(content_details, dict):
            raise ValueError("body.contentDetails.channels is required")
        if content_details.get("playlists") not in (None, [], ()):
            raise ValueError(f"{section_type} does not accept body.contentDetails.playlists")
        _validated_reference_values(
            content_details.get("channels"),
            reference_label="channel",
            required_message="body.contentDetails.channels is required",
            duplicate_message="duplicate channel references are unsupported",
        )
        return

    if not isinstance(content_details, dict):
        return
    if content_details.get("playlists") not in (None, [], ()):
        raise ValueError(f"{section_type} does not accept body.contentDetails.playlists")
    if content_details.get("channels") not in (None, [], ()):
        raise ValueError(f"{section_type} does not accept body.contentDetails.channels")

def _require_channel_sections_insert_body(arguments: dict[str, object]) -> None:
    """Validate the supported `channelSections.insert` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported section rules.
    """
    _validate_channel_sections_body(arguments, require_existing_id=False)

def _require_channel_sections_update_body(arguments: dict[str, object]) -> None:
    """Validate the supported `channelSections.update` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported update rules.
    """
    _validate_channel_sections_body(arguments, require_existing_id=True)

__all__ = [
    "_validate_channel_sections_body",
    "_require_channel_sections_insert_body",
    "_require_channel_sections_update_body",
]
