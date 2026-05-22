# ruff: noqa: F405
"""Response normalizers for channel banners resources."""

from __future__ import annotations

import json

from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _channel_banners_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `channelBanners.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Lightweight banner-upload result with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return {
        "bannerUrl": parsed.get("url"),
        "isUploaded": bool(parsed.get("url")),
        "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
    }

NORMALIZERS = (
    ResponseNormalizer.context_and_payload(
        family_name="channel_banners",
        operation_key="channelBanners.insert",
        handler=_channel_banners_insert_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_channel_banners_insert_payload",
]
