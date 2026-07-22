# Contract: Layer 2 `videos_update` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `videos_update` tool. The tool exposes the upstream YouTube Data API `videos.update` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, auth, response-boundary, mutation, writable-part, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `videos.update` request
- Video identity, writable-part, update-body, OAuth, delegated content-owner, and replacement-semantics rules
- Near-raw successful updated video-resource result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define media upload, media replacement, transcoding, automatic publishing workflow, video creation, video deletion, rating mutation, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, hosted transport changes, persistence, or cross-endpoint orchestration.

## Tool Identity

The public tool must expose:

- `name`: `videos_update`
- `upstream.resource`: `videos`
- `upstream.method`: `update`
- `upstream.operationKey`: `videos.update`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active mutation operation with OAuth, writable-part, update-body, and replacement-semantics caveats
- `resourceFamily`: `videos`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `videos.update`, `Quota cost: 50`, OAuth-required access, required video identity, required writable part selection, supported update body fields, and replacement-oriented update semantics for included parts.

## Input Contract

The input schema must accept one object request.

Required fields:

- `part`: writable video resource part selected for the update. The current supported value is `snippet`.
- `body`: video resource update body containing the target identity and supported writable fields.

Required body shape:

- `body.id`: target video identifier.
- `body.snippet.title`: required title value for the current minimum supported update path.

Optional request fields:

- `onBehalfOfContentOwner`: delegated content-owner context for eligible authorized callers when supported.

Rules:

- `part` must be present, non-empty, and supported.
- `body` must be present and must satisfy the supported update shape.
- `body.id` must identify the existing target video.
- `body.snippet.title` must be present for the current supported `snippet` update path.
- OAuth authorization must be available for every supported request.
- Delegation context may be supplied only with eligible OAuth authorization.
- Unsupported fields must be rejected when the public schema disallows them.
- Read-only fields, media fields, upload fields, and cross-endpoint workflow fields must be rejected before endpoint execution.
- Public examples, logs, metadata, and errors must not expose tokens, authorization headers, secret values, raw upstream diagnostics, stack traces, or unsafe request context.

## Input Schema

