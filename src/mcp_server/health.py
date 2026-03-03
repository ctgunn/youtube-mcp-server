"""Liveness and readiness payload helpers."""

from __future__ import annotations

from mcp_server.config import StartupValidationResult


def health_payload() -> dict:
    return {"status": "ok"}


def readiness_payload(validation: StartupValidationResult) -> dict:
    if validation.is_valid:
        return {
            "status": "ready",
            "checks": {
                "configuration": "pass",
                "secrets": "pass",
            },
        }
    return {
        "status": "not_ready",
        "checks": {
            "configuration": "fail",
            "secrets": "fail",
        },
        "reason": {
            "code": "CONFIG_VALIDATION_ERROR",
            "message": "Required configuration is invalid or incomplete.",
        },
    }

