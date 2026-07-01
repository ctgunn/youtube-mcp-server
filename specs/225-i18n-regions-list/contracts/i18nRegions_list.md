# Contract: `i18nRegions_list`

## Public Identity

- **Tool name**: `i18nRegions_list`
- **Upstream resource**: `i18nRegions`
- **Upstream method**: `list`
- **Operation key**: `i18nRegions.list`
- **HTTP method/path**: `GET /youtube/v3/i18nRegions`
- **Quota cost**: `1`
- **Auth mode**: `api_key`
- **Availability**: `active`
- **Layer 1 dependency**: `build_i18n_regions_list_wrapper()`

## Description Requirements

The public description and usage notes must state:

- The tool retrieves YouTube content regions through the upstream `i18nRegions.list` endpoint.
- The official quota cost is `1`.
- API-key-backed read access is the supported auth mode for this dependency-backed slice.
- `part` is required and the supported official part value is `snippet`.
- `hl` may be supplied as an optional display-language preference.
- When `hl` is omitted, the upstream default display-language behavior applies.
- Empty successful localization-region collections are distinct from validation failures and upstream failures.
- The tool does not perform language lookup, translation, country validation, region-code conversion, geotargeting, search filtering, recommendation, ranking, summarization, enrichment, analytics, or cross-endpoint aggregation.

## Input Schema

```json
{
  "type": "object",
  "required": ["part"],
  "properties": {
    "part": {
      "type": "string",
      "enum": ["snippet"],
      "description": "i18nRegion resource parts to return. The supported official value for this endpoint is snippet."
    },
    "hl": {
      "type": "string",
      "minLength": 1,
      "description": "Optional language preference for text values in the response. When omitted, upstream default display-language behavior applies."
    }
  },
  "additionalProperties": false
}
```

## Validation Rules

| Request Shape | Outcome |
|---------------|---------|
| `part=snippet` + API key | Valid default localization-region lookup |
| `part=snippet` + `hl` + API key | Valid display-language-specific localization-region lookup |
| Missing `part` | `invalid_request` |
| Empty or unsupported `part` | `invalid_request` |
| Empty or unsupported `hl` | `invalid_request` |
| Selectors such as `id`, `regionCode`, `videoId`, `channelId`, or `captionId` | `invalid_request` |
| Paging, ordering, country-validation, geotargeting, analytics, or filtering fields | `invalid_request` |
| Language lookup, translation, search filtering, recommendation, ranking, summarization, enrichment, or aggregation fields | `invalid_request` |
| Missing API key | `authentication_failed` |
| API-key access denied | `authorization_failed` |
| Quota exhausted | `quota_exhausted` |
| Upstream invalid request | `invalid_request` |
| Endpoint unavailable | `endpoint_unavailable` |

## Successful Result Shape

Default region listing:

```json
{
  "endpoint": "i18nRegions.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "availability": {
    "state": "active"
  },
  "items": [
    {
      "kind": "youtube#i18nRegion",
      "id": "US",
      "snippet": {
        "gl": "US",
        "name": "United States"
      }
    }
  ]
}
```

Display-language-specific listing:

```json
{
  "endpoint": "i18nRegions.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "localization": {
    "hl": "es"
  },
  "availability": {
    "state": "active"
  },
  "items": [
    {
      "kind": "youtube#i18nRegion",
      "id": "US",
      "snippet": {
        "gl": "US",
        "name": "Estados Unidos"
      }
    }
  ]
}
```

Empty success:

```json
{
  "endpoint": "i18nRegions.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
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
- `partFields`: `part`
- `localizationFields`: `hl`
- `emptyResultPolicy`: successful empty `items` collection
- `availabilityState`: `active`

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `requestedParts`, `localization`, `availability`, `items`, `kind`, `etag`, `id`, `snippet`
- **Preserved upstream fields**: `kind`, `etag`, `id`, `snippet`, `items`
- **Disallowed behavior**: `language_lookup`, `translation`, `country_validation`, `region_code_conversion`, `geotargeting`, `search_filtering`, `recommendation`, `ranking`, `summarization`, `enrichment`, `analytics`, `cross_endpoint_aggregation`

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

Invalid part:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "part",
    "allowed": ["snippet"]
  }
}
```

Invalid display language:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "hl"
  }
}
```

Unsupported field:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "regionCode"
  }
}
```

Quota exhausted:

```json
{
  "category": "quota_exhausted",
  "details": {
    "operation": "i18nRegions.list"
  }
}
```

## Example Set Requirements

The descriptor metadata must include examples named:

- `default_region_listing`
- `display_language_region_listing`
- `empty_success`
- `missing_part`
- `invalid_part`
- `invalid_display_language`
- `unsupported_option`
- `out_of_scope_language_or_geotargeting_request`

Each example description must include quota cost `1` when it represents a call attempt.

## Security and Safety Requirements

- Public metadata, examples, results, and errors must never include API keys, OAuth tokens, signed URLs, stack traces, raw upstream diagnostics, raw request bodies containing secrets, or unsafe credential details.
- Safe error details may identify invalid public fields and shared error categories only.
- Handler behavior must rely on the Layer 1 wrapper and shared executor rather than duplicating credential handling.
