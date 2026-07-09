# Contract: Layer 2 Tool `playlistItems_list`

## Purpose

Expose YouTube Data API `playlistItems.list` as a low-level public MCP tool named `playlistItems_list`. The contract stays close to the upstream list endpoint while making request validation, quota cost, access expectations, pagination behavior, result context, examples, and safe errors visible to MCP clients.

## Tool Identity

- **Public name**: `playlistItems_list`
- **Layer**: Layer 2 public endpoint-backed MCP tool
- **Mapped upstream operation**: `playlistItems.list`
- **Resource**: `playlistItems`
- **Method**: `list`
- **Official quota cost**: `1` unit per call
- **Access mode**: API-key access for the supported selector set documented by YT-132
- **Availability**: Available unless official documentation or local endpoint metadata records a caveat

## Scope

### In Scope

- Playlist-scoped playlist item retrieval by `playlistId`
- Direct playlist item retrieval by `id`
- Required part selection
- Playlist-scoped pagination with `pageToken` and `maxResults` where supported
- Near-raw list results that preserve returned playlist item fields
- Empty successful list results
- Safe validation, access, quota, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream errors

### Out of Scope

- Playlist item insertion, update, or deletion
- Playlist mutation or playlist management
- Playlist search or ranking
- Video, playlist, channel, transcript, analytics, recommendation, summarization, or enrichment workflows
- Cross-endpoint fan-out or Layer 3 composition
- Persistent playlist-item storage

## Input Schema

The public input schema is an object with no additional properties.

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `part` | Yes | string | Playlist item resource sections to return. Must be non-empty and supported by the shared Layer 1 contract. |
| `playlistId` | Conditional | string | Playlist identifier for playlist-scoped retrieval. Mutually exclusive with `id`. |
| `id` | Conditional | string or supported identifier value | One or more playlist item identifiers for direct lookup, according to the shared contract. Mutually exclusive with `playlistId`. |
| `pageToken` | No | string | Page token for supported playlist-scoped traversal. Must be rejected for selector modes where paging is unsupported. |
| `maxResults` | No | integer | Requested page size within the official supported bounds. Must be rejected when out of range or incompatible with the selected lookup mode. |

## Selector Rules

- Exactly one lookup selector is required.
- `playlistId` and `id` must not appear together.
- Missing selector input must fail with a validation error.
- Empty, malformed, duplicate, excessive, or unsupported selector values must fail with a validation error.
- `playlistId` supports playlist-scoped retrieval and playlist traversal.
- `id` supports direct playlist-item lookup and must not imply playlist traversal unless the shared contract explicitly allows paging for that selector.

## Pagination Rules

- Playlist-scoped retrieval must support requests without a page token.
- Playlist-scoped retrieval must support valid `pageToken` and `maxResults` values.
- Returned page context, including next page token or page summary when available, must be preserved in successful results.
- Empty or malformed page tokens must fail with validation feedback.
- Out-of-range page-size values must fail with validation feedback.
- Paging controls supplied with selector modes that do not support paging must fail with validation feedback.

## Metadata Requirements

Tool discovery metadata must include:

- Public tool name `playlistItems_list`
- Upstream identity `playlistItems.list`
- Resource `playlistItems`
- Method `list`
- Official quota cost `1`
- API-key access expectation for the supported selector set
- Availability state
- Required part-selection guidance
- Supported selector guidance for `playlistId` and `id`
- Selector-specific pagination guidance
- Empty-result behavior
- Out-of-scope workflow boundaries
- Representative caller examples

## Successful Result Shape

A successful result must include safe, MCP-compatible structured data with:

- Endpoint identity `playlistItems.list`
- Source operation identity when included by shared conventions
- Quota cost `1`
- Selected part context
- Lookup selector context
- Pagination context when applicable or returned
- Safe access context
- Returned playlist item collection, including zero or more items
- Returned upstream fields preserved according to selected parts

The result must not fabricate missing optional playlist item fields. It must not enrich returned items with video, playlist, channel, transcript, ranking, analytics, recommendation, summarization, or heuristic data.

## Empty Success

A valid accessible request that returns no playlist items is a successful empty collection. The response must be distinguishable from:

- Missing or invalid `part`
- Missing or conflicting selectors
- Invalid identifiers
- Incompatible pagination
- Access failure
- Quota failure
- Missing-resource failure
- Unavailable upstream service
- Unexpected upstream failure

## Error Contract

Errors must follow shared Layer 2 safe error conventions and must not expose credentials, API keys, OAuth tokens, raw upstream response bodies, stack traces, or unsafe request context.

| Scenario | Expected Category |
|----------|-------------------|
| Missing `part` | validation or invalid request |
| Unsupported or malformed `part` | validation or invalid request |
| Missing selector | validation or invalid request |
| Both `playlistId` and `id` supplied | validation or invalid request |
| Invalid selector value | validation or invalid request |
| Unsupported optional field | validation or invalid request |
| Empty or invalid `pageToken` | validation or invalid request |
| Out-of-range `maxResults` | validation or invalid request |
| Paging supplied with incompatible selector | validation or invalid request |
| Missing, invalid, or insufficient access | access failure |
| Upstream quota limit | quota failure |
| Missing or unavailable resource | missing-resource or upstream failure category |
| Upstream service unavailable | unavailable-service category |
| Deprecated or unavailable endpoint behavior | deprecated-behavior or availability category |
| Unexpected upstream failure | unexpected upstream failure category |

## Representative Examples

### Playlist-Scoped Retrieval

```json
{
  "part": "snippet,contentDetails",
  "playlistId": "PL123"
}
```

Expected outcome: a successful `playlistItems.list` result with quota cost `1`, selector context `playlistId`, selected part context, and zero or more playlist item resources.

### Paginated Playlist Traversal

```json
{
  "part": "snippet",
  "playlistId": "PL123",
  "pageToken": "NEXT_PAGE",
  "maxResults": 25
}
```

Expected outcome: a successful list result that preserves requested paging context and returned page context when available.

### Identifier-Based Retrieval

```json
{
  "part": "id,snippet",
  "id": "playlist-item-123"
}
```

Expected outcome: a successful `playlistItems.list` result with quota cost `1`, selector context `id`, selected part context, and matching playlist item records when available.

### Missing Part

```json
{
  "playlistId": "PL123"
}
```

Expected outcome: safe validation error explaining that part selection is required.

### Conflicting Selectors

```json
{
  "part": "snippet",
  "playlistId": "PL123",
  "id": "playlist-item-123"
}
```

Expected outcome: safe validation error explaining that exactly one supported selector is allowed.

### Unsupported Workflow Request

```json
{
  "part": "snippet",
  "playlistId": "PL123",
  "videoEnrichment": true
}
```

Expected outcome: safe validation error explaining that enrichment and unsupported fields are outside this low-level endpoint tool.

## Acceptance Contract

An implementation satisfies this contract when:

- `playlistItems_list` appears in public tool discovery and default registry output.
- Discovery metadata, description, usage notes, caveats, and examples display `playlistItems.list` and quota cost `1`.
- Valid playlist-scoped, paginated playlist-scoped, and identifier-based requests return near-raw playlist item collection results.
- Empty valid results are successful empty collections.
- Invalid part, selector, pagination, unsupported field, access, quota, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream scenarios are categorized safely and distinctly.
- All new or changed Python functions include reStructuredText docstrings that describe purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
