# ruff: noqa: F405
"""Response normalizers for channels resources."""

from __future__ import annotations

import json

from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _channels_update_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `channels.update` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed channel-resource payload for update consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed

NORMALIZERS = (
    ResponseNormalizer.payload_only(
        family_name="channels",
        operation_key="channels.update",
        handler=_channels_update_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_channels_update_payload",
]
