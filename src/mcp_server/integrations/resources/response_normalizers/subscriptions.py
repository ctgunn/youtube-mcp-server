# ruff: noqa: F405
"""Response normalizers for subscriptions resources."""

from __future__ import annotations

import json

from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _subscriptions_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `subscriptions.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed subscription create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    resource_id = snippet.get("resourceId", {}) if isinstance(snippet, dict) else {}
    parsed_snippet = parsed.get("snippet", {}) if isinstance(parsed.get("snippet"), dict) else {}
    parsed_resource_id = (
        parsed_snippet.get("resourceId", {}) if isinstance(parsed_snippet.get("resourceId"), dict) else {}
    )
    parsed["part"] = execution.arguments.get("part")
    parsed["subscriptionId"] = parsed.get("subscriptionId") or parsed.get("id")
    parsed["targetChannelId"] = (
        parsed.get("targetChannelId")
        or parsed_resource_id.get("channelId")
        or resource_id.get("channelId")
    )
    parsed["targetResourceKind"] = (
        parsed.get("targetResourceKind")
        or parsed_resource_id.get("kind")
        or resource_id.get("kind")
        or "youtube#channel"
    )
    return parsed

def _subscriptions_delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `subscriptions.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight delete result with stable metadata fields.
    """
    return {
        "subscriptionId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "upstreamBodyState": "empty",
    }

def _subscriptions_list_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `subscriptions.list` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed subscriptions list payload with stable selector context.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    selector_name = next(
        (
            selector
            for selector in ("channelId", "id", "mine", "myRecentSubscribers", "mySubscribers")
            if (isinstance(execution.arguments.get(selector), str) and bool(str(execution.arguments.get(selector)).strip()))
            or execution.arguments.get(selector) is True
        ),
        None,
    )
    selector_value = execution.arguments.get(selector_name) if selector_name else None
    parsed["part"] = execution.arguments.get("part")
    parsed["selectorName"] = selector_name
    parsed["selectorValue"] = selector_value
    parsed["authPath"] = (
        "oauth"
        if selector_name in {"mine", "myRecentSubscribers", "mySubscribers"}
        else "public"
    )
    parsed["requestContext"] = {
        key: value
        for key, value in {
            "part": execution.arguments.get("part"),
            "selectorName": selector_name,
            "selectorValue": selector_value,
            "pageToken": execution.arguments.get("pageToken"),
            "maxResults": execution.arguments.get("maxResults"),
            "order": execution.arguments.get("order"),
        }.items()
        if value not in (None, "", False)
    }
    return parsed

NORMALIZERS = (
    ResponseNormalizer.context_and_payload(
        family_name="subscriptions",
        operation_key="subscriptions.insert",
        handler=_subscriptions_insert_payload,
    ),
    ResponseNormalizer.context_only(
        family_name="subscriptions",
        operation_key="subscriptions.delete",
        handler=_subscriptions_delete_payload,
    ),
    ResponseNormalizer.context_and_payload(
        family_name="subscriptions",
        operation_key="subscriptions.list",
        handler=_subscriptions_list_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_subscriptions_delete_payload",
    "_subscriptions_insert_payload",
    "_subscriptions_list_payload",
]
