# ruff: noqa: F405
"""Response normalizers for captions resources."""

from __future__ import annotations


from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _download_payload(execution: RequestExecution, payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `captions.download` response.

    :param execution: Shared request execution details.
    :param payload: Raw caption body returned by the upstream response.
    :return: Lightweight download result with stable metadata fields.
    """
    return {
        "captionId": _stringify_scalar(execution.arguments.get("id")),
        "content": payload,
        "contentFormat": execution.arguments.get("tfmt"),
        "contentLanguage": execution.arguments.get("tlang"),
        "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
    }

def _delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `captions.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight delete result with stable metadata fields.
    """
    return {
        "captionId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
    }

NORMALIZERS = (
    ResponseNormalizer.context_and_payload(
        family_name="captions",
        operation_key="captions.download",
        handler=_download_payload,
    ),
    ResponseNormalizer.context_only(
        family_name="captions",
        operation_key="captions.delete",
        handler=_delete_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_delete_payload",
    "_download_payload",
]
