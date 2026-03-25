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

PUBLIC_INVOCATION_INTENTS = (
    "public_remote_mcp",
    "private_only",
)

ACCESS_FAILURE_LAYERS = (
    "cloud_platform",
    "mcp_application",
)

DEPENDENCY_FAILURE_LAYERS = (
    "secret_access",
    "session_connectivity",
)


def normalize_capability_name(value: str) -> str:
    """Return the canonical snake_case name used for shared capabilities."""

    normalized = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return normalized.strip("_")


def is_supported_execution_mode(value: str) -> bool:
    """Check whether a mode name is part of the shared execution model."""

    return normalize_capability_name(value) in EXECUTION_MODES


def is_supported_public_invocation_intent(value: str) -> bool:
    """Check whether a public invocation intent is part of the hosted model."""

    return normalize_capability_name(value) in PUBLIC_INVOCATION_INTENTS


def is_supported_access_failure_layer(value: str) -> bool:
    """Check whether a failure layer is part of the hosted access model."""

    return normalize_capability_name(value) in ACCESS_FAILURE_LAYERS


def is_supported_dependency_failure_layer(value: str) -> bool:
    """Check whether a failure layer is part of hosted dependency diagnostics."""

    return normalize_capability_name(value) in DEPENDENCY_FAILURE_LAYERS
