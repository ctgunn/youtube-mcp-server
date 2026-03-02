"""Response envelope helpers."""

from __future__ import annotations


def _sanitize_message(message: str) -> str:
    text = str(message or "").strip()
    if not text:
        return "Unexpected error."
    # Keep only the first line and remove traceback leakage.
    first_line = text.splitlines()[0]
    return first_line.replace("Traceback (most recent call last)", "").strip() or "Unexpected error."


def success_response(data, request_id=None):
    return {
        "success": True,
        "data": data,
        "meta": {"requestId": request_id},
        "error": None,
    }


def error_response(code: str, message: str, request_id=None, details=None):
    return {
        "success": False,
        "data": None,
        "meta": {"requestId": request_id},
        "error": {
            "code": code,
            "message": _sanitize_message(message),
            "details": details,
        },
    }
