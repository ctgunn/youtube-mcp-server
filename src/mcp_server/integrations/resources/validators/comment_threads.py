# ruff: noqa: F405
"""Validation helpers for comment threads resource wrappers."""

from __future__ import annotations

from mcp_server.integrations.contracts import require_mapping_fields
from mcp_server.integrations.resources.constants import *  # noqa: F403
from mcp_server.integrations.resources.validators.base import *  # noqa: F403

def _require_comment_threads_insert_body(arguments: dict[str, object]) -> None:
    """Validate the supported `commentThreads.insert` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported top-level rules.
    """
    require_mapping_fields("body", required_keys=("snippet",))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_video_id = snippet.get("videoId")
    if not isinstance(raw_video_id, str) or not raw_video_id.strip():
        raise ValueError("body.snippet.videoId is required")

    top_level_comment = snippet.get("topLevelComment")
    if not isinstance(top_level_comment, dict):
        raise ValueError("body.snippet.topLevelComment is required")

    top_level_snippet = top_level_comment.get("snippet")
    if not isinstance(top_level_snippet, dict):
        raise ValueError("body.snippet.topLevelComment.snippet is required")

    raw_comment_text = top_level_snippet.get("textOriginal")
    if not isinstance(raw_comment_text, str) or not raw_comment_text.strip():
        raise ValueError("body.snippet.topLevelComment.snippet.textOriginal is required")

    unsupported_top_level_fields = [
        field for field in top_level_comment if field not in {"kind", "snippet"}
    ]
    if unsupported_top_level_fields:
        raise ValueError(
            f"body.snippet.topLevelComment.{unsupported_top_level_fields[0]} is read-only or unsupported"
        )

    unsupported_top_level_snippet_fields = [
        field for field in top_level_snippet if field not in {"textOriginal"}
    ]
    if unsupported_top_level_snippet_fields:
        raise ValueError(
            "body.snippet.topLevelComment.snippet."
            f"{unsupported_top_level_snippet_fields[0]} is read-only or unsupported"
        )

    unsupported_snippet_fields = [
        field for field in snippet if field not in {"channelId", "videoId", "topLevelComment"}
    ]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")

__all__ = [
    "_require_comment_threads_insert_body",
]
