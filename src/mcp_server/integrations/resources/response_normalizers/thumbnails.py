# ruff: noqa: F405
"""Response normalizers for thumbnails resources."""

from __future__ import annotations

import json

from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _thumbnails_set_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `thumbnails.set` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed thumbnail-update payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    parsed["videoId"] = parsed.get("videoId") or execution.arguments.get("videoId")
    parsed["thumbnailUrl"] = parsed.get("thumbnailUrl") or parsed.get("url")
    parsed["isUpdated"] = bool(parsed.get("videoId"))
    return parsed

NORMALIZERS = (
    ResponseNormalizer.context_and_payload(
        family_name="thumbnails",
        operation_key="thumbnails.set",
        handler=_thumbnails_set_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_thumbnails_set_payload",
]
