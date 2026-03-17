"""Runtime configuration and startup validation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

SUPPORTED_PROFILES = {"dev", "staging", "prod"}

PROFILE_REQUIREMENTS = {
    "dev": {
        "required_config": ["MCP_ENVIRONMENT"],
        "required_secrets": [],
    },
    "staging": {
        "required_config": ["MCP_ENVIRONMENT"],
        "required_secrets": ["YOUTUBE_API_KEY"],
    },
    "prod": {
        "required_config": ["MCP_ENVIRONMENT"],
        "required_secrets": ["YOUTUBE_API_KEY"],
    },
}


@dataclass(frozen=True)
class ValidationFailure:
    key: str
    reason: str
    is_secret: bool = False


@dataclass(frozen=True)
class StartupValidationResult:
    is_valid: bool
    profile: str
    failures: tuple[ValidationFailure, ...]
    checked_at: str

    @property
    def reason_code(self) -> str | None:
        if self.is_valid:
            return None
        return "CONFIG_VALIDATION_ERROR"


class ConfigValidationError(RuntimeError):
    def __init__(self, result: StartupValidationResult):
        self.result = result
        super().__init__("Required runtime configuration is invalid.")


@dataclass(frozen=True)
class HostedRuntimeSettings:
    host: str
    port: int
    app_module: str
    server_implementation: str
    log_level: str
    reload_enabled: bool
    rollback_command: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _value(env: Mapping[str, str], key: str) -> str | None:
    raw = env.get(key)
    if raw is None:
        return None
    cleaned = str(raw).strip()
    return cleaned or None


def load_hosted_runtime_settings(env: Mapping[str, str]) -> HostedRuntimeSettings:
    port_text = _value(env, "PORT") or "8080"
    log_level = (_value(env, "MCP_SERVER_LOG_LEVEL") or "info").lower()
    reload_enabled = (_value(env, "MCP_SERVER_RELOAD") or "false").lower() in {"1", "true", "yes", "on"}
    return HostedRuntimeSettings(
        host=_value(env, "HOST") or "0.0.0.0",
        port=int(port_text),
        app_module=_value(env, "MCP_ASGI_APP") or "mcp_server.cloud_run_entrypoint:app",
        server_implementation=_value(env, "MCP_SERVER_IMPLEMENTATION") or "uvicorn",
        log_level=log_level,
        reload_enabled=reload_enabled,
        rollback_command="python3 -m mcp_server.cloud_run_entrypoint",
    )


def validate_runtime_config(env: Mapping[str, str]) -> StartupValidationResult:
    failures: list[ValidationFailure] = []
    profile = _value(env, "MCP_ENVIRONMENT") or "unknown"
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

    return StartupValidationResult(
        is_valid=(len(failures) == 0),
        profile=(profile_raw or "unknown"),
        failures=tuple(failures),
        checked_at=_now_iso(),
    )


def ensure_runtime_config(env: Mapping[str, str]) -> StartupValidationResult:
    result = validate_runtime_config(env)
    if not result.is_valid:
        raise ConfigValidationError(result)
    return result


def sanitized_failures(result: StartupValidationResult) -> list[dict]:
    return [{"key": item.key, "reason": item.reason} for item in result.failures]


def config_validation_error_details(result: StartupValidationResult) -> dict:
    return {
        "profile": result.profile,
        "failures": sanitized_failures(result),
    }
