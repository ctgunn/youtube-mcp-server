"""Contract tests for additive production-hardening MCP behavior."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.protocol.envelope import error_response_for_category
from mcp_server.security import DEFAULT_BROWSER_EXPOSED_RESPONSE_HEADERS


def test_rate_limited_error_has_only_safe_retry_details():
    """Keep admission rejection protocol-native and credential-free."""
    response = error_response_for_category(
        "rate_limited",
        "Too many requests.",
        request_id="request-1",
        details={"retryable": True, "retryAfterSeconds": 12},
    )

    assert response["error"]["data"] == {
        "category": "rate_limited",
        "retryable": True,
        "retryAfterSeconds": 12,
    }


def test_cache_status_header_is_safely_available_to_browser_clients():
    """Keep cache reuse observability additive and content-free."""
    assert "MCP-Cache-Status" in DEFAULT_BROWSER_EXPOSED_RESPONSE_HEADERS
