# ruff: noqa: F405
"""Validation helpers for channels resource wrappers."""

from __future__ import annotations

from mcp_server.integrations.contracts import require_mapping_fields
from mcp_server.integrations.resources.constants import *  # noqa: F403
from mcp_server.integrations.resources.validators.base import *  # noqa: F403

def _channels_update_parts(arguments: dict[str, object]) -> tuple[str, ...]:
    """Return normalized writable parts for one `channels.update` request.

    :param arguments: Wrapper arguments to inspect.
    :return: Ordered supported writable parts without duplicates.
    :raises ValueError: If no writable part is declared.
    """
    raw_part = arguments.get("part")
    if not isinstance(raw_part, str):
        raise ValueError("part must identify at least one supported writable part")
    parts: list[str] = []
    for part_name in raw_part.split(","):
        normalized = part_name.strip()
        if normalized and normalized not in parts:
            parts.append(normalized)
    if not parts:
        raise ValueError("part must identify at least one supported writable part")
    return tuple(parts)

def _require_channels_update_body(arguments: dict[str, object]) -> None:
    """Validate the supported `channels.update` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported writable parts.
    """
    require_mapping_fields("body", required_keys=("id",))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    parts = _channels_update_parts(arguments)
    unsupported_parts = [part for part in parts if part not in _CHANNELS_UPDATE_SUPPORTED_PARTS]
    if unsupported_parts:
        raise ValueError(f"unsupported writable part: {unsupported_parts[0]}")
    for part_name in parts:
        if part_name not in body:
            raise ValueError(f"body.{part_name} is required for selected part")
    allowed_keys = {"id", *parts}
    unsupported_fields = [field for field in body if field not in allowed_keys]
    if unsupported_fields:
        raise ValueError(f"body.{unsupported_fields[0]} is read-only or unsupported")

__all__ = [
    "_channels_update_parts",
    "_require_channels_update_body",
]
