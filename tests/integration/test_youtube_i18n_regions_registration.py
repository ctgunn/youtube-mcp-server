"""Integration tests for registering and invoking ``i18nRegions_list``."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.localization import (
    I18nRegionsListToolError,
    build_i18n_regions_list_tool_descriptor,
)


def _register_i18n_regions_list(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete i18n-regions list tool in a fresh dispatcher."""
    descriptor = build_i18n_regions_list_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_i18n_regions_list_descriptor_registers_as_executable_tool_for_default_lookup():
    """Register and execute ``i18nRegions_list`` for a default lookup."""
    dispatcher = _register_i18n_regions_list()

    result = dispatcher.call_tool("i18nRegions_list", {"part": "snippet"})

    assert result["endpoint"] == "i18nRegions.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet"]
    assert result["availability"] == {"state": "active"}
    assert result["items"][0]["id"] == "US"


def test_i18n_regions_list_descriptor_registers_as_executable_tool_for_display_language_lookup():
    """Register and execute ``i18nRegions_list`` for a display-language lookup."""
    dispatcher = _register_i18n_regions_list()

    result = dispatcher.call_tool("i18nRegions_list", {"part": "snippet", "hl": "es"})

    assert result["localization"] == {"hl": "es"}


def test_i18n_regions_list_dispatcher_surfaces_validation_failure():
    """Reject invalid dispatcher calls with the concrete tool error."""
    dispatcher = _register_i18n_regions_list()

    with pytest.raises((I18nRegionsListToolError, ValueError), match="part|required combinations") as exc_info:
        dispatcher.call_tool("i18nRegions_list", {"part": "id"})

    if isinstance(exc_info.value, I18nRegionsListToolError):
        assert exc_info.value.category == "invalid_request"
        assert exc_info.value.details["field"] == "part"


def test_i18n_regions_list_dispatcher_surfaces_safe_upstream_error():
    """Expose safe upstream failure categories through dispatcher execution."""
    class FailingWrapper:
        """Raise one normalized upstream error from the registered descriptor."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a fake upstream quota error.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: API-key auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError(
                "quota exhausted",
                category="rate_limit",
                retryable=False,
                details={"reason": "quotaExceeded", "apiKey": "secret", "stackTrace": "traceback"},
            )

    dispatcher = _register_i18n_regions_list(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(I18nRegionsListToolError) as exc_info:
        dispatcher.call_tool("i18nRegions_list", {"part": "snippet"})

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"reason": "quotaExceeded"}
