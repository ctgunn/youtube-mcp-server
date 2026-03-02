# MCP Tool Registry and Dispatcher Contract: FND-002

## Purpose
Define behavior contracts for tool registration lifecycle and runtime dispatch
for MCP foundation methods `tools/list` and `tools/call`.

## Scope
- Internal registration requirements for discoverable/invokable tools.
- External MCP response behavior for list and call flows.
- Error contracts for invalid input and unknown tool references.

## Tool Registration Contract

Required registration fields:

```json
{
  "name": "server_ping",
  "description": "Return service status and timestamp",
  "inputSchema": {
    "type": "object",
    "additionalProperties": false
  },
  "handler": "callable"
}
```

Contract rules:
- `name`, `description`, `inputSchema`, and `handler` are required.
- Tool names are normalized case-insensitively for uniqueness and lookup.
- Duplicate normalized names are rejected with structured validation errors.

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

Contract rules:
- Returns currently registered tools only.
- Ordering is deterministic based on normalized tool names.

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

Contract rules:
- Dispatcher resolves `toolName` against registered tools using normalized lookup.
- `arguments` are validated against the tool's declared input schema before handler execution.
- Handler executes only after validation succeeds.

## Common Error Contracts

- Unknown tool -> `RESOURCE_NOT_FOUND`

```json
{
  "success": false,
  "data": null,
  "meta": { "requestId": "req-001" },
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Tool not found.",
    "details": { "toolName": "unknown_tool" }
  }
}
```

- Invalid invocation arguments -> `INVALID_ARGUMENT`

```json
{
  "success": false,
  "data": null,
  "meta": { "requestId": "req-002" },
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "arguments must be an object",
    "details": null
  }
}
```

- Runtime handler failure -> `INTERNAL_ERROR`
  - MUST remain structured and MUST NOT expose stack traces.

## Validation Notes

- `toolName` is required and must be non-empty.
- `arguments` must be an object when supplied.
- Unknown tools must not execute any handler code.
- Contract behavior remains compatible with FND-001 response envelopes.

## Test Coverage Mapping

- Unit tests: registration validation, duplicate protection, deterministic listing, lookup/dispatch behavior.
- Contract tests: `tools/list` and `tools/call` response envelopes and error shapes.
- Integration tests: register -> list -> call flow and unknown tool call behavior.
