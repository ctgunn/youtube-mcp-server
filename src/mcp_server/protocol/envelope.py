"""Protocol response helpers."""

from __future__ import annotations


def _sanitize_message(message: str) -> str:
    text = str(message or "").strip()
    if not text:
        return "Unexpected error."
    # Keep only the first line and remove traceback leakage.
    first_line = text.splitlines()[0]
    return first_line.replace("Traceback (most recent call last)", "").strip() or "Unexpected error."


def success_response(result, request_id=None):
    response = {
        "jsonrpc": "2.0",
        "result": result,
    }
    if request_id is not None:
        response["id"] = request_id
    return response


def error_response(code: str, message: str, request_id=None, details=None):
    response = {
        "jsonrpc": "2.0",
        "error": {
            "code": code,
            "message": _sanitize_message(message),
            "data": details,
        },
    }
    if request_id is not None:
        response["id"] = request_id
    return response
