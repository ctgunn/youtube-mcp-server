"""Protocol response helpers."""

from __future__ import annotations

from typing import Any


ERROR_CODE_BY_CATEGORY = {
    "malformed_request": -32600,
    "invalid_json": -32600,
    "malformed_security_input": -32600,
    "malformed_origin": -32600,
    "unsupported_method": -32601,
    "method_not_allowed": -32601,
    "unsupported_browser_method": -32601,
    "unsupported_browser_route": -32601,
    "invalid_argument": -32602,
    "unsupported_media_type": -32602,
    "unsupported_headers": -32602,
    "unsupported_browser_headers": -32602,
    "replay_unavailable": -32602,
    "internal_execution_failure": -32603,
    "unknown_tool": -32001,
    "path_not_found": -32001,
    "resource_missing": -32001,
    "session_not_found": -32001,
    "expired_session": -32001,
    "unavailable_source": -32001,
    "unauthenticated": -32002,
    "invalid_credential": -32002,
    "forbidden": -32003,
    "origin_denied": -32003,
    "authorization_denied": -32003,
    "transport_not_supported": -32004,
}


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


def code_for_category(category: str) -> int:
    if category not in ERROR_CODE_BY_CATEGORY:
        raise KeyError(f"Unknown MCP error category: {category}")
    return ERROR_CODE_BY_CATEGORY[category]


def _merge_error_details(category: str | None, details: dict[str, Any] | None) -> dict[str, Any] | None:
    if category is None:
        return details
    merged = dict(details or {})
    merged.setdefault("category", category)
    return merged


def error_response(code: int | str, message: str, request_id=None, details=None):
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


def error_response_for_category(category: str, message: str, request_id=None, details=None):
    return error_response(
        code_for_category(category),
        message,
        request_id=request_id,
        details=_merge_error_details(category, details),
    )
