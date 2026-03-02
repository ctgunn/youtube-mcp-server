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
