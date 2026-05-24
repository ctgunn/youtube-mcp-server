# ruff: noqa: F405
"""Response normalizers for comments resources."""

from __future__ import annotations

import json

from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _comments_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `comments.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed comments list payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed

def _comments_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `comments.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed comment create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    parsed["delegatedOwner"] = execution.arguments.get("onBehalfOfContentOwner")
    return parsed

def _comments_update_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `comments.update` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed comment update payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    parsed["delegatedOwner"] = execution.arguments.get("onBehalfOfContentOwner")
    return parsed

def _comments_set_moderation_status_payload(
    execution: RequestExecution,
) -> dict[str, Any]:
    """Return the internal result shape for a moderation-status response.

    :param execution: Shared request execution details.
    :return: Lightweight moderation acknowledgment with stable metadata fields.
    """
    raw_ids = execution.arguments.get("id")
    if isinstance(raw_ids, str):
        comment_ids = (raw_ids,)
    elif isinstance(raw_ids, (list, tuple)):
        comment_ids = tuple(str(value) for value in raw_ids)
    else:
        comment_ids = ()
    return {
        "commentIds": comment_ids,
        "isModerated": True,
        "moderationStatus": execution.arguments.get("moderationStatus"),
        "authorBanApplied": bool(execution.arguments.get("banAuthor")),
        "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
        "upstreamBodyState": "empty",
    }

def _comments_delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `comments.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight delete result with stable metadata fields.
    """
    return {
        "commentId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
        "upstreamBodyState": "empty",
    }

NORMALIZERS = (
    ResponseNormalizer.payload_only(
        family_name="comments",
        operation_key="comments.list",
        handler=_comments_list_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="comments",
        operation_key="comments.insert",
        handler=_comments_insert_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="comments",
        operation_key="comments.update",
        handler=_comments_update_payload,
    ),
    ResponseNormalizer.context_only(
        family_name="comments",
        operation_key="comments.setModerationStatus",
        handler=_comments_set_moderation_status_payload,
    ),
    ResponseNormalizer.context_only(
        family_name="comments",
        operation_key="comments.delete",
        handler=_comments_delete_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_comments_delete_payload",
    "_comments_insert_payload",
    "_comments_list_payload",
    "_comments_set_moderation_status_payload",
    "_comments_update_payload",
]
