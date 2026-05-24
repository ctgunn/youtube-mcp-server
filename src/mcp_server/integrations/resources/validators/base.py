# ruff: noqa: F405
"""Validation helpers for base resource wrappers."""

from __future__ import annotations



def _validated_reference_values(
    raw_values: object,
    *,
    reference_label: str,
    required_message: str,
    duplicate_message: str,
) -> tuple[str, ...]:
    """Return validated channel or playlist references from one request body.

    :param raw_values: Candidate list-like value from ``contentDetails``.
    :param reference_label: Human-readable label for one reference type.
    :param required_message: Validation message used when no usable values exist.
    :param duplicate_message: Validation message used when duplicates appear.
    :return: Normalized ordered references without duplicates.
    :raises ValueError: If the list is missing, empty, malformed, or duplicated.
    """
    if not isinstance(raw_values, list):
        raise ValueError(required_message)
    values: list[str] = []
    for raw_value in raw_values:
        if not isinstance(raw_value, str) or not raw_value.strip():
            raise ValueError(required_message)
        normalized = raw_value.strip()
        if normalized in values:
            raise ValueError(duplicate_message)
        values.append(normalized)
    if not values:
        raise ValueError(required_message)
    return tuple(values)

__all__ = [
    "_validated_reference_values",
]
