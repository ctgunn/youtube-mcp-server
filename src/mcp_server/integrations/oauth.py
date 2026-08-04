"""Renewable OAuth credential support for live YouTube execution."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

GOOGLE_OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"


class OAuthCredentialRefreshError(RuntimeError):
    """Represent a credential-safe OAuth token refresh failure.

    :param message: Safe explanation for the failed credential lifecycle step.
    :param category: Stable downstream error category.
    """

    def __init__(self, message: str, *, category: str = "authentication_failed") -> None:
        """Initialize the safe OAuth refresh failure.

        :param message: Credential-free failure message.
        :param category: Stable downstream error category.
        """
        super().__init__(message)
        self.category = category


class OAuthCredentialProvider:
    """Resolve a static or refreshable OAuth access token on demand."""

    def __init__(
        self,
        *,
        oauth_token: str | None,
        refresh_token: str | None,
        client_id: str | None,
        client_secret: str | None,
        opener: Callable[..., Any] | None = None,
        timeout_seconds: float = 10.0,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        """Initialize one OAuth credential provider.

        :param oauth_token: Explicit static access token for local development.
        :param refresh_token: OAuth refresh token for hosted renewal.
        :param client_id: Google OAuth client identifier.
        :param client_secret: Google OAuth client secret.
        :param opener: Optional controlled HTTP opener for tests.
        :param timeout_seconds: Timeout for token refresh requests.
        :param now: Optional clock for cache-expiration tests.
        """
        self._oauth_token = oauth_token
        self._refresh_token = refresh_token
        self._client_id = client_id
        self._client_secret = client_secret
        self._opener = opener or urlopen
        self._timeout_seconds = timeout_seconds
        self._now = now or (lambda: datetime.now(timezone.utc))
        self._cached_access_token: str | None = None
        self._expires_at: datetime | None = None

    @property
    def is_configured(self) -> bool:
        """Return whether static or complete refresh credentials are available.

        :return: ``True`` when the provider can resolve an access token.
        """
        return bool(self._oauth_token) or self.has_refresh_configuration

    @property
    def has_refresh_configuration(self) -> bool:
        """Return whether all refresh-grant credentials are available.

        :return: ``True`` when token refresh can be requested from Google.
        """
        return bool(self._refresh_token and self._client_id and self._client_secret)

    @property
    def lifecycle_mode(self) -> str:
        """Return the configured OAuth credential lifecycle mode.

        :return: ``refreshable``, ``static``, or ``not_configured``.
        """
        if self.has_refresh_configuration:
            return "refreshable"
        if self._oauth_token:
            return "static"
        return "not_configured"

    def access_token(self) -> str:
        """Return a valid access token, refreshing it when necessary.

        :return: OAuth bearer token suitable for one upstream request.
        :raises OAuthCredentialRefreshError: If no usable credential is configured.
        """
        if self._oauth_token:
            return self._oauth_token
        if not self.has_refresh_configuration:
            raise OAuthCredentialRefreshError("YouTube OAuth renewal is not configured.")
        if self._cached_access_token and self._expires_at and self._expires_at > self._now() + timedelta(seconds=60):
            return self._cached_access_token
        return self._refresh_access_token()

    def _refresh_access_token(self) -> str:
        """Exchange the configured refresh token for a fresh access token.

        :return: Fresh OAuth access token.
        :raises OAuthCredentialRefreshError: If Google rejects or malforms the token response.
        """
        body = urlencode(
            {
                "client_id": self._client_id or "",
                "client_secret": self._client_secret or "",
                "refresh_token": self._refresh_token or "",
                "grant_type": "refresh_token",
            }
        ).encode("utf-8")
        request = Request(
            GOOGLE_OAUTH_TOKEN_URL,
            data=body,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        )
        try:
            with self._opener(request, timeout=self._timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as error:
            raise OAuthCredentialRefreshError("YouTube OAuth token renewal failed.") from error
        access_token = payload.get("access_token") if isinstance(payload, dict) else None
        expires_in = payload.get("expires_in") if isinstance(payload, dict) else None
        if not isinstance(access_token, str) or not access_token.strip():
            raise OAuthCredentialRefreshError("YouTube OAuth token renewal returned no access token.")
        try:
            lifetime_seconds = max(int(expires_in), 1)
        except (TypeError, ValueError):
            lifetime_seconds = 300
        self._cached_access_token = access_token.strip()
        self._expires_at = self._now() + timedelta(seconds=lifetime_seconds)
        return self._cached_access_token


class RenewableOAuthToken(str):
    """Present an on-demand OAuth credential through legacy string token seams."""

    def __new__(cls, provider: OAuthCredentialProvider):
        """Create a non-secret truthy sentinel for legacy token checks.

        :param provider: Credential provider used to resolve actual access tokens.
        :return: String-compatible OAuth token adapter.
        """
        instance = super().__new__(cls, "configured-renewable-oauth-token")
        instance._provider = provider
        return instance

    def __str__(self) -> str:
        """Resolve the current access token when the adapter is stringified.

        :return: Current OAuth access token.
        """
        return self._provider.access_token()

    def __format__(self, format_spec: str) -> str:
        """Resolve the current token for formatted Authorization header output.

        :param format_spec: Standard string format specification.
        :return: Formatted current access token.
        """
        return format(str(self), format_spec)

    def strip(self, chars: str | None = None) -> str:
        """Resolve then strip the current token for legacy validation helpers.

        :param chars: Optional characters removed by ``str.strip``.
        :return: Stripped current access token.
        """
        return str(self).strip(chars)


def build_oauth_credential_provider(
    *,
    oauth_token: str | None,
    refresh_token: str | None,
    client_id: str | None,
    client_secret: str | None,
    opener: Callable[..., Any] | None = None,
    timeout_seconds: float = 10.0,
    now: Callable[[], datetime] | None = None,
) -> OAuthCredentialProvider:
    """Build the OAuth provider used by configured YouTube runtime composition.

    :param oauth_token: Optional static access token.
    :param refresh_token: Optional OAuth refresh token.
    :param client_id: Optional Google OAuth client identifier.
    :param client_secret: Optional Google OAuth client secret.
    :param opener: Optional controlled token HTTP opener.
    :param timeout_seconds: Timeout for refresh requests.
    :param now: Optional clock for expiration handling.
    :return: Configured OAuth credential provider.
    """
    return OAuthCredentialProvider(
        oauth_token=oauth_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        opener=opener,
        timeout_seconds=timeout_seconds,
        now=now,
    )
