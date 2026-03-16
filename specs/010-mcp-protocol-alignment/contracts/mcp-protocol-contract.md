# Contract: FND-010 MCP Protocol Contract Alignment

## Purpose

Define the externally visible MCP protocol contract for initialize, tool
discovery, tool invocation, and protocol failure handling after removing the
legacy server-specific wrapper.

## Scope

- MCP-native request and response bodies carried over the existing `/mcp`
  endpoint
- Initialize, `tools/list`, and `tools/call` flows
- Protocol-native error behavior for malformed requests, invalid parameters,
  unsupported methods, and tool execution failures
- Local and hosted parity for the same logical MCP interactions

## Relationship to Prior Contracts

- This contract supersedes the wrapper-based response contract documented in
  `/specs/001-mcp-transport-handshake/contracts/mcp-transport-contract.md` for
  covered MCP flows.
- This contract does not replace the hosted transport/session rules in
  `/specs/009-mcp-streamable-http-transport/contracts/mcp-streamable-http-contract.md`;
  it defines the protocol bodies carried by that transport.

## Common Request Shape

```json
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "method": "initialize",
  "params": {}
}
```

Request rules:
- `jsonrpc` identifies the protocol message version for client requests.
- `method` is required for covered request flows.
- `params` must be an object when present.
- Requests that require a response include `id`.

## Common Success Shape

```json
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "result": {}
}
```

Success rules:
- Success payloads use `result`, not `success`, `data`, `meta`, or `error`.
- The response `id` matches the request `id` when the request expects a
  response.
- Hosted JSON responses and SSE-delivered responses use the same protocol body
  shape for the same logical outcome.

## Common Error Shape

```json
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "method is required",
    "data": null
  }
}
```

Error rules:
- Error payloads use `error.code`, `error.message`, and optional `error.data`.
- Client-visible errors remain sanitized and must not expose stack traces,
  secrets, or server-only diagnostics.
- Protocol errors may be returned with the matching request `id` when one was
  supplied and could be associated with the failure.

## Method: `initialize`

### Request params

```json
{
  "clientInfo": {
    "name": "example-client",
    "version": "1.0.0"
  }
}
```

### Result

```json
{
  "protocolVersion": "2025-11-25",
  "serverInfo": {
    "name": "youtube-mcp-server",
    "version": "0.1.0"
  },
  "capabilities": {
    "tools": {
      "listChanged": false
    }
  }
}
```

Rules:
- Initialization fails when required client information is missing.
- The response advertises the server capabilities needed for subsequent MCP
  interactions.
- Hosted initialize responses may also issue `MCP-Session-Id` headers under
  the FND-009 transport contract.

## Method: `tools/list`

### Request params

```json
{}
```

### Result

```json
{
  "tools": [
    {
      "name": "server_ping",
      "description": "Return service status and timestamp"
    }
  ]
}
```

Rules:
- Discovery returns the currently registered tools available to the client.
- The baseline tool set remains discoverable after the protocol migration.
- Richer tool metadata expansion remains in scope for FND-011, not this slice.

## Method: `tools/call`

### Request params

```json
{
  "name": "server_ping",
  "arguments": {}
}
```

### Result

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"status\":\"ok\",\"timestamp\":\"2026-03-01T00:00:00Z\"}"
    }
  ],
  "isError": false
}
```

Rules:
- Tool invocation uses MCP-native call parameters and result shape rather than
  the wrapper object containing `toolName` and `result`.
- Successful baseline tool calls return deterministic MCP-compatible content.
- Tool execution failures that are not protocol failures are still surfaced in
  a documented client-consumable way without leaking internal stack traces.

## Protocol Error Mapping

- Malformed request object -> protocol error `INVALID_ARGUMENT`
- Missing or empty method name -> protocol error `INVALID_ARGUMENT`
- Unsupported method -> protocol error `METHOD_NOT_SUPPORTED`
- Unknown tool -> protocol error `RESOURCE_NOT_FOUND`
- Invalid tool arguments -> protocol error `INVALID_ARGUMENT`
- Unexpected internal tool execution failure -> protocol error `INTERNAL_ERROR`

Mapping rules:
- The same failure category must map to the same protocol error code in local
  and hosted flows.
- Hosted transport status codes may still differ by transport condition, but
  the protocol error body remains stable when returned.

## Testable Assertions

- Contract tests can prove initialize, tool discovery, and tool invocation all
  return MCP-native `result` bodies instead of the legacy wrapper.
- Contract tests can prove malformed requests and unsupported methods return
  MCP-native `error` bodies.
- Integration tests can prove initialize -> list -> call works in both local
  and hosted flows with the same protocol body shapes.
- Regression tests can prove baseline tools remain callable and health/readiness
  behavior remains unchanged by the protocol migration.
