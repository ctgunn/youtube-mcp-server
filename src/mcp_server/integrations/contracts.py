"""Contracts for internal Layer 1 endpoint wrappers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EndpointRequestShape:
    """Describe the supported argument shape for one endpoint wrapper.

    :param required_fields: Required request field names.
    :param optional_fields: Optional request field names.
    """

    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Validate that the request shape includes at least one required field."""
        if not self.required_fields:
            raise ValueError("required_fields must contain at least one field")

    def validate_arguments(self, arguments: dict[str, object]) -> None:
        """Validate one wrapper argument payload against the declared shape.

        :param arguments: Wrapper arguments to validate.
        :raises ValueError: If required fields are missing or unexpected fields appear.
        """
        if not isinstance(arguments, dict):
            raise ValueError("arguments must be a dictionary")

        for field in self.required_fields:
            value = arguments.get(field)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                raise ValueError(f"missing required field: {field}")

        allowed = set(self.required_fields) | set(self.optional_fields)
        for field in arguments:
            if field not in allowed:
                raise ValueError(f"unexpected field: {field}")


@dataclass(frozen=True)
class EndpointMetadata:
    """Describe one upstream endpoint wrapper for Layer 1.

    :param resource_name: Upstream resource name.
    :param operation_name: Upstream operation name.
    :param http_method: Upstream HTTP method.
    :param path_shape: Upstream path shape.
    :param request_shape: Declared wrapper request shape.
    :param auth_mode: Supported auth mode for the wrapper.
    :param quota_cost: Official quota-unit cost for the endpoint.
    :param lifecycle_state: Lifecycle note for the wrapper.
    :param notes: Additional maintainer-facing notes.
    """

    resource_name: str
    operation_name: str
    http_method: str
    path_shape: str
    request_shape: EndpointRequestShape
    auth_mode: object
    quota_cost: int
    lifecycle_state: str = "active"
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate wrapper metadata for completeness and reviewability."""
        for field_name in ("resource_name", "operation_name", "http_method", "path_shape", "lifecycle_state"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} is required")
        if self.quota_cost <= 0:
            raise ValueError("quota_cost must be greater than zero")

    @property
    def operation_key(self) -> str:
        """Return the stable resource and operation identifier."""
        return f"{self.resource_name}.{self.operation_name}"
