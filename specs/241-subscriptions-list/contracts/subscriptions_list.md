# Contract: `subscriptions_list`

## Public Identity

- **Tool name**: `subscriptions_list`
- **Layer**: Layer 2 public MCP endpoint tool
- **Mapped operation**: YouTube resource `subscriptions`, method `list`
- **Operation key**: `subscriptions.list`
- **Quota cost**: `1` official quota unit per invocation
- **Availability**: Active unless implementation discovers an official documentation caveat that must be recorded
- **Auth mode**: Conditional public-compatible access or OAuth-backed user-context access
- **Scope**: Low-level subscription resource listing only

## Discovery Metadata Requirements

Discovery metadata, descriptions, usage notes, caveats, and examples must make the following visible before invocation:

- Public tool name `subscriptions_list`
- Upstream operation `subscriptions.list`
- Quota cost `1`
- Conditional access behavior for public-compatible and user-context selector patterns
- Required `part` input
- Exactly-one selector requirement for `channelId`, `id`, `mine`, `myRecentSubscribers`, or `mySubscribers`
- Supported `pageToken`, `maxResults`, and `order` behavior
- Empty-result success behavior
- Private subscriber and visibility limitations for user-context selectors
- Subscription resources are returned without channel enrichment or subscriber analytics
- Safe failure categories
- Out-of-scope workflows, including subscription creation, subscription deletion, partner-only delegation, channel enrichment, subscriber analytics, ranking, summarization, recommendation, and cross-endpoint aggregation

## Input Contract

```json
{
  "type": "object",
  "required": ["part"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1
    },
    "channelId": {
      "type": "string",
      "minLength": 1
    },
    "id": {
      "type": "string",
      "minLength": 1
    },
    "mine": {
      "type": "boolean"
    },
    "myRecentSubscribers": {
      "type": "boolean"
    },
    "mySubscribers": {
      "type": "boolean"
    },
    "pageToken": {
      "type": "string",
      "minLength": 1
    },
    "maxResults": {
      "type": "integer",
      "minimum": 0,
      "maximum": 50
    },
    "order": {
      "type": "string",
      "enum": ["alphabetical", "relevance", "unread"]
    }
  },
  "oneOf": [
    { "required": ["channelId"] },
    { "required": ["id"] },
    { "required": ["mine"] },
    { "required": ["myRecentSubscribers"] },
    { "required": ["mySubscribers"] }
  ],
  "additionalProperties": false
}
```

## Input Validation Rules

- `part` is required and must be non-empty.
- Supported part names are `contentDetails`, `id`, `snippet`, and `subscriberSnippet`.
- Exactly one selector must be active from `channelId`, `id`, `mine`, `myRecentSubscribers`, and `mySubscribers`.
- Boolean selectors only count as active when set to `true`; false-only selector requests are invalid.
- `mine`, `myRecentSubscribers`, and `mySubscribers` require eligible OAuth-backed access.
- `channelId` and `id` use public-compatible lookup access.
- `pageToken` must be non-empty when provided.
- `maxResults` must be between `0` and `50`, inclusive.
- `order` must be one of `alphabetical`, `relevance`, or `unread`.
- Pagination and ordering must stay compatible with the selected list mode and must not be reused across unrelated selector contexts.
- Partner-only delegation fields, unsupported official optional fields not present in this slice, subscription mutation requests, channel enrichment requests, analytics requests, ranking or summarization instructions, unsupported modifiers, and higher-level workflow instructions are rejected before endpoint execution.

## Success Result Contract

Successful calls return a near-raw subscription collection with safe context:

```json
{
  "endpoint": "subscriptions.list",
  "quotaCost": 1,
  "items": [
    {
      "kind": "youtube#subscription",
      "id": "subscription-123",
      "snippet": {
        "title": "Example channel"
      },
      "contentDetails": {
        "totalItemCount": 42
      }
    }
  ],
  "empty": false,
  "selectorContext": {
    "part": "snippet,contentDetails",
    "selector": "channelId",
    "channelId": "UC123"
  },
  "pagination": {
    "nextPageToken": "NEXT_PAGE",
    "pageInfo": {
      "totalResults": 42,
      "resultsPerPage": 25
    }
  },
  "auth": {
    "mode": "api_key",
    "path": "public"
  }
}
```

