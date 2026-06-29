# Contract: `guideCategories_list`

## Public Identity

- **Tool name**: `guideCategories_list`
- **Upstream resource**: `guideCategories`
- **Upstream method**: `list`
- **Operation key**: `guideCategories.list`
- **HTTP method/path**: `GET /youtube/v3/guideCategories`
- **Quota cost**: `1`
- **Auth mode**: `api_key`
- **Availability**: `deprecated`
- **Layer 1 dependency**: `build_guide_categories_list_wrapper()`

## Description Requirements

The public description and usage notes must state:

- The tool retrieves legacy YouTube guide categories through the upstream `guideCategories.list` endpoint.
- The official quota cost is `1`.
- API-key-backed read access is the supported auth mode for this dependency-backed slice.
- `part` is required.
- Exactly one supported selector is required: `regionCode` or `id`.
- `id` lookup requires Layer 1 wrapper metadata and validation support before it is exposed publicly.
- `hl` may be supplied only as supported localization context.
- The endpoint is deprecated and may be unavailable or removed from current platform behavior.
- Empty successful guide-category collections are distinct from validation failures and legacy-unavailable behavior.
- The tool does not perform channel listing, channel category assignment, video-category lookup, search, recommendation, ranking, summarization, enrichment, taxonomy migration, or cross-endpoint aggregation.

## Input Schema

```json
{
  "type": "object",
  "required": ["part"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1,
      "description": "Comma-separated guideCategory resource parts to return, usually snippet."
    },
    "regionCode": {
      "type": "string",
      "minLength": 2,
      "maxLength": 2,
      "description": "Region code for one region-scoped guide-category lookup."
    },
    "id": {
      "type": "string",
      "minLength": 1,
      "description": "One or more guide category identifiers when Layer 1 supports ID lookup."
    },
    "hl": {
      "type": "string",
      "minLength": 1,
      "description": "Optional language preference for localized category text when supported."
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
| `part` + `regionCode` + API key | Valid region-scoped guide-category lookup |
| `part` + `id` + API key + Layer 1 ID support | Valid ID-based guide-category lookup |
| `part` + selector + `hl` + API key | Valid localized guide-category lookup when `hl` is supported |
| Missing `part` | `invalid_request` |
| Missing both `regionCode` and `id` | `invalid_request` |
| Both `regionCode` and `id` supplied | `invalid_request` |
| Empty or malformed `regionCode` | `invalid_request` |
| Empty or malformed `id` | `invalid_request` |
| ID lookup before Layer 1 support is added | `invalid_request` or blocked before public exposure |
| Empty or unsupported `hl` | `invalid_request` |
| Unknown guide category ID | `resource_not_found` |
| Unsupported optional parameters | `invalid_request` |
| Channel listing/category fields | `invalid_request` |
| Video-category lookup fields | `invalid_request` |
| Search, recommendation, ranking, summarization, enrichment, or taxonomy migration fields | `invalid_request` |
| Missing API key | `authentication_failed` |
| API-key access denied | `authorization_failed` |
| Quota exhausted | `quota_exhausted` |
| Deprecated endpoint rejected by platform | `deprecated_endpoint` |
| Endpoint removed or unavailable | `endpoint_unavailable` |

## Successful Result Shape

Region lookup:

```json
{
  "endpoint": "guideCategories.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "selector": {
    "mode": "regionCode",
    "regionCode": "US"
  },
  "availability": {
    "state": "deprecated"
  },
  "items": [
    {
      "kind": "youtube#guideCategory",
      "id": "GCQmVzdCBvZiBZb3VUdWJl",
      "snippet": {
        "channelId": "UCBR8-60-B28hp2BmDPdntcQ",
        "title": "Best of YouTube"
      }
    }
  ]
}
```

ID lookup:

```json
{
  "endpoint": "guideCategories.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "selector": {
    "mode": "id",
    "id": ["GCQmVzdCBvZiBZb3VUdWJl"]
  },
  "availability": {
    "state": "deprecated"
  },
  "items": [
    {
      "id": "GCQmVzdCBvZiBZb3VUdWJl",
      "snippet": {
        "title": "Best of YouTube"
      }
    }
  ]
}
```

Empty success:

```json
{
  "endpoint": "guideCategories.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "selector": {
    "mode": "regionCode",
    "regionCode": "US"
  },
  "availability": {
    "state": "deprecated"
  },
  "items": []
}
```

Legacy unavailable:

```json
{
  "endpoint": "guideCategories.list",
  "quotaCost": 1,
  "availability": {
    "state": "unavailable",
    "reason": "removed_resource"
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
- `availabilityState`: `deprecated` with possible per-call `unavailable` outcome

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `requestedParts`, `selector`, `localization`, `availability`, `items`, `kind`, `etag`, `id`, `snippet`
- **Preserved upstream fields**: `kind`, `etag`, `id`, `snippet`, `items`
- **Disallowed behavior**: `channel_listing`, `channel_category_assignment`, `video_category_lookup`, `search`, `recommendation`, `ranking`, `summarization`, `enrichment`, `taxonomy_migration`, `cross_endpoint_aggregation`

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

Guide category not found:

```json
{
  "category": "resource_not_found",
  "details": {
    "reason": "notFound"
  }
}
```

Deprecated or unavailable endpoint:

```json
{
  "category": "deprecated_endpoint",
  "details": {
    "operation": "guideCategories.list",
    "availabilityState": "deprecated"
  }
}
```

Endpoint removed or unavailable:

```json
{
  "category": "endpoint_unavailable",
  "details": {
    "operation": "guideCategories.list",
    "reason": "removed_resource"
  }
}
```

## Required Examples

- `region_lookup`: `{"part": "snippet", "regionCode": "US"}`
- `id_lookup`: `{"part": "snippet", "id": "GCQmVzdCBvZiBZb3VUdWJl"}`
- `localized_lookup`: `{"part": "snippet", "regionCode": "US", "hl": "es"}`
- `empty_success`: valid selector returning `items: []`
- `missing_part`: selector without `part`
- `missing_selector`: `part` without selector
- `conflicting_selectors`: `part` with both `regionCode` and `id`
- `invalid_id`: unknown or malformed guide category ID
- `invalid_region`: unsupported or malformed region code
- `unsupported_option`: channel/video/search/ranking/enrichment field
- `legacy_unavailable`: deprecated or removed platform behavior

## Safe Metadata Requirements

- Public metadata must never expose API keys, OAuth tokens, stack traces, raw upstream diagnostics, signed URLs, raw request context, or secret-bearing fields.
- Metadata must include `quotaCost: 1`, `authMode: api_key`, `availabilityState: deprecated`, and the upstream operation identity.
- Description, usage notes, caveats, and examples must each make the quota and deprecated availability visible to callers.
