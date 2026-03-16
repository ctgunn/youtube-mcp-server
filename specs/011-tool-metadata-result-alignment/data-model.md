# Data Model: FND-011 Tool Metadata + Invocation Result Alignment

## Entity: ToolDefinition
Description: The registry-owned MCP-facing definition of one callable tool.

Fields:
- `name` (string, required): Stable tool identifier used for discovery and
  invocation.
- `normalizedName` (string, derived): Canonical lowercase form used for lookup.
- `description` (string, required): Human-readable explanation of the tool's
  purpose.
- `inputSchema` (object, required): Machine-readable input definition exposed
  to clients during discovery.
- `handler` (callable, required for runtime only): Function that executes the
  tool and returns a successful tool payload.

Validation rules:
- `name` MUST be present, non-empty, and unique after normalization.
- `description` MUST be present and non-empty.
- `inputSchema` MUST be an object and remain discoverable without additional
  transformation by clients.
- A tool definition MUST not be exposed through discovery if the registration
  payload is incomplete or invalid.

## Entity: ToolDiscoveryResult
Description: The MCP result returned by `tools/list` containing the complete
catalog view available to a client.

Fields:
- `tools` (list of ToolDefinitionSummary, required): Ordered set of discoverable
  tool descriptors.

Validation rules:
- Discovery output MUST include each registered tool exactly once.
- Discovery output MUST remain deterministic for the same registry state.
- Every listed tool MUST expose the fields clients need to prepare valid
  invocation input.

## Entity: ToolDefinitionSummary
Description: The client-visible subset of a registered tool returned in
discovery responses and by `server_list_tools`.

Fields:
- `name` (string, required): Tool identifier.
- `description` (string, required): Tool purpose.
- `inputSchema` (object, required): Tool input definition.

Validation rules:
- The summary MUST be derived from the registry source of truth.
- `server_list_tools` and `tools/list` MUST return the same descriptor shape.
- The summary MUST stay structurally consistent for baseline tools and newly
  added tools.

## Entity: InvocationResultContent
Description: One MCP content item returned from a successful tool invocation.

Fields:
- `type` (string, required): MCP content item type.
- `text` (string, optional): Human-readable or serialized representation of the
  returned information.
- `structuredContent` (object or list, optional): Structured tool output
  preserved for downstream agent use.

Validation rules:
- Successful tool calls MUST return at least one content item.
- Content items MUST preserve the meaningful output of the tool.
- The same tool and contract version MUST yield the same content-item structure
  for repeated successful invocations.

## Entity: ToolCallSuccessResult
Description: The MCP result returned when a tool invocation succeeds.

Fields:
- `content` (list of InvocationResultContent, required): Ordered content items
  emitted to the client.
- `isError` (boolean, optional): Explicit success/failure marker when included.

Validation rules:
- Success results MUST use MCP-compatible content structures rather than the
  previous simplified wrapper convention.
- Success results MUST not expose internal-only fields from the registry or
  transport layers.

## Entity: BaselineToolPayload
Description: The domain payload returned by `server_ping`, `server_info`, or
`server_list_tools` before it is shaped into MCP result content.

Fields:
- `server_ping` payload: status and timestamp.
- `server_info` payload: version, environment, and build metadata.
- `server_list_tools` payload: list of ToolDefinitionSummary values.

Validation rules:
- Baseline payloads MUST remain available after FND-011.
- Baseline payloads MUST be convertible into aligned MCP result content without
  losing their meaningful fields.

## Relationships

- `ToolDefinition` is the source of truth for `ToolDefinitionSummary`.
- `ToolDiscoveryResult` contains zero or more `ToolDefinitionSummary` values.
- `ToolCallSuccessResult` contains one or more `InvocationResultContent` items.
- `BaselineToolPayload` is transformed into `ToolCallSuccessResult` through the
  protocol success-result shaping layer.

## State Transitions

1. Tool registers successfully -> `ToolDefinition` is stored in the registry.
2. Client requests `tools/list` -> registry definitions are projected into a
   `ToolDiscoveryResult`.
3. Client invokes `server_list_tools` -> baseline tool returns the same
   `ToolDefinitionSummary` values as the discovery path.
4. Client invokes any successful baseline tool -> `BaselineToolPayload` is
   transformed into a `ToolCallSuccessResult`.
5. New tool is added later -> it follows the same `ToolDefinition` to
   `ToolDefinitionSummary` and invocation-content path as baseline tools.
