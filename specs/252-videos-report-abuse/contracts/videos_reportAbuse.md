# Contract: Layer 2 `videos_reportAbuse` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `videos_reportAbuse` tool. The tool exposes the upstream YouTube Data API `videos.reportAbuse` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, auth, mutation-result, payload-boundary, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `videos.reportAbuse` request
- Abuse-report body, OAuth, partner-delegation boundary, and no-content acknowledgment rules
- Structured successful mutation acknowledgment result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define abuse-reason discovery, automated abuse classification, evidence gathering, moderation decisions, video metadata lookup or update, rating lookup or mutation, upload, deletion, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, hosted transport changes, persistence, or cross-endpoint orchestration.

## Tool Identity

The public tool must expose:

- `name`: `videos_reportAbuse`
- `upstream.resource`: `videos`
- `upstream.method`: `reportAbuse`
- `upstream.operationKey`: `videos.reportAbuse`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active OAuth mutation operation with no-content acknowledgment and payload-boundary caveats
- `resourceFamily`: `videos`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `videos.reportAbuse`, `Quota cost: 50`, OAuth-required access, required `body.videoId`, required `body.reasonId`, supported optional `body.secondaryReasonId`, `body.comments`, and `body.language`, rejected `onBehalfOfContentOwner` in this slice, and successful report acknowledgment.

## Input Contract

The input schema must accept one object request.

Required fields:

- `body`: report-abuse request body object.
- `body.videoId`: target YouTube video identifier.
- `body.reasonId`: primary abuse reason identifier.

Optional body fields:

- `body.secondaryReasonId`: secondary abuse reason identifier.
- `body.comments`: explanatory comments for the report.
- `body.language`: language context for the report.

Rules:

- `body` must be present and must be an object.
- `body.videoId` must be present, non-empty, and identify one video.
- `body.reasonId` must be present, non-empty, and identify one abuse reason.
- Optional body fields, when supplied, must be non-empty strings within the documented payload boundary.
- OAuth authorization must be available for every supported request.
- `onBehalfOfContentOwner` is not accepted by this public slice because the local Layer 1 wrapper leaves partner delegation outside the guaranteed boundary.
- Unsupported fields, top-level aliases, request-shape aliases, partner delegation, classification fields, evidence fields, moderation fields, rating fields, deletion fields, and cross-endpoint workflow fields must be rejected before endpoint execution.
- Public examples, logs, metadata, and errors must not expose tokens, authorization headers, secret values, raw upstream diagnostics, stack traces, unsafe request context, or sensitive report details beyond safe caller context.

## Input Schema

