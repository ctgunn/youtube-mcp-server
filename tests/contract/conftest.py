def build_mcp_payload(request_id, method, params):
    return {
        "id": request_id,
        "method": method,
        "params": params,
    }


def build_tool_call_payload(request_id, tool_name, arguments=None):
    return build_mcp_payload(
        request_id,
        "tools/call",
        {
            "toolName": tool_name,
            "arguments": arguments or {},
        },
    )


def build_initialize_payload(request_id, client_name="client", client_version="1.0.0", *, params_override=None):
    params = {
        "clientInfo": {
            "name": client_name,
            "version": client_version,
        }
    }
    if params_override is not None:
        params = params_override
    return build_mcp_payload(request_id, "initialize", params)


def stream_headers(session_id=None, *, include_json=True, protocol_version=None, origin=None):
    accept = "application/json, text/event-stream" if include_json else "text/event-stream"
    headers = {"Accept": accept}
    if session_id:
        headers["MCP-Session-Id"] = session_id
    if protocol_version:
        headers["MCP-Protocol-Version"] = protocol_version
    if origin:
        headers["Origin"] = origin
    return headers
