"""Contracts for internal Layer 1 endpoint wrappers."""

from __future__ import annotations

from dataclasses import dataclass

from mcp_server.integrations.auth import AuthMode


_REVIEWABLE_LIFECYCLE_STATES = frozenset({"deprecated", "limited", "inconsistent-docs"})


@dataclass(frozen=True)
class EndpointRequestShape:
    """Describe the supported argument shape for one endpoint wrapper.

    :param required_fields: Required request field names.
    :param optional_fields: Optional request field names.
    :param exactly_one_of: Selector fields where exactly one must be present.
    """

    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...] = ()
    exactly_one_of: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Validate that the request shape includes at least one required field.

        :raises ValueError: If the declared selector fields are not supported.
        """
        if not self.required_fields:
            raise ValueError("required_fields must contain at least one field")
        allowed = set(self.required_fields) | set(self.optional_fields)
        missing_selectors = [field for field in self.exactly_one_of if field not in allowed]
        if missing_selectors:
            raise ValueError(
                "exactly_one_of fields must be included in required_fields or optional_fields"
            )

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
        if self.exactly_one_of:
            self._validate_exactly_one_of(arguments)

    def _validate_exactly_one_of(self, arguments: dict[str, object]) -> None:
        """Validate a mutually exclusive selector set.

        :param arguments: Wrapper arguments to validate.
        :raises ValueError: If zero or more than one selector is provided.
        """
        selected = [
            field
            for field in self.exactly_one_of
            if self._has_value(arguments.get(field))
        ]
        if len(selected) != 1:
            joined = ", ".join(self.exactly_one_of)
            raise ValueError(f"exactly one selector is required from: {joined}")

    @staticmethod
    def _has_value(value: object) -> bool:
        """Return whether one argument value should count as present.

        :param value: Candidate argument value.
        :return: ``True`` when the value is not empty for selector purposes.
        """
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        return True


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
    :param caveat_note: Required maintainer-facing caveat note for reviewable lifecycle states.
    :param auth_condition_note: Required explanation when auth mode is conditional.
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
    caveat_note: str | None = None
    auth_condition_note: str | None = None

    def __post_init__(self) -> None:
        """Validate wrapper metadata for completeness and reviewability.

        :raises ValueError: If required metadata or review notes are missing.
        """
        for field_name in ("resource_name", "operation_name", "http_method", "path_shape", "lifecycle_state"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} is required")
        if self.quota_cost <= 0:
            raise ValueError("quota_cost must be greater than zero")
        if self.auth_mode is AuthMode.CONDITIONAL and not self._has_text(self.auth_condition_note):
            raise ValueError("auth_condition_note is required for conditional auth metadata")
        if self.requires_caveat_note and not self._has_text(self.caveat_note):
            raise ValueError("caveat_note is required for reviewable lifecycle states")

    @property
    def operation_key(self) -> str:
        """Return the stable resource and operation identifier."""
        return f"{self.resource_name}.{self.operation_name}"

    @property
    def review_auth_mode(self) -> str:
        """Return the maintainer-facing auth mode label for review surfaces."""
        if self.auth_mode is AuthMode.CONDITIONAL:
            return "mixed/conditional"
        if isinstance(self.auth_mode, AuthMode):
            return self.auth_mode.value
        return str(self.auth_mode)

    @property
    def requires_caveat_note(self) -> bool:
        """Return whether the lifecycle state requires a maintainer-facing caveat note."""
        return self.lifecycle_state in _REVIEWABLE_LIFECYCLE_STATES

    def review_surface(self) -> dict[str, object]:
        """Return maintainer-visible metadata used for review and planning.

        :return: Reviewable identity, quota, auth, and caveat details.
        """
        return {
            "resourceName": self.resource_name,
            "operationName": self.operation_name,
            "operationKey": self.operation_key,
            "httpMethod": self.http_method,
            "pathShape": self.path_shape,
            "requiredFields": self.request_shape.required_fields,
            "optionalFields": self.request_shape.optional_fields,
            "exclusiveSelectors": self.request_shape.exactly_one_of,
            "quotaCost": self.quota_cost,
            "authMode": self.review_auth_mode,
            "lifecycleState": self.lifecycle_state,
            "caveatNote": self.caveat_note,
            "authConditionNote": self.auth_condition_note,
        }

    @staticmethod
    def _has_text(value: str | None) -> bool:
        """Return whether a maintainer-facing metadata note contains visible text.

        :param value: Candidate note text.
        :return: ``True`` when the note has non-whitespace content.
        """
        return isinstance(value, str) and bool(value.strip())
