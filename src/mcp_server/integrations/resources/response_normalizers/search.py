# ruff: noqa: F405
"""Response normalizers for search resources."""

from __future__ import annotations

import json

from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _search_list_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `search.list` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed search payload with stable request context.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    parsed["queryContext"] = {
        key: value
        for key, value in execution.arguments.items()
        if value not in (None, "")
        and key
        in {
            "part",
            "q",
            "type",
            "channelId",
            "publishedAfter",
            "publishedBefore",
            "regionCode",
            "relevanceLanguage",
            "safeSearch",
            "order",
            "pageToken",
            "maxResults",
        }
    }
    parsed["part"] = execution.arguments.get("part")
    parsed["query"] = execution.arguments.get("q")
    parsed["searchType"] = execution.arguments.get("type")
    parsed["authPath"] = (
        "restricted"
        if any(
            execution.arguments.get(field) not in (None, "", False)
            for field in ("forContentOwner", "forDeveloper", "forMine")
        )
        else "public"
    )
    return parsed

NORMALIZERS = (
    ResponseNormalizer.context_and_payload(
        family_name="search",
        operation_key="search.list",
        handler=_search_list_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_search_list_payload",
]
