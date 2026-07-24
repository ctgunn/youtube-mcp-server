# Contract: Layer 2 `videos_delete` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `videos_delete` tool. The tool exposes the upstream YouTube Data API `videos.delete` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, auth, mutation-result, destructive-action, target-boundary, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `videos.delete` request
- Required target video identity, OAuth, partner-delegation boundary, no-body rule, and no-content acknowledgment rules
- Structured successful mutation acknowledgment result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define video listing, metadata lookup, metadata update, media upload, media replacement, transcoding, automatic publishing, rating lookup, rating mutation, abuse reporting, abuse-reason discovery, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, recovery, policy review, hosted transport changes, persistence, or cross-endpoint orchestration.

## Tool Identity

The public tool must expose:

- `name`: `videos_delete`
- `upstream.resource`: `videos`
- `upstream.method`: `delete`
- `upstream.operationKey`: `videos.delete`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active OAuth mutation operation with no-content acknowledgment and destructive-action caveats
- `resourceFamily`: `videos`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `videos.delete`, `Quota cost: 50`, OAuth-required access, required `id`, no request body, rejected `onBehalfOfContentOwner` in this slice, destructive deletion behavior, and successful deletion acknowledgment.

## Input Contract

The input schema must accept one object request.

Required fields:

- `id`: target YouTube video identifier.

Rules:

- `id` must be present, non-empty, and identify one video.
- OAuth authorization must be available for every supported request.
- No request body is accepted.
- `onBehalfOfContentOwner` is not accepted by this public slice because the local Layer 1 wrapper leaves partner delegation outside the guaranteed boundary.
- Unsupported fields, target aliases such as `videoId`, request bodies, bulk delete shapes, partner delegation, lookup fields, update fields, upload fields, rating fields, abuse-report fields, caption fields, thumbnail fields, playlist fields, comment fields, transcript fields, analytics fields, recommendation fields, ranking fields, summarization fields, enrichment fields, recovery fields, and cross-endpoint workflow fields must be rejected before endpoint execution.
- Public examples, logs, metadata, and errors must not expose tokens, authorization headers, secret values, raw upstream diagnostics, stack traces, unsafe request context, or sensitive authorization details.

## Input Schema

```json
{
  "type": "object",
  "required": ["id"],
  "properties": {
    "id": {
      "type": "string",
      "minLength": 1,
      "description": "YouTube video identifier to delete."
    }
  },
  "additionalProperties": false
}
```

## Validation Rules

| Request Shape | Outcome |
|---------------|---------|
| `id` + OAuth | Valid delete submission |
| Missing `id` | `invalid_request` |
| Empty or non-string `id` | `invalid_request` |
| Ambiguous multi-target `id` where locally detectable | `invalid_request` |
| Request body supplied | `invalid_request` |
| Unsupported top-level fields | `invalid_request` |
| `onBehalfOfContentOwner` supplied | `invalid_request` |
| Top-level `videoId` alias without `id` | `invalid_request` |
| Lookup, update, upload, rating, abuse-report, caption, thumbnail, playlist, comment, transcript, analytics, recommendation, ranking, summarization, enrichment, recovery, or policy-review fields | `invalid_request` |
| API-key-only access | `authentication_failed` |
| Missing OAuth | `authentication_failed` |
| OAuth exists but cannot delete the target video | `authorization_failed` |
| Target video not found or already unavailable | `resource_not_found` or `authorization_failed` according to upstream classification |
| Quota exhausted | `quota_exhausted` |
| Delete endpoint unavailable | `endpoint_unavailable` |
| Deprecated behavior reported by upstream | `deprecated_endpoint` |
| Upstream refusal, conflict, forbidden, or policy outcome | `authorization_failed` or `upstream_failure` according to shared classification |

## Successful Result Shape

```json
{
  "endpoint": "videos.delete",
  "quotaCost": 50,
  "target": {
    "id": "abc123"
  },
  "auth": {
    "mode": "oauth_required",
    "path": "restricted"
  },
  "availability": {
    "state": "active"
  },
  "deleted": true,
  "acknowledgment": {
    "accepted": true,
    "status": "deleted"
  },
  "status": {
    "code": 204,
    "body": "none"
  }
}
```

Successful `videos.delete` behavior is a no-content deletion acknowledgment. The public result must not claim that YouTube returned refreshed video metadata, created a recovery record, changed a rating, submitted an abuse report, updated a playlist, or returned analytics.

## Response Convention

- `resultKind`: `mutation_acknowledgment`
- `resourcePath`: absent for no-content success
- `authMode`: `oauth_required`
- `requiredFields`: `id`
- `optionalFields`: none in this slice
- `successStatus`: `204`
- `statusBody`: no content

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `target`, `auth`, `availability`, `deleted`, `acknowledgment`, `status`, `sourceOperation`
- **Preserved request fields**: `id`
- **Disallowed behavior**: `video_listing`, `metadata_lookup`, `metadata_update`, `rating_lookup`, `rating_mutation`, `abuse_reporting`, `abuse_reason_discovery`, `media_upload`, `media_replacement`, `transcoding`, `automatic_publishing`, `thumbnail_management`, `caption_management`, `playlist_management`, `comment_management`, `transcript_retrieval`, `analytics`, `recommendation`, `ranking`, `summarization`, `enrichment`, `recovery`, `policy_review`, `cross_endpoint_aggregation`

## Validation Failures

Missing target:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "id"
  }
}
```

Body supplied:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "body"
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
- raw upstream bodies
- stack traces
- signed URLs or secret-bearing values
- unsafe request context
- private authorization details

## Registration Contract

- `videos_delete` must appear in default tool discovery.
- The descriptor must include the same schema as this contract.
- Dispatcher invocation must execute the concrete handler for valid requests.
- Dispatcher validation and direct handler validation must produce compatible safe outcomes for invalid requests.
- Representative examples must align with the concrete contract and include successful deletion, missing target, unsupported body, rejected partner delegation, missing OAuth, upstream failure, and out-of-scope workflow rejection.
