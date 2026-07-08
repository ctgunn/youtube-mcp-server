# Contract: `playlistImages_insert`

## Public Tool Identity

- **Tool name**: `playlistImages_insert`
- **Layer**: Layer 2 public MCP endpoint-backed tool
- **Upstream operation**: `playlistImages.insert`
- **Resource family**: `playlist_images`
- **Auth mode**: `oauth_required`
- **Official quota cost**: `50`
- **Availability**: Active, OAuth-required playlist-image insertion with required media upload

## Purpose

Expose YouTube playlist-image insertion while preserving low-level endpoint behavior. The tool is for direct creation, debugging, and downstream composition, not for playlist image listing, update, deletion, thumbnail replacement, playlist management, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint aggregation.

## Input Contract

The public input schema must be object-shaped and must reject additional properties.

```json
{
  "type": "object",
  "required": ["part", "body", "media"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1
    },
    "body": {
      "type": "object",
      "required": ["snippet"],
      "additionalProperties": false
    },
    "media": {
      "type": "object",
      "required": ["mimeType", "content"],
      "properties": {
        "mimeType": {
          "type": "string",
          "minLength": 1
        },
        "content": {
          "type": "string",
          "minLength": 1
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

### Input Rules

- `part` is required and must name supported playlist-image resource parts returned after insertion.
- `body` is required and must include supported playlist-image metadata, including required creation metadata under `snippet`.
- `media` is required and must include supported upload content descriptors.
- `media.mimeType` is required and must describe a supported image upload type.
- `media.content` is required for the supported local contract, but raw upload content must not be echoed in public metadata, examples, validation details, or errors.
- Empty `part`, missing `body`, malformed `body`, missing `media`, malformed `media`, unsupported upload shapes, unsupported fields, playlist management directives, analytics fields, ranking fields, summarization fields, enrichment fields, and unrelated endpoint modifiers are unsupported in this slice and must fail clearly.
- API-key-only access or missing OAuth access must not be treated as successful requests.

## Metadata Contract

Discovery metadata must expose:

- Public tool name `playlistImages_insert`
- Upstream resource `playlistImages`
- Upstream method `insert`
- Operation key `playlistImages.insert`
- Quota cost `50`
- Auth mode `oauth_required`
- Active availability with OAuth-required and upload-required caveats
- Supported request fields and rejected unsupported fields
- Required `part`, `body`, and `media` guidance
- Mutation response convention and safe error categories

Descriptions, usage notes, caveats, and examples must visibly state quota cost `50`.

## Result Contract

A successful result must preserve a near-raw mutation shape:

```json
{
  "endpoint": "playlistImages.insert",
  "quotaCost": 50,
  "requestedParts": ["snippet"],
  "bodyContext": {
    "hasSnippet": true,
    "playlistId": "PL123"
  },
  "mediaContext": {
    "mimeType": "image/jpeg",
    "contentProvided": true
  },
  "auth": {
    "mode": "oauth_required"
  },
  "item": {
    "kind": "youtube#playlistImage",
    "etag": "etag-value",
    "id": "playlist-image-123",
    "snippet": {
      "playlistId": "PL123",
      "type": "medium"
    }
  }
}
```

### Result Rules

- Returned playlist-image resource fields must be preserved when present.
- Returned `kind`, `etag`, `id`, `snippet`, and additional upstream fields must be preserved when present.
- Missing optional upstream fields must not be fabricated.
- Requested parts, safe body context, safe media context, and auth context must be preserved in wrapper context.
- Raw upload content must not be echoed in successful results.
- The result must not add playlist image listing, update, deletion, thumbnail activation, playlist management, playlist-item expansion, analytics, ranking, summarization, recommendation, enrichment, or heuristic classification.

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

- Missing `part`, invalid `part`, empty `part`, missing `body`, malformed `body`, unsupported `body`, missing `media`, malformed `media`, unsupported media type, missing upload content, unsupported fields, unsupported request bodies beyond the documented metadata body, unsupported actions, and out-of-scope workflow fields must map to `invalid_request`.
- Missing OAuth credentials should map to `authentication_failed`.
- Insufficient OAuth access or inaccessible playlist-image insertion should map to `authorization_failed` unless the upstream category provides a more specific safe shared category.
- Quota failures must map to `quota_exhausted`.
- Missing resources must map to `resource_not_found`.
- Media eligibility failures, unavailable endpoint failures, or service failures must map to `invalid_request`, `endpoint_unavailable`, or `upstream_failure` according to the normalized upstream category.
- Errors must not expose OAuth tokens, API keys, raw media content, stack traces, raw upstream bodies, raw request context, or unsafe diagnostics.

## Required Examples

The contract must include caller-facing examples for:

- OAuth-backed playlist-image insertion with `part`, `body`, and `media`
- Missing `part` validation failure
- Invalid `part` validation failure
- Missing `body` validation failure
- Invalid `body` validation failure
- Missing `media` validation failure
- Unsupported media validation failure
- OAuth failure
- Quota or upstream insertion failure
- Out-of-scope image-management request rejection
