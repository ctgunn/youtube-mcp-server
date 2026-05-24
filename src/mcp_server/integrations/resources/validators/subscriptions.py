# ruff: noqa: F405
"""Validation helpers for subscriptions resource wrappers."""

from __future__ import annotations

from mcp_server.integrations.contracts import require_mapping_fields
from mcp_server.integrations.resources.constants import *  # noqa: F403
from mcp_server.integrations.resources.validators.base import *  # noqa: F403

def _require_subscriptions_list_arguments(arguments: dict[str, object]) -> None:
    """Validate selector-specific arguments for `subscriptions.list`.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If paging or ordering fields are supplied for direct ID lookups.
    """
    has_collection_selector = any(
        (
            isinstance(arguments.get("channelId"), str) and bool(str(arguments.get("channelId")).strip()),
            arguments.get("mine") is True,
            arguments.get("myRecentSubscribers") is True,
            arguments.get("mySubscribers") is True,
        )
    )
    has_id_selector = isinstance(arguments.get("id"), str) and bool(str(arguments.get("id")).strip())
    has_paging = any(arguments.get(field) not in (None, "") for field in ("pageToken", "maxResults"))
    has_order = arguments.get("order") not in (None, "")
    if has_paging and not has_collection_selector:
        raise ValueError(
            "paging fields are only supported for channelId, mine, myRecentSubscribers, or mySubscribers lookups"
        )
    if has_id_selector and has_paging:
        raise ValueError(
            "paging fields are only supported for channelId, mine, myRecentSubscribers, or mySubscribers lookups"
        )
    if has_order and not has_collection_selector:
        raise ValueError(
            "order is only supported for channelId, mine, myRecentSubscribers, or mySubscribers lookups"
        )
    if has_id_selector and has_order:
        raise ValueError(
            "order is only supported for channelId, mine, myRecentSubscribers, or mySubscribers lookups"
        )

def _require_subscriptions_insert_body(arguments: dict[str, object]) -> None:
    """Validate the supported `subscriptions.insert` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported create rules.
    """
    part = str(arguments.get("part", "")).strip()
    if part != "snippet":
        raise ValueError("unsupported writable part: only snippet is supported")

    require_mapping_fields("body", required_keys=("snippet",))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    resource_id = snippet.get("resourceId")
    if not isinstance(resource_id, dict):
        raise ValueError("body.snippet.resourceId is required")

    raw_channel_id = resource_id.get("channelId")
    if not isinstance(raw_channel_id, str) or not raw_channel_id.strip():
        raise ValueError("body.snippet.resourceId.channelId is required")

    resource_kind = resource_id.get("kind")
    if resource_kind not in (None, "", "youtube#channel"):
        raise ValueError("body.snippet.resourceId.kind must be youtube#channel when provided")

    unsupported_snippet_fields = [field for field in snippet if field not in {"resourceId"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")

    unsupported_resource_fields = [field for field in resource_id if field not in {"kind", "channelId"}]
    if unsupported_resource_fields:
        raise ValueError(
            f"body.snippet.resourceId.{unsupported_resource_fields[0]} is read-only or unsupported"
        )

def _require_subscriptions_delete_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `subscriptions.delete` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the delete request is incomplete or unsupported.
    """
    raw_subscription_id = arguments.get("id")
    if not isinstance(raw_subscription_id, str) or not raw_subscription_id.strip():
        raise ValueError("id must identify one subscription")

def _subscriptions_insert_target_channel_id(
    arguments: dict[str, object],
    response: dict[str, Any],
) -> str | None:
    """Return the stable target channel identifier for one create response.

    :param arguments: Wrapper arguments used for the request.
    :param response: Successful response payload to normalize.
    :return: Target channel identifier when one is available.
    """
    response_snippet = response.get("snippet")
    if isinstance(response_snippet, dict):
        response_resource_id = response_snippet.get("resourceId")
        if isinstance(response_resource_id, dict):
            channel_id = response_resource_id.get("channelId")
            if isinstance(channel_id, str) and channel_id.strip():
                return channel_id

    body = arguments.get("body")
    if isinstance(body, dict):
        snippet = body.get("snippet")
        if isinstance(snippet, dict):
            resource_id = snippet.get("resourceId")
            if isinstance(resource_id, dict):
                channel_id = resource_id.get("channelId")
                if isinstance(channel_id, str) and channel_id.strip():
                    return channel_id
    return None

def _subscriptions_insert_target_resource_kind(
    arguments: dict[str, object],
    response: dict[str, Any],
) -> str:
    """Return the stable target resource kind for one create response.

    :param arguments: Wrapper arguments used for the request.
    :param response: Successful response payload to normalize.
    :return: Target resource kind with the channel default preserved.
    """
    response_snippet = response.get("snippet")
    if isinstance(response_snippet, dict):
        response_resource_id = response_snippet.get("resourceId")
        if isinstance(response_resource_id, dict):
            resource_kind = response_resource_id.get("kind")
            if isinstance(resource_kind, str) and resource_kind.strip():
                return resource_kind

    body = arguments.get("body")
    if isinstance(body, dict):
        snippet = body.get("snippet")
        if isinstance(snippet, dict):
            resource_id = snippet.get("resourceId")
            if isinstance(resource_id, dict):
                resource_kind = resource_id.get("kind")
                if isinstance(resource_kind, str) and resource_kind.strip():
                    return resource_kind
    return "youtube#channel"

__all__ = [
    "_require_subscriptions_list_arguments",
    "_require_subscriptions_insert_body",
    "_require_subscriptions_delete_arguments",
    "_subscriptions_insert_target_channel_id",
    "_subscriptions_insert_target_resource_kind",
]
