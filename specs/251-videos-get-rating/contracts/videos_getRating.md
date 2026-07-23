# Contract: Layer 2 `videos_getRating` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `videos_getRating` tool. The tool exposes the upstream YouTube Data API `videos.getRating` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, auth, read-result, rating-state, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `videos.getRating` request
- Video identifier, OAuth, optional partner delegation, no-request-body, and returned rating-state rules
- Structured successful per-video rating lookup result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define rating mutation, rating history, aggregate like/dislike counts, video metadata lookup or update, upload, deletion, abuse reporting, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, hosted transport changes, persistence, or cross-endpoint orchestration.

## Tool Identity

The public tool must expose:

- `name`: `videos_getRating`
- `upstream.resource`: `videos`
- `upstream.method`: `getRating`
- `upstream.operationKey`: `videos.getRating`
- `quotaCost`: `1`
- `authMode`: `oauth_required`
- `availabilityState`: active OAuth read operation with returned rating-state and no-request-body caveats
- `resourceFamily`: `videos`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `videos.getRating`, `Quota cost: 1`, OAuth-required access, required video identifier input, one-to-fifty comma-separated video IDs, optional partner-only `onBehalfOfContentOwner` if exposed, no request body, and per-video rating lookup success.

## Input Contract

The input schema must accept one object request.

Required fields:

- `id`: comma-separated list of one to fifty YouTube video identifiers.

Optional fields:

- `onBehalfOfContentOwner`: partner-only content owner identifier for eligible OAuth delegation contexts.

Rules:

- `id` must be present, non-empty, and identify one to fifty unique videos.
- OAuth authorization must be available for every supported request.
- `onBehalfOfContentOwner` is accepted only as eligible partner OAuth delegation context and must not imply public API-key access.
- No request body is accepted for this tool.
- Unsupported fields, request-body fields, aliases, mutation fields, aggregation fields, and cross-endpoint workflow fields must be rejected before endpoint execution.
- Public examples, logs, metadata, and errors must not expose tokens, authorization headers, secret values, raw upstream diagnostics, stack traces, or unsafe request context.

## Input Schema

```json
{
  "type": "object",
  "required": ["id"],
  "properties": {
    "id": {
      "type": "string",
      "minLength": 1,
      "description": "Comma-separated YouTube video identifiers whose authorized-viewer ratings should be retrieved."
    },
    "onBehalfOfContentOwner": {
      "type": "string",
      "minLength": 1,
      "description": "Optional partner-only content-owner delegation value for eligible OAuth contexts."
    }
  },
  "additionalProperties": false
}
```

## Validation Rules

| Request Shape | Outcome |
|---------------|---------|
| One `id` + OAuth | Valid single-video rating lookup |
| Comma-separated `id` list up to 50 unique IDs + OAuth | Valid multi-video rating lookup |
| `id` + `onBehalfOfContentOwner` + eligible partner OAuth | Valid delegated partner lookup |
| Missing `id` | `invalid_request` |
| Empty or non-string `id` | `invalid_request` |
| Duplicate identifiers | `invalid_request` |
| More than 50 identifiers | `invalid_request` |
| Empty identifier inside comma-separated list | `invalid_request` |
| Request `body` supplied | `invalid_request` |
| Unsupported top-level fields | `invalid_request` |
| Invalid or unsupported `onBehalfOfContentOwner` | `invalid_request` or `authorization_failed` according to whether the value or caller access is invalid |
| Rating mutation, rating history, aggregate rating count, metadata, update, upload, delete, abuse report, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, or enrichment fields | `invalid_request` |
| API-key-only access | `authentication_failed` |
| Missing OAuth | `authentication_failed` |
| OAuth exists but cannot retrieve requested rating state | `authorization_failed` |
| Target video not found | `resource_not_found` |
| Quota exhausted | `quota_exhausted` |
| Rating lookup endpoint unavailable | `endpoint_unavailable` |
| Deprecated behavior reported by upstream | `deprecated_endpoint` |

## Successful Result Shape

```json
{
  "endpoint": "videos.getRating",
  "quotaCost": 1,
  "lookup": {
    "requestedIds": ["abc123", "def456"],
    "resultCount": 2
  },
  "auth": {
    "mode": "oauth_required",
    "path": "restricted"
  },
  "availability": {
    "state": "active"
  },
  "items": [
    {
      "videoId": "abc123",
      "rating": "like"
    },
    {
      "videoId": "def456",
      "rating": "none"
    }
  ],
  "kind": "youtube#videoGetRatingResponse"
}
```

Returned ratings may include `like`, `dislike`, `none`, or `unspecified`. `none` and `unspecified` are successful lookup states and must not be represented as local validation failures.

## Response Convention

- `resultKind`: `rating_lookup`
- `resourcePath`: `items`
- `authMode`: `oauth_required`
- `requiredFields`: `id`
- `optionalFields`: `onBehalfOfContentOwner`
- `ratingValues`: `like`, `dislike`, `none`, `unspecified`
- `successBody`: `videoGetRatingResponse`

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `lookup`, `auth`, `availability`, `items`, `kind`, `etag`
- **Preserved upstream fields**: `kind`, `etag`, `items[].videoId`, `items[].rating` when present and safe
- **Disallowed behavior**: `rating_mutation`, `rating_history`, `aggregate_rating_counts`, `metadata_lookup`, `metadata_update`, `media_upload`, `media_replacement`, `transcoding`, `automatic_publishing`, `video_creation`, `video_delete`, `abuse_reporting`, `thumbnail_management`, `caption_management`, `playlist_management`, `comment_management`, `transcript_retrieval`, `analytics`, `recommendation`, `ranking`, `summarization`, `enrichment`, `cross_endpoint_aggregation`

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

Duplicate identifiers:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "id",
    "reason": "duplicate_identifiers"
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

Delegation not permitted:

```json
{
  "category": "authorization_failed",
  "details": {
    "field": "onBehalfOfContentOwner"
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

MCP clients must be able to discover `videos_getRating` in the default tool catalog with:

- tool name and description
- input schema above
- mapped upstream operation metadata
- quota cost `1`
- OAuth-required auth mode
- one-to-fifty comma-separated identifier boundary
- optional partner delegation caveat when exposed
- returned rating-state values
- no-request-body caveat
- per-video rating lookup success result
- safe error categories
- representative examples for success and failure

## Registration Expectations

- `build_videos_get_rating_contract()` builds the shared contract metadata.
- `build_videos_get_rating_tool_descriptor()` returns a dispatcher-ready descriptor.
- `build_videos_get_rating_handler()` validates, executes, and maps one request.
- `validate_videos_get_rating_arguments()` normalizes one request or raises a safe validation error.
- `map_videos_get_rating_result()` returns structured per-video lookup results without fabricating unrelated video data.
- `VIDEOS_GET_RATING_*` or project-consistent `VIDEOS_GETRATING_*` symbols are exported through the videos family module and shared package exports.
- Default dispatcher registration includes `videos_getRating` once the descriptor exists.
