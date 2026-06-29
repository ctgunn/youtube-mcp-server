"""Integration tests for registering concrete Layer 2 ``guideCategories`` tools."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.guide_categories import (
    GuideCategoriesListToolError,
    build_guide_categories_list_tool_descriptor,
)


def _register_guide_categories_list(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete guide-categories list tool in a fresh dispatcher."""
    descriptor = build_guide_categories_list_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_guide_categories_list_descriptor_registers_as_executable_tool_for_region_lookup():
    """Register and execute ``guideCategories_list`` for a region lookup."""
    dispatcher = _register_guide_categories_list()

    result = dispatcher.call_tool("guideCategories_list", {"part": "snippet", "regionCode": "US"})

    assert result["endpoint"] == "guideCategories.list"
    assert result["quotaCost"] == 1
    assert result["selector"] == {"mode": "regionCode", "regionCode": "US"}
    assert result["availability"] == {"state": "deprecated"}
    assert result["items"][0]["id"] == "guide-category-123"


def test_guide_categories_list_descriptor_registers_as_executable_tool_for_id_lookup():
    """Register and execute ``guideCategories_list`` for an ID lookup."""
    dispatcher = _register_guide_categories_list()

    result = dispatcher.call_tool(
        "guideCategories_list",
        {"part": "snippet", "id": "GCQmVzdCBvZiBZb3VUdWJl", "hl": "es"},
    )

    assert result["selector"] == {"mode": "id", "id": ["GCQmVzdCBvZiBZb3VUdWJl"]}
    assert result["localization"] == {"hl": "es"}


def test_guide_categories_list_dispatcher_surfaces_validation_failure():
    """Reject invalid dispatcher calls with the concrete tool error."""
    dispatcher = _register_guide_categories_list()

    with pytest.raises((GuideCategoriesListToolError, ValueError), match="selector|required combinations") as exc_info:
        dispatcher.call_tool("guideCategories_list", {"part": "snippet"})

    if isinstance(exc_info.value, GuideCategoriesListToolError):
        assert exc_info.value.category == "invalid_request"
        assert exc_info.value.details["field"] == "selector"


def test_guide_categories_list_dispatcher_surfaces_safe_upstream_error():
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

    dispatcher = _register_guide_categories_list(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(GuideCategoriesListToolError) as exc_info:
        dispatcher.call_tool("guideCategories_list", {"part": "snippet", "regionCode": "US"})

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"reason": "quotaExceeded"}
