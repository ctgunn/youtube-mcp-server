"""Shared infrastructure portability helpers used by design-level tests."""

from __future__ import annotations

import re


SHARED_PLATFORM_CAPABILITIES = (
    "hosted_runtime",
    "network_ingress",
    "runtime_identity",
    "secret_backed_configuration",
    "observability_integration",
    "durable_session_support",
)

EXECUTION_MODES = (
    "minimal_local",
    "hosted_like_local",
    "hosted",
)


def normalize_capability_name(value: str) -> str:
    """Return the canonical snake_case name used for shared capabilities."""

    normalized = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return normalized.strip("_")


def is_supported_execution_mode(value: str) -> bool:
    """Check whether a mode name is part of the shared execution model."""

    return normalize_capability_name(value) in EXECUTION_MODES
