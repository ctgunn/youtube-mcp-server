# Contract: Layer 2 `watermarks_unset` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `watermarks_unset` tool. The tool exposes the upstream YouTube Data API `watermarks.unset` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, auth, mutation-result, target-boundary, no-upload, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `watermarks.unset` request
- Required target channel context, OAuth, partner-delegation boundary, no-upload rules, no-removal-possible behavior, and sparse acknowledgment rules
- Structured successful mutation acknowledgment result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define watermark upload, watermark placement updates, watermark lookup, channel lookup, channel metadata update, banner upload, thumbnail upload, video management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated branding workflows, hosted transport changes, persistence, or cross-endpoint orchestration.

## Tool Identity

The public tool must expose:

- `name`: `watermarks_unset`
- `upstream.resource`: `watermarks`
- `upstream.method`: `unset`
- `upstream.operationKey`: `watermarks.unset`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: owner-only OAuth mutation operation with sparse acknowledgment and no-upload caveats
- `resourceFamily`: `watermarks`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `watermarks.unset`, `Quota cost: 50`, OAuth-required access, required `channelId`, no media upload, rejected watermark metadata, rejected `onBehalfOfContentOwner` in this slice, watermark removal behavior, no-removal-possible behavior, and successful watermark-removal acknowledgment.

## Input Contract

The input schema must accept one object request.

Required fields:

- `channelId`: target YouTube channel identifier.

Rules:

- `channelId` must be present, non-empty, and identify one channel.
- OAuth authorization must be available for every supported request.
- Media upload content is not accepted.
- Watermark placement or display metadata is not accepted.
- `body` and `media` are not accepted by this public slice because those belong to `watermarks_set`.
- `onBehalfOfContentOwner` is not accepted by this public slice because the local Layer 1 wrapper leaves partner delegation outside the guaranteed boundary.
- Unsupported fields, target aliases, bulk watermark shapes, upload fields, metadata fields, lookup fields, channel update fields, banner fields, thumbnail fields, video fields, caption fields, playlist fields, comment fields, transcript fields, analytics fields, recommendation fields, ranking fields, summarization fields, enrichment fields, and cross-endpoint workflow fields must be rejected before endpoint execution.
- Public examples, logs, metadata, and errors must not expose tokens, authorization headers, secret values, raw media content, raw upstream diagnostics, stack traces, unsafe request context, or sensitive authorization details.

## Input Schema

```json
{
  "type": "object",
  "required": ["channelId"],
  "properties": {
    "channelId": {
      "type": "string",
      "minLength": 1,
      "description": "YouTube channel identifier whose watermark will be removed."
    }
  },
  "additionalProperties": false
}
```

## Validation Rules

| Request Shape | Outcome |
|---------------|---------|
| `channelId` + OAuth | Valid watermark-unset submission |
| Missing `channelId` | `invalid_request` |
| Empty or non-string `channelId` | `invalid_request` |
| Ambiguous multi-target `channelId` where locally detectable | `invalid_request` |
| `body` supplied | `invalid_request` |
| `media` supplied | `invalid_request` |
| Metadata-only or media-only request | `invalid_request` |
| Unsupported top-level fields | `invalid_request` |
| `onBehalfOfContentOwner` supplied | `invalid_request` |
| Upload, lookup, channel update, banner, thumbnail, video, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, enrichment, or automated branding fields | `invalid_request` |
| API-key-only access | `authentication_failed` |
| Missing OAuth | `authentication_failed` |
| OAuth exists but cannot remove the target channel watermark | `authorization_failed` |
| Target channel not found, unavailable, or ineligible | `target_channel_failed` or `authorization_failed` according to upstream classification |
| Target channel has no current removable watermark or upstream reports already removed | `no_removal_possible` |
| Quota exhausted | `quota_exhausted` |
| Watermark endpoint unavailable | `endpoint_unavailable` |
| Deprecated behavior reported by upstream | `deprecated_endpoint` |
| Upstream refusal, conflict, forbidden, or policy outcome | `authorization_failed`, `conflict`, or `upstream_refused` according to shared classification |

## Successful Result Shape

```json
{
  "endpoint": "watermarks.unset",
  "sourceOperation": "watermarks.unset",
  "quotaCost": 50,
  "target": {
    "channelId": "UC123"
  },
  "auth": {
    "mode": "oauth_required"
  },
  "availability": {
    "state": "owner_only"
  },
  "noUpload": {
    "bodyAccepted": false,
    "mediaAccepted": false
  },
  "removed": true,
  "acknowledgment": {
    "accepted": true,
    "status": "watermark_unset"
  }
}
```

Successful `watermarks.unset` behavior is represented as a watermark-removal acknowledgment. The public result must not claim that YouTube returned refreshed channel branding metadata, uploaded media, generated a watermark URL, updated a banner, replaced a thumbnail, returned analytics, or performed automated branding.

## Response Convention

- `resultKind`: `mutation_acknowledgment`
- `resourcePath`: absent for sparse or no-content success
- `authMode`: `oauth_required`
- `requiredFields`: `channelId`
- `optionalFields`: none for this slice
- `successStatus`: sparse or no-content acknowledgment
- `statusBody`: no content or safe sparse payload

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `sourceOperation`, `quotaCost`, `removed`, `target`, `auth`, `availability`, `noUpload`, `acknowledgment`, `upstream`
- **Preserved request fields**: `channelId`
- **Disallowed behavior**: `watermark_upload`, `watermark_metadata_update`, `watermark_lookup`, `channel_lookup`, `channel_metadata_update`, `banner_upload`, `thumbnail_upload`, `video_management`, `caption_management`, `playlist_management`, `comment_management`, `transcript_retrieval`, `analytics`, `recommendation`, `ranking`, `summarization`, `enrichment`, `automated_branding`, `cross_endpoint_aggregation`

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

Unsupported upload or metadata payload:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "media"
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

No removal possible:

```json
{
  "category": "no_removal_possible",
  "details": {
    "channelId": "UC123"
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

- The default tool registry must include an executable `watermarks_unset` descriptor.
- The descriptor must use `WATERMARKS_UNSET_INPUT_SCHEMA`.
- The descriptor metadata must come from `build_watermarks_unset_contract().to_tool_metadata()`.
- The descriptor metadata must include caller examples from `WATERMARKS_UNSET_CALLER_EXAMPLES`.
- Shared exports from `mcp_server.tools.youtube_common` must expose the public constants, contract builder, descriptor builder, handler builder, result mapper, validator, and safe error type.
- The representative shared catalog must use the concrete `build_watermarks_unset_contract()` once the tool is implemented.

## Example Coverage

Required caller-facing examples:

- successful authorized watermark removal
- sparse or no-content success
- missing channel validation failure
- malformed or ambiguous channel validation failure
- unsupported `body` or `media` failure
- unsupported top-level modifier failure
- rejected partner delegation failure
- missing OAuth failure
- insufficient permission failure
- quota or upstream failure
- unavailable channel failure
- no-removal-possible outcome
- out-of-scope workflow request rejection

## Contract Tests

Focused contract tests must prove:

- public name is `watermarks_unset`
- upstream identity is `watermarks.unset`
- quota cost is `50` in metadata, descriptions, usage notes, and examples
- auth mode is `oauth_required`
- input schema requires only `channelId`
- `body`, `media`, and unsupported fields are rejected
- successful result is a watermark-removal acknowledgment
- no-removal-possible behavior is distinct from successful removal
- errors are safe and categorized
- default registry and representative catalog expose the concrete contract
- new or changed Python functions include reStructuredText docstrings
