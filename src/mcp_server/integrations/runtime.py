"""Configured live-execution composition for Layer 1 YouTube wrappers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from mcp_server.config import YouTubeLiveRuntimeSettings
from mcp_server.integrations.auth import AuthContext, AuthMode, CredentialBundle
from mcp_server.integrations.executor import IntegrationExecutor, build_observability_hooks
from mcp_server.integrations.oauth import OAuthCredentialProvider, RenewableOAuthToken, build_oauth_credential_provider
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.integrations.youtube import build_youtube_data_api_executor
from mcp_server.observability import InMemoryObservability


class LiveRuntimeConfigurationError(RuntimeError):
    """Represent a safe failure to select configured live credentials.

    :param message: Caller-safe explanation of the missing configuration.
    :param category: Stable safe failure category.
    :param details: Credential-free diagnostic details.
    """

    def __init__(self, message: str, *, category: str, details: dict[str, object]) -> None:
        """Initialize the credential-selection failure.

        :param message: Caller-safe error message.
        :param category: Stable error category for downstream mapping.
        :param details: Credential-free diagnostics.
        """
        super().__init__(message)
        self.category = category
        self.details = details


@dataclass(frozen=True)
class ConfiguredYouTubeRuntime:
    """Store the shared live executor and secret-backed credential availability.

    :param settings: Validated live-runtime configuration.
    :param executor: Shared executor wired to the concrete YouTube transport.
    :param retry_policy: Retry policy applied by the executor.
    """

    settings: YouTubeLiveRuntimeSettings
    executor: IntegrationExecutor
    retry_policy: RetryPolicy
    oauth_provider: OAuthCredentialProvider

    @property
    def timeout_seconds(self) -> float:
        """Return the configured upstream timeout.

        :return: Timeout applied to each upstream request attempt.
        """
        return self.settings.timeout_seconds

    @property
    def oauth_token(self) -> RenewableOAuthToken | None:
        """Return a token-compatible adapter that renews OAuth access on demand.

        :return: String-compatible adapter, or ``None`` when OAuth is unavailable.
        """
        if not self.oauth_provider.is_configured:
            return None
        return RenewableOAuthToken(self.oauth_provider)

    def auth_context_for(self, mode: AuthMode) -> AuthContext:
        """Return the configured credential context for a resolved auth mode.

        :param mode: Resolved endpoint authorization mode.
        :return: Auth context containing only the credential required by ``mode``.
        :raises LiveRuntimeConfigurationError: If the required credential is absent.
        """
        if mode is AuthMode.API_KEY:
            if self.settings.api_key is None:
                raise LiveRuntimeConfigurationError(
                    "YouTube API-key access is not configured.",
                    category="authentication_failed",
                    details={"credential": "YOUTUBE_API_KEY"},
                )
            return AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key=self.settings.api_key),
            )
        if mode is AuthMode.OAUTH_REQUIRED:
            if not self.oauth_provider.is_configured:
                raise LiveRuntimeConfigurationError(
                    "YouTube OAuth access is not configured.",
                    category="authorization_failed",
                    details={"credential": "YOUTUBE_OAUTH_TOKEN"},
                )
            return AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token=self.oauth_token),
            )
        raise LiveRuntimeConfigurationError(
            "A conditional YouTube operation must resolve its authorization mode before execution.",
            category="invalid_request",
            details={"authMode": mode.value},
        )


def build_configured_youtube_runtime(
    settings: YouTubeLiveRuntimeSettings,
    *,
    observability: InMemoryObservability | None = None,
    request_id: str = "layer1-live-runtime",
    opener: Callable[..., Any] | None = None,
    oauth_opener: Callable[..., Any] | None = None,
) -> ConfiguredYouTubeRuntime:
    """Build the configured shared executor for live YouTube requests.

    :param settings: Secret-backed runtime configuration selected at composition time.
    :param observability: Optional sink for safe integration lifecycle events.
    :param request_id: Correlation identifier attached to lifecycle events.
    :param opener: Optional controlled opener for isolated tests or local development.
    :param oauth_opener: Optional controlled opener for OAuth refresh tests.
    :return: Configured runtime with a concrete YouTube transport executor.
    """
    retry_policy = RetryPolicy(max_attempts=settings.max_attempts)
    hooks = build_observability_hooks(observability, request_id=request_id) if observability is not None else None
    executor = build_youtube_data_api_executor(
        opener=opener,
        timeout_seconds=settings.timeout_seconds,
        retry_policy=retry_policy,
        hooks=hooks,
    )
    oauth_provider = build_oauth_credential_provider(
        oauth_token=settings.oauth_token,
        refresh_token=settings.oauth_refresh_token,
        client_id=settings.oauth_client_id,
        client_secret=settings.oauth_client_secret,
        opener=oauth_opener,
        timeout_seconds=settings.timeout_seconds,
    )
    return ConfiguredYouTubeRuntime(
        settings=settings,
        executor=executor,
        retry_policy=retry_policy,
        oauth_provider=oauth_provider,
    )
