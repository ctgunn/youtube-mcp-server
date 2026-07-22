# Contract: Layer 2 `videos_insert` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `videos_insert` tool. The tool exposes the upstream YouTube Data API `videos.insert` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, auth, response-boundary, mutation, media-upload, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `videos.insert` request
- Video metadata, media-upload, OAuth, delegated content-owner, upload-mode, and availability caveat rules
- Near-raw successful created video-resource result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define automatic publishing, post-upload editing, thumbnail management, caption management, playlist management, comment management, rating mutation, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, hosted transport changes, persistence, or cross-endpoint orchestration.

## Tool Identity

The public tool must expose:

- `name`: `videos_insert`
- `upstream.resource`: `videos`
- `upstream.method`: `insert`
- `upstream.operationKey`: `videos.insert`
- `quotaCost`: `1600`
- `authMode`: `oauth_required`
- `availabilityState`: media-constrained or limited upload operation, with visible audit/private-default, policy, release, and delegation caveats where applicable
- `resourceFamily`: `videos`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `videos.insert`, `Quota cost: 1600`, OAuth-required access, required video media input, required metadata input, and upload availability caveats.

## Input Contract

The input schema must accept one object request.

Required fields:

- `part`: comma-separated video resource parts requested for the creation response.
- `body`: video resource metadata body.
- `media`: video media input or safe media descriptor accepted by the implementation contract.

Required body shape:

- `body.snippet`: required metadata object for the primary supported creation path.

Required media shape:

- `media.mimeType`: media type when required by the supported descriptor.
- `media.content` or safe content reference: upload content or implementation-supported media reference.

Optional request fields:

- `uploadMode`: supported upload mode, limited to `multipart` or `resumable`.
- `notifySubscribers`: boolean notification preference when supported.
- `onBehalfOfContentOwner`: delegated content-owner context for eligible authorized callers.

Rules:

- `part` must be present and non-empty.
- `body` must be present and must satisfy the supported metadata shape.
- `media` must be present and must satisfy the supported safe media descriptor shape.
- OAuth authorization must be available for every supported request.
- `uploadMode`, when supplied, must be a supported upload mode.
- `notifySubscribers`, when supplied, must be boolean.
- Delegation context may be supplied only with eligible OAuth authorization.
- Unsupported fields must be rejected when the public schema disallows them.
- Public examples, logs, metadata, and errors must not expose raw video media, signed URLs, tokens, authorization headers, secret values, or unsafe upstream diagnostics.

## Input Schema

```json
{
  "type": "object",
  "required": ["part", "body", "media"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1,
      "description": "Comma-separated video resource parts requested for the creation response."
    },
    "body": {
      "type": "object",
      "description": "Video resource metadata body for the supported creation path."
    },
    "media": {
      "type": "object",
      "description": "Safe video media upload descriptor."
    },
    "uploadMode": {
      "type": "string",
      "enum": ["multipart", "resumable"],
      "description": "Optional supported upload mode."
    },
    "notifySubscribers": {
      "type": "boolean",
      "description": "Optional subscriber-notification preference when supported."
    },
    "onBehalfOfContentOwner": {
      "type": "string",
      "minLength": 1,
      "description": "Optional delegated content-owner context requiring eligible OAuth authorization."
    }
  },
  "additionalProperties": false
}
```

## Validation Rules

| Request Shape | Outcome |
|---------------|---------|
| `part` + `body` + `media` + OAuth | Valid video creation request |
| `part` + `body` + `media` + supported `uploadMode` + OAuth | Valid upload-mode-specific creation request |
| `part` + `body` + `media` + `onBehalfOfContentOwner` + eligible OAuth | Valid delegated creation request |
| Missing `part` | `invalid_request` |
| Empty or non-string `part` | `invalid_request` |
| Missing `body` | `invalid_request` |
| Incomplete or unsupported `body` | `invalid_request` |
| Missing `media` | `invalid_request` |
| Incomplete or unsupported `media` | `invalid_request` |
| Unsupported `uploadMode` | `invalid_request` |
| Non-boolean `notifySubscribers` | `invalid_request` |
| Delegation context without eligible OAuth | `authentication_failed` or `authorization_failed` depending on credential state |
| API-key-only access | `authentication_failed` |
| OAuth exists but cannot upload for selected account, channel, or delegated owner | `authorization_failed` |
| Unsupported optional fields | `invalid_request` |
| Automatic publishing, edit, delete, rating, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, or enrichment fields | `invalid_request` |
| Quota exhausted | `quota_exhausted` |
| Upload endpoint unavailable | `endpoint_unavailable` |
| Policy or release availability refusal | `authorization_failed`, `endpoint_unavailable`, or closest shared safe category |
| Deprecated behavior reported by upstream | `deprecated_endpoint` |

## Successful Result Shape

