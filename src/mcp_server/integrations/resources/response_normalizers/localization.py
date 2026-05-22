# ruff: noqa: F405
"""Response normalizers for localization resources."""

from __future__ import annotations

import json

from mcp_server.integrations.resources.response_normalizers.base import *  # noqa: F403

def _i18n_languages_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for an `i18nLanguages.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed i18n-languages list payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed

def _i18n_regions_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for an `i18nRegions.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed i18n-regions list payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed

NORMALIZERS = (
    ResponseNormalizer.payload_only(
        family_name="localization",
        operation_key="i18nLanguages.list",
        handler=_i18n_languages_list_payload,
    ),
    ResponseNormalizer.payload_only(
        family_name="localization",
        operation_key="i18nRegions.list",
        handler=_i18n_regions_list_payload,
    ),
)

__all__ = [
    "NORMALIZERS",
    "_i18n_languages_list_payload",
    "_i18n_regions_list_payload",
]
