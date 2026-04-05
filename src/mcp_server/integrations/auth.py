"""Authentication helpers for internal Layer 1 wrappers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AuthMode(str, Enum):
    """Enumerate supported Layer 1 auth modes."""

    API_KEY = "api_key"
    OAUTH_REQUIRED = "oauth_required"
    CONDITIONAL = "conditional"


@dataclass(frozen=True)
class CredentialBundle:
    """Store credentials available to a wrapper execution.

    :param api_key: API key credential when available.
    :param oauth_token: OAuth token when available.
    """

    api_key: str | None = None
    oauth_token: str | None = None


@dataclass(frozen=True)
class AuthContext:
    """Describe the auth mode and credentials for one wrapper execution.

    :param mode: Auth mode selected for the execution.
    :param credentials: Credentials available to the wrapper.
    :param conditional_reason: Reason for a conditional auth choice.
    """

    mode: AuthMode
    credentials: CredentialBundle
    conditional_reason: str | None = None

    def __post_init__(self) -> None:
        """Validate auth-mode-specific requirements for the execution context."""
        if self.mode is AuthMode.CONDITIONAL and not self.conditional_reason:
            raise ValueError("conditional_reason is required for conditional auth")
        if self.mode is AuthMode.API_KEY and not self.credentials.api_key:
            raise ValueError("api_key credentials are required for api_key mode")
        if self.mode is AuthMode.OAUTH_REQUIRED and not self.credentials.oauth_token:
            raise ValueError("oauth_token credentials are required for oauth_required mode")

    def resolve_credentials(self) -> dict[str, str]:
        """Resolve the credential payload used by the shared executor.

        :return: Sanitized credential fields for internal request execution.
        """
        payload: dict[str, str] = {}
        if self.credentials.api_key:
            payload["apiKey"] = self.credentials.api_key
        if self.credentials.oauth_token:
            payload["oauthToken"] = self.credentials.oauth_token
        if self.conditional_reason:
            payload["conditionalReason"] = self.conditional_reason
        return payload
