# ruff: noqa: F405
"""Response normalizers for watermarks resources."""

from __future__ import annotations


from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _watermarks_set_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `watermarks.set` response.

    Official quota cost: ``50`` quota units. Successful upstream responses are
    HTTP 204 no-content acknowledgements, so the result preserves target channel
    context and source contract details without exposing credentials or media.

    :param execution: Shared request execution details.
    :return: Lightweight watermark-update acknowledgement.
    """
    return {
        "channelId": _stringify_scalar(execution.arguments.get("channelId")),
        "isSet": True,
        "sourceOperation": execution.metadata.operation_key,
        "sourceQuotaCost": execution.metadata.quota_cost,
        "authPath": "oauth_required",
        "upstreamBodyState": "empty",
    }

def _watermarks_unset_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `watermarks.unset` response.

    Official quota cost: ``50`` quota units. Successful upstream responses are
    HTTP 204 no-content acknowledgements, so the result preserves target channel
    context and source contract details without exposing credentials or media.

    :param execution: Shared request execution details.
    :return: Lightweight watermark-removal acknowledgement.
    """
    return {
        "channelId": _stringify_scalar(execution.arguments.get("channelId")),
        "isUnset": True,
        "sourceOperation": execution.metadata.operation_key,
        "sourceQuotaCost": execution.metadata.quota_cost,
        "authPath": "oauth_required",
        "upstreamBodyState": "empty",
    }

NORMALIZERS = (
    ResponseNormalizer.context_only(
        family_name="watermarks",
        operation_key="watermarks.set",
        handler=_watermarks_set_payload,
    ),
    ResponseNormalizer.context_only(
        family_name="watermarks",
        operation_key="watermarks.unset",
        handler=_watermarks_unset_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_watermarks_set_payload",
    "_watermarks_unset_payload",
]
