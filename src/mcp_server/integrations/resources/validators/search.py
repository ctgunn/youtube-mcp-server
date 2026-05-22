# ruff: noqa: F405
"""Validation helpers for search resource wrappers."""

from __future__ import annotations

from mcp_server.integrations.resources.constants import *  # noqa: F403
from mcp_server.integrations.resources.validators.base import *  # noqa: F403

def _require_search_list_arguments(arguments: dict[str, object]) -> None:
    """Validate supported argument combinations for `search.list`.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If restricted filters conflict or video filters lack `type=video`.
    """
    restricted_filters = [
        field
        for field in _SEARCH_RESTRICTED_FIELDS
        if (arguments.get(field) is True)
        or (isinstance(arguments.get(field), str) and bool(str(arguments.get(field)).strip()))
    ]
    if len(restricted_filters) > 1:
        raise ValueError("restricted search filters are mutually exclusive")

    uses_video_only_filters = any(
        arguments.get(field) not in (None, "")
        for field in _SEARCH_VIDEO_ONLY_FIELDS
    )
    search_type = str(arguments.get("type", "")).strip()
    if uses_video_only_filters and search_type != "video":
        raise ValueError("video-specific refinements require type=video")

__all__ = [
    "_require_search_list_arguments",
]
