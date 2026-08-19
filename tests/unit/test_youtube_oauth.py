"""Tests for renewable YouTube OAuth credentials."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime, timedelta

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.config import load_youtube_live_runtime_settings
from mcp_server.integrations.oauth import (
    OAuthCredentialRefreshError,
    RenewableOAuthToken,
    build_oauth_credential_provider,
)
from mcp_server.integrations.runtime import build_configured_youtube_runtime
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class _FakeHTTPResponse:
    """Represent a controlled OAuth token-endpoint response."""

    def __init__(self, payload: dict[str, object]) -> None:
        """Serialize one response payload for the token opener.

        :param payload: JSON-compatible OAuth token response.
        """
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        """Return the serialized controlled response body.

        :return: UTF-8 JSON response bytes.
        """
        return self._payload

    def __enter__(self):
        """Enter the controlled response context.

        :return: This response.
        """
        return self

    def __exit__(self, exc_type, exc, tb):
        """Exit the controlled response context without suppressing errors.

        :param exc_type: Exception type, if any.
        :param exc: Exception instance, if any.
        :param tb: Exception traceback, if any.
        :return: ``False`` to preserve exceptions.
        """
        return False


def test_refreshable_oauth_token_uses_google_refresh_grant_and_caches_response():
    """Refresh an access token once and reuse it until its safety window expires."""
    captured = []
    now = datetime(2026, 8, 3, tzinfo=UTC)
    provider = build_oauth_credential_provider(
        oauth_token=None,
        refresh_token="refresh-secret",
        client_id="client-id",
        client_secret="client-secret",
        opener=lambda request, timeout: captured.append((request, timeout))
        or _FakeHTTPResponse({"access_token": "fresh-access-token", "expires_in": 3600}),
        now=lambda: now,
    )

    token = RenewableOAuthToken(provider)

    assert str(token) == "fresh-access-token"
    assert token.strip() == "fresh-access-token"
    assert str(token) == "fresh-access-token"
    assert len(captured) == 1
    assert captured[0][0].full_url == "https://oauth2.googleapis.com/token"
    assert b"grant_type=refresh_token" in captured[0][0].data
    assert b"refresh_token=refresh-secret" in captured[0][0].data
    assert b"client_secret=client-secret" in captured[0][0].data
    assert captured[0][1] == 10.0


def test_refreshable_oauth_token_replaces_expired_cached_access_token():
    """Obtain a second access token after the cached token has expired."""
    clock = [datetime(2026, 8, 3, tzinfo=UTC)]
    responses = iter((
        {"access_token": "first-access-token", "expires_in": 120},
        {"access_token": "second-access-token", "expires_in": 120},
    ))
    provider = build_oauth_credential_provider(
        oauth_token=None,
        refresh_token="refresh-secret",
        client_id="client-id",
        client_secret="client-secret",
        opener=lambda _request, timeout: _FakeHTTPResponse(next(responses)),
        now=lambda: clock[0],
    )

    assert provider.access_token() == "first-access-token"
    clock[0] += timedelta(seconds=90)
    assert provider.access_token() == "second-access-token"


def test_static_oauth_token_remains_supported_for_deliberate_local_development():
    """Preserve explicit static-token injection while exposing its lifecycle mode."""
    provider = build_oauth_credential_provider(
        oauth_token="local-access-token",
        refresh_token=None,
        client_id=None,
        client_secret=None,
    )

    assert provider.access_token() == "local-access-token"
    assert provider.lifecycle_mode == "static"


def test_incomplete_refresh_configuration_fails_without_leaking_secrets():
    """Reject incomplete refresh credentials before issuing a token request."""
    provider = build_oauth_credential_provider(
        oauth_token=None,
        refresh_token="refresh-secret",
        client_id="client-id",
        client_secret=None,
    )

    try:
        provider.access_token()
    except OAuthCredentialRefreshError as error:
        assert error.category == "authentication_failed"
        assert "refresh-secret" not in str(error)
    else:  # pragma: no cover - assertion guard
        raise AssertionError("expected OAuthCredentialRefreshError")


def test_configured_dispatcher_uses_refreshed_oauth_token_for_an_upstream_tool_call():
    """Resolve a fresh token through the existing OAuth descriptor seam."""
    oauth_requests = []
    youtube_requests = []
    runtime = build_configured_youtube_runtime(
        load_youtube_live_runtime_settings(
            {
                "YOUTUBE_OAUTH_REFRESH_TOKEN": "refresh-secret",
                "YOUTUBE_OAUTH_CLIENT_ID": "client-id",
                "YOUTUBE_OAUTH_CLIENT_SECRET": "client-secret",
            }
        ),
        opener=lambda request, timeout: youtube_requests.append((request, timeout))
        or _FakeHTTPResponse({"items": [{"id": "subscription-123"}]}),
        oauth_opener=lambda request, timeout: oauth_requests.append((request, timeout))
        or _FakeHTTPResponse({"access_token": "fresh-access-token", "expires_in": 3600}),
    )

    result = InMemoryToolDispatcher(youtube_runtime=runtime).call_tool(
        "subscriptions_insert",
        {"part": "snippet", "body": {"snippet": {"resourceId": {"channelId": "UC123"}}}},
    )

    assert "subscription-123" in str(result)
    assert len(oauth_requests) == 1
    assert len(youtube_requests) == 1
    assert youtube_requests[0][0].headers.get("Authorization") == "Bearer fresh-access-token"
