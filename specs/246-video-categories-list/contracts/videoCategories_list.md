# Contract: `videoCategories_list`

## Public Identity

- **Tool name**: `videoCategories_list`
- **Upstream resource**: `videoCategories`
- **Upstream method**: `list`
- **Operation key**: `videoCategories.list`
- **HTTP method/path**: `GET /youtube/v3/videoCategories`
- **Quota cost**: `1`
- **Auth mode**: `api_key`
- **Availability**: `active`
- **Layer 1 dependency**: `build_video_categories_list_wrapper()`

## Description Requirements

The public description and usage notes must state:

- The tool retrieves YouTube video categories through the upstream `videoCategories.list` endpoint.
- The official quota cost is `1`.
- API-key-backed read access is the supported auth mode for this dependency-backed slice.
- `part` is required.
- Exactly one supported selector is required: `regionCode` or `id`.
- `regionCode` returns the category catalog for one regional context.
- `id` retrieves one or more specific video category resources.
- `hl` may be supplied only as optional display-language context.
- Empty successful category collections are distinct from validation failures and upstream failures.
- The tool does not perform video search, automatic category selection, category recommendation, popularity analysis, ranking, summarization, analytics, enrichment, video classification, or cross-endpoint aggregation.

## Input Schema

```json
{
  "type": "object",
  "required": ["part"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1,
      "description": "Comma-separated videoCategory resource parts to return, usually snippet."
    },
    "regionCode": {
      "type": "string",
      "minLength": 2,
      "maxLength": 2,
      "description": "Region code for one region-scoped video-category lookup."
    },
    "id": {
      "type": "string",
      "minLength": 1,
      "description": "One or more video category identifiers."
    },
    "hl": {
      "type": "string",
      "minLength": 1,
      "description": "Optional display-language preference for localized category labels when available."
    }
  },
  "oneOf": [
    { "required": ["regionCode"] },
    { "required": ["id"] }
  ],
  "additionalProperties": false
}
```

## Validation Rules

| Request Shape | Outcome |
|---------------|---------|
| `part` + `regionCode` + API key | Valid region-scoped category lookup |
| `part` + `id` + API key | Valid category-ID lookup |
| `part` + selector + `hl` + API key | Valid localized category lookup when `hl` is accepted |
| Missing `part` | `invalid_request` |
| Missing both `regionCode` and `id` | `invalid_request` |
| Both `regionCode` and `id` supplied | `invalid_request` |
| Empty or malformed `regionCode` | `invalid_request` |
| Empty or malformed `id` | `invalid_request` |
| Empty or unsupported `hl` | `invalid_request` |
| Unknown video category ID | `resource_not_found` or successful empty result, depending on dependency/upstream outcome |
| Unsupported optional parameters | `invalid_request` |
| Paging, ordering, search, video, channel, analytics, classification, ranking, summarization, or enrichment fields | `invalid_request` |
| Missing API key | `authentication_failed` |
| API-key access denied | `authorization_failed` |
| Quota exhausted | `quota_exhausted` |
| Endpoint unavailable | `endpoint_unavailable` |
| Deprecated behavior reported by upstream | `deprecated_endpoint` |

## Successful Result Shape

Region lookup:

```json
{
  "endpoint": "videoCategories.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "selector": {
    "mode": "regionCode",
    "regionCode": "US"
  },
  "availability": {
    "state": "active"
  },
  "items": [
    {
      "kind": "youtube#videoCategory",
      "id": "10",
      "snippet": {
        "title": "Music",
        "assignable": true
      }
    }
  ]
}
```

ID lookup:

```json
{
  "endpoint": "videoCategories.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "selector": {
    "mode": "id",
    "id": ["10"]
  },
  "availability": {
    "state": "active"
  },
  "items": [
    {
      "id": "10",
      "snippet": {
        "title": "Music",
        "assignable": true
      }
    }
  ]
}
```

Localized lookup:

```json
{
  "endpoint": "videoCategories.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "selector": {
    "mode": "regionCode",
    "regionCode": "US"
  },
  "localization": {
    "hl": "es"
  },
  "availability": {
    "state": "active"
  },
  "items": [
    {
      "id": "10",
      "snippet": {
        "title": "Música",
        "assignable": true
      }
    }
  ]
}
```

Empty success:

```json
{
  "endpoint": "videoCategories.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "selector": {
    "mode": "id",
    "id": ["999999"]
  },
  "availability": {
    "state": "active"
  },
  "items": []
}
```

## Response Convention

- `resultKind`: `list`
- `itemsPath`: `items`
- `authMode`: `api_key`
- `selectorFields`: `regionCode`, `id`
- `localizationFields`: `hl`
- `emptyResultPolicy`: successful empty `items` collection
- `availabilityState`: `active`

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `requestedParts`, `selector`, `localization`, `availability`, `items`, `kind`, `etag`, `pageInfo`, `id`, `snippet`
- **Preserved upstream fields**: `kind`, `etag`, `id`, `snippet`, `items`, `pageInfo`
- **Disallowed behavior**: `video_search`, `video_lookup`, `channel_lookup`, `category_recommendation`, `automatic_category_selection`, `automatic_video_classification`, `popularity_analysis`, `analytics`, `ranking`, `summarization`, `enrichment`, `cross_endpoint_aggregation`

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
    "allowed": ["regionCode", "id"]
  }
}
```

Invalid region:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "regionCode"
  }
}
```

Invalid category ID:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "id"
  }
}
```

Unsupported behavior:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "unsupported",
    "reason": "video search, category recommendation, analytics, ranking, summarization, and enrichment are outside videoCategories_list"
  }
}
```

## Upstream and Access Failures

Authentication failure:

```json
{
  "category": "authentication_failed",
  "details": {
    "authMode": "api_key"
  }
}
```

Quota failure:

```json
{
  "category": "quota_exhausted",
  "details": {
    "operation": "videoCategories.list",
    "quotaCost": 1
  }
}
```

Endpoint unavailable:

```json
{
  "category": "endpoint_unavailable",
  "details": {
    "operation": "videoCategories.list"
  }
}
```

## Example Requirements

The implementation must include caller-facing examples for:

- Region-scoped category lookup.
- Category-ID lookup.
- Localized category lookup.
- Successful populated results.
- Successful empty results.
- Missing `part` validation failure.
- Missing selector validation failure.
- Conflicting selector validation failure.
- Invalid localization validation failure.
- Missing API-key access failure.
- Quota or upstream failure.
- Out-of-scope category-analysis request rejection.

## Security Requirements

- Public metadata, examples, results, and errors must not expose API keys, OAuth tokens, authorization headers, signed URLs, stack traces, raw upstream diagnostics, raw request bodies, or secret-bearing values.
- Errors must use shared safe categories and sanitized details.
- Result context must identify selector, localization, quota, access mode, and operation identity without exposing credential material.
