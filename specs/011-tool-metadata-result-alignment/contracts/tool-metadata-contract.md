# Contract: FND-011 Tool Metadata + Invocation Result Alignment

## Purpose

Define the externally visible MCP contract for complete tool discovery metadata
and aligned successful tool invocation results after FND-010 established the
protocol-native request and error envelope.

## Scope

- MCP `tools/list` result shape for registered tools
- MCP `tools/call` success result shape for baseline tools
- Registry-backed consistency between `tools/list` and `server_list_tools`
- Local and hosted parity for the same discovery and successful invocation
  behavior

## Relationship to Prior Contracts

- This contract extends
  `/specs/010-mcp-protocol-alignment/contracts/mcp-protocol-contract.md` by
  defining richer MCP-facing tool metadata and success-result content.
- This contract does not replace the hosted transport/session rules in
  `/specs/009-mcp-streamable-http-transport/contracts/mcp-streamable-http-contract.md`;
  it defines the discovery and successful invocation bodies carried by that
  transport.

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
      "description": "Return service status and timestamp",
      "inputSchema": {
        "type": "object",
        "properties": {},
        "additionalProperties": false
      }
    }
  ]
}
```

Rules:
- Every discoverable tool includes `name`, `description`, and `inputSchema`.
- `inputSchema` is the machine-readable invocation definition clients use to
  prepare arguments.
- Discovery results remain deterministic for the same registry state.
- Baseline tools and future tools use the same descriptor shape.

## Tool: `server_list_tools`

### Request params

```json
{}
```

### Success result requirements

- The logical tool payload matches the `tools` array returned from `tools/list`.
- The tool remains callable through `tools/call` like the other baseline tools.
- The successful tool result uses the same aligned MCP content contract defined
  below for all successful tool calls.

## Method: `tools/call`

### Request params

```json
{
  "name": "server_ping",
  "arguments": {}
}
```

### Success result

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"status\":\"ok\",\"timestamp\":\"2026-03-16T00:00:00Z\"}",
      "structuredContent": {
        "status": "ok",
        "timestamp": "2026-03-16T00:00:00Z"
      }
    }
  ],
  "isError": false
}
```

Rules:
- Successful tool calls return one or more MCP content items.
- Content items preserve the meaningful output of the tool in structured form.
- The result shape is stable for repeated successful invocations of the same
  tool under the same contract version.
- The result no longer relies only on the previous simplified convention of
  putting the entire payload inside one JSON string.

## Baseline Tool Result Expectations

- `server_ping` success content preserves `status` and `timestamp`.
- `server_info` success content preserves `version`, `environment`, and build
  metadata.
- `server_list_tools` success content preserves the same complete tool
  descriptors returned by `tools/list`.

## Invalid Registry Definition Handling

- Tools with invalid or incomplete registration payloads are rejected before
  they can appear in discovery results.
- Clients are never shown partially defined tool metadata as if it were valid.

## Testable Assertions

- Contract tests can prove `tools/list` includes `inputSchema` for each listed
  baseline tool.
- Unit and integration tests can prove `server_list_tools` matches the richer
  `tools/list` descriptors.
- Contract and integration tests can prove successful baseline tool invocations
  return aligned MCP content with preserved structured meaning.
- Hosted and local flows produce the same logical discovery and success-result
  bodies for the same requests.
