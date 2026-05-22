"""Shared response-normalizer foundations for resource-family modules."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Any

from mcp_server.integrations.executor import RequestExecution

@dataclass(frozen=True)
class ResponseNormalizer:
    """Adapt one operation-specific response normalizer to a shared signature.

    :param family_name: Resource-family name that owns the normalizer.
    :param operation_key: Stable operation key handled by the normalizer.
    :param input_requirements: Input shape required by the wrapped handler.
    :param _handler: Callable invoked for the selected input shape.
    """

    family_name: str
    operation_key: str
    input_requirements: str
    _handler: Callable[..., dict[str, Any]]

    @classmethod
    def context_only(
        cls,
        *,
        family_name: str,
        operation_key: str,
        handler: Callable[[RequestExecution], dict[str, Any]],
    ) -> "ResponseNormalizer":
        """Build a normalizer that only needs execution context.

        :param family_name: Resource-family name that owns the normalizer.
        :param operation_key: Stable operation key handled by the normalizer.
        :param handler: Callable accepting a ``RequestExecution``.
        :return: Response normalizer adapted to the shared dispatch shape.
        """
        return cls(family_name=family_name, operation_key=operation_key, input_requirements="context", _handler=handler)

    @classmethod
    def payload_only(
        cls,
        *,
        family_name: str,
        operation_key: str,
        handler: Callable[[str], dict[str, Any]],
    ) -> "ResponseNormalizer":
        """Build a normalizer that only needs response payload content.

        :param family_name: Resource-family name that owns the normalizer.
        :param operation_key: Stable operation key handled by the normalizer.
        :param handler: Callable accepting response payload content.
        :return: Response normalizer adapted to the shared dispatch shape.
        """
        return cls(family_name=family_name, operation_key=operation_key, input_requirements="payload", _handler=handler)

    @classmethod
    def context_and_payload(
        cls,
        *,
        family_name: str,
        operation_key: str,
        handler: Callable[[RequestExecution, str], dict[str, Any]],
    ) -> "ResponseNormalizer":
        """Build a normalizer that needs execution context and payload content.

        :param family_name: Resource-family name that owns the normalizer.
        :param operation_key: Stable operation key handled by the normalizer.
        :param handler: Callable accepting execution context and payload content.
        :return: Response normalizer adapted to the shared dispatch shape.
        """
        return cls(family_name=family_name, operation_key=operation_key, input_requirements="context_payload", _handler=handler)

    def normalize(self, execution: RequestExecution, payload: str) -> dict[str, Any]:
        """Normalize one response payload for the configured operation.

        :param execution: Shared request execution details.
        :param payload: Raw response payload content.
        :return: Normalized response payload.
        :raises ValueError: If the normalizer was created with an unsupported input shape.
        """
        if self.input_requirements == "context":
            return self._handler(execution)
        if self.input_requirements == "payload":
            return self._handler(payload)
        if self.input_requirements == "context_payload":
            return self._handler(execution, payload)
        raise ValueError(f"unsupported response normalizer input shape: {self.input_requirements}")

    def metadata_for_test(self, metadata: Any) -> Any:
        """Return metadata with this normalizer's operation key for tests.

        :param metadata: Endpoint metadata to copy.
        :return: Metadata copy whose operation key matches the normalizer.
        """
        resource_name, operation_name = self.operation_key.split(".", 1)
        return replace(metadata, resource_name=resource_name, operation_name=operation_name)

def build_response_normalizer_registry(
    normalizers: Sequence[ResponseNormalizer],
) -> Mapping[str, ResponseNormalizer]:
    """Build an operation-key response normalizer registry.

    :param normalizers: Response normalizers to register by operation key.
    :return: Mapping from operation key to response normalizer.
    :raises ValueError: If duplicate operation keys are supplied.
    """
    registry: dict[str, ResponseNormalizer] = {}
    for normalizer in normalizers:
        if normalizer.operation_key in registry:
            raise ValueError(f"duplicate response normalizer: {normalizer.operation_key}")
        registry[normalizer.operation_key] = normalizer
    return registry

def normalize_youtube_response(
    execution: RequestExecution,
    payload: str,
    *,
    registry: Mapping[str, ResponseNormalizer],
) -> dict[str, Any]:
    """Normalize a YouTube response through explicit dispatch or JSON fallback.

    :param execution: Shared request execution details.
    :param payload: Raw response payload content.
    :param registry: Operation-key to response normalizer mapping.
    :return: Normalized response payload.
    :raises ValueError: If fallback JSON parsing does not produce an object.
    """
    normalizer = registry.get(execution.metadata.operation_key)
    if normalizer is not None:
        return normalizer.normalize(execution, payload)
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed

def _normalized_video_rating_state(raw_value: object) -> str:
    """Return the stable rating-state label for one upstream lookup entry.

    :param raw_value: Upstream rating value for one video.
    :return: Stable internal rating-state label.
    """
    normalized = _stringify_scalar(raw_value).strip().lower()
    if normalized in {"like", "liked"}:
        return "liked"
    if normalized in {"dislike", "disliked"}:
        return "disliked"
    if normalized in {"none", "unrated", ""}:
        return "none"
    return normalized

def _split_comma_delimited_ids(raw_value: str) -> tuple[str, ...]:
    """Return normalized comma-delimited identifiers from one scalar value.

    :param raw_value: Raw comma-delimited identifier string.
    :return: Ordered identifier values with blanks removed.
    """
    return tuple(part.strip() for part in raw_value.split(",") if part.strip())

def _stringify_scalar(value: object) -> str:
    """Convert one scalar wrapper argument value into its query-string form.

    :param value: Scalar value to encode.
    :return: String form suitable for URL encoding.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)

def _update_payload_with_request_fallbacks(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return a parsed update payload with request-derived fallback fields.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed update payload with stable `part`, `id`, and `title` fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    parsed_snippet = parsed.get("snippet", {}) if isinstance(parsed.get("snippet"), dict) else {}
    parsed["part"] = execution.arguments.get("part")
    parsed["id"] = parsed.get("id") or (body.get("id") if isinstance(body, dict) else None)
    parsed["title"] = parsed.get("title") or parsed_snippet.get("title") or snippet.get("title")
    return parsed

def _videos_get_rating_summary(video_ratings: Sequence[Mapping[str, object]]) -> str:
    """Return a stable summary label for normalized rating-state outcomes.

    :param video_ratings: Normalized per-video rating entries.
    :return: Stable summary label for downstream review surfaces.
    """
    if not video_ratings:
        return "empty"

    rated_count = sum(1 for entry in video_ratings if bool(entry.get("isRated")))
    unrated_count = sum(1 for entry in video_ratings if bool(entry.get("isUnrated")))
    if rated_count and unrated_count:
        return "mixed_rated_and_unrated"
    if rated_count:
        return "all_rated"
    return "all_unrated"

__all__ = [
    "ResponseNormalizer",
    "_normalized_video_rating_state",
    "_split_comma_delimited_ids",
    "_stringify_scalar",
    "_update_payload_with_request_fallbacks",
    "_videos_get_rating_summary",
    "build_response_normalizer_registry",
    "normalize_youtube_response",
]
