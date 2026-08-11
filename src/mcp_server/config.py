"""Runtime configuration and startup validation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Mapping

from mcp_server.security import HostedSecuritySettings, parse_allowed_origins

SUPPORTED_PROFILES = {"dev", "staging", "prod"}

PROFILE_REQUIREMENTS = {
    "dev": {
        "required_config": ["MCP_ENVIRONMENT"],
        "required_secrets": [],
    },
    "staging": {
        "required_config": ["MCP_ENVIRONMENT"],
        "required_secrets": ["YOUTUBE_API_KEY", "MCP_AUTH_TOKEN"],
    },
    "prod": {
        "required_config": ["MCP_ENVIRONMENT"],
        "required_secrets": ["YOUTUBE_API_KEY", "MCP_AUTH_TOKEN"],
    },
}


@dataclass(frozen=True)
class ValidationFailure:
    """Describe one failed startup configuration check."""

    key: str
    reason: str
    is_secret: bool = False


@dataclass(frozen=True)
class StartupValidationResult:
    """Capture the full outcome of startup configuration validation."""

    is_valid: bool
    profile: str
    failures: tuple[ValidationFailure, ...]
    checked_at: str

    @property
    def reason_code(self) -> str | None:
        """Return the readiness reason code for invalid configurations."""
        if self.is_valid:
            return None
        return "CONFIG_VALIDATION_ERROR"


class ConfigValidationError(RuntimeError):
    """Raised when required runtime configuration is missing or invalid."""

    def __init__(self, result: StartupValidationResult):
        self.result = result
        super().__init__("Required runtime configuration is invalid.")


@dataclass(frozen=True)
class YouTubeLiveRuntimeSettings:
    """Store secret-backed settings for configured Layer 1 live execution.

    :param api_key: Optional YouTube API-key credential.
    :param oauth_token: Optional YouTube OAuth access token.
    :param timeout_seconds: Timeout applied to one upstream request attempt.
    :param max_attempts: Maximum shared-executor attempts for one request.
    """

    api_key: str | None
    oauth_token: str | None
    oauth_refresh_token: str | None = None
    oauth_client_id: str | None = None
    oauth_client_secret: str | None = None
    transcript_language: str | None = None
    transcript_language_error: str | None = None
    timeout_seconds: float = 10.0
    max_attempts: int = 3

    @property
    def has_api_key(self) -> bool:
        """Return whether a nonblank API-key credential is available.

        :return: ``True`` when API-key access can be selected.
        """
        return self.api_key is not None

    @property
    def has_oauth_token(self) -> bool:
        """Return whether a static or renewable OAuth credential is available.

        :return: ``True`` when OAuth-required access can be selected.
        """
        return self.oauth_token is not None or self.has_oauth_refresh_configuration

    @property
    def has_oauth_refresh_configuration(self) -> bool:
        """Return whether a complete Google OAuth refresh grant is configured.

        :return: ``True`` when the runtime can renew an expiring access token.
        """
        return all((self.oauth_refresh_token, self.oauth_client_id, self.oauth_client_secret))

    def safe_details(self) -> dict[str, object]:
        """Return a credential-free description of available runtime settings.

        :return: Safe diagnostics containing configuration state but no secrets.
        """
        details = {
            "apiKeyConfigured": self.has_api_key,
            "oauthTokenConfigured": self.has_oauth_token,
            "oauthLifecycle": "refreshable" if self.has_oauth_refresh_configuration else ("static" if self.oauth_token else "notConfigured"),
            "timeoutSeconds": self.timeout_seconds,
            "maxAttempts": self.max_attempts,
        }
        if self.transcript_language is not None or self.transcript_language_error is not None:
            details["transcriptLanguage"] = self.transcript_language or "invalid"
        return details


def load_youtube_live_runtime_settings(env: Mapping[str, str]) -> YouTubeLiveRuntimeSettings:
    """Load secret-backed Layer 1 live-execution settings from an environment.

    Blank credential values are treated as unavailable so configured callers can
    return a safe failure instead of accidentally using representative data.

    :param env: Environment mapping to read without mutating process state.
    :return: Normalized settings with default timeout and retry-attempt values.
    """
    transcript_language, transcript_language_error = _transcript_language_setting(env.get("YOUTUBE_TRANSCRIPT_LANG"))
    return YouTubeLiveRuntimeSettings(
        api_key=_optional_secret(env.get("YOUTUBE_API_KEY")),
        oauth_token=_optional_secret(env.get("YOUTUBE_OAUTH_TOKEN")),
        oauth_refresh_token=_optional_secret(env.get("YOUTUBE_OAUTH_REFRESH_TOKEN")),
        oauth_client_id=_optional_secret(env.get("YOUTUBE_OAUTH_CLIENT_ID")),
        oauth_client_secret=_optional_secret(env.get("YOUTUBE_OAUTH_CLIENT_SECRET")),
        transcript_language=transcript_language,
        transcript_language_error=transcript_language_error,
    )


def youtube_capability_readiness(settings: YouTubeLiveRuntimeSettings) -> dict[str, str]:
    """Describe configured YouTube capability without exposing credentials.

    :param settings: Normalized live-execution settings for the runtime.
    :return: Stable API-key and OAuth capability states for readiness reporting.
    """
    return {
        "apiKeyRead": "available" if settings.has_api_key else "not_configured",
        "oauthOwnerAndMutation": "available" if settings.has_oauth_token else "not_configured",
        "oauthLifecycle": "refreshable" if settings.has_oauth_refresh_configuration else (
            "static" if settings.oauth_token else "not_configured"
        ),
    }


def _optional_secret(value: str | None) -> str | None:
    """Normalize a secret value without returning blank credentials.

    :param value: Candidate secret value from runtime configuration.
    :return: Stripped secret value when nonblank, otherwise ``None``.
    """
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _transcript_language_setting(value: str | None) -> tuple[str | None, str | None]:
    """Normalize a non-secret configured transcript language.

    :param value: Candidate ``YOUTUBE_TRANSCRIPT_LANG`` value.
    :return: Normalized BCP-47 language tag and an optional safe error category.
    """
    if not isinstance(value, str) or not value.strip():
        return None, None
    normalized = value.strip()
    if not re.fullmatch(r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*", normalized):
        return None, "invalid_language"
    pieces = normalized.split("-")
    canonical = [pieces[0].lower()]
    for piece in pieces[1:]:
        canonical.append(piece.upper() if len(piece) == 2 else piece.title() if len(piece) == 4 else piece.lower())
    return "-".join(canonical), None


@dataclass(frozen=True)
class HostedRuntimeSettings:
    """Normalized hosted runtime settings derived from environment variables."""

    host: str
    port: int
    app_module: str
    server_implementation: str
    log_level: str
    reload_enabled: bool
    rollback_command: str
    environment: str
    secret_access_mode: str
    secret_reference_names: tuple[str, ...]
    security: HostedSecuritySettings
    session: "HostedSessionSettings"


@dataclass(frozen=True)
class HostedSessionSettings:
    """Session durability settings for hosted MCP transport behavior."""

    backend: str
    store_url: str | None
    durability_required: bool
    session_ttl_seconds: int
    replay_ttl_seconds: int
    connectivity_model: str = "local_process"


def _now_iso() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _value(env: Mapping[str, str], key: str) -> str | None:
    """Return a stripped environment value or ``None`` when blank."""
    raw = env.get(key)
    if raw is None:
        return None
    cleaned = str(raw).strip()
    return cleaned or None


def _bool_value(env: Mapping[str, str], key: str, default: bool) -> bool:
    """Parse a boolean-like environment value."""
    raw = _value(env, key)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


def _csv_values(env: Mapping[str, str], key: str) -> tuple[str, ...]:
    """Parse a comma-separated environment variable into individual values."""
    raw = _value(env, key)
    if raw is None:
        return ()
    return tuple(item for item in (part.strip() for part in raw.split(",")) if item)


def load_hosted_runtime_settings(env: Mapping[str, str]) -> HostedRuntimeSettings:
    """Load normalized hosted runtime settings from environment values.

    :param env: Environment-style mapping with runtime settings.
    :return: Hosted runtime settings object.
    """
    port_text = _value(env, "PORT") or "8080"
    log_level = (_value(env, "MCP_SERVER_LOG_LEVEL") or "info").lower()
    reload_enabled = (_value(env, "MCP_SERVER_RELOAD") or "false").lower() in {"1", "true", "yes", "on"}
    environment = _value(env, "MCP_ENVIRONMENT") or "dev"
    auth_token = _value(env, "MCP_AUTH_TOKEN")
    auth_required = _bool_value(env, "MCP_AUTH_REQUIRED", default=(environment in {"staging", "prod"} or auth_token is not None))
    secret_reference_names = _csv_values(env, "MCP_SECRET_REFERENCE_NAMES")
    secret_access_mode = (_value(env, "MCP_SECRET_ACCESS_MODE") or ("secret_manager_env" if secret_reference_names else "env_only")).lower()
    session_store_url = _value(env, "MCP_SESSION_STORE_URL")
    session_backend = (_value(env, "MCP_SESSION_BACKEND") or ("redis" if session_store_url and session_store_url.startswith("redis") else "memory")).lower()
    session_connectivity_model = (_value(env, "MCP_SESSION_CONNECTIVITY_MODEL") or ("serverless_vpc_connector" if session_backend == "redis" else "local_process")).lower()
    session_durability_required = _bool_value(env, "MCP_SESSION_DURABILITY_REQUIRED", default=False)
    session_ttl_seconds = int(_value(env, "MCP_SESSION_TTL_SECONDS") or "1800")
    replay_ttl_seconds = int(_value(env, "MCP_SESSION_REPLAY_TTL_SECONDS") or "300")
    return HostedRuntimeSettings(
        host=_value(env, "HOST") or "0.0.0.0",
        port=int(port_text),
        app_module=_value(env, "MCP_ASGI_APP") or "mcp_server.cloud_run_entrypoint:app",
        server_implementation=_value(env, "MCP_SERVER_IMPLEMENTATION") or "uvicorn",
        log_level=log_level,
        reload_enabled=reload_enabled,
        rollback_command="python3 -m mcp_server.cloud_run_entrypoint",
        environment=environment,
        secret_access_mode=secret_access_mode,
        secret_reference_names=secret_reference_names,
        security=HostedSecuritySettings(
            auth_required=auth_required,
            auth_token=auth_token,
            allowed_origins=parse_allowed_origins(_value(env, "MCP_ALLOWED_ORIGINS")),
            allow_originless_clients=_bool_value(env, "MCP_ALLOW_ORIGINLESS_CLIENTS", default=True),
        ),
        session=HostedSessionSettings(
            backend=session_backend,
            store_url=session_store_url,
            connectivity_model=session_connectivity_model,
            durability_required=session_durability_required,
            session_ttl_seconds=session_ttl_seconds,
            replay_ttl_seconds=replay_ttl_seconds,
        ),
    )


def validate_runtime_config(env: Mapping[str, str]) -> StartupValidationResult:
    """Validate required runtime configuration for the selected profile.

    :param env: Environment-style mapping to validate.
    :return: Validation result including all collected failures.
    """
    failures: list[ValidationFailure] = []
    profile_raw = _value(env, "MCP_ENVIRONMENT")

    if not profile_raw:
        failures.append(ValidationFailure("MCP_ENVIRONMENT", "missing required value"))
    elif profile_raw not in SUPPORTED_PROFILES:
        failures.append(ValidationFailure("MCP_ENVIRONMENT", "unsupported value"))

    requirements = PROFILE_REQUIREMENTS.get(profile_raw or "", {"required_config": [], "required_secrets": []})
    for key in requirements["required_config"]:
        if not _value(env, key):
            failures.append(ValidationFailure(key, "missing required value"))

    for key in requirements["required_secrets"]:
        if not _value(env, key):
            failures.append(ValidationFailure(key, "missing required secret", is_secret=True))

    if _value(env, "MCP_ALLOWED_ORIGINS") and not parse_allowed_origins(_value(env, "MCP_ALLOWED_ORIGINS")):
        failures.append(ValidationFailure("MCP_ALLOWED_ORIGINS", "must contain one or more valid absolute origins"))
    session_backend = (_value(env, "MCP_SESSION_BACKEND") or ("redis" if (_value(env, "MCP_SESSION_STORE_URL") or "").startswith("redis") else "memory")).lower()
    if session_backend not in {"memory", "redis"}:
        failures.append(ValidationFailure("MCP_SESSION_BACKEND", "must be one of memory or redis"))
    for key in ("MCP_SESSION_TTL_SECONDS", "MCP_SESSION_REPLAY_TTL_SECONDS"):
        value = _value(env, key)
        if value is None:
            continue
        try:
            if int(value) <= 0:
                failures.append(ValidationFailure(key, "must be a positive integer"))
        except ValueError:
            failures.append(ValidationFailure(key, "must be a positive integer"))

    return StartupValidationResult(
        is_valid=(len(failures) == 0),
        profile=(profile_raw or "unknown"),
        failures=tuple(failures),
        checked_at=_now_iso(),
    )


def ensure_runtime_config(env: Mapping[str, str]) -> StartupValidationResult:
    """Validate configuration and raise when it is not usable."""
    result = validate_runtime_config(env)
    if not result.is_valid:
        raise ConfigValidationError(result)
    return result


def sanitized_failures(result: StartupValidationResult) -> list[dict]:
    """Return failure details without secret markers or sensitive values."""
    return [{"key": item.key, "reason": item.reason} for item in result.failures]


def config_validation_error_details(result: StartupValidationResult) -> dict:
    """Build structured error details for invalid startup configuration."""
    return {
        "profile": result.profile,
        "failures": sanitized_failures(result),
    }


def secret_access_readiness(env: Mapping[str, str], validation: StartupValidationResult) -> dict[str, object]:
    """Summarize whether secret-backed configuration is ready for use.

    :param env: Environment-style mapping for secret settings.
    :param validation: Startup validation result for the current runtime.
    :return: Structured readiness payload for secret access.
    """
    secret_failures = tuple(item for item in validation.failures if item.is_secret)
    reference_names = _csv_values(env, "MCP_SECRET_REFERENCE_NAMES")
    explicit_access_mode = _value(env, "MCP_SECRET_ACCESS_MODE")
    access_mode = (explicit_access_mode or ("secret_manager_env" if reference_names else "env_only")).lower()
    if not secret_failures:
        return {
            "available": True,
            "mode": access_mode,
            "references": list(reference_names),
            "reason": None,
        }

    # Preserve the legacy readiness contract unless hosted secret wiring has been
    # declared explicitly for this runtime.
    if access_mode == "env_only" and not reference_names and explicit_access_mode is None:
        return {
            "available": False,
            "mode": access_mode,
            "references": [],
            "reason": {
                "code": "CONFIG_VALIDATION_ERROR",
                "message": "Required configuration is invalid or incomplete.",
            },
        }

    missing_keys = sorted(item.key for item in secret_failures)
    missing_references = sorted(key for key in missing_keys if key not in reference_names)
    if missing_references or not reference_names:
        return {
            "available": False,
            "mode": access_mode,
            "references": list(reference_names),
            "reason": {
                "code": "SECRET_REFERENCE_MISSING",
                "message": "Required secret references are missing from the hosted runtime configuration.",
                "details": {"missingReferences": missing_references or missing_keys},
            },
        }

    return {
        "available": False,
        "mode": access_mode,
        "references": list(reference_names),
        "reason": {
            "code": "SECRET_ACCESS_UNAVAILABLE",
            "message": "Required secret-backed configuration is not accessible to the hosted runtime.",
            "details": {"missingSecrets": missing_keys},
        },
    }
