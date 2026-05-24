# ruff: noqa: F405
"""Response normalizers for channel sections resources."""

from __future__ import annotations

import json

from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _channel_sections_delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `channelSections.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight delete result with stable metadata fields.
    """
    return {
        "channelSectionId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
        "delegatedOwnerChannel": execution.arguments.get("onBehalfOfContentOwnerChannel"),
    }

def _channel_sections_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `channelSections.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed channel-sections list payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed

def _channel_sections_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `channelSections.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed channel-section create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    parsed["delegatedOwner"] = execution.arguments.get("onBehalfOfContentOwner")
    parsed["delegatedOwnerChannel"] = execution.arguments.get("onBehalfOfContentOwnerChannel")
    return parsed

def _channel_sections_update_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `channelSections.update` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed channel-section update payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    parsed["delegatedOwner"] = execution.arguments.get("onBehalfOfContentOwner")
    parsed["delegatedOwnerChannel"] = execution.arguments.get("onBehalfOfContentOwnerChannel")
    return parsed

NORMALIZERS = (
    ResponseNormalizer.context_only(
        family_name="channel_sections",
        operation_key="channelSections.delete",
        handler=_channel_sections_delete_payload,
    ),
    ResponseNormalizer.payload_only(
        family_name="channel_sections",
        operation_key="channelSections.list",
        handler=_channel_sections_list_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="channel_sections",
        operation_key="channelSections.insert",
        handler=_channel_sections_insert_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="channel_sections",
        operation_key="channelSections.update",
        handler=_channel_sections_update_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_channel_sections_delete_payload",
    "_channel_sections_insert_payload",
    "_channel_sections_list_payload",
    "_channel_sections_update_payload",
]
