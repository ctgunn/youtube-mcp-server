"""Typed runtime context shared by resource consumer mixins."""

from __future__ import annotations

from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.base import RepresentativeEndpointWrapper


class ConsumerMixinBase:
    """Declare the dependencies supplied by the composed resource consumer.

    The concrete consumer is a dataclass that owns these attributes.  Each
    mixin inherits this declaration so static analysis can verify its wrapper
    and executor calls without changing the runtime composition model.
    """

    wrapper: RepresentativeEndpointWrapper
    executor: IntegrationExecutor
