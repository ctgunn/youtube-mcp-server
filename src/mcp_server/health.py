"""Liveness and readiness payload helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from mcp_server.config import StartupValidationResult


def _now_iso() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RuntimeLifecycleState:
    """Track the runtime readiness and shutdown lifecycle for hosted execution."""

    state: str = "starting"
    started_at: str = field(default_factory=_now_iso)
    ready_at: str | None = None
    stopped_at: str | None = None
    degraded_reason: dict | None = None
    accepting_traffic: bool = False
    health_visible: bool = True

    def mark_ready(self) -> None:
        """Mark the runtime as ready to accept traffic."""
        self.state = "ready"
        self.ready_at = _now_iso()
        self.degraded_reason = None
        self.accepting_traffic = True

    def mark_degraded(self, reason: dict | None = None) -> None:
        """Mark the runtime as degraded with an optional readiness reason.

        :param reason: Structured readiness failure payload.
        """
        self.state = "degraded"
        self.degraded_reason = reason
        self.accepting_traffic = False

    def mark_stopping(self) -> None:
        """Mark the runtime as beginning shutdown."""
        self.state = "stopping"
        self.accepting_traffic = False

    def mark_stopped(self) -> None:
        """Mark the runtime as fully stopped and hide health visibility."""
        self.state = "stopped"
        self.stopped_at = _now_iso()
        self.accepting_traffic = False
        self.health_visible = False


def initialize_runtime_lifecycle(validation: StartupValidationResult) -> RuntimeLifecycleState:
    """Create lifecycle state from startup validation.

    :param validation: Startup validation result for the current environment.
    :return: Initialized lifecycle state.
    """
    lifecycle = RuntimeLifecycleState()
    if validation.is_valid:
        lifecycle.mark_ready()
    else:
        lifecycle.mark_degraded(
            {
                "code": "CONFIG_VALIDATION_ERROR",
                "message": "Required configuration is invalid or incomplete.",
            }
        )
    return lifecycle


def health_payload(lifecycle: RuntimeLifecycleState | None = None) -> dict:
    """Build the liveness response payload.

    :param lifecycle: Unused lifecycle state placeholder kept for symmetry.
    :return: Minimal health payload.
    """
    return {"status": "ok"}


def readiness_payload(
    validation: StartupValidationResult,
    lifecycle: RuntimeLifecycleState | None = None,
    secret_access: dict | None = None,
    session_durability: dict | None = None,
) -> dict:
    """Build the readiness payload for hosted probes.

    :param validation: Startup validation result for the current runtime.
    :param lifecycle: Optional lifecycle state tracking runtime readiness.
    :param secret_access: Optional secret-access readiness details.
    :param session_durability: Optional durable-session readiness details.
    :return: Structured readiness response.
    """
    lifecycle_state = lifecycle.state if lifecycle is not None else ("ready" if validation.is_valid else "degraded")
    secret_ok = True if secret_access is None else bool(secret_access.get("available", validation.is_valid))
    session_ok = True if session_durability is None else bool(session_durability.get("available", True))
    if validation.is_valid and lifecycle_state == "ready" and secret_ok and session_ok:
        return {
            "status": "ready",
            "checks": {
                "configuration": "pass",
                "secrets": "pass",
                "runtime": "pass",
                "sessionDurability": "pass" if session_ok else "fail",
            },
        }
    reason = lifecycle.degraded_reason if lifecycle and lifecycle.degraded_reason else {
        "code": "CONFIG_VALIDATION_ERROR",
        "message": "Required configuration is invalid or incomplete.",
    }
    if secret_access and not secret_ok:
        reason = secret_access.get("reason") or {
            "code": "SECRET_ACCESS_UNAVAILABLE",
            "message": "Required secret-backed configuration is not accessible.",
        }
    if session_durability and not session_ok:
        reason = session_durability.get("reason") or {
            "code": "SESSION_DURABILITY_UNAVAILABLE",
            "message": "Durable hosted sessions are not available.",
        }
    return {
        "status": "not_ready",
        "checks": {
            "configuration": "pass" if validation.is_valid else "fail",
            "secrets": "pass" if secret_ok else "fail",
            "runtime": "pass" if lifecycle_state == "ready" else "fail",
            "sessionDurability": "pass" if session_ok else "fail",
        },
        "reason": reason,
    }
