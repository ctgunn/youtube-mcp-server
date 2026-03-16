# Data Model: FND-010 MCP Protocol Contract Alignment

## Entity: MCPProtocolRequest
Description: A client-issued protocol message accepted by the server for
initialization, tool discovery, tool invocation, or a failure path.

Fields:
- `jsonrpc` (string, required): Protocol version marker expected on incoming
  requests.
- `id` (string or number, optional): Request identifier echoed on responses
  when the interaction expects a response.
- `method` (string, required): Requested lifecycle action such as
  `initialize`, `tools/list`, or `tools/call`.
- `params` (object, optional): Method-specific input payload.
- `sessionId` (string, optional): Hosted session identifier carried at the
  transport layer for non-initialize hosted calls.

Validation rules:
- `method` MUST be present and non-empty for all covered request flows.
- `params` MUST be an object when supplied.
- `tools/call` requests MUST include a non-empty tool identifier and an object
  of arguments.
- Requests missing required protocol structure MUST fail before tool dispatch.

## Entity: MCPInitializeResult
Description: The protocol-native result returned when a client successfully
initializes the server.

Fields:
- `protocolVersion` (string, required): The protocol version the server agrees
  to use for the interaction.
- `serverInfo` (object, required): Visible server identity metadata.
- `capabilities` (object, required): Supported server capabilities available
  after initialization.
- `instructions` (string, optional): Human-readable initialization guidance if
  exposed by the server contract.

Validation rules:
- The result MUST not be wrapped in legacy `success/data/meta/error` fields.
- `capabilities` MUST reflect the behaviors currently supported by the server.

## Entity: MCPToolDescriptor
Description: The discoverable MCP-facing summary of one registered tool.

Fields:
- `name` (string, required): Stable tool identifier.
- `description` (string, required): Human-readable purpose of the tool.
- `inputSchema` (object, optional in this slice): Invocation schema metadata
  when already available through the current registry surface.

Validation rules:
- Each descriptor MUST map to a registered tool that can be invoked by name.
- Discovery results MUST stay consistent with the baseline tool set available
  after FND-003.

## Entity: MCPToolCallResult
Description: The protocol-native content returned when a registered tool
completes successfully.

Fields:
- `content` (list, required): Ordered result content items returned to the
  client.
- `isError` (boolean, optional): Explicit tool-level failure marker when the
  call returns a tool-result error instead of a protocol error.
- `toolName` (string, derived): The tool invoked to produce the result.

Validation rules:
- Successful tool invocation MUST return MCP-compatible result content rather
  than the current wrapper object containing `toolName` and `result`.
- Result content MUST be deterministic for the same tool output shape.

## Entity: MCPProtocolError
Description: A protocol-native failure payload returned for malformed requests,
unsupported methods, invalid arguments, or internal execution failures.

Fields:
- `code` (string or integer, required): Stable protocol error identifier.
- `message` (string, required): Sanitized client-visible error message.
- `data` (object, optional): Structured failure details safe to expose.
- `requestId` (string or number, optional): Request identifier echoed when the
  failed interaction included one.

Validation rules:
- Errors MUST not expose stack traces, secret values, or server-only internal
  diagnostics.
- The same failure category MUST map to the same protocol error shape across
  local and hosted environments.
- Unsupported methods and malformed requests MUST use protocol-native errors
  rather than transport-only failures when a protocol body is returned.

## Entity: HostedProtocolExchange
Description: One end-to-end hosted MCP interaction after FND-009 transport
validation succeeds and the request reaches protocol handling.

Fields:
- `transportMode` (string, required): `json_response`, `sse_response`, or
  `accepted_no_body`.
- `sessionId` (string, optional): Hosted session used for the exchange.
- `request` (MCPProtocolRequest, required): Normalized request entering the
  protocol layer.
- `outcome` (MCPInitializeResult, list of MCPToolDescriptor, MCPToolCallResult,
  or MCPProtocolError): The protocol-level response body for the exchange.

Validation rules:
- Hosted JSON and SSE flows MUST carry the same protocol payload shapes for the
  same logical request outcome.
- Session handling MUST remain a transport concern; protocol payload shapes
  must remain consistent regardless of delivery mode.

## Relationships

- `MCPProtocolRequest` resolves to exactly one of `MCPInitializeResult`, a list
  of `MCPToolDescriptor`, `MCPToolCallResult`, or `MCPProtocolError` when a
  response is required.
- `HostedProtocolExchange` carries one `MCPProtocolRequest` and one protocol
  outcome through the existing hosted transport.
- `MCPToolDescriptor` and `MCPToolCallResult` depend on the current registered
  baseline tools and dispatcher behavior.

## State Transitions

1. Client sends `MCPProtocolRequest` for `initialize` -> server returns
   `MCPInitializeResult`.
2. Initialized client sends `tools/list` request -> server returns a list of
   `MCPToolDescriptor`.
3. Initialized client sends `tools/call` request -> server returns
   `MCPToolCallResult` on success.
4. Client sends malformed, unsupported, or invalid request -> server returns
   `MCPProtocolError`.
5. Hosted delivery chooses JSON or SSE transport mode -> the protocol outcome
   remains unchanged while the transport framing varies.
