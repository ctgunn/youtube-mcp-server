# Contract: Layer 2 `videos_rate` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `videos_rate` tool. The tool exposes the upstream YouTube Data API `videos.rate` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, auth, mutation-result, rating-state, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `videos.rate` request
- Video identity, rating action, OAuth, no-request-body, and clear-rating rules
- Structured successful rating acknowledgment result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define current-rating lookup, rating history, aggregate like/dislike counts, video metadata update, upload, deletion, abuse reporting, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, hosted transport changes, persistence, or cross-endpoint orchestration.

## Tool Identity

The public tool must expose:

- `name`: `videos_rate`
- `upstream.resource`: `videos`
- `upstream.method`: `rate`
- `upstream.operationKey`: `videos.rate`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active OAuth mutation operation with rating-state and no-content acknowledgment caveats
- `resourceFamily`: `videos`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `videos.rate`, `Quota cost: 50`, OAuth-required access, required video identity, supported rating actions `like`, `dislike`, and `none`, `none` as clear-rating behavior, no request body, and acknowledgment-style success.

## Input Contract

The input schema must accept one object request.

Required fields:

- `id`: target video identifier.
- `rating`: requested rating action. Supported values are `like`, `dislike`, and `none`.

Rules:

- `id` must be present, non-empty, and identify one video.
- `rating` must be present and exactly one of `like`, `dislike`, or `none`.
- `rating: "none"` means clear the authenticated caller's rating.
- Missing `rating` must not be treated as `none`.
- OAuth authorization must be available for every supported request.
- No request body is accepted for this tool.
- Unsupported fields, request-body fields, aliases, delegated modifiers, analytics fields, lookup fields, aggregation fields, and cross-endpoint workflow fields must be rejected before endpoint execution.
- Public examples, logs, metadata, and errors must not expose tokens, authorization headers, secret values, raw upstream diagnostics, stack traces, or unsafe request context.

## Input Schema

```json
{
  "type": "object",
  "required": ["id", "rating"],
  "properties": {
    "id": {
      "type": "string",
      "minLength": 1,
      "description": "YouTube video identifier targeted by the rating mutation."
    },
    "rating": {
      "type": "string",
      "enum": ["like", "dislike", "none"],
      "description": "Rating state to apply. Use none to clear the authenticated caller's rating."
    }
  },
  "additionalProperties": false
}
```

## Validation Rules

| Request Shape | Outcome |
|---------------|---------|
| `id` + `rating=like` + OAuth | Valid like-rating request |
| `id` + `rating=dislike` + OAuth | Valid dislike-rating request |
| `id` + `rating=none` + OAuth | Valid clear-rating request |
| Missing `id` | `invalid_request` |
| Empty or non-string `id` | `invalid_request` |
| Missing `rating` | `invalid_request` |
| Empty, non-string, differently cased, unknown, duplicated, or conflicting `rating` | `invalid_request` |
| Request `body` supplied | `invalid_request` |
| Unsupported top-level fields | `invalid_request` |
| Current-rating lookup, rating history, aggregate rating count, update, upload, delete, abuse report, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, or enrichment fields | `invalid_request` |
| API-key-only access | `authentication_failed` |
| Missing OAuth | `authentication_failed` |
| OAuth exists but cannot rate the selected video | `authorization_failed` |
| User email is unverified | `authorization_failed` |
| Video cannot be rated, rating is disabled, rental access is required, or policy restrictions apply | `authorization_failed` |
| Target video not found | `resource_not_found` |
| Quota exhausted | `quota_exhausted` |
| Rating endpoint unavailable | `endpoint_unavailable` |
| Deprecated behavior reported by upstream | `deprecated_endpoint` |

## Successful Result Shape

```json
{
  "endpoint": "videos.rate",
  "quotaCost": 50,
  "rating": {
    "videoId": "abc123",
    "requestedRating": "like"
  },
  "auth": {
    "mode": "oauth_required",
    "path": "restricted"
  },
  "availability": {
    "state": "active"
  },
  "mutation": {
    "type": "rated",
    "acknowledged": true
  },
  "status": {
    "code": 204,
    "body": "none"
  }
}
```

For `rating=none`, `requestedRating` remains `none` and the mutation acknowledgment represents a clear-rating request.

## Response Convention

- `resultKind`: `mutation_acknowledgment`
- `resourcePath`: `rating`
- `authMode`: `oauth_required`
- `requiredFields`: `id`, `rating`
- `ratingValues`: `like`, `dislike`, `none`
- `mutationType`: `rated`
- `successBody`: `none`

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `rating`, `auth`, `availability`, `mutation`, `status`
- **Preserved upstream fields**: no refreshed resource fields are promised for success; no-content success must remain valid
- **Disallowed behavior**: `rating_lookup`, `rating_history`, `aggregate_rating_counts`, `metadata_update`, `media_upload`, `media_replacement`, `transcoding`, `automatic_publishing`, `video_creation`, `video_delete`, `abuse_reporting`, `thumbnail_management`, `caption_management`, `playlist_management`, `comment_management`, `transcript_retrieval`, `analytics`, `recommendation`, `ranking`, `summarization`, `enrichment`, `cross_endpoint_aggregation`

## Validation Failures

Missing identity:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "id"
  }
}
```

Missing rating:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "rating",
    "allowed": ["like", "dislike", "none"]
  }
}
```

Unsupported rating:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "rating",
    "allowed": ["like", "dislike", "none"]
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

Non-ratable target:

```json
{
  "category": "authorization_failed",
  "details": {
    "reason": "rating_not_allowed"
  }
}
```

Target not found:

```json
{
  "category": "resource_not_found",
  "details": {
    "field": "id"
  }
}
```

## Discovery Expectations

MCP clients must be able to discover `videos_rate` in the default tool catalog with:

- tool name and description
- input schema above
- mapped upstream operation metadata
- quota cost `50`
- OAuth-required auth mode
- supported rating-state values
- clear-rating semantics for `none`
- no-request-body caveat
- acknowledgment-style success result
- safe error categories
- representative examples for success and failure

## Registration Expectations

- `build_videos_rate_contract()` builds the shared contract metadata.
- `build_videos_rate_tool_descriptor()` returns a dispatcher-ready descriptor.
- `build_videos_rate_handler()` validates, executes, and maps one request.
- `validate_videos_rate_arguments()` normalizes one request or raises a safe validation error.
- `map_videos_rate_result()` returns a structured acknowledgment without fabricating refreshed video data.
- `VIDEOS_RATE_*` symbols are exported through the videos family module and shared package exports.
- Default dispatcher registration includes `videos_rate` once the descriptor exists.
