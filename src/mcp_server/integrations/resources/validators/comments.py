# ruff: noqa: F405
"""Validation helpers for comments resource wrappers."""

from __future__ import annotations

from mcp_server.integrations.contracts import require_mapping_fields
from mcp_server.integrations.resources.constants import *  # noqa: F403
from mcp_server.integrations.resources.validators.base import *  # noqa: F403

def _require_comments_insert_body(arguments: dict[str, object]) -> None:
    """Validate the supported `comments.insert` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported reply rules.
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

    raw_parent_id = snippet.get("parentId")
    if not isinstance(raw_parent_id, str) or not raw_parent_id.strip():
        raise ValueError("body.snippet.parentId is required")

    raw_reply_text = snippet.get("textOriginal")
    if not isinstance(raw_reply_text, str) or not raw_reply_text.strip():
        raise ValueError("body.snippet.textOriginal is required")

    unsupported_snippet_fields = [field for field in snippet if field not in {"parentId", "textOriginal"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")

def _require_comments_update_body(arguments: dict[str, object]) -> None:
    """Validate the supported `comments.update` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported update rules.
    """
    require_mapping_fields("body", required_keys=("id", "snippet"))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"id", "kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    raw_comment_id = body.get("id")
    if not isinstance(raw_comment_id, str) or not raw_comment_id.strip():
        raise ValueError("body.id is required")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_reply_text = snippet.get("textOriginal")
    if not isinstance(raw_reply_text, str) or not raw_reply_text.strip():
        raise ValueError("body.snippet.textOriginal is required")

    unsupported_snippet_fields = [field for field in snippet if field not in {"textOriginal"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")

def _validated_comment_ids(raw_values: object) -> tuple[str, ...]:
    """Return validated comment identifiers for moderation requests.

    :param raw_values: Candidate comment identifier value or collection.
    :return: Normalized ordered comment identifiers without duplicates.
    :raises ValueError: If no usable identifiers are present or duplicates appear.
    """
    if isinstance(raw_values, str):
        values = [raw_values]
    elif isinstance(raw_values, (list, tuple)):
        values = list(raw_values)
    else:
        raise ValueError("id must contain at least one comment identifier")

    normalized_ids: list[str] = []
    for raw_value in values:
        if not isinstance(raw_value, str) or not raw_value.strip():
            raise ValueError("id must contain at least one comment identifier")
        normalized = raw_value.strip()
        if normalized in normalized_ids:
            raise ValueError("duplicate comment identifiers are unsupported")
        normalized_ids.append(normalized)
    if not normalized_ids:
        raise ValueError("id must contain at least one comment identifier")
    return tuple(normalized_ids)

def _require_comments_set_moderation_status_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `comments.setModerationStatus` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the moderation request is incomplete or unsupported.
    """
    _validated_comment_ids(arguments.get("id"))

    raw_status = arguments.get("moderationStatus")
    if not isinstance(raw_status, str) or not raw_status.strip():
        raise ValueError("moderationStatus is required")
    moderation_status = raw_status.strip()
    supported_statuses = {"published", "heldForReview", "rejected"}
    if moderation_status not in supported_statuses:
        raise ValueError(f"unsupported moderationStatus: {moderation_status}")

    ban_author = arguments.get("banAuthor")
    if ban_author is not None and not isinstance(ban_author, bool):
        raise ValueError("banAuthor must be a boolean when provided")
    if ban_author and moderation_status != "rejected":
        raise ValueError("banAuthor is only supported when moderationStatus is rejected")

def _require_comments_delete_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `comments.delete` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the delete request is incomplete or unsupported.
    """
    raw_comment_id = arguments.get("id")
    if not isinstance(raw_comment_id, str) or not raw_comment_id.strip():
        raise ValueError("id must identify one comment")

__all__ = [
    "_require_comments_insert_body",
    "_require_comments_update_body",
    "_validated_comment_ids",
    "_require_comments_set_moderation_status_arguments",
    "_require_comments_delete_arguments",
]
