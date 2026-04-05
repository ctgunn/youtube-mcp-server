"""Shared request execution for internal Layer 1 wrappers."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Callable

from mcp_server.integrations.auth import AuthContext
from mcp_server.integrations.contracts import EndpointMetadata
from mcp_server.integrations.errors import NormalizedUpstreamError, normalize_upstream_error
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.observability import InMemoryObservability, integration_execution_event


@dataclass(frozen=True)
class RequestExecution:
    """Represent one shared Layer 1 execution.

    :param metadata: Wrapper metadata for the execution.
    :param arguments: Wrapper arguments for the request.
    :param auth_context: Auth configuration selected for the request.
    """

    metadata: EndpointMetadata
    arguments: dict[str, Any]
    auth_context: AuthContext

    @property
    def credentials(self) -> dict[str, str]:
        """Return the credential payload selected for this execution."""
        return self.auth_context.resolve_credentials()


@dataclass(frozen=True)
class IntegrationHooks:
    """Store optional hooks used by the shared executor.

    :param on_request: Hook fired before request execution.
    :param on_response: Hook fired after a successful response.
    :param on_error: Hook fired after a normalized failure.
    """

    on_request: Callable[[RequestExecution], None] | None = None
    on_response: Callable[[RequestExecution, dict[str, Any]], None] | None = None
    on_error: Callable[[RequestExecution, NormalizedUpstreamError], None] | None = None


class IntegrationExecutor:
    """Execute Layer 1 wrapper requests through one shared path."""

    def __init__(
        self,
        *,
        transport: Callable[[RequestExecution], dict[str, Any]],
        retry_policy: RetryPolicy,
        hooks: IntegrationHooks | None = None,
    ) -> None:
        """Initialize the shared executor.

        :param transport: Callable that performs the actual upstream work.
        :param retry_policy: Retry behavior for failures.
        :param hooks: Optional request, response, and error hooks.
        """
        self._transport = transport
        self._retry_policy = retry_policy
        self._hooks = hooks or IntegrationHooks()

    def execute(self, execution: RequestExecution) -> dict[str, Any]:
        """Execute one request through the shared transport and retry policy.

        :param execution: Wrapper execution request.
        :return: Structured response from the transport.
        :raises NormalizedUpstreamError: If execution fails after allowed retries.
        """
        attempt_number = 0
        while True:
            attempt_number += 1
            if self._hooks.on_request is not None:
                self._hooks.on_request(execution)
            try:
                response = self._transport(execution)
            except NormalizedUpstreamError as error:
                if self._hooks.on_error is not None:
                    self._hooks.on_error(execution, error)
                if self._retry_policy.should_retry(error, attempt_number):
                    continue
                raise
            except Exception as error:  # pragma: no cover - exercised in integration tests
                normalized = normalize_upstream_error(error)
                if self._hooks.on_error is not None:
                    self._hooks.on_error(execution, normalized)
                if self._retry_policy.should_retry(normalized, attempt_number):
                    continue
                raise normalized
            if self._hooks.on_response is not None:
                self._hooks.on_response(execution, response)
            return response


def build_observability_hooks(
    observability: InMemoryObservability,
    *,
    request_id: str,
) -> IntegrationHooks:
    """Build executor hooks that emit integration execution events.

    :param observability: Observability sink used by the application.
    :param request_id: Request identifier associated with the internal workflow.
    :return: Executor hook bundle wired to the observability sink.
    """

    def on_request(execution: RequestExecution) -> None:
        observability.record_integration_execution(
            integration_execution_event(
                request_id=request_id,
                phase="request",
                status="success",
                metadata=execution.metadata,
                auth_mode=execution.auth_context.mode.value,
                latency_ms=0.0,
            )
        )

    def on_response(execution: RequestExecution, _response: dict[str, Any]) -> None:
        observability.record_integration_execution(
            integration_execution_event(
                request_id=request_id,
                phase="response",
                status="success",
                metadata=execution.metadata,
                auth_mode=execution.auth_context.mode.value,
                latency_ms=0.0,
            )
        )

    def on_error(execution: RequestExecution, error: NormalizedUpstreamError) -> None:
        observability.record_integration_execution(
            integration_execution_event(
                request_id=request_id,
                phase="error",
                status="error",
                metadata=execution.metadata,
                auth_mode=execution.auth_context.mode.value,
                latency_ms=0.0,
                error=error,
            )
        )

    return IntegrationHooks(on_request=on_request, on_response=on_response, on_error=on_error)


def timed_execution(
    executor: IntegrationExecutor,
    execution: RequestExecution,
) -> tuple[dict[str, Any], float]:
    """Execute one request and return the response plus elapsed time.

    :param executor: Shared executor instance.
    :param execution: Execution request to run.
    :return: Tuple of response payload and elapsed milliseconds.
    """
    started = perf_counter()
    response = executor.execute(execution)
    return response, (perf_counter() - started) * 1000.0
