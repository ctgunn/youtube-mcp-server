# Data Model: MCP Transport + Handshake (FND-001)

## Entity: MCPRequest
Description: Incoming MCP message for initialize, list tools, or invoke tool.

Fields:
- `jsonrpc` (string, required): Must be `"2.0"` when present.
- `id` (string | number | null, optional): Client correlation identifier.
- `method` (string, required): Supported values in FND-001:
  - `initialize`
  - `tools/list`
  - `tools/call`
- `params` (object, optional): Method-specific payload.

Validation rules:
- `method` MUST be non-empty and supported.
- `params` MUST be an object when provided.
- Invalid shape MUST map to structured MCP-safe error responses.

## Entity: MCPResponseEnvelope
Description: Standard response returned by transport for all handled methods.

Fields:
- `success` (boolean, required)
- `data` (object | array | null, required)
- `meta` (object, required)
  - `requestId` (string | number | null)
- `error` (object | null, required)
  - `code` (string, required when error exists)
  - `message` (string, required when error exists)
  - `details` (object | null, optional)

Validation rules:
- `success=true` requires `error=null`.
- `success=false` requires error object with `code` and `message`.
- Stack traces or internal implementation details MUST NOT appear in `message`
  or `details`.

## Entity: CapabilityDescriptor
Description: Declares server identity/capabilities in initialize response.

Fields:
- `serverName` (string, required)
- `serverVersion` (string, required)
- `capabilities` (object, required)
  - `tools` (object, required)

Validation rules:
- Capability declaration MUST remain deterministic across requests for same build.

## Entity: ToolDescriptor
Description: Metadata for discoverable tools returned by list operation.

Fields:
- `name` (string, required)
- `description` (string, required)
- `inputSchema` (object, optional in FND-001 stub responses)

Validation rules:
- `name` MUST be unique per response.
- Tool listing order SHOULD be deterministic.

## Entity: ToolInvocation
Description: Invocation request payload and result for `tools/call`.

Fields:
- `toolName` (string, required)
- `arguments` (object, optional)
- `result` (object | array | primitive | null)

Validation rules:
- Unknown `toolName` MUST return `RESOURCE_NOT_FOUND`.
- Invalid `arguments` shape MUST return validation error code.

## Relationships

- `MCPRequest` (method=`initialize`) -> returns `MCPResponseEnvelope(data=CapabilityDescriptor)`.
- `MCPRequest` (method=`tools/list`) -> returns `MCPResponseEnvelope(data=ToolDescriptor[])`.
- `MCPRequest` (method=`tools/call`) -> uses `ToolInvocation` and returns `MCPResponseEnvelope`.

## State Transitions

- Request received -> validated -> routed by method -> handler result/error ->
  envelope emitted.
- Any validation or runtime failure -> mapped through error model ->
  failure envelope emitted.
