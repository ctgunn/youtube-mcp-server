"""Opt-in real YouTube Data API smoke test.

This check deliberately remains disabled unless an operator supplies a real
credential and explicitly enables it. It performs no mutation.
"""

from __future__ import annotations

import os

import pytest

from mcp_server.app import create_app


@pytest.mark.skipif(
    os.environ.get("RUN_YOUTUBE_LIVE_SMOKE") != "1",
    reason="set RUN_YOUTUBE_LIVE_SMOKE=1 with a real API key to run live YouTube verification",
)
def test_i18n_languages_uses_the_live_youtube_data_api() -> None:
    """Call a public read-only endpoint with the operator-provided API key."""
    if not os.environ.get("YOUTUBE_API_KEY", "").strip():
        pytest.fail("YOUTUBE_API_KEY is required when RUN_YOUTUBE_LIVE_SMOKE=1")

    app = create_app(env={**os.environ, "MCP_ENVIRONMENT": os.environ.get("MCP_ENVIRONMENT", "dev")})
    result = app.dispatcher.call_tool("i18nLanguages_list", {"part": "snippet"})

    assert isinstance(result, dict)
    assert isinstance(result.get("items"), list)
