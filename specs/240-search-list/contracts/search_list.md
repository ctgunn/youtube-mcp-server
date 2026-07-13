# Contract: `search_list`

## Public Identity

- **Tool name**: `search_list`
- **Layer**: Layer 2 public MCP endpoint tool
- **Mapped operation**: YouTube resource `search`, method `list`
- **Operation key**: `search.list`
- **Quota cost**: `100` official quota units per invocation
- **Availability**: Active unless implementation discovers an official documentation caveat that must be recorded
- **Auth mode**: Conditional API-key public access or OAuth-backed restricted access
- **Scope**: Low-level search result listing only

## Discovery Metadata Requirements

Discovery metadata, descriptions, usage notes, caveats, and examples must make the following visible before invocation:

- Public tool name `search_list`
- Upstream operation `search.list`
- Quota cost `100`
- Conditional access behavior for public and restricted search patterns
- Required supported baseline inputs `part` and `q`
- Supported search type, channel, date, language, region, ordering, safe-search, pagination, restricted, and video-specific refinement boundaries
- Empty-result success behavior
- Search result references are returned without resource hydration
- Safe failure categories
- Out-of-scope workflows, including video hydration, channel hydration, playlist hydration, transcript retrieval, analytics, ranking, summarization, recommendation, research synthesis, and cross-endpoint enrichment

## Input Contract

```json
{
  "type": "object",
  "required": ["part", "q"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1
    },
    "q": {
      "type": "string",
      "minLength": 1
    },
    "type": {
      "type": "string"
    },
    "channelId": {
      "type": "string"
    },
    "publishedAfter": {
      "type": "string"
    },
    "publishedBefore": {
      "type": "string"
    },
    "regionCode": {
      "type": "string"
    },
    "relevanceLanguage": {
      "type": "string"
    },
    "safeSearch": {
      "type": "string"
    },
    "order": {
      "type": "string"
    },
    "pageToken": {
      "type": "string"
    },
    "maxResults": {
      "type": "integer",
      "minimum": 0
    },
    "forContentOwner": {
      "type": "boolean"
    },
    "forDeveloper": {
      "type": "boolean"
    },
    "forMine": {
      "type": "boolean"
    },
    "videoCaption": {
      "type": "string"
    },
    "videoDefinition": {
      "type": "string"
    },
    "videoDuration": {
      "type": "string"
    },
    "videoEmbeddable": {
      "type": "string"
    },
    "videoLicense": {
      "type": "string"
    },
    "videoPaidProductPlacement": {
      "type": "string"
    },
    "videoSyndicated": {
      "type": "string"
    },
    "videoType": {
      "type": "string"
    }
  },
  "additionalProperties": false
}
```

## Input Validation Rules

- `part` and `q` are required and must be non-empty.
- `forContentOwner`, `forDeveloper`, and `forMine` are mutually exclusive restricted filters.
- Restricted filters require eligible OAuth-backed access.
- Video-specific refinements require `type=video`.
- `pageToken` must be non-empty when provided.
- `maxResults` must stay within supported official limits.
- Resource hydration instructions, transcript inputs, analytics inputs, ranking or summarization instructions, unsupported modifiers, and higher-level workflow instructions are rejected before endpoint execution.

## Success Result Contract

Successful calls return a near-raw search collection with safe context:

```json
{
  "endpoint": "search.list",
  "quotaCost": 100,
  "items": [
    {
      "kind": "youtube#searchResult",
      "id": {
        "kind": "youtube#video",
        "videoId": "abc123"
      },
      "snippet": {
        "title": "Example result"
      }
    }
  ],
  "empty": false,
  "queryContext": {
    "part": "snippet",
    "q": "mcp server",
    "type": "video"
  },
  "pagination": {
    "nextPageToken": "NEXT_PAGE"
  },
  "auth": {
    "mode": "api_key",
    "path": "public"
  }
}
```

Result rules:
- `endpoint` must be `search.list`.
- `quotaCost` must be `100`.
- `items` must preserve returned search result records.
- `empty` must distinguish successful empty collections from failures.
- `queryContext` must preserve safe request criteria and filters.
- `pagination` must preserve returned page tokens when present.
- `auth` must identify the safe access mode, not credentials.
- The result must not fabricate full video, channel, playlist, transcript, analytics, ranking, recommendation, summary, or enrichment fields.

## Error Contract

Failures must use safe caller-facing categories and sanitized details:

- `invalid_request`: Missing `part`, missing `q`, blank inputs, non-string inputs, unsupported field, unsupported modifier, mutually exclusive restricted filters, video-only refinement without `type=video`, invalid pagination, invalid filter value, or out-of-scope workflow request
- `authentication_failed`: Required API-key or OAuth credential material missing or invalid
- `authorization_failed`: Caller lacks access for a restricted search path
- `quota_exhausted`: Upstream quota failure
- `endpoint_unavailable`: Upstream service unavailable or timeout category
- `deprecated_endpoint`: Official endpoint behavior is deprecated or unavailable
- `upstream_failure`: Unexpected upstream failure after sanitization

Error details must not include API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, raw request context, or secret-bearing diagnostics.

## Representative Examples

### Public Keyword Search

```json
{
  "part": "snippet",
  "q": "mcp server"
}
```

Expected context:
- Endpoint `search.list`
- Quota cost `100`
- API-key public access mode
- Search result collection or successful empty result

### Type-Filtered Video Search

```json
{
  "part": "snippet",
  "q": "mcp server",
  "type": "video"
}
```

Expected context:
- Endpoint `search.list`
- Quota cost `100`
- Result type filter preserved in query context

### Channel-Scoped Search

```json
{
  "part": "snippet",
  "q": "release notes",
  "channelId": "UC123"
}
```

Expected context:
- Channel filter preserved in query context
- Returned search result references are not hydrated channel or video details

### Date and Locale Refinement

```json
{
  "part": "snippet",
  "q": "conference keynote",
  "publishedAfter": "2026-01-01T00:00:00Z",
  "regionCode": "US",
  "relevanceLanguage": "en"
}
```

Expected context:
- Date, region, and language filters preserved in query context

### Restricted OAuth Search

```json
{
  "part": "snippet",
  "q": "private uploads",
  "forMine": true
}
```

Expected context:
- OAuth-backed restricted access required
- Missing or insufficient OAuth must fail as authentication or authorization failure

### Paginated Search

```json
{
  "part": "snippet",
  "q": "mcp server",
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
  "part": "snippet"
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `q`

### Incompatible Filter Failure

```json
{
  "part": "snippet",
  "q": "mcp server",
  "videoDuration": "short"
}
```

Expected error:
- Category `invalid_request`
- Safe detail explaining that video-specific refinements require `type=video`

### Restricted Filter Conflict Failure

```json
{
  "part": "snippet",
  "q": "mcp server",
  "forMine": true,
  "forDeveloper": true
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying mutually exclusive restricted filters

### Out-of-Scope Enrichment Request

```json
{
  "part": "snippet",
  "q": "mcp server",
  "includeTranscript": true
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `includeTranscript`
