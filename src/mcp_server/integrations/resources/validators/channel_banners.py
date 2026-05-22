# ruff: noqa: F405
"""Validation helpers for channel banners resource wrappers."""

from __future__ import annotations

from mcp_server.integrations.contracts import require_mapping_fields
from mcp_server.integrations.resources.constants import *  # noqa: F403
from mcp_server.integrations.resources.validators.base import *  # noqa: F403

def _require_channel_banner_media(arguments: dict[str, object]) -> None:
    """Validate the supported `channelBanners.insert` media payload.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the media payload is missing, unsupported, or too large.
    """
    media = arguments.get("media")
    require_mapping_fields("media", required_keys=("mimeType", "content"))(arguments)
    assert isinstance(media, dict)  # Narrowed by the validator above.
    mime_type = str(media.get("mimeType"))
    if mime_type not in _CHANNEL_BANNER_ALLOWED_MIME_TYPES:
        raise ValueError("media.mimeType must be image/jpeg, image/png, or application/octet-stream")
    content = media.get("content")
    content_bytes = content if isinstance(content, bytes) else str(content).encode("utf-8")
    if not content_bytes:
        raise ValueError("media.content is required")
    if len(content_bytes) > _CHANNEL_BANNER_MAX_BYTES:
        raise ValueError("media.content exceeds the 6 MB channel banner limit")

__all__ = [
    "_require_channel_banner_media",
]
