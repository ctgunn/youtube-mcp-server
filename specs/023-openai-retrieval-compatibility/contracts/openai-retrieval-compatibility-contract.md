# Contract: FND-023 OpenAI Retrieval Compatibility

## Purpose

Define the externally visible MCP contract updates required so the foundational `search` and `fetch` tools align with the current OpenAI retrieval compatibility guidance for ChatGPT Apps, deep research, and company-knowledge-style retrieval.

## Scope

- MCP `tools/list` discovery metadata for `search` and `fetch`
- MCP `tools/call` request-shape expectations for the supported OpenAI-compatible retrieval flow
- MCP `tools/call` success-result bodies for OpenAI-compatible `search` and `fetch`
- Stable structured failure behavior for unsupported legacy retrieval shapes and unavailable retrieval targets
- Hosted verification expectations proving the OpenAI-specific flow through protected `/mcp`

## Relationship to Prior Contracts

- This contract extends the baseline retrieval behavior introduced in [deep-research-tools-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/contracts/deep-research-tools-contract.md).
- This contract supersedes the repo-specific retrieval request/result shape documented in [retrieval-tool-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/contracts/retrieval-tool-contract.md) wherever OpenAI compatibility requires a different public contract.
- This contract preserves the MCP-native tool discovery and result transport model established by [tool-metadata-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/contracts/tool-metadata-contract.md) and the hosted security model defined in [hosted-mcp-security.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md).

## External Guidance Source

This contract is based on the OpenAI MCP guide current as of 2026-03-25:

- https://developers.openai.com/api/docs/mcp

The guide states that, for ChatGPT deep research and company knowledge, the MCP server should implement two read-only tools, `search` and `fetch`, using the documented compatibility schema.

## Tool Discovery

### `tools/list` expectations

Discovery MUST include both retrieval tools with descriptions and input shapes sufficient for OpenAI-targeted clients to construct valid calls without undocumented rules.

Representative descriptors:

```json
[
  {
    "name": "search",
    "description": "Search the retrieval corpus for relevant documents.",
    "inputSchema": {
      "type": "object",
      "required": ["query"],
      "properties": {
        "query": { "type": "string", "minLength": 1 }
      },
      "additionalProperties": false
    }
  },
  {
    "name": "fetch",
    "description": "Fetch the full contents of a previously identified document.",
    "inputSchema": {
      "type": "object",
      "required": ["id"],
      "properties": {
        "id": { "type": "string", "minLength": 1 }
      },
      "additionalProperties": false
    }
  }
]
```

Rules:

- `search` and `fetch` MUST remain discoverable through the standard MCP `tools/list` flow.
- Discovery metadata MUST make the OpenAI-compatible request shape the primary published contract.
- Discovery metadata MUST NOT silently imply support for older repo-specific `resourceId`/`uri` fetch inputs unless a documented compatibility path explicitly exists.

## Tool: `search`

### Request params

```json
{
  "name": "search",
  "arguments": {
    "query": "remote MCP research"
  }
}
```

### Success result

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"results\":[{\"id\":\"doc-1\",\"title\":\"Remote MCP Research Workflows\",\"url\":\"https://example.com/remote-mcp-research\"}]}",
      "structuredContent": {
        "results": [
          {
            "id": "doc-1",
            "title": "Remote MCP Research Workflows",
            "url": "https://example.com/remote-mcp-research"
          }
        ]
      }
    }
  ],
  "isError": false
}
```

Rules:

- `query` is the required request argument for the supported OpenAI-compatible `search` flow.
- Successful `search` responses MUST return an object with a single top-level `results` key.
- Each search result MUST include `id`, `title`, and `url`.
- Empty search outcomes MUST return `results: []` and MUST NOT be treated as failures.

## Tool: `fetch`

### Request params

```json
{
  "name": "fetch",
  "arguments": {
    "id": "doc-1"
  }
}
```

### Success result

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"id\":\"doc-1\",\"title\":\"Remote MCP Research Workflows\",\"text\":\"Remote MCP research workflows depend on discoverable tools and stable document retrieval.\",\"url\":\"https://example.com/remote-mcp-research\",\"metadata\":{\"sourceName\":\"Example Research\"}}",
      "structuredContent": {
        "id": "doc-1",
        "title": "Remote MCP Research Workflows",
        "text": "Remote MCP research workflows depend on discoverable tools and stable document retrieval.",
        "url": "https://example.com/remote-mcp-research",
        "metadata": {
          "sourceName": "Example Research"
        }
      }
    }
  ],
  "isError": false
}
```

Rules:

- `id` is the required request argument for the supported OpenAI-compatible `fetch` flow.
- Successful `fetch` responses MUST return `id`, `title`, `text`, and `url`.
- Optional `metadata` MAY be included when useful and safe.
- The `id` returned by `search` MUST be valid for follow-up `fetch` calls.

## Compatibility Boundary

Rules:

- The supported public retrieval contract for FND-023 is the OpenAI-compatible `query`-based `search` input and `id`-based `fetch` input described above.
- If the service temporarily accepts older repo-specific shapes such as `resourceId` or `uri`, that behavior MUST be documented as a compatibility path rather than implied by the primary discovery schema.
- If older shapes are not supported, they MUST fail with stable structured errors that preserve MCP safety and make the contract boundary explicit.

## Failure Contract

Representative categories:

| Category | When It Applies | Expected MCP Error Code Family |
|----------|-----------------|--------------------------------|
| `invalid_argument` | Missing or blank `query`, missing or blank `id`, unsupported extra fields, or unsupported legacy request shapes | Numeric invalid-argument code (`-32602`) |
| `unavailable_source` | `fetch` identifier is validly shaped but does not resolve to an available source | Numeric resource-missing code (`-32001`) or equivalent retrieval-safe numeric code |

Rules:

- Empty `search` is not a failure.
- Failure payloads MUST remain safe for hosted exposure and MUST NOT leak secrets or internal stack traces.
- Unsupported legacy-shape failures MUST be distinguishable from unavailable-source failures.

## Hosted Verification Contract

Protected hosted verification MUST prove:

1. `initialize` succeeds and the protected hosted session is established.
2. `tools/list` exposes the OpenAI-compatible `search` and `fetch` schemas.
3. One valid OpenAI-compatible `search` call succeeds.
4. One valid OpenAI-compatible `fetch` call succeeds using an `id` returned from the discovery or search flow.
5. One empty `search` call returns a successful empty result set.
6. One unsupported legacy-shape retrieval request fails with the documented structured error behavior.
7. One unavailable `fetch` call fails with the documented unavailable-source behavior.

Representative hosted verification check names:

- `search-tool-call-openai`
- `fetch-tool-call-openai`
- `search-tool-call-empty`
- `fetch-tool-call-legacy-shape`
- `fetch-tool-call-missing`

## Testable Assertions

- Unit tests can prove discovery publishes the OpenAI-compatible retrieval schema and rejects unsupported fields predictably.
- Contract tests can prove `tools/list` and `tools/call` match this contract for valid and invalid OpenAI-targeted flows.
- Integration tests can prove a `search` result `id` hands off successfully into `fetch`.
- Hosted verification can prove the same OpenAI-specific retrieval flow works on the protected `/mcp` route.