```json
{
  "type": "object",
  "required": ["body"],
  "properties": {
    "body": {
      "type": "object",
      "required": ["videoId", "reasonId"],
      "properties": {
        "videoId": {
          "type": "string",
          "minLength": 1,
          "description": "YouTube video identifier being reported."
        },
        "reasonId": {
          "type": "string",
          "minLength": 1,
          "description": "Primary abuse reason identifier supplied by the caller."
        },
        "secondaryReasonId": {
          "type": "string",
          "minLength": 1,
          "description": "Optional secondary abuse reason identifier."
        },
        "comments": {
          "type": "string",
          "minLength": 1,
          "description": "Optional caller-provided report comments."
        },
        "language": {
          "type": "string",
          "minLength": 1,
          "description": "Optional language context for report comments or reason details."
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
| `body.videoId` + `body.reasonId` + OAuth | Valid abuse-report submission |
| Supported optional `secondaryReasonId`, `comments`, or `language` + OAuth | Valid abuse-report submission with optional details |
| Missing `body` | `invalid_request` |
| Non-object `body` | `invalid_request` |
| Missing `body.videoId` | `invalid_request` |
| Empty or non-string `body.videoId` | `invalid_request` |
| Missing `body.reasonId` | `invalid_request` |
| Empty or non-string `body.reasonId` | `invalid_request` |
| Empty or non-string optional body fields | `invalid_request` |
| Unsupported body fields | `invalid_request` |
| Unsupported top-level fields | `invalid_request` |
| `onBehalfOfContentOwner` supplied | `invalid_request` |
| Top-level `videoId` or `reasonId` aliases | `invalid_request` |
| Abuse-reason discovery, classification, evidence, moderation, metadata, rating, delete, comment, caption, transcript, analytics, recommendation, ranking, summarization, or enrichment fields | `invalid_request` |
| API-key-only access | `authentication_failed` |
| Missing OAuth | `authentication_failed` |
| OAuth exists but cannot submit the report | `authorization_failed` |
| Target video not found or not reportable | `resource_not_found` or `authorization_failed` according to upstream classification |
| Quota exhausted | `quota_exhausted` |
| Report-abuse endpoint unavailable | `endpoint_unavailable` |
| Deprecated behavior reported by upstream | `deprecated_endpoint` |
| Upstream refusal or duplicate-report-style outcome | `authorization_failed` |

## Successful Result Shape

```json
{
  "endpoint": "videos.reportAbuse",
  "quotaCost": 50,
  "report": {
    "videoId": "abc123",
    "reasonId": "VIOLENCE",
    "hasSecondaryReason": false,
    "hasComments": true,
    "language": "en"
  },
  "auth": {
    "mode": "oauth_required",
    "path": "restricted"
  },
  "availability": {
    "state": "active"
  },
  "acknowledgment": {
    "accepted": true,
    "status": "submitted"
  },
  "status": {
    "code": 204,
    "body": "none"
  }
}
```

Successful `videos.reportAbuse` behavior is a no-content report submission acknowledgment. The public result must not claim that YouTube accepted a moderation decision, removed a video, classified content, created an evidence record, or returned a refreshed video resource.

## Response Convention

- `resultKind`: `mutation_acknowledgment`
- `resourcePath`: absent for no-content success
- `authMode`: `oauth_required`
- `requiredFields`: `body.videoId`, `body.reasonId`
- `optionalFields`: `body.secondaryReasonId`, `body.comments`, `body.language`
- `successStatus`: `204`
- `statusBody`: no content

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `report`, `auth`, `availability`, `acknowledgment`, `status`
- **Preserved request fields**: `body.videoId`, `body.reasonId`, optional-field presence, `body.language` when safe
- **Disallowed behavior**: `abuse_reason_discovery`, `abuse_classification`, `evidence_collection`, `moderation_decision`, `metadata_lookup`, `metadata_update`, `rating_lookup`, `rating_mutation`, `media_upload`, `media_replacement`, `transcoding`, `automatic_publishing`, `video_delete`, `thumbnail_management`, `caption_management`, `playlist_management`, `comment_management`, `transcript_retrieval`, `analytics`, `recommendation`, `ranking`, `summarization`, `enrichment`, `cross_endpoint_aggregation`

## Validation Failures

Missing body:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "body"
  }
}
```

Missing target video:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "body.videoId"
  }
}
```

Missing reason:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "body.reasonId"
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

Partner delegation not accepted in this slice:

```json
{
  "category": "invalid_request",
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
    "field": "body.videoId"
  }
}
```

## Discovery Expectations

MCP clients must be able to discover `videos_reportAbuse` in the default tool catalog with:

- tool name and description
- input schema above
- mapped upstream operation metadata
- quota cost `50`
- OAuth-required auth mode
- required `body.videoId` and `body.reasonId`
- optional body fields
- rejected partner-delegation caveat
- no-content acknowledgment success result
- safe error categories
- representative examples for success and failure

## Registration Expectations

- `build_videos_report_abuse_contract()` builds the shared contract metadata.
- `build_videos_report_abuse_tool_descriptor()` returns a dispatcher-ready descriptor.
- `build_videos_report_abuse_handler()` validates, executes, and maps one request.
- `validate_videos_report_abuse_arguments()` normalizes one request or raises a safe validation error.
- `map_videos_report_abuse_result()` returns a structured acknowledgment without fabricating unrelated video or moderation data.
- `VIDEOS_REPORT_ABUSE_*` symbols are exported through the videos family module and shared package exports.
- Default dispatcher registration includes `videos_reportAbuse` once the descriptor exists.
