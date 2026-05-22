# ruff: noqa: F405
"""Validation helpers for thumbnails resource wrappers."""

from __future__ import annotations

from mcp_server.integrations.contracts import require_mapping_fields
from mcp_server.integrations.resources.constants import *  # noqa: F403
from mcp_server.integrations.resources.validators.base import *  # noqa: F403

def _require_thumbnails_set_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `thumbnails.set` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the target or upload payload is incomplete.
    """
    raw_video_id = arguments.get("videoId")
    if not isinstance(raw_video_id, str) or not raw_video_id.strip():
        raise ValueError("videoId is required")
    require_mapping_fields("media", required_keys=("mimeType", "content"))(arguments)
    media = arguments.get("media")
    assert isinstance(media, dict)  # Narrowed by validator above.
    mime_type = media.get("mimeType")
    if not isinstance(mime_type, str) or not mime_type.strip():
        raise ValueError("media.mimeType is required")
    content = media.get("content")
    content_bytes = content if isinstance(content, bytes) else str(content).encode("utf-8")
    if not content_bytes:
        raise ValueError("media.content is required")

__all__ = [
    "_require_thumbnails_set_arguments",
]
