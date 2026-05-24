# ruff: noqa: F405
"""Response normalizers for comment threads resources."""

from __future__ import annotations

import json

from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _comment_threads_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `commentThreads.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed comment-threads list payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed

def _comment_threads_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `commentThreads.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed comment-thread create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    parsed["delegatedOwner"] = execution.arguments.get("onBehalfOfContentOwner")
    return parsed

NORMALIZERS = (
    ResponseNormalizer.payload_only(
        family_name="comment_threads",
        operation_key="commentThreads.list",
        handler=_comment_threads_list_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="comment_threads",
        operation_key="commentThreads.insert",
        handler=_comment_threads_insert_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_comment_threads_insert_payload",
    "_comment_threads_list_payload",
]
