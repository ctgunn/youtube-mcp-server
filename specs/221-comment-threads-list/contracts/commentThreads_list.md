# Contract: `commentThreads_list`

## Public Identity

- **Tool name**: `commentThreads_list`
- **Upstream resource**: `commentThreads`
- **Upstream method**: `list`
- **Operation key**: `commentThreads.list`
- **HTTP method/path**: `GET /youtube/v3/commentThreads`
- **Quota cost**: `1`
- **Auth mode**: `api_key` public retrieval, with documented access-sensitive caveats for moderation-status usage and inaccessible resources
- **Availability**: `active`
- **Layer 1 dependency**: `build_comment_threads_list_wrapper()`

## Description Requirements

The public description and usage notes must state:

- The tool retrieves comment threads through the upstream `commentThreads.list` endpoint.
- The official quota cost is `1`.
- `part` is required.
- Exactly one selector is required: `videoId`, `allThreadsRelatedToChannelId`, or `id`.
- `maxResults`, `moderationStatus`, `order`, `pageToken`, and `searchTerms` are not supported with `id`.
- `moderationStatus` is access-sensitive and only valid when the caller is eligible for the requested moderation view.
- `textFormat` may be `html` or `plainText`.
- A request body is unsupported.
- Missing videos, missing channels, missing thread IDs, disabled comments, and inaccessible resources are distinct from empty successful collections.
- The tool does not perform reply-only listing, thread creation, comment insertion, comment updates, comment deletion, moderation actions, sentiment analysis, ranking, summarization, enrichment, or cross-endpoint aggregation.

## Input Schema

```json
{
  "type": "object",
  "required": ["part"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1,
      "description": "Comma-separated commentThread resource parts to return, such as id, replies, or snippet."
    },
    "videoId": {
      "type": "string",
      "minLength": 1,
      "description": "Video ID whose comment threads should be retrieved."
    },
    "allThreadsRelatedToChannelId": {
      "type": "string",
      "minLength": 1,
      "description": "Channel ID whose related comment threads should be retrieved."
    },
    "id": {
      "type": "string",
      "minLength": 1,
      "description": "Comma-separated comment thread IDs for direct thread retrieval."
    },
    "maxResults": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "description": "Maximum number of comment threads to return for supported non-id selectors."
    },
    "moderationStatus": {
      "type": "string",
      "enum": ["heldForReview", "likelySpam", "published"],
      "description": "Access-sensitive moderation filter for supported non-id selectors."
    },
    "order": {
      "type": "string",
      "enum": ["time", "relevance"],
      "description": "Ordering for supported non-id selector results."
    },
    "pageToken": {
      "type": "string",
      "minLength": 1,
      "description": "Result page token for supported non-id selector pagination."
    },
    "searchTerms": {
      "type": "string",
      "minLength": 1,
      "description": "Search terms used to limit returned comment threads for supported non-id selectors."
    },
    "textFormat": {
      "type": "string",
      "enum": ["html", "plainText"],
      "description": "Comment text format requested from upstream."
    }
  },
  "oneOf": [
    {"required": ["videoId"]},
    {"required": ["allThreadsRelatedToChannelId"]},
    {"required": ["id"]}
  ],
  "additionalProperties": false
}
```

## Selector Rules

| Request Shape | Outcome |
|---------------|---------|
| `part` + `videoId` | Valid video-based thread retrieval |
| `part` + `allThreadsRelatedToChannelId` | Valid channel-related thread retrieval |
| `part` + `id` | Valid direct thread retrieval |
| `part` + `videoId` + `maxResults` | Valid paginated video-based retrieval |
| `part` + `allThreadsRelatedToChannelId` + `pageToken` | Valid paginated channel-related retrieval |
| `part` + `videoId` + `order` | Valid ordered video-based retrieval |
| `part` + `videoId` + `searchTerms` | Valid searched video-based retrieval |
| `part` + `videoId` + `textFormat` | Valid formatted video-based retrieval |
| `part` + `videoId` + `moderationStatus` | Valid only with eligible access; otherwise authorization failure |
| `part` only | `invalid_request` |
| `part` + multiple selectors | `invalid_request` |
| `part` + `id` + `maxResults` | `invalid_request` |
| `part` + `id` + `moderationStatus` | `invalid_request` |
| `part` + `id` + `order` | `invalid_request` |
| `part` + `id` + `pageToken` | `invalid_request` |
| `part` + `id` + `searchTerms` | `invalid_request` |
| Missing `part` | `invalid_request` |
| Unsupported request body or workflow fields | `invalid_request` |

## Successful Result Shape

Video-based retrieval:

