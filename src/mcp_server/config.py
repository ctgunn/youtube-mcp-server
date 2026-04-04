"""Runtime configuration and startup validation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
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
