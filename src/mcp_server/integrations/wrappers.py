"""Representative internal endpoint wrappers for Layer 1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mcp_server.integrations.auth import AuthContext
from mcp_server.integrations.contracts import EndpointMetadata
from mcp_server.integrations.executor import IntegrationExecutor, RequestExecution


@dataclass(frozen=True)
class RepresentativeEndpointWrapper:
    """Represent one metadata-driven Layer 1 wrapper.

    :param metadata: Declared wrapper metadata and request shape.
    """

    metadata: EndpointMetadata

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute the representative wrapper through the shared executor.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        """
        self.metadata.request_shape.validate_arguments(arguments)
        execution = RequestExecution(
            metadata=self.metadata,
            arguments=arguments,
            auth_context=auth_context,
        )
        return executor.execute(execution)
