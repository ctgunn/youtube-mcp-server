# Contract: FND-018 JSON-RPC / MCP Error Code Alignment

## Purpose

Define the external MCP error-code contract changes required to replace string-style server error codes with a numeric JSON-RPC / MCP-aligned mapping across covered local and hosted failure flows.

## Scope

- Local MCP request validation, method routing, tool-dispatch, and tool-failure responses
- Hosted `/mcp` request failures that return MCP error payloads
- Numeric `error.code` mapping for covered malformed request, unsupported method, invalid argument, auth or authorization denial, resource-missing, and unexpected execution failures
- Stable `error.data.category` detail and precedence rules for ambiguous failures
- Hosted verification and deployment evidence proving local and hosted parity

## Relationship to Prior Contracts

- This contract tightens the error mapping defined by [~/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/contracts/mcp-protocol-contract.md](~/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/contracts/mcp-protocol-contract.md), which currently documents string-style codes.
- This contract preserves the hosted access-control and status-family behavior defined by [~/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md](~/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md).
- This contract must remain compatible with the streamable hosted transport expectations defined by [~/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/contracts/mcp-streamable-http-contract.md](~/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/contracts/mcp-streamable-http-contract.md).
- This contract also updates downstream tool contracts that still refer to string-style failure codes, including retrieval-tool error examples introduced in prior features.

## Common Error Shape

```json
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "error": {
    "code": -32602,
    "message": "arguments must be an object",
    "data": {
      "category": "invalid_argument"
    }
  }
}
```

Rules:
- `error.code` MUST be numeric for covered MCP error responses.
- `error.message` MUST remain sanitized and safe for client consumption.
- `error.data.category` SHOULD carry the stable category detail clients and operators can use for finer-grained handling.
- `error.data` MAY include safe contextual fields such as `toolName`, `sessionId`, or denial reason, but MUST NOT include secrets, raw exception objects, or stack traces.

## Numeric Code Mapping

### Core protocol-aligned codes

| Failure category | Numeric code | Notes |
|------------------|--------------|-------|
| `malformed_request` | `-32600` | Request body or top-level protocol shape is invalid. |
| `unsupported_method` | `-32601` | Method is not supported by the MCP service. |
| `invalid_argument` | `-32602` | Supported operation received invalid arguments or unsupported fields. |
| `internal_execution_failure` | `-32603` | Unexpected execution failure with no safer client-correctable classification. |

### Reserved service-extension codes

| Failure category | Numeric code | Notes |
|------------------|--------------|-------|
| `resource_missing` | `-32001` | Unknown tool, missing session, expired session, or other covered lookup failure. |
| `unauthenticated` | `-32002` | Missing, malformed, invalid, expired, or environment-mismatched credential. |
| `forbidden` | `-32003` | Access denied after request classification, including denied browser origin. |
| `transport_not_supported` | `-32004` | Covered hosted negotiation or replay failures that do not fit the core protocol set. |

Rules:
- Covered failures MUST map to the table above rather than to string-style codes such as `INVALID_ARGUMENT`, `METHOD_NOT_SUPPORTED`, `UNAUTHENTICATED`, or `ORIGIN_DENIED`.
- The extension-code set MUST stay small and stable; new categories require explicit contract updates.
- Downstream contract examples MUST assert numeric codes, not the retired string values.

## Category Detail Mapping

Representative `error.data.category` values:

| Numeric code | Representative categories |
|--------------|---------------------------|
| `-32600` | `malformed_request`, `invalid_json`, `malformed_security_input` |
| `-32601` | `unsupported_method`, `unsupported_browser_method`, `unsupported_browser_route` |
| `-32602` | `invalid_argument`, `unsupported_media_type`, `unsupported_headers`, `replay_unavailable` |
| `-32603` | `internal_execution_failure` |
| `-32001` | `unknown_tool`, `session_not_found`, `expired_session`, `unavailable_source` |
| `-32002` | `unauthenticated`, `invalid_credential` |
| `-32003` | `origin_denied`, `authorization_denied` |
| `-32004` | `transport_not_supported` |

Rules:
- `category` carries the project-specific nuance that was previously encoded directly into the top-level string code.
- Equivalent local and hosted failures MUST return the same top-level numeric code and the same stable `category` value.

## Precedence Rules

1. Security denials at the hosted edge take precedence over later protocol or tool validation because protected processing must not continue after denial.
2. Malformed request shape takes precedence over invalid-argument classification when the request cannot be safely interpreted as a supported operation.
3. Unsupported method takes precedence over argument validation because unsupported operations are rejected before operation-specific validation begins.
4. Resource-missing takes precedence over internal failure when the service can determine the request targets a missing tool, session, or resource without an unexpected exception.
5. Internal execution failure is the fallback only when no more specific covered category applies safely.

## Representative Contract Cases

### Unsupported method

```json
{
  "jsonrpc": "2.0",
  "id": "req-method",
  "error": {
    "code": -32601,
    "message": "Method is not supported.",
    "data": {
      "category": "unsupported_method",
      "method": "unknown/method"
    }
  }
}
```

### Unknown tool

```json
{
  "jsonrpc": "2.0",
  "id": "req-tool",
  "error": {
    "code": -32001,
    "message": "Tool not found.",
    "data": {
      "category": "unknown_tool",
      "toolName": "missing_tool"
    }
  }
}
```

### Hosted authentication denial

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32002,
    "message": "Authentication is required.",
    "data": {
      "category": "unauthenticated"
    }
  }
}
```

Rules:
- Hosted authentication denial may still return HTTP `401`, but the MCP body uses the numeric code contract above.
- Hosted origin denial may still return HTTP `403`, but the MCP body uses `-32003` with `category = "origin_denied"`.

## Hosted Verification Contract

Covered hosted verification MUST prove:

1. Malformed JSON or malformed request shape returns the documented numeric malformed-request code.
2. Unsupported MCP method returns the documented numeric unsupported-method code.
3. Invalid MCP arguments return the documented numeric invalid-argument code.
4. Missing or invalid hosted authentication returns the documented numeric unauthenticated code while preserving the existing status family.
5. Unknown tool or missing session returns the documented numeric resource-missing code.
6. Unexpected tool execution failure returns the documented numeric internal-execution code without leaking internal details.
7. Equivalent local and hosted representative failures return the same numeric code and category detail.

## Testable Assertions

- Unit tests can prove the shared mapper emits numeric codes and stable categories for protocol, tool, and security-related failures.
- Contract tests can prove local and hosted MCP bodies use the same numeric code mapping for equivalent covered scenarios.
- Integration tests can prove HTTP statuses and access-control behavior remain unchanged while the MCP body changes to the aligned numeric code set.
- Deployment verification can prove hosted smoke checks and failure-path checks use numeric codes consistently in Cloud Run evidence.
