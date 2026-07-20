# Contract: `thumbnails_set`

## Public Tool Identity

- **Tool name**: `thumbnails_set`
- **Layer**: Layer 2 public MCP endpoint tool
- **Mapped upstream operation**: `thumbnails.set`
- **Resource family**: `thumbnails`
- **Official quota cost**: `50` units per invocation
- **Auth mode**: `oauth_required`
- **Availability**: Active unless official endpoint caveats recorded during implementation say otherwise
- **Response boundary**: Near-raw endpoint-backed thumbnail-set result

## Purpose

Set the custom thumbnail for one YouTube video using the low-level `thumbnails.set` endpoint behavior. This tool is for direct endpoint access, debugging, power-user workflows, and later composition by higher layers.

## Out Of Scope

`thumbnails_set` does not generate thumbnails, edit or transform images, upload videos, update video metadata, manage channel branding, list videos, infer video identifiers from URLs or search terms, perform bulk thumbnail updates, preflight target-video eligibility, provide analytics, rank results, summarize results, enrich video data, or compose multiple endpoint calls.

## Input Schema

```json
{
  "type": "object",
  "required": ["videoId", "media"],
  "properties": {
    "videoId": {
      "type": "string",
      "minLength": 1,
      "description": "Identifier for the video whose custom thumbnail should be set."
    },
    "media": {
      "type": "object",
      "required": ["mimeType", "content"],
      "properties": {
        "mimeType": {
          "type": "string",
          "description": "Safe descriptor for the thumbnail media type."
        },
        "content": {
          "type": "string",
          "minLength": 1,
          "description": "Thumbnail upload content. Raw content must never be echoed in results or errors."
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

## Input Rules

- `videoId` is required and must be non-empty text after trimming.
- `media` is required and must include supported upload content.
- OAuth-backed user authorization is required before execution.
- API-key-only access is invalid for thumbnail setting.
- Additional fields are rejected before endpoint execution unless explicitly documented as supported.
- Video URLs, search terms, channel selectors, playlist selectors, request bodies for video metadata, thumbnail generation prompts, image transformation options, paging controls, analytics flags, ranking flags, summarization flags, and enrichment flags are invalid.
- Raw upload content is accepted only as request input and must never be echoed in success results, failures, logs, metadata, or examples.

## Success Result Shape

```json
{
  "endpoint": "thumbnails.set",
  "quotaCost": 50,
  "updated": true,
  "target": {
    "videoId": "video-123"
  },
  "upload": {
    "mimeType": "image/png",
    "contentProvided": true
  },
  "auth": {
    "mode": "oauth_required"
  },
  "upstream": {}
}
```

## Success Result Rules

- `endpoint` is always `thumbnails.set`.
- `quotaCost` is always `50`.
- `updated` is `true` only when thumbnail setting succeeds.
- `target.videoId` preserves the caller's validated target video identifier.
- `upload` contains safe upload descriptors only and never includes raw content.
- `auth.mode` discloses the safe authorization mode and never includes credentials.
- `upstream` may include safe thumbnail-set fields when returned; it must not include raw diagnostics, credentials, or raw upload content.
- The result must not fabricate thumbnail image details, video metadata, channel details, analytics, recommendations, rankings, summaries, or enrichment.

## Failure Categories

| Category | Trigger | Required Detail |
|----------|---------|-----------------|
| `invalid_request` | Missing, empty, malformed, unsupported, or extra input fields | Include `field` when one field caused the failure |
| `authentication_failed` | OAuth access is missing, expired, invalid, or unavailable | Include `authMode: oauth_required` |
| `authorization_failed` | Caller has OAuth but cannot update the target video thumbnail | Include safe reason when available |
| `target_video_failed` | Target video is missing, unavailable, unwritable, or custom-thumbnail-ineligible | Include safe target context when available |
| `unsupported_upload` | Upload content is missing, malformed, empty, unsupported, or outside the public upload boundary | Include safe upload descriptor when available |
| `upload_rejected` | Upstream rejects the uploaded thumbnail content | Include sanitized reason when available |
| `quota_exhausted` | Quota prevents thumbnail setting | Include safe quota context when available |
| `endpoint_unavailable` | Upstream thumbnail-setting endpoint is unavailable | Include safe availability context when available |
| `deprecated_endpoint` | Upstream thumbnail-setting endpoint is deprecated or disabled | Include safe caveat when available |
| `upstream_failure` | Unexpected upstream failure | Include only sanitized diagnostic details |

## Required Caller Examples

### Successful Thumbnail Setting

```json
{
  "name": "oauth_thumbnail_set",
  "description": "Quota cost: 50. Set one video's custom thumbnail with OAuth authorization and media upload content.",
  "arguments": {
    "videoId": "video-123",
    "media": {
      "mimeType": "image/png",
      "content": "<thumbnail content omitted>"
    }
  },
  "result": {
    "endpoint": "thumbnails.set",
    "quotaCost": 50,
    "updated": true,
    "target": {
      "videoId": "video-123"
    },
    "upload": {
      "mimeType": "image/png",
      "contentProvided": true
    }
  },
  "quotaCost": 50
}
```

### Sparse Successful Result

```json
{
  "name": "sparse_success",
  "description": "Quota cost: 50. Preserve target and upload context when the upstream success response is sparse.",
  "arguments": {
    "videoId": "video-123",
    "media": {
      "mimeType": "image/jpeg",
      "content": "<thumbnail content omitted>"
    }
  },
  "result": {
    "endpoint": "thumbnails.set",
    "quotaCost": 50,
    "updated": true,
    "target": {
      "videoId": "video-123"
    }
  }
}
```

### Missing Video Identifier

```json
{
  "name": "missing_video_id",
  "description": "Quota cost: 50. Reject thumbnail-setting requests missing the required videoId.",
  "arguments": {
    "media": {
      "mimeType": "image/png",
      "content": "<thumbnail content omitted>"
    }
  },
  "error": {
    "category": "invalid_request",
    "field": "videoId"
  }
}
```

### Missing Upload Content

```json
{
  "name": "missing_media",
  "description": "Quota cost: 50. Reject thumbnail-setting requests missing required media upload content.",
  "arguments": {
    "videoId": "video-123"
  },
  "error": {
    "category": "invalid_request",
    "field": "media"
  }
}
```

### Unsupported Upload Content

```json
{
  "name": "unsupported_upload",
  "description": "Quota cost: 50. Reject malformed or unsupported thumbnail upload content safely.",
  "arguments": {
    "videoId": "video-123",
    "media": {
      "mimeType": "text/plain",
      "content": "<thumbnail content omitted>"
    }
  },
  "error": {
    "category": "unsupported_upload",
    "field": "media"
  }
}
```

### Missing OAuth

```json
{
  "name": "access_failure",
  "description": "Quota cost: 50. Map missing or invalid OAuth access to safe authentication errors.",
  "arguments": {
    "videoId": "video-123",
    "media": {
      "mimeType": "image/png",
      "content": "<thumbnail content omitted>"
    }
  },
  "error": {
    "category": "authentication_failed",
    "authMode": "oauth_required"
  }
}
```

### Target Video Or Quota Failure

```json
{
  "name": "target_video_or_quota_failure",
  "description": "Quota cost: 50. Map target-video, upload, quota, and upstream failures to safe categories.",
  "arguments": {
    "videoId": "video-ineligible",
    "media": {
      "mimeType": "image/png",
      "content": "<thumbnail content omitted>"
    }
  },
  "error": {
    "category": "target_video_failed"
  }
}
```

### Out-Of-Scope Workflow Request

```json
{
  "name": "out_of_scope_thumbnail_management_request",
  "description": "Quota cost: 50. Thumbnail generation, image editing, metadata updates, analytics, and enrichment are out of scope.",
  "arguments": {
    "videoId": "video-123",
    "media": {
      "mimeType": "image/png",
      "content": "<thumbnail content omitted>"
    },
    "generateThumbnail": true
  },
  "error": {
    "category": "invalid_request",
    "field": "generateThumbnail"
  }
}
```

## Discovery Metadata Requirements

- Metadata includes `name: thumbnails_set`.
- Metadata includes upstream `resource: thumbnails`, `method: set`, and `operationKey: thumbnails.set`.
- Metadata includes `quotaCost: 50`.
- Metadata includes `authMode: oauth_required`.
- Metadata includes the input schema above.
- Metadata response convention identifies a thumbnail-set media-upload mutation result.
- Description, usage notes, caveats, and examples all mention quota cost `50`.
- Description, usage notes, caveats, and examples all make OAuth-required access visible.
- Description, usage notes, caveats, and examples all make the required media-upload boundary visible.

## Security Requirements

- Results and errors must not expose API keys, OAuth tokens, authorization headers, raw upload bytes, raw upstream bodies, stack traces, or unsafe request context.
- Error details must be sanitized before returning to MCP callers.
- Examples must not contain real credentials, real account identifiers, or raw media content.
