# Contract: Layer 2 `watermarks_set` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `watermarks_set` tool. The tool exposes the upstream YouTube Data API `watermarks.set` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, auth, upload-result, mutation-result, target-boundary, media-safety, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `watermarks.set` request
- Required target channel identity, watermark metadata, media upload, OAuth, partner-delegation boundary, and sparse acknowledgment rules
- Structured successful upload or mutation acknowledgment result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define watermark removal, watermark lookup, channel lookup, channel metadata update, banner upload, thumbnail upload, video management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated branding workflows, hosted transport changes, persistence, or cross-endpoint orchestration.

## Tool Identity

The public tool must expose:

- `name`: `watermarks_set`
- `upstream.resource`: `watermarks`
- `upstream.method`: `set`
- `upstream.operationKey`: `watermarks.set`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: owner-only OAuth upload mutation operation with sparse acknowledgment and media-upload caveats
- `resourceFamily`: `watermarks`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `watermarks.set`, `Quota cost: 50`, OAuth-required access, required `channelId`, required `body`, required `media`, accepted media types, 10 MB upload boundary, rejected `onBehalfOfContentOwner` in this slice, watermark update behavior, and successful watermark-update acknowledgment.

## Input Contract

The input schema must accept one object request.

Required fields:

- `channelId`: target YouTube channel identifier.
- `body`: watermark metadata containing timing and position details.
- `media`: watermark media upload descriptor.

Rules:

- `channelId` must be present, non-empty, and identify one channel.
- `body.timing` must be present and non-empty.
- `body.position` must be present and non-empty.
- `body.targetChannelId`, when present, must be text.
- `media.mimeType` must be present and use a supported media type.
- `media.content` must be present and non-empty.
- Media content must not exceed the documented 10 MB watermark boundary when determinable locally.
- OAuth authorization must be available for every supported request.
- Metadata-only and media-only requests are not accepted.
- `onBehalfOfContentOwner` is not accepted by this public slice because the local Layer 1 wrapper leaves partner delegation outside the guaranteed boundary.
- Unsupported fields, target aliases, bulk watermark shapes, removal fields, lookup fields, channel update fields, banner fields, thumbnail fields, video fields, caption fields, playlist fields, comment fields, transcript fields, analytics fields, recommendation fields, ranking fields, summarization fields, enrichment fields, and cross-endpoint workflow fields must be rejected before endpoint execution.
- Public examples, logs, metadata, and errors must not expose tokens, authorization headers, secret values, raw media content, raw upstream diagnostics, stack traces, unsafe request context, or sensitive authorization details.

## Input Schema

