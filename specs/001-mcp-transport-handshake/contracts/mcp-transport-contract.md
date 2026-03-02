# MCP Transport Contract: FND-001

## Purpose
Define request and response contracts for foundation MCP HTTP transport methods:
`initialize`, `tools/list`, and `tools/call`.

## Transport
- Protocol: HTTP
- Content-Type: `application/json`
- Endpoint: `/mcp`

## Common Request Shape

```json
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "method": "initialize",
  "params": {}
}
```

## Common Success Envelope

```json
{
  "success": true,
  "data": {},
  "meta": {
    "requestId": "req-001"
  },
  "error": null
}
```

## Common Error Envelope

```json
{
  "success": false,
  "data": null,
  "meta": {
    "requestId": "req-001"
  },
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Tool not found.",
    "details": {
      "toolName": "unknown_tool"
    }
  }
}
```

## Method: `initialize`

Request params:

```json
{
  "clientInfo": {
    "name": "example-client",
    "version": "1.0.0"
  }
}
```

Response `data`:

```json
{
  "serverName": "youtube-mcp-server",
  "serverVersion": "0.1.0",
  "capabilities": {
    "tools": {
      "listChanged": false
    }
  }
}
```

## Method: `tools/list`

Request params:

```json
{}
```

Response `data`:

```json
[
  {
    "name": "server_ping",
    "description": "Return service status and timestamp"
  }
]
```

## Method: `tools/call`

Request params:

```json
{
  "toolName": "server_ping",
  "arguments": {}
}
```

Response `data` (success example):

```json
{
  "toolName": "server_ping",
  "result": {
    "status": "ok",
    "timestamp": "2026-03-01T00:00:00Z"
  }
}
```

Error contracts:
- Unknown tool -> `RESOURCE_NOT_FOUND`
- Invalid arguments -> `INVALID_ARGUMENT`
- Unsupported method -> `METHOD_NOT_SUPPORTED`
- Internal unexpected failure -> `INTERNAL_ERROR`

## Validation Notes
- `method` is required and must be one of the supported FND-001 methods.
- `params` must be an object when supplied.
- `tools/call` requires `toolName`.
- Client-visible errors must not include stack traces.

## Test Coverage Mapping
- Contract tests must validate each method's success envelope.
- Contract tests must validate unknown tool and malformed request error envelope.
- Integration tests must validate initialize -> list -> call sequence in one session.
