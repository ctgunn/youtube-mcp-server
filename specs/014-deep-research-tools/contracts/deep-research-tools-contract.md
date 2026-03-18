# Contract: FND-014 Deep Research Tools

## Purpose

Define the externally visible MCP contract for the foundational `search` and `fetch` tools used by deep research consumers.

## Scope

- MCP tool discovery metadata for `search` and `fetch`
- MCP `tools/call` request and success-result bodies for both tools
- Stable failure categories for invalid, unavailable, and empty-result paths
- Hosted verification expectations for protected `/mcp` usage

## Relationship to Prior Contracts

- This contract extends [/Users/ctgunn/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/contracts/tool-metadata-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/contracts/tool-metadata-contract.md) by adding the first non-baseline MCP tools and their result shapes.
- This contract depends on the hosted access rules defined in [/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md).

## Tool Discovery

### `tools/list` expectations

Discovery MUST include both tool definitions with MCP-visible descriptions and input schemas.

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
        "resourceId": { "type": "string" },
        "uri": { "type": "string", "minLength": 1 }
      },
      "additionalProperties": false
    }
  }
]
```

Rules:
- `search` and `fetch` MUST be discoverable through the same `tools/list` flow as baseline tools.
- Discovery metadata MUST be sufficient for a client to form a valid `tools/call` request without separate schema documentation.

## Tool: `search`

### Request params

```json
{
  "name": "search",
  "arguments": {
    "query": "OpenAI Agent Builder remote MCP",
    "pageSize": 3
  }
}
```

### Success result

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"results\":[{\"resourceId\":\"res_001\",\"uri\":\"https://example.com/article\",\"title\":\"Example Article\",\"snippet\":\"Example summary\",\"sourceName\":\"Example\",\"position\":1}],\"totalReturned\":1}",
      "structuredContent": {
        "results": [
          {
            "resourceId": "res_001",
            "uri": "https://example.com/article",
            "title": "Example Article",
            "snippet": "Example summary",
            "sourceName": "Example",
            "position": 1
          }
        ],
        "totalReturned": 1
      }
    }
  ],
  "isError": false
}
```

Rules:
- Successful `search` responses MUST return ordered candidate results in structured form.
- Each result MUST include a stable `resourceId` or equivalent follow-up identifier plus the canonical `uri`.
- Empty search outcomes MUST return `results: []` and MUST NOT be treated as errors.

## Tool: `fetch`

### Request params

```json
{
  "name": "fetch",
  "arguments": {
    "resourceId": "res_001",
    "uri": "https://example.com/article"
  }
}
```

### Success result

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"resourceId\":\"res_001\",\"uri\":\"https://example.com/article\",\"title\":\"Example Article\",\"content\":\"Retrieved article text\",\"excerpt\":\"Retrieved article text\",\"contentType\":\"text/html\",\"retrievalStatus\":\"complete\"}",
      "structuredContent": {
        "resourceId": "res_001",
        "uri": "https://example.com/article",
        "title": "Example Article",
        "content": "Retrieved article text",
        "excerpt": "Retrieved article text",
        "contentType": "text/html",
        "retrievalStatus": "complete"
      }
    }
  ],
  "isError": false
}
```

Rules:
- `fetch` MUST accept a search-derived `resourceId`, a canonical `uri`, or both when they identify the same source.
- Successful `fetch` responses MUST return source identity and consumable content in structured form.
- Partial retrieval MUST be explicit through a retrieval-status field rather than inferred.

## Failure Contract

Representative categories:

| Category | When It Applies | Expected MCP Error Code Family |
|----------|-----------------|--------------------------------|
| `invalid_input` | Missing query, malformed cursor, or conflicting retrieval identifiers | `INVALID_ARGUMENT` |
| `unavailable_source` | Requested source no longer exists or cannot be retrieved | `RESOURCE_NOT_FOUND` or equivalent retrieval-safe code |
| `upstream_failure` | Retrieval dependency fails after valid input | `INTERNAL_ERROR` or mapped service-safe code |

Rules:
- Failure responses MUST preserve the existing MCP-safe error contract from FND-010.
- Empty `search` outcomes are not failures and therefore do not use this table.
- Failure details MUST remain safe for hosted exposure and must not leak secrets or stack traces.

## Hosted Verification Contract

Protected hosted verification MUST prove:

1. `tools/list` exposes both `search` and `fetch`.
2. One valid `search` call succeeds.
3. One valid `fetch` call succeeds for a selected result.
4. One empty or invalid `search` call returns the documented non-error or error behavior.
5. One invalid or unavailable `fetch` call returns the documented error behavior.
6. Hosted verification evidence records distinct `search-tool-call` and `fetch-tool-call` checks.

## Testable Assertions

- Unit tests can prove `search` and `fetch` are registered with valid schemas.
- Contract tests can prove discovery metadata and `tools/call` result bodies match this document.
- Integration tests can prove the `search` -> `fetch` handoff works through the MCP request path.
- Hosted verification can prove the same logical contract holds on the protected `/mcp` endpoint.