```json
{
  "endpoint": "commentThreads.list",
  "quotaCost": 1,
  "requestedParts": ["snippet", "replies"],
  "selector": {
    "name": "videoId"
  },
  "textFormat": "html",
  "items": [
    {
      "kind": "youtube#commentThread",
      "id": "thread-123",
      "snippet": {
        "videoId": "video-123"
      }
    }
  ],
  "kind": "youtube#commentThreadListResponse",
  "etag": "etag-123"
}
```

Channel-related retrieval with pagination:

```json
{
  "endpoint": "commentThreads.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "selector": {
    "name": "allThreadsRelatedToChannelId"
  },
  "textFormat": "plainText",
  "items": [
    {
      "kind": "youtube#commentThread",
      "id": "thread-456",
      "snippet": {
        "channelId": "channel-123"
      }
    }
  ],
  "nextPageToken": "NEXT_PAGE",
  "pageInfo": {
    "totalResults": 1,
    "resultsPerPage": 1
  }
}
```

ID-based retrieval:

```json
{
  "endpoint": "commentThreads.list",
  "quotaCost": 1,
  "requestedParts": ["id", "snippet"],
  "selector": {
    "name": "id"
  },
  "items": [
    {
      "kind": "youtube#commentThread",
      "id": "thread-123"
    }
  ]
}
```

Empty successful result:

```json
{
  "endpoint": "commentThreads.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "selector": {
    "name": "videoId"
  },
  "textFormat": "html",
  "items": []
}
```

## Response Convention

- `resultKind`: `list`
- `successStatus`: `commentThreadListResponse`
- `itemField`: `items`
- `paginationFields`: `nextPageToken`, `pageInfo`
- `selectorFields`: `videoId`, `allThreadsRelatedToChannelId`, `id`
- `optionalContextFields`: `maxResults`, `moderationStatus`, `order`, `pageToken`, `searchTerms`, `textFormat`
- `emptyResultPolicy`: `empty_success_when_upstream_returns_empty_items`

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `requestedParts`, `selector`, `textFormat`, `options`, `items`, `kind`, `etag`, `nextPageToken`, `pageInfo`
- **Preserved upstream fields**: `kind`, `etag`, `nextPageToken`, `pageInfo`, `items`
- **Disallowed behavior**: `reply_only_listing`, `thread_creation`, `comment_insert`, `comment_update`, `comment_delete`, `moderation_action`, `sentiment_analysis`, `ranking`, `summarization`, `enrichment`, `cross_endpoint_aggregation`

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

Missing selector:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "selector"
  }
}
```

Conflicting selectors:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "selector",
    "selectors": ["videoId", "id"]
  }
}
```

ID selector with unsupported modifier:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "maxResults",
    "selector": "id"
  }
}
```

Invalid moderation status:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "moderationStatus",
    "allowed": ["heldForReview", "likelySpam", "published"]
  }
}
```

Access-sensitive moderation status without eligible access:

```json
{
  "category": "authorization_failed",
  "details": {
    "reason": "forbidden",
    "upstreamStatus": 403
  }
}
```

Disabled comments:

```json
{
  "category": "invalid_request",
  "details": {
    "reason": "commentsDisabled",
    "upstreamStatus": 403
  }
}
```

Not found:

```json
{
  "category": "resource_not_found",
  "details": {
    "reason": "videoNotFound",
    "upstreamStatus": 404
  }
}
```

## Caller Examples Required

- Video-based retrieval with `part` and `videoId`.
- Channel-related retrieval with `part` and `allThreadsRelatedToChannelId`.
- ID-based retrieval with `part` and `id`.
- Paginated retrieval with `maxResults` and `pageToken`.
- Ordered retrieval with `order`.
- Searched retrieval with `searchTerms`.
- Plain-text retrieval with `textFormat`.
- Moderation-status retrieval with access-sensitive caveat.
- Empty successful result.
- Missing selector validation failure.
- Conflicting selector validation failure.
- Invalid identifier validation failure.
- ID selector with unsupported option validation failure.
- Disabled-comments failure.
- Access-sensitive failure.

## Contract Tests Required

- Discovery metadata exposes `commentThreads_list`, upstream identity, quota cost `1`, auth/access expectations, availability, selector list, and description-level quota visibility.
- Descriptor schema matches this input contract and rejects additional properties.
- Examples cover the required success and failure modes.
- Handler returns near-raw list results with endpoint, quota, requested parts, selector, options, pagination, and returned upstream fields.
- Handler distinguishes empty success from validation, authorization, disabled-comments, not-found, quota, unavailable endpoint, deprecated endpoint, and unexpected upstream failures.
- Public metadata and errors never expose API keys, OAuth tokens, raw request secrets, stack traces, or raw upstream diagnostics.
