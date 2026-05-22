# ruff: noqa: F405
"""Validation helpers for watermarks resource wrappers."""

from __future__ import annotations

from mcp_server.integrations.contracts import require_mapping_fields
from mcp_server.integrations.resources.constants import *  # noqa: F403
from mcp_server.integrations.resources.validators.base import *  # noqa: F403

def _require_watermarks_set_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `watermarks.set` request arguments.

    Official quota cost: ``50`` quota units. The supported request requires
    ``channelId``, watermark ``body`` metadata, and ``media`` upload content.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If channel, watermark metadata, or media details are incomplete.
    """
    raw_channel_id = arguments.get("channelId")
    if not isinstance(raw_channel_id, str) or not raw_channel_id.strip():
        raise ValueError("channelId must identify one channel")
    require_mapping_fields("body", required_keys=("timing", "position"))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    for field_name in ("timing", "position"):
        if not isinstance(body.get(field_name), dict) or not body.get(field_name):
            raise ValueError(f"body.{field_name} must be a non-empty mapping")
    target_channel_id = body.get("targetChannelId")
    if target_channel_id is not None and not isinstance(target_channel_id, str):
        raise ValueError("body.targetChannelId must be a string when provided")
    require_mapping_fields("media", required_keys=("mimeType", "content"))(arguments)
    media = arguments.get("media")
    assert isinstance(media, dict)  # Narrowed by validator above.
    mime_type = media.get("mimeType")
    if not isinstance(mime_type, str) or not mime_type.strip():
        raise ValueError("media.mimeType is required")
    if mime_type not in _WATERMARK_ALLOWED_MIME_TYPES:
        allowed = ", ".join(sorted(_WATERMARK_ALLOWED_MIME_TYPES))
        raise ValueError(f"media.mimeType must be one of: {allowed}")
    content = media.get("content")
    content_bytes = content if isinstance(content, bytes) else str(content).encode("utf-8")
    if not content_bytes:
        raise ValueError("media.content is required")
    if len(content_bytes) > _WATERMARK_MAX_BYTES:
        raise ValueError("media.content exceeds the 10 MB watermark limit")

def _require_watermarks_unset_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `watermarks.unset` request arguments.

    Official quota cost: ``50`` quota units. The supported request requires
    ``channelId`` only; watermark metadata, media upload content, set-only
    fields, and partner delegation are outside this slice.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If channel details are incomplete.
    """
    raw_channel_id = arguments.get("channelId")
    if not isinstance(raw_channel_id, str) or not raw_channel_id.strip():
        raise ValueError("channelId must identify one channel")

__all__ = [
    "_require_watermarks_set_arguments",
    "_require_watermarks_unset_arguments",
]
