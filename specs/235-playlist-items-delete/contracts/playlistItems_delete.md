# Contract: `playlistItems_delete`

## Public Tool Identity

- **Tool name**: `playlistItems_delete`
- **Layer**: Layer 2 public MCP endpoint-backed tool
- **Upstream operation**: `playlistItems.delete`
- **Resource family**: `playlist_items`
- **Auth mode**: `oauth_required`
- **Official quota cost**: `50`
- **Availability**: Active, OAuth-required destructive playlist-item deletion

## Purpose

Expose YouTube playlist-item deletion while preserving low-level endpoint behavior. The tool is for direct deletion, debugging, and downstream composition, not for playlist-item listing, insertion, update, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated curation, or cross-endpoint aggregation.

## Input Contract

The public input schema must be object-shaped and must reject additional properties.

```json
{
  "type": "object",
  "required": ["id"],
  "properties": {
    "id": {
      "type": "string",
      "minLength": 1
    }
  },
  "additionalProperties": false
}
```

### Input Rules

- `id` is required and identifies the playlist item being deleted.
- The request targets exactly one playlist item per invocation.
- Empty `id`, malformed `id`, missing `id`, `part`, `body`, playlist metadata payloads, playlist/video assignment data, placement controls, paging controls, listing selectors, playlist-management directives, analytics fields, ranking fields, summarization fields, enrichment fields, and unrelated endpoint modifiers are unsupported in this slice and must fail clearly.
- API-key-only access or missing OAuth access must not be treated as successful requests.

## Metadata Contract

Discovery metadata must expose:

- Public tool name `playlistItems_delete`
- Upstream resource `playlistItems`
- Upstream method `delete`
- Operation key `playlistItems.delete`
- Quota cost `50`
- Auth mode `oauth_required`
- Active availability with OAuth-required and destructive-delete caveats
- Supported request field `id` and rejected unsupported fields
- Mutation acknowledgment response convention
- No-body success behavior
- Safe error categories

Descriptions, usage notes, caveats, and examples must visibly state quota cost `50`.

## Result Contract

A successful result must preserve a near-raw deletion acknowledgment shape:

```json
{
  "endpoint": "playlistItems.delete",
  "quotaCost": 50,
  "target": {
    "id": "playlist-item-123"
  },
  "auth": {
    "mode": "oauth_required"
  },
  "deleted": true,
  "acknowledged": true
}
```

### Result Rules

- Successful deletion must be acknowledged even when the upstream operation returns no deleted resource body.
- The target playlist item identifier must be preserved in safe result context.
- No deleted playlist-item fields may be fabricated from request context.
- The result must not add playlist-item listing, insertion, update, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, enrichment, automated curation, or heuristic classification.

## Error Contract

The tool must return or raise safe caller-facing errors using shared Layer 2 categories:

- `invalid_request`
- `authentication_failed`
- `authorization_failed`
- `quota_exhausted`
- `resource_not_found`
- `endpoint_unavailable`
- `deprecated`
- `upstream_failure`

### Error Rules

- Missing `id`, invalid `id`, empty `id`, unsupported fields, unsupported request bodies, unsupported part selection, unsupported selectors, unsupported actions, and out-of-scope workflow fields must map to `invalid_request`.
- Missing OAuth credentials should map to `authentication_failed`.
- Insufficient OAuth access or inaccessible playlist-item deletion should map to `authorization_failed` unless the upstream category provides a more specific safe shared category.
- Quota failures must map to `quota_exhausted`.
- Missing playlist items or unavailable deletion targets must map to `resource_not_found`.
- Deprecated or unavailable endpoint behavior must map to `deprecated`, `endpoint_unavailable`, or `upstream_failure` according to the normalized upstream category.
- Errors must not expose OAuth tokens, API keys, stack traces, raw upstream bodies, raw request context, or unsafe diagnostics.

## Required Examples

The contract must include caller-facing examples for:

- OAuth-backed playlist-item deletion with `id`
- Successful no-body deletion acknowledgment
- Missing `id` validation failure
- Invalid `id` validation failure
- Unsupported input validation failure
- OAuth failure
- Missing-resource, quota, or upstream deletion failure
- Out-of-scope playlist-management request rejection
