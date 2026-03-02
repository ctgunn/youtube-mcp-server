"""Method routing for MCP protocol."""

from __future__ import annotations

from mcp_server.protocol.envelope import error_response, success_response


def _validate_payload(payload):
    if not isinstance(payload, dict):
        return False, None, None, error_response("INVALID_ARGUMENT", "payload must be an object")
    request_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params", {})

    if not isinstance(method, str) or not method.strip():
        return False, request_id, None, error_response(
            "INVALID_ARGUMENT", "method is required", request_id=request_id
        )
    if not isinstance(params, dict):
        return False, request_id, None, error_response(
            "INVALID_ARGUMENT", "params must be an object", request_id=request_id
        )
    return True, request_id, (method, params), None


def _handle_initialize(request_id, params):
    client_info = params.get("clientInfo")
    if not isinstance(client_info, dict) or not client_info.get("name"):
        return error_response(
            "INVALID_ARGUMENT",
            "clientInfo with name is required",
            request_id=request_id,
        )
    return success_response(
        {
            "serverName": "youtube-mcp-server",
            "serverVersion": "0.1.0",
            "capabilities": {"tools": {"listChanged": False}},
        },
        request_id=request_id,
    )


def _handle_list(request_id, _params, dispatcher):
    return success_response(dispatcher.list_tools(), request_id=request_id)


def _handle_call(request_id, params, dispatcher):
    tool_name = params.get("toolName")
    if not isinstance(tool_name, str) or not tool_name.strip():
        return error_response(
            "INVALID_ARGUMENT",
            "toolName is required",
            request_id=request_id,
        )

    arguments = params.get("arguments", {})
    if not isinstance(arguments, dict):
        return error_response(
            "INVALID_ARGUMENT",
            "arguments must be an object",
            request_id=request_id,
        )

    try:
        result = dispatcher.call_tool(tool_name, arguments)
    except KeyError:
        return error_response(
            "RESOURCE_NOT_FOUND",
            "Tool not found.",
            request_id=request_id,
            details={"toolName": tool_name},
        )
    except ValueError as exc:
        return error_response("INVALID_ARGUMENT", str(exc), request_id=request_id)
    except Exception:
        return error_response("INTERNAL_ERROR", "Unexpected tool execution error.", request_id=request_id)

    return success_response({"toolName": tool_name, "result": result}, request_id=request_id)


def route_mcp_request(payload: dict, dispatcher) -> dict:
    valid, request_id, parsed, error = _validate_payload(payload)
    if not valid:
        return error

    method, params = parsed
    if method == "initialize":
        return _handle_initialize(request_id, params)
    if method == "tools/list":
        return _handle_list(request_id, params, dispatcher)
    if method == "tools/call":
        return _handle_call(request_id, params, dispatcher)

    return error_response(
        "METHOD_NOT_SUPPORTED",
        "Method is not supported.",
        request_id=request_id,
        details={"method": method},
    )