Result rules:
- `endpoint` must be `subscriptions.list`.
- `quotaCost` must be `1`.
- `items` must preserve returned subscription resource records.
- `empty` must distinguish successful empty collections from failures.
- `selectorContext` must preserve safe request parts and selector context.
- `pagination` must preserve returned page tokens and page information when present.
- `auth` must identify the safe access mode, not credentials.
- The result must not fabricate full channel details, subscriber profiles, analytics, ranking, recommendation, summary, or enrichment fields.

## Error Contract

Failures must use safe caller-facing categories and sanitized details:

- `invalid_request`: Missing `part`, invalid part, missing selector, false-only selector, conflicting selectors, unsupported field, unsupported modifier, invalid pagination, invalid order, incompatible paging or order usage, subscription mutation request, partner-only delegation request, or out-of-scope workflow request
- `authentication_failed`: Required API-key or OAuth credential material missing or invalid
- `authorization_failed`: Caller lacks access for a user-context subscription selector or requested subscription visibility
- `quota_exhausted`: Upstream quota failure
- `not_found`: Subscriber or subscription target cannot be found
- `endpoint_unavailable`: Upstream service unavailable or timeout category
- `deprecated_endpoint`: Official endpoint behavior is deprecated or unavailable
- `upstream_failure`: Unexpected upstream failure after sanitization

Error details must not include API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, raw request context, or secret-bearing diagnostics.

## Representative Examples

### Channel Subscription Listing

```json
{
  "part": "snippet,contentDetails",
  "channelId": "UC123"
}
```

Expected context:
- Endpoint `subscriptions.list`
- Quota cost `1`
- Public-compatible access mode
- Subscription item collection or successful empty result

### Direct Subscription Lookup

```json
{
  "part": "id,snippet",
  "id": "subscription-123"
}
```

Expected context:
- Endpoint `subscriptions.list`
- Quota cost `1`
- Public-compatible access mode
- Direct subscription identifier selector preserved

### Current User Subscriptions

```json
{
  "part": "snippet",
  "mine": true
}
```

Expected context:
- OAuth-backed user-context access required
- Missing or insufficient OAuth must fail as authentication or authorization failure

### Recent Subscribers

```json
{
  "part": "subscriberSnippet",
  "myRecentSubscribers": true,
  "maxResults": 25
}
```

Expected context:
- OAuth-backed user-context access required
- Subscriber visibility limitations preserved as caller-facing caveats
- Page size preserved in selector context

### Subscriber List

```json
{
  "part": "subscriberSnippet",
  "mySubscribers": true,
  "order": "relevance"
}
```

Expected context:
- OAuth-backed user-context access required
- Ordering preserved when the selected mode supports it

### Paginated Channel Subscription Listing

```json
{
  "part": "snippet",
  "channelId": "UC123",
  "pageToken": "NEXT_PAGE",
  "maxResults": 25
}
```

Expected context:
- Continuation token and page size preserved in pagination context
- Token compatibility remains tied to the original selector context

### Successful Empty Result

```json
{
  "part": "snippet",
  "channelId": "UC_NO_PUBLIC_SUBSCRIPTIONS"
}
```

Expected context:
- Successful result with `items` as an empty collection
- `empty` set to `true`
- Not treated as `not_found` or authorization failure

### Missing Selector

```json
{
  "part": "snippet"
}
```

Expected failure:
- Category `invalid_request`
- Field or detail identifies `selector`

### Conflicting Selectors

```json
{
  "part": "snippet",
  "channelId": "UC123",
  "mine": true
}
```

Expected failure:
- Category `invalid_request`
- Detail identifies conflicting selectors

### Unsupported Enrichment Request

```json
{
  "part": "snippet",
  "channelId": "UC123",
  "includeChannelStatistics": true
}
```

Expected failure:
- Category `invalid_request`
- Detail identifies `includeChannelStatistics` as unsupported and out of scope

## Contract Validation Expectations

- Contract tests must prove discovery metadata exposes identity, quota cost, auth mode, selector modes, pagination/order support, examples, caveats, safe failure categories, and out-of-scope boundaries.
- Unit tests must prove argument validation, selector detection, auth-path selection, result mapping, empty-result mapping, and safe error sanitization.
- Integration tests must prove dispatcher discovery and invocation through the default registry.
- Full-suite verification must run after implementation cleanup.
