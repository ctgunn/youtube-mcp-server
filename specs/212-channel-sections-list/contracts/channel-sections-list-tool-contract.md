# Contract: Layer 2 `channelSections_list` Tool

## Public Tool Identity

- **Tool name**: `channelSections_list`
- **Mapped upstream operation**: `channelSections.list`
- **Resource family**: `channel_sections`
- **Layer**: Layer 2 endpoint-backed public MCP tool
- **Official quota cost**: `1` unit per invocation
- **Auth mode**: `mixed/conditional`
- **Availability**: Active, with selector, deprecated localization, and partner authorization caveats

## Scope

`channelSections_list` retrieves zero or more YouTube channel-section resources through the upstream channel-section listing endpoint and returns the collection in a near-raw shape.

The tool does not:

- Search for channels by arbitrary query text, handle, or username.
- Rank, enrich, summarize, analyze, or recommend channel sections.
- Expand returned channel sections into playlist items, videos, playlists, channels, captions, comments, analytics, or related resources.
- Insert, update, delete, reorder, or otherwise mutate channel sections.
- Call `channelSections.insert`, `channelSections.update`, `channelSections.delete`, `playlistItems.list`, `playlists.list`, `videos.list`, `channels.list`, `search.list`, or analytics endpoints.
- Persist channel-section results or pagination state.

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
    "channelId": {
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
    "hl": {
      "type": "string",
      "minLength": 1,
      "deprecated": true
    },
    "onBehalfOfContentOwner": {
      "type": "string",
      "minLength": 1
    }
  },
  "oneOf": [
    { "required": ["channelId"] },
    { "required": ["id"] },
    { "required": ["mine"] }
  ],
  "additionalProperties": false
}
```

### Input Rules

- `part` is required and must be non-empty.
- Exactly one selector is required from `channelId`, `id`, or `mine`.
- Officially documented part values include `contentDetails`, `id`, and `snippet`.
- `channelId` and `id` are public selector paths in the current contract.
- `mine` is owner-scoped and requires eligible OAuth authorization.
- `mine` must be `true` when used.
- `hl` is deprecated in current official documentation and must be documented as a caveat if exposed.
- `onBehalfOfContentOwner` is authorization-sensitive, intended exclusively for eligible YouTube content partners, and must not be presented as public API-key behavior.
- Pagination request fields such as `pageToken` and `maxResults` are not core official contract fields for this endpoint unless implementation verifies support against the current dependency and contract. If retained for compatibility, their usage notes must state that caveat clearly.
- Unsupported fields, query-search fields, channel update fields, analytics fields, video expansion fields, playlist expansion fields, layout recommendation fields, and enrichment instructions must be rejected or clearly flagged as outside this endpoint contract.

## Discovery Metadata Requirements

Tool discovery metadata must include:

- `name`: `channelSections_list`
- `upstream.resource`: `channelSections`
- `upstream.method`: `list`
- `upstream.operationKey`: `channelSections.list`
- `quotaCost`: `1`
- `authMode`: `mixed/conditional`
- `availabilityState`: active availability with deprecation and partner caveats
- `resourceFamily`: `channel_sections`
- `inputContract`: the public input contract
- `responseConvention`: list-result convention
- `responseBoundary`: near-raw boundary
- `usageNotes`: quota, public selector, owner-scoped OAuth, empty-result, deprecated `hl`, content-owner partner, and optional continuation notes
- `caveats`: selector exclusivity, deprecated localization behavior, partner-scoped content-owner behavior, optional pagination discrepancy, and out-of-scope higher-level channel-section workflow caveats

Discovery descriptions and usage notes must visibly include `Quota cost: 1`.

## Response Contract

Successful responses must preserve the upstream channel-section collection or valid empty collection.

Representative successful shape:

```json
{
  "endpoint": "channelSections.list",
  "quotaCost": 1,
  "items": [
    {
      "kind": "youtube#channelSection",
      "etag": "etag-value",
      "id": "section-123",
      "snippet": {
        "type": "singlePlaylist",
        "channelId": "UC123"
      },
      "contentDetails": {
        "playlists": ["PL123"]
      }
    }
  ],
  "requestedParts": ["snippet", "contentDetails"],
  "selector": {
    "name": "channelId"
  },
  "caveats": {
    "hlDeprecated": true
  }
}
```

Response rules:

- Preserve returned `items` as endpoint-backed channel-section resources.
- Preserve `nextPageToken`, `prevPageToken`, and `pageInfo` when present, but do not require them for success.
- Include requested part names after safe normalization.
- Include the selected selector name in safe operation context.
- Treat a valid no-match lookup as a successful empty `items` collection.
- Include safe operation context such as endpoint identity and quota cost.
- Include safe caveat context where relevant, such as deprecated `hl` use or partner-scoped content-owner behavior.
- Do not fabricate playlist item lists, video metadata, channel analytics, search ranking, layout recommendations, mutation state, or enriched summaries.

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
- Missing channel-section lookup selector.
- Multiple selectors in one request.
- Empty `channelId` or `id`.
- `mine` set to a value other than `true`.
- Unsupported selector aliases such as handle, username, query, playlist ID, or video ID.
- Unsupported request fields or higher-level channel-section workflow fields.
- Unsupported pagination fields if the final public contract does not support them.
- Upstream `idInvalid`.
- Upstream `invalidCriteria`.

Security rules:

- Errors must not expose OAuth tokens, API keys, stack traces, private channel data, or secret values.
- Authorization failures must be distinguishable from valid public lookups that return no channel-section resources.
- `mine` failures must identify the owner-scoped OAuth requirement without exposing user credentials.
- Content-owner failures must identify partner-scoped authorization requirements without exposing CMS account details.

## Required Examples

The implementation must provide safe caller-facing examples for:

- Channel ID lookup through `channelId`.
- Channel-section ID lookup through `id`.
- Authorized owner-scoped lookup through `mine`.
- Successful empty result.
- Deprecated `hl` caveat.
- Content-owner partner caveat when exposed.
- Missing selector validation failure.
- Conflicting selector validation failure.
- Authorization-sensitive `mine` failure.
- Unsupported higher-level workflow rejection.

## Verification Requirements

Before implementation is considered complete:

- Focused contract tests must prove discovery metadata includes endpoint identity, quota cost, mixed auth, supported selectors, OAuth requirement for `mine`, deprecated `hl` caveat, content-owner caveat, empty-result behavior, optional continuation handling, and out-of-scope boundaries.
- Unit tests must prove selector, caveat, and optional pagination validation rejects unsupported inputs safely.
- Integration tests must prove default registration exposes executable `channelSections_list`.
- Handler tests must prove successful result mapping preserves returned items, requested parts, selector context, optional continuation fields when present, caveats, and empty collections.
- Regression tests must preserve existing baseline, retrieval, activities, captions, channel banner, and channels tools.
- Final validation must include `python3 -m pytest` and `python3 -m ruff check .`.
- Every new or changed Python function must include a reStructuredText docstring.
