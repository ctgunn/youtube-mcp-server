# Contract: `videos_list`

## Public Identity

- **Tool name**: `videos_list`
- **Upstream resource**: `videos`
- **Upstream method**: `list`
- **Operation key**: `videos.list`
- **HTTP method/path**: `GET /youtube/v3/videos`
- **Quota cost**: `1`
- **Auth mode**: conditional; API-key-compatible for `id` and `chart`, OAuth-required for `myRating`
- **Availability**: `active`
- **Layer 1 dependency**: `build_videos_list_wrapper()`

## Description Requirements

The public description and usage notes must state:

- The tool retrieves YouTube video resources through the upstream `videos.list` endpoint.
- The official quota cost is `1`.
- `id` and `chart` retrieval use API-key-compatible access.
- `myRating` retrieval requires eligible OAuth access because it is caller-specific.
- `part` is required.
- Exactly one supported selector is required: `id`, `chart`, or `myRating`.
- `id` retrieves one or more specific video resources and does not support pagination.
- `chart` retrieves a supported video chart collection and may use `pageToken`, `maxResults`, `regionCode`, and `videoCategoryId` where compatible.
- `myRating` retrieves the caller's eligible rated-video collection and may use `pageToken` and `maxResults` where compatible.
- Empty successful video collections are distinct from validation failures and upstream failures.
- The tool does not perform video search, media upload, video update, video deletion, rating mutation, transcript retrieval, recommendation, ranking, analytics, summarization, enrichment, or cross-endpoint aggregation.

## Input Schema

```json
{
  "type": "object",
  "required": ["part"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1,
      "description": "Comma-separated video resource parts to return."
    },
    "id": {
      "type": "string",
      "minLength": 1,
      "description": "One or more video identifiers for direct lookup."
    },
    "chart": {
      "type": "string",
      "minLength": 1,
      "description": "A supported chart collection selector."
    },
    "myRating": {
      "type": "string",
      "minLength": 1,
      "description": "Caller-specific rating selector requiring OAuth access."
    },
    "pageToken": {
      "type": "string",
      "minLength": 1,
      "description": "Optional page token for compatible collection selectors."
    },
    "maxResults": {
      "type": "integer",
      "minimum": 1,
      "maximum": 50,
      "description": "Optional page size for compatible collection selectors."
    },
    "regionCode": {
      "type": "string",
      "minLength": 2,
      "maxLength": 2,
      "description": "Optional chart-only region refinement."
    },
    "videoCategoryId": {
      "type": "string",
      "minLength": 1,
      "description": "Optional chart-only category refinement."
    }
  },
  "oneOf": [
    { "required": ["id"] },
    { "required": ["chart"] },
    { "required": ["myRating"] }
  ],
  "additionalProperties": false
}
```

## Validation Rules

| Request Shape | Outcome |
|---------------|---------|
| `part` + `id` + API-key access | Valid direct video lookup |
| `part` + `chart` + API-key access | Valid chart collection lookup |
| `part` + `chart` + compatible pagination | Valid paginated chart traversal |
| `part` + `chart` + `regionCode` or `videoCategoryId` | Valid chart refinement when values are supported |
| `part` + `myRating` + OAuth access | Valid caller-specific rated-video lookup |
| `part` + `myRating` + compatible pagination | Valid paginated rated-video traversal |
| Missing `part` | `invalid_request` |
| Missing all selectors | `invalid_request` |
| Multiple selectors supplied | `invalid_request` |
| Empty or malformed `id` | `invalid_request` |
| Empty or unsupported `chart` | `invalid_request` |
| Empty or unsupported `myRating` | `invalid_request` |
| `pageToken` or `maxResults` with `id` | `invalid_request` |
| Empty `pageToken` | `invalid_request` |
| Invalid or out-of-range `maxResults` | `invalid_request` |
| `regionCode` or `videoCategoryId` without `chart` | `invalid_request` |
| Missing API key for `id` or `chart` | `authentication_failed` |
| Missing OAuth access for `myRating` | `authentication_failed` |
| Access denied for selected mode | `authorization_failed` |
| Unknown video ID | `resource_not_found` or successful empty result, depending on dependency/upstream outcome |
| Unsupported optional parameters | `invalid_request` |
| Search, upload, update, delete, rating mutation, transcript, analytics, recommendation, ranking, summarization, or enrichment fields | `invalid_request` |
| Quota exhausted | `quota_exhausted` |
| Endpoint unavailable | `endpoint_unavailable` |
| Deprecated behavior reported by upstream | `deprecated_endpoint` |

## Successful Result Shape

Direct ID lookup:

```json
{
  "endpoint": "videos.list",
  "quotaCost": 1,
  "requestedParts": ["snippet", "contentDetails"],
  "selector": {
    "mode": "id",
    "id": ["abc123"]
  },
  "auth": {
    "mode": "api_key",
    "path": "public"
  },
  "availability": {
    "state": "active"
  },
  "items": [
    {
      "kind": "youtube#video",
      "id": "abc123",
      "snippet": {
        "title": "Example video"
      }
    }
  ],
  "empty": false
}
```

Chart lookup:

