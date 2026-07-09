# Contract: `playlistImages_delete`

## Public Tool Identity

- **Tool name**: `playlistImages_delete`
- **Layer**: Layer 2 public MCP endpoint-backed tool
- **Upstream operation**: `playlistImages.delete`
- **Resource family**: `playlist_images`
- **Auth mode**: `oauth_required`
- **Official quota cost**: `50`
- **Availability**: Active, OAuth-required destructive playlist-image deletion

## Purpose

Expose YouTube playlist-image deletion while preserving low-level endpoint behavior. The tool is for direct deletion, debugging, and downstream composition, not for playlist image listing, insertion, update, media upload, thumbnail management, playlist management, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint aggregation.

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

- `id` is required and identifies the playlist image being deleted.
- The request targets exactly one playlist image per invocation.
- Empty `id`, malformed `id`, missing `id`, `part`, `body`, `media`, paging controls, listing selectors, metadata payloads, playlist management directives, analytics fields, ranking fields, summarization fields, enrichment fields, and unrelated endpoint modifiers are unsupported in this slice and must fail clearly.
- API-key-only access or missing OAuth access must not be treated as successful requests.

## Metadata Contract

Discovery metadata must expose:

- Public tool name `playlistImages_delete`
- Upstream resource `playlistImages`
- Upstream method `delete`
- Operation key `playlistImages.delete`
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
  "endpoint": "playlistImages.delete",
  "quotaCost": 50,
  "target": {
    "id": "playlist-image-123"
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
- The target playlist image identifier must be preserved in safe result context.
- No deleted playlist-image fields may be fabricated from request context.
- The result must not add playlist image listing, insertion, update, media upload, thumbnail activation, playlist management, playlist-item expansion, analytics, ranking, summarization, recommendation, enrichment, or heuristic classification.

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

- Missing `id`, invalid `id`, empty `id`, unsupported fields, unsupported request bodies, unsupported media input, unsupported part selection, unsupported selectors, unsupported actions, and out-of-scope workflow fields must map to `invalid_request`.
- Missing OAuth credentials should map to `authentication_failed`.
- Insufficient OAuth access or inaccessible playlist-image deletion should map to `authorization_failed` unless the upstream category provides a more specific safe shared category.
- Quota failures must map to `quota_exhausted`.
- Missing playlist images or unavailable deletion targets must map to `resource_not_found`.
- Unavailable endpoint failures or service failures must map to `endpoint_unavailable` or `upstream_failure` according to the normalized upstream category.
- Errors must not expose OAuth tokens, API keys, stack traces, raw upstream bodies, raw request context, or unsafe diagnostics.

## Required Examples

The contract must include caller-facing examples for:

- OAuth-backed playlist-image deletion with `id`
- Successful no-body deletion acknowledgment
- Missing `id` validation failure
- Invalid `id` validation failure
- Unsupported input validation failure
- OAuth failure
- Missing-resource, quota, or upstream deletion failure
- Out-of-scope image-management request rejection
