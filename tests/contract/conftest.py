def build_mcp_payload(request_id, method, params):
    return {
        "id": request_id,
        "method": method,
        "params": params,
    }