```json
{
  "endpoint": "videos.insert",
  "quotaCost": 1600,
  "requestedParts": ["snippet", "status"],
  "upload": {
    "mode": "resumable",
    "hasMedia": true,
    "mediaType": "video/mp4"
  },
  "auth": {
    "mode": "oauth_required",
    "path": "restricted"
  },
  "availability": {
    "state": "media_constrained",
    "caveats": [
      "New uploads may be audit-constrained or private by default depending on account and release state."
    ]
  },
  "delegation": {
    "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
  },
  "item": {
    "kind": "youtube#video",
    "id": "abc123",
    "snippet": {
      "title": "Example upload"
    },
    "status": {
      "privacyStatus": "private"
    }
  },
  "mutation": {
    "type": "created"
  }
}
```

## Response Convention

- `resultKind`: `upload_result`
- `resourcePath`: `item`
- `authMode`: `oauth_required`
- `requiredFields`: `part`, `body`, `media`
- `optionalFields`: `uploadMode`, `notifySubscribers`, `onBehalfOfContentOwner`
- `mediaFields`: `media`
- `delegationFields`: `onBehalfOfContentOwner`
- `availabilityState`: `media_constrained`

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `requestedParts`, `upload`, `auth`, `availability`, `delegation`, `item`, `mutation`
- **Preserved upstream fields**: `kind`, `etag`, `id`, `snippet`, `status`, `contentDetails`, `processingDetails`, `fileDetails`, `suggestions`, `localizations`, and other fields returned for requested parts
- **Disallowed behavior**: `automatic_publishing`, `metadata_update`, `video_delete`, `rating_mutation`, `thumbnail_management`, `caption_management`, `playlist_management`, `comment_management`, `transcript_retrieval`, `analytics`, `recommendation`, `ranking`, `summarization`, `enrichment`, `cross_endpoint_aggregation`

## Validation Failures

Missing media:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "media"
  }
}
```

Missing body:

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

Unsupported upload mode:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "uploadMode",
    "allowed": ["multipart", "resumable"]
  }
}
```

## Usage Examples

### Authorized Video Creation

```json
{
  "part": "snippet,status",
  "body": {
    "snippet": {
      "title": "Example upload",
      "description": "A test-safe upload example"
    },
    "status": {
      "privacyStatus": "private"
    }
  },
  "media": {
    "mimeType": "video/mp4",
    "contentRef": "test-safe-video-media"
  }
}
```

Expected metadata: `videos.insert`, `Quota cost: 1600`, eligible OAuth authorization required, video media input required.

### Resumable Upload

```json
{
  "part": "snippet,status",
  "body": {
    "snippet": {
      "title": "Resumable upload example"
    }
  },
  "media": {
    "mimeType": "video/mp4",
    "contentRef": "test-safe-video-media"
  },
  "uploadMode": "resumable"
}
```

Expected metadata: `videos.insert`, `Quota cost: 1600`, OAuth required, supported resumable upload mode visible.

### Delegated Content Owner

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "title": "Partner upload"
    }
  },
  "media": {
    "mimeType": "video/mp4",
    "contentRef": "test-safe-video-media"
  },
  "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
}
```

Expected metadata: `videos.insert`, `Quota cost: 1600`, eligible OAuth authorization required, delegated content-owner context visible.

### Metadata-Only Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "title": "Missing media"
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that media input is required.

### Media-Only Failure

```json
{
  "part": "snippet",
  "media": {
    "mimeType": "video/mp4",
    "contentRef": "test-safe-video-media"
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that video metadata body is required.

### Out-of-Scope Workflow Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "title": "Upload and rank this video"
    }
  },
  "media": {
    "mimeType": "video/mp4",
    "contentRef": "test-safe-video-media"
  },
  "analytics": true
}
```

Expected behavior: reject with safe `invalid_request` guidance because analytics, ranking, summarization, enrichment, and cross-endpoint behavior are outside `videos_insert`.

## Discovery and Registration Expectations

Reviewers must be able to verify through public discovery or registration artifacts that:

- `videos_insert` is listed as a callable tool.
- The input schema includes required `part`, required `body`, required `media`, optional `uploadMode`, optional `notifySubscribers`, and optional delegated content-owner context.
- The description and metadata expose quota cost `1600`.
- The description and metadata expose OAuth-required auth.
- Usage notes include quota, examples, metadata guidance, media-upload guidance, upload-mode guidance, delegation guidance, availability caveats, and out-of-scope workflow boundaries.
- The handler is executable and not merely a representative descriptor.

## Validation Expectations

Focused validation should include:

```bash
pytest tests/unit/test_youtube_videos.py tests/contract/test_youtube_videos_contract.py tests/integration/test_youtube_videos_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

If Layer 1 wrapper behavior is touched, focused validation should also include:

```bash
pytest tests/contract/test_layer1_videos_contract.py tests/unit/test_layer1_foundation.py
```