```json
{
  "endpoint": "videos.list",
  "quotaCost": 1,
  "requestedParts": ["snippet", "statistics"],
  "selector": {
    "mode": "chart",
    "chart": "mostPopular"
  },
  "chartRefinement": {
    "regionCode": "US",
    "videoCategoryId": "10"
  },
  "pagination": {
    "maxResults": 25,
    "nextPageToken": "NEXT_PAGE"
  },
  "auth": {
    "mode": "api_key",
    "path": "public"
  },
  "availability": {
    "state": "active"
  },
  "items": [
    {
      "id": "abc123",
      "snippet": {
        "title": "Popular video"
      },
      "statistics": {
        "viewCount": "1000"
      }
    }
  ],
  "empty": false
}
```

Rating lookup:

```json
{
  "endpoint": "videos.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "selector": {
    "mode": "myRating",
    "myRating": "like"
  },
  "auth": {
    "mode": "oauth_required",
    "path": "restricted"
  },
  "availability": {
    "state": "active"
  },
  "items": [],
  "empty": true
}
```

## Response Convention

- `resultKind`: `list`
- `itemsPath`: `items`
- `authMode`: `mixed`
- `selectorFields`: `id`, `chart`, `myRating`
- `paginationFields`: `pageToken`, `maxResults`, `nextPageToken`, `prevPageToken`
- `chartRefinementFields`: `regionCode`, `videoCategoryId`
- `emptyResultPolicy`: successful empty `items` collection
- `availabilityState`: `active`

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `requestedParts`, `selector`, `pagination`, `chartRefinement`, `auth`, `availability`, `items`, `empty`, `kind`, `etag`, `pageInfo`, `nextPageToken`, `prevPageToken`, `id`, `snippet`, `contentDetails`, `statistics`, `status`, `player`, `topicDetails`, `recordingDetails`, `fileDetails`, `processingDetails`, `suggestions`, `liveStreamingDetails`, `localizations`
- **Preserved upstream fields**: `kind`, `etag`, `id`, `snippet`, `contentDetails`, `statistics`, `status`, `player`, `topicDetails`, `recordingDetails`, `fileDetails`, `processingDetails`, `suggestions`, `liveStreamingDetails`, `localizations`, `items`, `pageInfo`, `nextPageToken`, `prevPageToken`
- **Disallowed behavior**: `video_search`, `media_upload`, `metadata_update`, `video_delete`, `rating_mutation`, `transcript_retrieval`, `analytics`, `recommendation`, `ranking`, `summarization`, `enrichment`, `cross_endpoint_aggregation`

## Validation Failures

Missing part:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "part"
  }
}
```

Conflicting selectors:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "selector",
    "allowed": ["id", "chart", "myRating"]
  }
}
```

Restricted access failure:

```json
{
  "category": "authentication_failed",
  "details": {
    "authMode": "oauth_required",
    "selector": "myRating"
  }
}
```

Invalid pagination:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "pageToken"
  }
}
```

Out-of-scope workflow:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "includeTranscript"
  }
}
```

## Error Contract

Failures must use safe caller-facing categories and sanitized details:

- `invalid_request`: Missing `part`, missing selector, blank inputs, non-string inputs, conflicting selectors, unsupported field, unsupported modifier, invalid pagination, incompatible selector/refinement combination, or out-of-scope workflow request
- `authentication_failed`: Required API-key or OAuth credential material missing or invalid
- `authorization_failed`: Caller lacks access for the selected video-list path
- `quota_exhausted`: Upstream quota failure
- `resource_not_found`: Upstream confirms requested video resources are unavailable or removed
- `endpoint_unavailable`: Upstream service unavailable or timeout category
- `deprecated_endpoint`: Official endpoint behavior is deprecated or unavailable
- `upstream_failure`: Unexpected upstream failure after sanitization

Error details must not include API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, raw request context, or secret-bearing diagnostics.

## Representative Examples

### Direct Video Lookup

```json
{
  "part": "snippet,contentDetails",
  "id": "abc123"
}
```

Expected context:
- Endpoint `videos.list`
- Quota cost `1`
- API-key-compatible public access mode
- Direct video selector preserved

### Chart Lookup

```json
{
  "part": "snippet,statistics",
  "chart": "mostPopular",
  "regionCode": "US",
  "videoCategoryId": "10"
}
```

Expected context:
- Endpoint `videos.list`
- Quota cost `1`
- API-key-compatible public access mode
- Chart selector and chart refinements preserved

### Rating Lookup

```json
{
  "part": "snippet",
  "myRating": "like"
}
```

Expected context:
- Endpoint `videos.list`
- Quota cost `1`
- OAuth-backed restricted access required
- Caller-specific rating selector preserved

### Paginated Chart Lookup

```json
{
  "part": "snippet",
  "chart": "mostPopular",
  "pageToken": "NEXT_PAGE",
  "maxResults": 25
}
```

Expected context:
- Page token and maximum result count preserved safely
- Returned next or previous page tokens preserved when present

### Missing Required Input Failure

```json
{
  "id": "abc123"
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `part`

### Conflicting Selector Failure

```json
{
  "part": "snippet",
  "id": "abc123",
  "chart": "mostPopular"
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying mutually exclusive selectors

### Invalid Pagination Failure

```json
{
  "part": "snippet",
  "id": "abc123",
  "pageToken": "NEXT_PAGE"
}
```

Expected error:
- Category `invalid_request`
- Safe detail explaining that pagination is not supported for direct ID lookup

### Out-of-Scope Enrichment Request

```json
{
  "part": "snippet",
  "id": "abc123",
  "includeTranscript": true
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `includeTranscript`
