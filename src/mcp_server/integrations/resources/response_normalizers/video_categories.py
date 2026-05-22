# ruff: noqa: F405
"""Response normalizers for video categories resources."""

from __future__ import annotations

import json

from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _video_categories_list_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `videoCategories.list` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed video-categories payload with stable selector context.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    selector_name = next(
        (
            selector
            for selector in ("id", "regionCode")
            if selector in execution.arguments and execution.arguments.get(selector) not in (None, "")
        ),
        None,
    )
    parsed["selectedSelector"] = selector_name
    if selector_name == "id":
        parsed["id"] = execution.arguments.get("id")
    if selector_name == "regionCode":
        parsed["regionCode"] = execution.arguments.get("regionCode")
    if execution.arguments.get("hl") not in (None, ""):
        parsed["hl"] = execution.arguments.get("hl")
    return parsed

NORMALIZERS = (
    ResponseNormalizer.context_and_payload(
        family_name="video_categories",
        operation_key="videoCategories.list",
        handler=_video_categories_list_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_video_categories_list_payload",
]
