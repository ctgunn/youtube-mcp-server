# Contract: `playlists_list`

## Public Identity

- **Tool name**: `playlists_list`
- **Layer**: Layer 2 public MCP endpoint tool
- **Mapped operation**: YouTube resource `playlists`, method `list`
- **Operation key**: `playlists.list`
- **Quota cost**: `1` official quota unit per invocation
- **Availability**: Active unless implementation discovers an official documentation caveat that must be recorded
- **Scope**: Low-level playlist retrieval only

## Discovery Metadata Requirements

Discovery metadata, descriptions, usage notes, caveats, and examples must make the following visible before invocation:

- Public tool name `playlists_list`
- Upstream operation `playlists.list`
- Quota cost `1`
- Conditional access behavior:
  - `channelId` and `id` are public lookup paths
  - `mine` is owner-scoped and requires eligible OAuth-backed access
- Required `part` selection
- Exactly one selector from `channelId`, `id`, or `mine`
- Selector-specific pagination behavior
- Successful empty collection behavior
- Safe failure categories
- Out-of-scope workflows, including playlist insertion, update, deletion, playlist item traversal, playlist image handling, playlist search, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, and cross-endpoint enrichment

## Input Contract

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
    "pageToken": {
      "type": "string",
      "minLength": 1
    },
    "maxResults": {
      "type": "integer",
      "minimum": 0,
      "maximum": 50
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

## Input Validation Rules

- `part` is required and must contain supported playlist part selection.
- Exactly one selector from `channelId`, `id`, and `mine` must be present.
- `channelId` must be a non-empty string when used.
- `id` must be a non-empty playlist identifier string or supported identifier list representation when used.
- `mine` must select owner-scoped retrieval and requires eligible OAuth-backed access.
- `pageToken` must be non-empty when present.
- `maxResults` must be an integer within the supported list limit.
- `pageToken` and `maxResults` are accepted for collection-style `channelId` and `mine` retrieval.
- `pageToken` and `maxResults` are rejected for direct `id` lookup unless a shared contract intentionally allows identifier paging.
- Unsupported fields and out-of-scope workflow modifiers are rejected before endpoint execution.

## Success Result Contract

Successful calls return a near-raw playlist collection with safe context:

```json
{
  "endpoint": "playlists.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "selector": {
    "name": "channelId",
    "value": "UC123"
  },
  "auth": {
    "mode": "api_key"
  },
  "pagination": {
    "requestPageToken": "NEXT_PAGE",
    "requestMaxResults": 25,
    "nextPageToken": "FOLLOWING_PAGE",
    "resultCount": 1
  },
  "items": [
    {
      "id": "PL123",
      "snippet": {
        "title": "Example playlist"
      }
    }
  ],
  "empty": false
}
```

Result rules:
- `endpoint` must be `playlists.list`.
- `quotaCost` must be `1`.
- `requestedParts` must reflect caller-selected parts.
- `selector` must identify the active lookup mode without exposing sensitive input.
- `auth` must identify the safe access mode, not credentials.
- `pagination` must appear when paging context exists or is useful for traversal.
- `items` may be empty for successful no-match or empty collection outcomes.
- Returned playlist fields must preserve upstream data for selected parts without fabricated playlist item, video, channel, image, transcript, analytics, ranking, or enrichment fields.

## Error Contract

Failures must use safe caller-facing categories and sanitized details:

- `invalid_request`: Missing part, invalid part, missing selector, conflicting selectors, malformed selector, unsupported paging, out-of-range max results, unsupported field, or out-of-scope workflow request
- `authentication_failed`: Required credential material missing or invalid
- `authorization_failed`: Caller lacks access for owner-scoped retrieval or selected resource
- `quota_exhausted`: Upstream quota failure
- `resource_not_found`: Upstream missing-resource or unavailable selected resource
- `upstream_unavailable`: Upstream service unavailable or timeout category
- `deprecated`: Official endpoint behavior is deprecated or unavailable
- `upstream_error`: Unexpected upstream failure after sanitization

Error details must not include API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, raw request context, or secret-bearing diagnostics.

## Representative Examples

### Channel-Scoped Retrieval

```json
{
  "part": "snippet,contentDetails",
  "channelId": "UC123"
}
```

Expected context:
- Endpoint `playlists.list`
- Quota cost `1`
- Selector `channelId`
- Public access mode
- Playlist collection result

### Identifier-Based Retrieval

```json
{
  "part": "id,snippet",
  "id": "PL123"
}
```

Expected context:
- Endpoint `playlists.list`
- Quota cost `1`
- Selector `id`
- Public access mode
- Direct playlist collection result

### Owner-Scoped Retrieval

```json
{
  "part": "snippet",
  "mine": true
}
```

Expected context:
- Endpoint `playlists.list`
- Quota cost `1`
- Selector `mine`
- OAuth-backed access mode
- Owner-scoped playlist collection result

### Paginated Collection Traversal

```json
{
  "part": "snippet",
  "channelId": "UC123",
  "pageToken": "NEXT_PAGE",
  "maxResults": 25
}
```

Expected context:
- Endpoint `playlists.list`
- Quota cost `1`
- Pagination request context
- Returned continuation context when available

### Empty Successful Collection

```json
{
  "part": "snippet",
  "channelId": "UC_NO_PLAYLISTS"
}
```

Expected context:
- Successful result
- Empty `items`
- No validation, access, or upstream failure category

### Missing Part Failure

```json
{
  "channelId": "UC123"
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `part`

### Conflicting Selector Failure

```json
{
  "part": "snippet",
  "channelId": "UC123",
  "id": "PL123"
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying selector conflict

### Unsupported Paging Failure

```json
{
  "part": "snippet",
  "id": "PL123",
  "pageToken": "NEXT_PAGE"
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying selector-incompatible paging

### Owner-Scoped Access Failure

```json
{
  "part": "snippet",
  "mine": true
}
```

Expected error when OAuth-backed access is missing:
- Category `authentication_failed` or `authorization_failed`
- Safe detail identifying owner-scoped access requirement

### Out-of-Scope Workflow Failure

```json
{
  "part": "snippet",
  "channelId": "UC123",
  "includePlaylistItems": true
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying unsupported workflow expansion

## Compatibility Requirements

- Must comply with YT-201 shared Layer 2 contracts.
- Must comply with YT-202 metadata standards.
- Must rely on YT-136 Layer 1 `playlists.list` wrapper behavior.
- Must be registered in the default tool registry when implemented.
- Must be visible in shared YouTube tool catalog exports when implemented.
- Must include focused contract, unit, integration, and catalog coverage before completion.