```json
{
  "type": "object",
  "required": ["channelId", "body", "media"],
  "properties": {
    "channelId": {
      "type": "string",
      "minLength": 1,
      "description": "YouTube channel identifier whose watermark will be set."
    },
    "body": {
      "type": "object",
      "required": ["timing", "position"],
      "properties": {
        "timing": {
          "type": "object",
          "minProperties": 1,
          "description": "Watermark timing metadata."
        },
        "position": {
          "type": "object",
          "minProperties": 1,
          "description": "Watermark position metadata."
        },
        "targetChannelId": {
          "type": "string",
          "minLength": 1,
          "description": "Optional linked channel identifier when supported."
        }
      },
      "additionalProperties": true
    },
    "media": {
      "type": "object",
      "required": ["mimeType", "content"],
      "properties": {
        "mimeType": {
          "type": "string",
          "enum": ["image/jpeg", "image/png", "application/octet-stream"],
          "description": "Watermark upload media type."
        },
        "content": {
          "type": "string",
          "minLength": 1,
          "description": "Watermark media content. Public results and examples must omit raw private media."
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

## Validation Rules

| Request Shape | Outcome |
|---------------|---------|
| `channelId` + `body` + `media` + OAuth | Valid watermark-set submission |
| Missing `channelId` | `invalid_request` |
| Empty or non-string `channelId` | `invalid_request` |
| Ambiguous multi-target `channelId` where locally detectable | `invalid_request` |
| Missing `body` | `invalid_request` |
| Non-object `body` | `invalid_request` |
| Missing or empty `body.timing` | `invalid_request` |
| Missing or empty `body.position` | `invalid_request` |
| Non-string `body.targetChannelId` | `invalid_request` |
| Missing `media` | `invalid_request` |
| Non-object `media` | `invalid_request` |
| Missing or unsupported `media.mimeType` | `unsupported_upload` or `invalid_request` according to shared conventions |
| Missing or empty `media.content` | `unsupported_upload` or `invalid_request` according to shared conventions |
| Oversized upload content where locally detectable | `unsupported_upload` |
| Metadata-only or media-only request | `invalid_request` |
| Unsupported top-level fields | `invalid_request` |
| `onBehalfOfContentOwner` supplied | `invalid_request` |
| Removal, lookup, channel update, banner, thumbnail, video, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, enrichment, or automated branding fields | `invalid_request` |
| API-key-only access | `authentication_failed` |
| Missing OAuth | `authentication_failed` |
| OAuth exists but cannot update the target channel watermark | `authorization_failed` |
| Target channel not found or unavailable | `resource_not_found` or `authorization_failed` according to upstream classification |
| Quota exhausted | `quota_exhausted` |
| Watermark endpoint unavailable | `endpoint_unavailable` |
| Deprecated behavior reported by upstream | `deprecated_endpoint` |
| Upstream refusal, conflict, forbidden, unsupported media, upload, or policy outcome | `authorization_failed`, `unsupported_upload`, or `upstream_failure` according to shared classification |

## Successful Result Shape

```json
{
  "endpoint": "watermarks.set",
  "quotaCost": 50,
  "target": {
    "channelId": "UC123"
  },
  "metadata": {
    "hasTiming": true,
    "hasPosition": true,
    "targetChannelId": "UC123"
  },
  "upload": {
    "mimeType": "image/png",
    "contentProvided": true
  },
  "auth": {
    "mode": "oauth_required",
    "path": "restricted"
  },
  "availability": {
    "state": "owner_only"
  },
  "updated": true,
  "acknowledgment": {
    "accepted": true,
    "status": "watermark_set"
  },
  "status": {
    "body": "none_or_sparse"
  }
}
```

Successful `watermarks.set` behavior is represented as a watermark-update acknowledgment. The public result must not claim that YouTube returned refreshed channel branding metadata, generated a watermark URL, removed a watermark, updated a banner, replaced a thumbnail, returned analytics, or performed automated branding.

## Response Convention

- `resultKind`: `upload_result` or `mutation_acknowledgment`
- `resourcePath`: absent for sparse or no-content success
- `authMode`: `oauth_required`
- `requiredFields`: `channelId`, `body`, `media`
- `optionalFields`: `body.targetChannelId` only when supported by the wrapper contract
- `successStatus`: sparse or no-content acknowledgment
- `statusBody`: no content or safe sparse payload

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `target`, `metadata`, `upload`, `auth`, `availability`, `updated`, `acknowledgment`, `status`, `sourceOperation`
- **Preserved request fields**: `channelId`, safe `body` context, safe `media` descriptor
- **Disallowed behavior**: `watermark_removal`, `watermark_lookup`, `channel_lookup`, `channel_metadata_update`, `banner_upload`, `thumbnail_upload`, `video_management`, `caption_management`, `playlist_management`, `comment_management`, `transcript_retrieval`, `analytics`, `recommendation`, `ranking`, `summarization`, `enrichment`, `automated_branding`, `cross_endpoint_aggregation`

## Validation Failures

Missing target:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "channelId"
  }
}
```

Missing metadata:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "body"
  }
}
```

Unsupported upload:

```json
{
  "category": "unsupported_upload",
  "details": {
    "field": "media.mimeType"
  }
}
```

Missing OAuth:

```json
{
  "category": "authentication_failed",
  "details": {
    "authMode": "oauth_required"
  }
}
```

## Error Safety

Errors must preserve caller-actionable categories and field context while removing:

- OAuth tokens
- API keys
- authorization headers
- raw media content
- raw upstream bodies
- stack traces
- signed URLs or secret-bearing values
- unsafe request context
- private authorization details

## Registration Contract

- `watermarks_set` must appear in default tool discovery.
- The descriptor must include the same schema as this contract.
- Dispatcher invocation must execute the concrete handler for valid requests.
- Dispatcher validation and direct handler validation must produce compatible safe outcomes for invalid requests.
- Representative examples must align with the concrete contract and include successful watermark update, sparse success, missing channel, missing metadata, unsupported metadata, missing upload, unsupported upload, rejected partner delegation, missing OAuth, upstream failure, unavailable channel, and out-of-scope workflow rejection.
