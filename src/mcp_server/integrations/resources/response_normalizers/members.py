# ruff: noqa: F405
"""Response normalizers for members resources."""

from __future__ import annotations

import json

from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _members_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `members.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed members list payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed

NORMALIZERS = (
    ResponseNormalizer.payload_only(
        family_name="members",
        operation_key="members.list",
        handler=_members_list_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_members_list_payload",
]