```json
{
  "type": "object",
  "required": ["part", "body"],
  "properties": {
    "part": {
      "type": "string",
      "enum": ["snippet"],
      "description": "Writable video resource part selected for update."
    },
    "body": {
      "type": "object",
      "required": ["id", "snippet"],
      "properties": {
        "id": {
          "type": "string",
          "minLength": 1,
          "description": "Existing video identifier targeted by the update."
        },
        "kind": {
          "type": "string",
          "description": "Optional safe upstream resource hint when accepted by the current contract."
        },
        "snippet": {
          "type": "object",
          "required": ["title"],
          "properties": {
            "title": {
              "type": "string",
              "minLength": 1,
              "description": "Updated video title for the current supported snippet path."
            }
          },
          "additionalProperties": false
        }
      },
      "additionalProperties": false
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
| `part=snippet` + `body.id` + `body.snippet.title` + OAuth | Valid video update request |
| `part=snippet` + `body.id` + `body.snippet.title` + `onBehalfOfContentOwner` + eligible OAuth | Valid delegated update request |
| Missing `part` | `invalid_request` |
| Empty or non-string `part` | `invalid_request` |
| Unsupported or read-only `part` | `invalid_request` |
| Missing `body` | `invalid_request` |
| Missing or empty `body.id` | `invalid_request` |
| Missing `body.snippet` | `invalid_request` |
| Missing or empty `body.snippet.title` | `invalid_request` |
| Unsupported body fields | `invalid_request` |
| Unsupported snippet fields | `invalid_request` |
| Media upload or media replacement fields | `invalid_request` |
| Delegation context without eligible OAuth | `authentication_failed` or `authorization_failed` depending on credential state |
| API-key-only access | `authentication_failed` |
| OAuth exists but cannot update selected video, account, channel, or delegated owner | `authorization_failed` |
| Unsupported optional fields | `invalid_request` |
| Automatic publishing, create, delete, rating, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, or enrichment fields | `invalid_request` |
| Target video not found | `resource_not_found` |
| Quota exhausted | `quota_exhausted` |
| Update endpoint unavailable | `endpoint_unavailable` |
| Policy or release availability refusal | `authorization_failed`, `endpoint_unavailable`, or closest shared safe category |
| Deprecated behavior reported by upstream | `deprecated_endpoint` |

## Successful Result Shape

```json
{
  "endpoint": "videos.update",
  "quotaCost": 50,
  "requestedParts": ["snippet"],
  "update": {
    "videoId": "abc123",
    "bodyFields": ["id", "snippet"],
    "snippetFields": ["title"]
  },
  "auth": {
    "mode": "oauth_required",
    "path": "restricted"
  },
  "delegation": {
    "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
  },
  "item": {
    "kind": "youtube#video",
    "id": "abc123",
    "snippet": {
      "title": "Updated example title"
    }
  },
  "mutation": {
    "type": "updated"
  }
}
```

## Response Convention

- `resultKind`: `mutation_result`
- `resourcePath`: `item`
- `authMode`: `oauth_required`
- `requiredFields`: `part`, `body`
- `optionalFields`: `onBehalfOfContentOwner`
- `delegationFields`: `onBehalfOfContentOwner`
- `mutationType`: `updated`

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `requestedParts`, `update`, `auth`, `delegation`, `item`, `mutation`
- **Preserved upstream fields**: `kind`, `etag`, `id`, `snippet`, `status`, `contentDetails`, `processingDetails`, `fileDetails`, `suggestions`, `localizations`, and other fields returned for requested parts
- **Disallowed behavior**: `media_upload`, `media_replacement`, `transcoding`, `automatic_publishing`, `video_creation`, `video_delete`, `rating_mutation`, `thumbnail_management`, `caption_management`, `playlist_management`, `comment_management`, `transcript_retrieval`, `analytics`, `recommendation`, `ranking`, `summarization`, `enrichment`, `cross_endpoint_aggregation`

## Validation Failures

Missing identity:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "body.id"
  }
}
```

Missing writable part:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "part",
    "allowed": ["snippet"]
  }
}
```

Read-only or unsupported field:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "body.status"
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

## Usage Examples

### Authorized Video Metadata Update

```json
{
  "part": "snippet",
  "body": {
    "id": "abc123",
    "snippet": {
      "title": "Updated example title"
    }
  }
}
```

Expected response:

```json
{
  "endpoint": "videos.update",
  "quotaCost": 50,
  "requestedParts": ["snippet"],
  "mutation": {
    "type": "updated"
  },
  "item": {
    "id": "abc123",
    "snippet": {
      "title": "Updated example title"
    }
  }
}
```

### Delegated Content Owner Update

```json
{
  "part": "snippet",
  "body": {
    "id": "abc123",
    "snippet": {
      "title": "Partner updated title"
    }
  },
  "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
}
```

### Missing Identity Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "title": "Updated example title"
    }
  }
}
```

Expected category: `invalid_request`

### Unsupported Field Failure

```json
{
  "part": "snippet",
  "body": {
    "id": "abc123",
    "snippet": {
      "title": "Updated example title",
      "description": "Not supported by the current public contract"
    }
  }
}
```

Expected category: `invalid_request`

### Missing OAuth Failure

```json
{
  "part": "snippet",
  "body": {
    "id": "abc123",
    "snippet": {
      "title": "Updated example title"
    }
  }
}
```

Expected category: `authentication_failed` when OAuth is not available.

## Discovery and Registration Requirements

- `videos_update` appears in MCP tool discovery with schema, description, usage notes, quota, auth, examples, and caveats.
- Default tool registration includes `videos_update` without requiring bespoke caller setup.
- Dispatcher invocation accepts the documented request shape and returns the documented result or error categories.
- Discovery and examples remain safe for public client inspection.
