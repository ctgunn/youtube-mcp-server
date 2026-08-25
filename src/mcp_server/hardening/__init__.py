"""Provide internal production-hardening policy dependencies.

This package contains admission, result-reuse, and operational-alerting
components used by the hosted transport.  It is not a public MCP surface.
"""

from __future__ import annotations

from dataclasses import dataclass

from mcp_server.config import ProductionHardeningSettings
from mcp_server.hardening.alerting import AlertEvaluator
from mcp_server.hardening.rate_limit import RateLimiter
from mcp_server.hardening.result_cache import ResultCache


@dataclass(frozen=True)
class HardeningDependencies:
    """Expose validated internal hardening settings to the hosted transport.

    :param settings: Safe policy configuration selected for this process.
    """

    settings: ProductionHardeningSettings
    rate_limiter: RateLimiter
    result_cache: ResultCache
    alert_evaluator: AlertEvaluator


def build_hardening_dependencies(settings: ProductionHardeningSettings) -> HardeningDependencies:
    """Construct the internal dependency group for one runtime.

    :param settings: Validated production-hardening settings.
    :return: Transport-ready dependency container.
    """
    return HardeningDependencies(
        settings=settings,
        rate_limiter=RateLimiter(settings.rate_limit),
        result_cache=ResultCache(settings.result_cache),
        alert_evaluator=AlertEvaluator(settings.alerting),
    )
