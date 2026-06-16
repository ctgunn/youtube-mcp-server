# Contract: `comments_list`

## Public Identity

- **Tool name**: `comments_list`
- **Upstream resource**: `comments`
- **Upstream method**: `list`
- **Operation key**: `comments.list`
- **HTTP method/path**: `GET /youtube/v3/comments`
- **Quota cost**: `1`
- **Auth mode**: `mixed/conditional`
- **Availability**: `active`
- **Layer 1 dependency**: `build_comments_list_wrapper()`

## Description Requirements

The public description and usage notes must state:

- The tool retrieves comments through the upstream `comments.list` endpoint.
- The official quota cost is `1`.
- `part` is required.
- Exactly one selector is required: `id` for direct comment lookup or `parentId` for replies to a parent comment.
- `maxResults` and `pageToken` are supported only with `parentId`, not with `id`.
- `textFormat` may be `html` or `plainText`.
- Access-sensitive comments can fail with authorization or not-found outcomes.
- The tool does not perform comment-thread discovery, reply creation, comment updates, moderation status changes, deletion, sentiment analysis, ranking, summarization, enrichment, or search.

## Input Schema

```json
{
  "type": "object",
  "required": ["part"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1,
      "description": "Comma-separated comment resource parts to return, such as id or snippet."
    },
    "id": {
      "type": "string",
      "minLength": 1,
      "description": "Comma-separated comment IDs for direct comment retrieval."
    },
    "parentId": {
      "type": "string",
      "minLength": 1,
      "description": "Parent comment ID whose replies should be retrieved."
    },
    "maxResults": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "description": "Maximum number of reply comments to return when using parentId."
    },
    "pageToken": {
      "type": "string",
      "minLength": 1,
      "description": "Result page token for parentId pagination."
    },
    "textFormat": {
      "type": "string",
      "enum": ["html", "plainText"],
      "description": "Comment text format requested from upstream."
    }
  },
  "additionalProperties": false
}
```

## Selector Rules

| Request Shape | Outcome |
|---------------|---------|
| `part` + `id` | Valid direct comment retrieval |
| `part` + `parentId` | Valid reply retrieval |
| `part` + `parentId` + `maxResults` | Valid paginated reply retrieval |
| `part` + `parentId` + `pageToken` | Valid next-page reply retrieval |
| `part` + `parentId` + `textFormat` | Valid formatted reply retrieval |
| `part` only | `invalid_request` |
| `part` + `id` + `parentId` | `invalid_request` |
| `part` + `id` + `maxResults` | `invalid_request` |
| `part` + `id` + `pageToken` | `invalid_request` |
| Missing `part` | `invalid_request` |
| Unsupported request body or workflow fields | `invalid_request` |

## Successful Result Shape

ID-based retrieval:

```json
{
  "endpoint": "comments.list",
  "quotaCost": 1,
  "requestedParts": ["id", "snippet"],
  "selector": {
    "name": "id"
  },
  "textFormat": "html",
  "items": [
    {
      "kind": "youtube#comment",
      "id": "comment-123",
      "snippet": {
        "textDisplay": "Thanks!"
      }
    }
  ],
  "kind": "youtube#commentListResponse",
  "etag": "etag-123"
}
```

Parent-comment reply retrieval with pagination:

```json
{
  "endpoint": "comments.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "selector": {
    "name": "parentId"
  },
  "textFormat": "plainText",
  "items": [
    {
      "kind": "youtube#comment",
      "id": "reply-123",
      "snippet": {
        "textDisplay": "Reply text"
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

Empty successful result:

```json
{
  "endpoint": "comments.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "selector": {
    "name": "parentId"
  },
  "textFormat": "html",
  "items": []
}
```

## Response Convention

- `resultKind`: `list`
- `successStatus`: `commentListResponse`
- `itemField`: `items`
- `paginationFields`: `nextPageToken`, `pageInfo`
- `selectorFields`: `id`, `parentId`
- `textFormatFields`: `html`, `plainText`
- `emptyResultPolicy`: `empty_success_when_upstream_returns_empty_items`

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `requestedParts`, `selector`, `textFormat`, `items`, `kind`, `etag`, `nextPageToken`, `pageInfo`
- **Preserved upstream fields**: `kind`, `etag`, `nextPageToken`, `pageInfo`, `items`
- **Disallowed behavior**: `comment_thread_discovery`, `reply_creation`, `comment_update`, `comment_moderation`, `comment_delete`, `comment_search`, `sentiment_analysis`, `ranking`, `summarization`, `enrichment`, `cross_endpoint_aggregation`

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
    "supportedSelectors": ["id", "parentId"]
  }
}
```

Pagination with ID selector:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "maxResults",
    "selector": "id"
  }
}
```

Unsupported text format:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "textFormat",
    "allowed": ["html", "plainText"]
  }
}
```

## Upstream Error Mapping

| Upstream Signal | Public Category | Notes |
|-----------------|-----------------|-------|
| missing `part`, missing filter, conflicting filters | `invalid_request` | Reject locally when possible |
| `operationNotSupported` | `invalid_request` | Preserve safe status/reason only |
| `forbidden`, insufficient permissions | `authorization_failed` | Do not leak credential details |
| `commentNotFound` | `resource_not_found` | Covers missing `id` or `parentId` targets |
| quota/rate limit | `quota_exhausted` | Preserve safe upstream status |
| transient/unavailable | `endpoint_unavailable` | Retry behavior remains Layer 1 concern |
| deprecated endpoint | `deprecated_endpoint` | Surface shared category when Layer 1 reports it |
| unknown upstream failure | `upstream_failure` | Safe fallback |

## Required Caller Examples

- `id_lookup`: Valid retrieval with `part` and `id`.
- `parent_reply_lookup`: Valid retrieval with `part` and `parentId`.
- `paginated_parent_lookup`: Valid retrieval with `parentId`, `maxResults`, and `pageToken`.
- `plain_text_parent_lookup`: Valid retrieval with `textFormat: plainText`.
- `empty_success`: Valid parent reply retrieval returning `items: []`.
- `missing_selector`: Rejects absent `id` and `parentId`.
- `conflicting_selectors`: Rejects combined `id` and `parentId`.
- `invalid_id`: Rejects empty or malformed `id`.
- `unsupported_option`: Rejects request body, search, sort, moderation, mutation, or enrichment options.
- `access_sensitive_failure`: Maps inaccessible comments to a safe authorization or not-found category.

Every example must include `quotaCost: 1` or text stating `Quota cost: 1`.
