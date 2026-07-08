# Contract: `playlistImages_list`

## Public Tool Identity

- **Tool name**: `playlistImages_list`
- **Layer**: Layer 2 public MCP endpoint-backed tool
- **Upstream operation**: `playlistImages.list`
- **Resource family**: `playlist_images`
- **Auth mode**: `oauth_required`
- **Official quota cost**: `1`
- **Availability**: Active, OAuth-required playlist-image retrieval

## Purpose

Expose YouTube playlist-image listing while preserving low-level endpoint behavior. The tool is for direct retrieval, debugging, and downstream composition, not for playlist image insertion, update, deletion, media upload, thumbnail replacement, playlist management, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint aggregation.

## Input Contract

The public input schema must be object-shaped and must reject additional properties.

```json
{
  "type": "object",
  "required": ["part"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1
    },
    "playlistId": {
      "type": "string",
      "minLength": 1
    },
    "id": {
      "type": "string",
      "minLength": 1
    },
    "pageToken": {
      "type": "string",
      "minLength": 1
    },
    "maxResults": {
      "type": "integer",
      "minimum": 0
    }
  },
  "additionalProperties": false
}
```

### Input Rules

- `part` is required and must name supported playlist-image resource parts.
- Exactly one selector from `playlistId` or `id` is required.
- `playlistId` lookup may include `pageToken` and `maxResults`.
- `id` lookup must reject `pageToken` and `maxResults`.
- Empty selector values, empty page tokens, invalid page sizes, unsupported fields, request bodies, mutation fields, media upload fields, analytics fields, ranking fields, summarization fields, and enrichment fields are unsupported in this slice and must fail clearly.
- API-key-only access or missing OAuth access must not be treated as successful requests.

## Metadata Contract

Discovery metadata must expose:

- Public tool name `playlistImages_list`
- Upstream resource `playlistImages`
- Upstream method `list`
- Operation key `playlistImages.list`
- Quota cost `1`
- Auth mode `oauth_required`
- Active availability with OAuth-required access caveats
- Supported request fields and rejected unsupported fields
- Exclusive selector rule for `playlistId` and `id`
- Selector-specific paging rule for `playlistId`
- Response convention and safe error categories

Descriptions, usage notes, caveats, and examples must visibly state quota cost `1`.

## Result Contract

A successful result must preserve a near-raw list shape:

```json
{
  "endpoint": "playlistImages.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "selector": {
    "name": "playlistId",
    "value": "PL123"
  },
  "paging": {
    "pageToken": "NEXT_PAGE",
    "maxResults": 25
  },
  "auth": {
    "mode": "oauth_required"
  },
  "items": [],
  "kind": "youtube#playlistImageListResponse",
  "etag": "etag-value",
  "nextPageToken": "NEXT_PAGE_2",
  "pageInfo": {
    "totalResults": 0,
    "resultsPerPage": 25
  }
}
```

### Result Rules

- `items` may be empty for a valid successful request.
- Returned `kind`, `etag`, `items`, `nextPageToken`, `prevPageToken`, and `pageInfo` fields must be preserved when present.
- Missing optional upstream fields must not be fabricated.
- Requested parts and selector context must be preserved in wrapper context.
- Paging context must be preserved only when present or applicable.
- The result must not add playlist image mutation, media upload, playlist management, playlist-item expansion, analytics, ranking, summarization, recommendation, enrichment, or heuristic classification.

## Error Contract

The tool must return or raise safe caller-facing errors using shared Layer 2 categories:

- `invalid_request`
- `authentication_failed`
- `authorization_failed`
- `quota_exhausted`
- `resource_not_found`
- `endpoint_unavailable`
- `upstream_failure`

### Error Rules

- Missing `part`, invalid `part`, empty `part`, missing selectors, conflicting selectors, paging with `id`, empty `pageToken`, invalid `maxResults`, unsupported fields, unsupported filters, unsupported request bodies, unsupported media inputs, and unsupported actions must map to `invalid_request`.
- Missing OAuth credentials should map to `authentication_failed`.
- Insufficient OAuth access or inaccessible playlist-image data should map to `authorization_failed` unless the upstream category provides a more specific safe shared category.
- Quota failures must map to `quota_exhausted`.
- Missing resources must map to `resource_not_found`.
- Unavailable endpoint or service failures must map to `endpoint_unavailable` or `upstream_failure`.
- Errors must not expose OAuth tokens, API keys, stack traces, raw upstream bodies, raw request context, or unsafe diagnostics.

## Required Examples

The contract must include caller-facing examples for:

- OAuth-backed playlist-scoped retrieval with `part` and `playlistId`
- OAuth-backed direct image lookup with `part` and `id`
- Playlist-scoped paged retrieval with `pageToken` or `maxResults`
- Empty successful result
- Missing `part` validation failure
- Invalid `part` validation failure
- Missing selector validation failure
- Conflicting selector validation failure
- Paging-with-`id` validation failure
- OAuth failure
- Out-of-scope image-management request rejection
