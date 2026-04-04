"""Method routing for MCP protocol."""

from __future__ import annotations

import json

from mcp_server.protocol.envelope import error_response_for_category, success_response
from mcp_server.transport.streaming import SUPPORTED_MCP_PROTOCOL_VERSIONS
from mcp_server.tools.retrieval import RetrievalError


UNKNOWN_TOOL_MESSAGE = "Tool not found."


def _validate_payload(payload):
    """Validate the top-level JSON-RPC request shape.

    :param payload: Decoded request payload.
    :return: Tuple of validity flag, request id, parsed method/params pair, and error response.
    """
    if not isinstance(payload, dict):
        return False, None, None, error_response_for_category("malformed_request", "payload must be an object")
    request_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params", {})

    if not isinstance(method, str) or not method.strip():
        return False, request_id, None, error_response_for_category(
            "malformed_request", "method is required", request_id=request_id
        )
    if not isinstance(params, dict):
        return False, request_id, None, error_response_for_category(
            "malformed_request", "params must be an object", request_id=request_id
        )
    return True, request_id, (method, params), None


def _serialize_tool_result(result) -> dict:
    """Convert a tool result into MCP content blocks.

    :param result: Raw tool result.
    :return: MCP ``tools/call`` result payload.
    """
    content = {
        "type": "text",
        "text": json.dumps(result, sort_keys=True),
    }
    if isinstance(result, (dict, list)):
        content["structuredContent"] = result
    else:
        content["structuredContent"] = {"value": result}
    return {
        "content": [content],
        "isError": False,
    }


def _parse_call_params(request_id, params):
    """Validate and extract tool call parameters.

    :param request_id: JSON-RPC request identifier.
    :param params: Raw method parameters.
    :return: Tuple of tool name, arguments, and optional validation error.
    """
    tool_name = params.get("name")
    if tool_name is None:
        tool_name = params.get("toolName")
    if not isinstance(tool_name, str) or not tool_name.strip():
        return None, None, error_response_for_category(
            "invalid_argument",
            "name is required",
            request_id=request_id,
        )

    arguments = params.get("arguments", {})
    if not isinstance(arguments, dict):
        return None, None, error_response_for_category(
            "invalid_argument",
            "arguments must be an object",
            request_id=request_id,
        )

    return tool_name, arguments, None


def _handle_initialize(request_id, params):
    """Handle the MCP ``initialize`` method.

    :param request_id: JSON-RPC request identifier.
    :param params: Initialization parameters from the client.
    :return: JSON-RPC response payload.
    """
    client_info = params.get("clientInfo")
    if not isinstance(client_info, dict) or not client_info.get("name"):
        return error_response_for_category(
            "invalid_argument",
            "clientInfo with name is required",
            request_id=request_id,
        )
    return success_response(
        {
            "protocolVersion": SUPPORTED_MCP_PROTOCOL_VERSIONS[0],
            "serverInfo": {
                "name": "youtube-mcp-server",
                "version": "0.1.0",
            },
            "capabilities": {"tools": {"listChanged": False}},
        },
        request_id=request_id,
    )


def initialize_succeeded(response: dict) -> bool:
    """Check whether an initialize response represents success.

    :param response: JSON-RPC response payload.
    :return: ``True`` when the response contains initialize capabilities.
    """
    if not isinstance(response, dict) or "error" in response:
        return False
    result = response.get("result")
    return isinstance(result, dict) and "capabilities" in result


def _handle_list(request_id, _params, dispatcher):
    """Handle the MCP ``tools/list`` method."""
    return success_response({"tools": dispatcher.list_tools()}, request_id=request_id)


def _handle_call(request_id, params, dispatcher):
    """Handle the MCP ``tools/call`` method.

    :param request_id: JSON-RPC request identifier.
    :param params: Tool call parameters.
    :param dispatcher: Tool dispatcher used for invocation.
    :return: JSON-RPC response payload.
    """
    tool_name, arguments, validation_error = _parse_call_params(request_id, params)
    if validation_error:
        return validation_error

    try:
        result = dispatcher.call_tool(tool_name, arguments)
    except KeyError:
        return error_response_for_category(
            "unknown_tool",
            UNKNOWN_TOOL_MESSAGE,
            request_id=request_id,
            details={"toolName": tool_name},
        )
    except RetrievalError as exc:
        return error_response_for_category(exc.category, str(exc), request_id=request_id, details=exc.details)
    except ValueError as exc:
        return error_response_for_category(
            "invalid_argument",
            str(exc),
            request_id=request_id,
            details={"toolName": tool_name},
        )
    except Exception:
        return error_response_for_category(
            "internal_execution_failure",
            "Unexpected tool execution error.",
            request_id=request_id,
            details={"toolName": tool_name},
        )

    return success_response(_serialize_tool_result(result), request_id=request_id)


def route_mcp_request(payload: dict, dispatcher) -> dict:
    """Route a decoded MCP request to the correct method handler.

    :param payload: Decoded JSON-RPC request payload.
    :param dispatcher: Tool dispatcher used for list/call methods.
    :return: JSON-RPC response payload.
    """
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

    return error_response_for_category(
        "unsupported_method",
        "Method is not supported.",
        request_id=request_id,
        details={"method": method},
    )
