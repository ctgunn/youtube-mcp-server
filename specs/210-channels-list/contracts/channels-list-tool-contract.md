# Contract: Layer 2 `channels_list` Tool

## Public Tool Identity

- **Tool name**: `channels_list`
- **Mapped upstream operation**: `channels.list`
- **Resource family**: `channels`
- **Layer**: Layer 2 endpoint-backed public MCP tool
- **Official quota cost**: `1` unit per invocation
- **Auth mode**: `mixed/conditional`
- **Availability**: Active, with selector and authorization caveats

## Scope

`channels_list` retrieves zero or more YouTube channel resources through the upstream channel listing endpoint and returns the channel collection in a near-raw shape.

The tool does not:

- Search channels by arbitrary query text.
- Rank, enrich, summarize, or analyze channels.
- Expand returned channels into videos, playlists, subscriptions, analytics, comments, captions, or branding data beyond requested channel resource parts.
- Update channel metadata or branding.
- Call `channels.update`, `search.list`, `playlistItems.list`, `playlists.list`, or analytics endpoints.
- Persist channel results or pagination state.

## Input Contract

The input is a JSON-compatible object.

```json
{
  "type": "object",
  "required": ["part"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1
    },
    "id": {
      "type": "string",
      "minLength": 1
    },
    "mine": {
      "type": "boolean"
    },
    "forHandle": {
      "type": "string",
      "minLength": 1
    },
    "forUsername": {
      "type": "string",
      "minLength": 1
    },
    "pageToken": {
      "type": "string",
      "minLength": 1
    },
    "maxResults": {
      "type": "integer",
      "minimum": 0,
      "maximum": 50
    },
    "hl": {
      "type": "string",
      "minLength": 1
    }
  },
  "oneOf": [
    { "required": ["id"] },
    { "required": ["mine"] },
    { "required": ["forHandle"] },
    { "required": ["forUsername"] }
  ],
  "additionalProperties": false
}
```

### Input Rules

- `part` is required and must be non-empty.
- Exactly one selector is required from `id`, `mine`, `forHandle`, or `forUsername`.
- `id`, `forHandle`, and `forUsername` are public selector paths in the current contract.
- `mine` is owner-scoped and requires eligible OAuth authorization.
- `forHandle` identifies a YouTube handle and may include an `@` prefix.
- `forUsername` is the username-style lookup selector and should be documented with legacy username caveats where relevant.
- `pageToken`, `maxResults`, and `hl` are optional endpoint modifiers when supported.
- `maxResults` must stay within the endpoint-supported page-size range.
- Unsupported fields, query-search fields, channel update fields, analytics fields, video expansion fields, playlist expansion fields, and enrichment instructions must be rejected or clearly flagged as outside this endpoint contract.

## Discovery Metadata Requirements

Tool discovery metadata must include:

- `name`: `channels_list`
- `upstream.resource`: `channels`
- `upstream.method`: `list`
- `upstream.operationKey`: `channels.list`
- `quotaCost`: `1`
- `authMode`: `mixed/conditional`
- `availabilityState`: active availability
- `resourceFamily`: `channels`
- `inputContract`: the public input contract
- `responseConvention`: list-result convention
- `responseBoundary`: near-raw boundary
- `usageNotes`: quota, public selector, owner-scoped OAuth, pagination, empty-result, and selector-exclusivity notes
- `caveats`: selector and out-of-scope higher-level channel workflow caveats

Discovery descriptions and usage notes must visibly include `Quota cost: 1`.

## Response Contract

Successful responses must preserve the upstream channel collection or valid empty collection.

Representative successful shape:

```json
{
  "endpoint": "channels.list",
  "quotaCost": 1,
  "items": [
    {
      "kind": "youtube#channel",
      "etag": "etag-value",
      "id": "UC123",
      "snippet": {
        "title": "Example Channel"
      }
    }
  ],
  "requestedParts": ["snippet"],
  "selector": {
    "name": "id"
  },
  "nextPageToken": "NEXT_PAGE",
  "pageInfo": {
    "totalResults": 1,
    "resultsPerPage": 1
  }
}
```

Response rules:

- Preserve returned `items` as endpoint-backed channel resources.
- Preserve `nextPageToken`, `prevPageToken`, and `pageInfo` when present.
- Include requested part names after safe normalization.
- Include the selected selector name in safe operation context.
- Treat a valid no-match lookup as a successful empty `items` collection.
- Include safe operation context such as endpoint identity and quota cost.
- Do not fabricate channel analytics, search ranking, video lists, playlist lists, branding update state, or enriched summaries.

## Error Contract

The tool must surface safe shared Layer 2 error categories:

- `invalid_request`
- `authentication_failed`
- `authorization_failed`
- `quota_exhausted`
- `resource_not_found`
- `endpoint_unavailable`
- `upstream_failure`

Endpoint-specific invalid request examples:

- Missing `part`.
- Missing channel lookup selector.
- Multiple selectors in one request.
- Empty `id`, `forHandle`, or `forUsername`.
- `mine` set to a value other than `true`.
- Malformed handle value.
- `maxResults` outside the endpoint-supported range.
- Unsupported request fields or higher-level channel workflow fields.
- Upstream `invalidCriteria`.

Security rules:

- Errors must not expose OAuth tokens, API keys, stack traces, private channel data, or secret values.
- Authorization failures must be distinguishable from valid public lookups that return no channel resources.
- `mine` failures must identify the owner-scoped OAuth requirement without exposing user credentials.

## Required Examples

The implementation must provide safe caller-facing examples for:

- Channel ID lookup.
- Handle lookup through `forHandle`.
- Username-style lookup through `forUsername`.
- Authorized owner-scoped lookup through `mine`.
- Paginated continuation.
- Successful empty result.
- Missing selector validation failure.
- Conflicting selector validation failure.
- Authorization-sensitive `mine` failure.

## Verification Requirements

Before implementation is considered complete:

- Focused contract tests must prove discovery metadata includes endpoint identity, quota cost, mixed auth, supported selectors, OAuth requirement for `mine`, pagination notes, empty-result behavior, and out-of-scope boundaries.
- Unit tests must prove selector and pagination validation rejects unsupported inputs safely.
- Integration tests must prove default registration exposes executable `channels_list`.
- Handler tests must prove successful result mapping preserves returned items, requested parts, selector context, pagination, and empty collections.
- Regression tests must preserve existing baseline, retrieval, activities, captions, and channel banner tools.
- Final validation must include `python3 -m pytest` and `python3 -m ruff check .`.
- Every new or changed Python function must include a reStructuredText docstring.
