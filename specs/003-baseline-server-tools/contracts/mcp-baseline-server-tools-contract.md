# MCP Baseline Server Tools Contract: FND-003

## Purpose
Define external MCP-facing behavior for the baseline non-YouTube smoke tools:
`server_ping`, `server_info`, and `server_list_tools`.

## Scope
- Tool discovery expectations for baseline tools.
- Invocation contract expectations for baseline tool calls.
- Envelope and error behavior compatibility.

## Discovery Contract

Baseline tools MUST be present in `tools/list` responses:

```json
[
  { "name": "server_ping", "description": "Return service status and timestamp" },
  { "name": "server_info", "description": "Return server version, environment, and build metadata" },
  { "name": "server_list_tools", "description": "Return currently registered tool names and descriptions" }
]
```

Contract rules:
- All three baseline tools are discoverable after startup.
- Discovery output remains deterministic and machine-readable.

## Invocation Contract: `server_ping`

Request params:

```json
{
  "toolName": "server_ping",
  "arguments": {}
}
```

Response `data.result`:

```json
{
  "status": "ok",
  "timestamp": "2026-03-02T00:00:00Z"
}
```

Contract rules:
- `status` and `timestamp` are always present on success.
- Invocation requires no external API dependencies.

## Invocation Contract: `server_info`

Request params:

```json
{
  "toolName": "server_info",
  "arguments": {}
}
```

Response `data.result`:

```json
{
  "version": "0.1.0",
  "environment": "dev",
  "build": {
    "buildId": "local",
    "commit": "unknown",
    "buildTime": "unknown"
  }
}
```

Contract rules:
- `version`, `environment`, and `build` container are returned on success.
- Optional build fields may use fallback values when unavailable.

## Invocation Contract: `server_list_tools`

Request params:

```json
{
  "toolName": "server_list_tools",
  "arguments": {}
}
```

Response `data.result`:

```json
[
  { "name": "server_ping", "description": "Return service status and timestamp" },
  { "name": "server_info", "description": "Return server version, environment, and build metadata" },
  { "name": "server_list_tools", "description": "Return currently registered tool names and descriptions" }
]
```

Contract rules:
- Output reflects active registry contents at invocation time.
- Baseline tools MUST appear in the returned list.

## Shared Envelope Contract

All baseline tool calls continue to use the standard MCP response envelope.
Success example:

```json
{
  "success": true,
  "data": {
    "toolName": "server_ping",
    "result": {
      "status": "ok",
      "timestamp": "2026-03-02T00:00:00Z"
    }
  },
  "meta": { "requestId": "req-001" },
  "error": null
}
```

Failure example:

```json
{
  "success": false,
  "data": null,
  "meta": { "requestId": "req-002" },
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Tool not found.",
    "details": { "toolName": "unknown_tool" }
  }
}
```

Contract rules:
- Error shape remains `code`, `message`, and optional `details`.
- No stack traces are exposed.

## Test Coverage Mapping

- Unit tests: payload construction for each baseline tool handler and fallback behavior.
- Integration tests: end-to-end register/list/call baseline tool lifecycle.
- Contract tests: response envelope and tool-specific result schema validation.

## Implementation Verification (2026-03-02)

Validated against local test suites:
- Unit: 24 passing
- Integration: 6 passing
- Contract: 7 passing
- Full regression: 37 passing

Observed payload parity:
- `tools/list` and `server_list_tools` return matching `name` + `description` entries.
- `server_ping` returns `status` and `timestamp` on every successful invocation.
- `server_info` returns `version`, `environment`, and `build` with fallback-safe values.
