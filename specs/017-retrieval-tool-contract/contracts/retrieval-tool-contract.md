# Contract: FND-017 Retrieval Tool Contract Completeness

## Purpose

Define the externally visible MCP contract updates required so clients can construct valid `search` and `fetch` calls from retrieval-tool discovery output alone.

## Scope

- MCP `tools/list` discovery metadata for `search` and `fetch`
- MCP `tools/call` request-shape expectations for both retrieval tools
- Machine-readable representation of supported `fetch` identifier combinations
- Stable failure behavior for invalid retrieval request shapes
- Hosted verification expectations proving discovery-driven retrieval calls

## Relationship to Prior Contracts

- This contract tightens the retrieval-tool discovery expectations introduced in [/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/contracts/deep-research-tools-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/contracts/deep-research-tools-contract.md).
- This contract preserves the MCP-native discovery and result format defined by [/Users/ctgunn/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/spec.md).
- This contract must remain compatible with the protected hosted access rules already defined in [/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md).

## Tool Discovery

### `tools/list` expectations

Discovery MUST include both retrieval tools with MCP-visible descriptions and input schemas that are sufficient for valid request construction without separate undocumented rules.

Representative descriptors:

```json
[
  {
    "name": "search",
    "description": "Discover relevant sources for deep research workflows.",
    "inputSchema": {
      "type": "object",
      "required": ["query"],
      "properties": {
        "query": { "type": "string", "minLength": 1 },
        "pageSize": { "type": "integer", "minimum": 1 },
        "cursor": { "type": "string" }
      },
      "additionalProperties": false
    }
  },
  {
    "name": "fetch",
    "description": "Retrieve a selected source in consumable content form.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "resourceId": { "type": "string", "minLength": 1 },
        "uri": { "type": "string", "minLength": 1 }
      },
      "oneOf": [
        { "required": ["resourceId"] },
        { "required": ["uri"] },
        { "required": ["resourceId", "uri"] }
      ],
      "additionalProperties": false
    }
  }
]
```

Rules:
- `search` and `fetch` MUST be discoverable through the standard `tools/list` flow.
- Discovery metadata MUST describe the required `search` query input and the supported optional controls.
- Discovery metadata MUST machine-readably describe that `fetch` accepts `resourceId`, `uri`, or both together.
- Discovery metadata MUST not imply that a request with neither identifier is valid.
- Discovery metadata and runtime validation MUST stay aligned for the same request shapes.

## Tool: `search`

### Request params

```json
{
  "name": "search",
  "arguments": {
    "query": "remote MCP research",
    "pageSize": 2
  }
}
```

Rules:
- `query` is required.
- `pageSize` and `cursor` are optional and MUST follow the published field restrictions.
- Unsupported extra fields MUST be rejected.

## Tool: `fetch`

### Supported request shapes

Valid by `resourceId`:

```json
{
  "name": "fetch",
  "arguments": {
    "resourceId": "res_remote_mcp_001"
  }
}
```

Valid by `uri`:

```json
{
  "name": "fetch",
  "arguments": {
    "uri": "https://example.com/remote-mcp-research"
  }
}
```

Valid by matching identifiers:

```json
{
  "name": "fetch",
  "arguments": {
    "resourceId": "res_remote_mcp_001",
    "uri": "https://example.com/remote-mcp-research"
  }
}
```

Rules:
- `fetch` MUST accept a valid request identified by `resourceId` alone.
- `fetch` MUST accept a valid request identified by `uri` alone.
- `fetch` MUST accept both identifiers together when they refer to the same source.
- `fetch` MUST reject a request with no identifiers.
- `fetch` MUST reject a request whose identifiers conflict.
- Unsupported extra fields MUST be rejected.

## Failure Contract

Representative categories:

| Category | When It Applies | Expected MCP Error Code Family |
|----------|-----------------|--------------------------------|
| `invalid_input` | Missing required `search` query, malformed retrieval fields, missing `fetch` identifiers, or conflicting `fetch` identifiers | Numeric invalid-argument code (`-32602`) |
| `unavailable_source` | `fetch` identifiers are well-formed but do not resolve to an available source | Numeric resource-missing code (`-32001`) or equivalent retrieval-safe numeric code |

Rules:
- Invalid retrieval shapes MUST fail with stable structured errors.
- Empty `search` results remain a successful non-error outcome and do not use the failure categories above.
- Failure payloads MUST remain safe for hosted exposure and MUST NOT leak secrets or internal stack traces.

## Hosted Verification Contract

Protected hosted verification MUST prove:

1. `tools/list` exposes both retrieval tools with the complete discovery contract.
2. One valid `search` call can be built from discovery output and succeeds.
3. One valid `fetch` call using `resourceId` succeeds.
4. One valid `fetch` call using `uri` succeeds.
5. One valid `fetch` call using matching `resourceId` and `uri` succeeds.
6. One invalid `fetch` call with no identifiers fails with the documented error behavior.
7. One invalid `fetch` call with conflicting identifiers fails with the documented error behavior.

Representative hosted verification check names:

- `search-tool-call`
- `fetch-tool-call-resource-id`
- `fetch-tool-call-uri`
- `fetch-tool-call-both`
- `fetch-tool-call-missing`
- `fetch-tool-call-conflict`

## Testable Assertions

- Unit tests can prove the discovery schema exposes the supported retrieval request shapes.
- Contract tests can prove `tools/list` and `tools/call` behavior stay aligned for valid and invalid retrieval requests.
- Integration tests can prove `search` results can still hand off to valid `fetch` calls after the contract is tightened.
- Hosted verification can prove discovery-driven retrieval requests work on the protected `/mcp` route without undocumented assumptions.
