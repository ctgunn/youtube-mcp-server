# Contract: `videos_getStatistics`

## Purpose

Return normalized public statistics for exactly one YouTube video. This is an additive Layer 3 public tool; it does not change the existing `videos_list` or `videos_getVideo` contracts.

## Discovery Metadata

| Property | Contract |
| --- | --- |
| Public name | `videos_getStatistics` |
| Family | `videos` |
| Retrieval boundary | Normalized retrieval of one video through `videos.list` |
| Lower-level dependency | `videos.list` using only `statistics` |
| Result bound | Exactly one normalized statistics result on success; no pagination, fan-out, ranking, enrichment, or derived analytics |
| Access and quota | Public video lookup uses the existing API-key-compatible path and one source read; surface safe authorization and capacity caveats without exposing credentials |

## Input Contract

```json
{
  "type": "object",
  "required": ["videoId"],
  "additionalProperties": false,
  "properties": {
    "videoId": {
      "type": "string",
      "minLength": 1,
      "description": "One YouTube video identifier."
    }
  }
}
```

The tool rejects missing, blank, non-text, non-object, and unknown inputs as `invalid_parameters` before requesting source data.

## Result Contract

Each successful result represents exactly one retrievable video and has this shape:

```json
{
  "videoId": "abc123",
  "statistics": {
    "viewCount": {"state": "available", "value": "1000", "provenance": "source_provided"},
    "likeCount": {"state": "available", "value": "45", "provenance": "source_provided"},
    "commentCount": {"state": "unavailable", "provenance": "normalized"},
    "favoriteCount": {"state": "available", "value": "0", "provenance": "source_provided"}
  },
  "fieldProvenance": {
    "statistics.*.value": "source_provided",
    "statistics.*.state": "normalized"
  },
  "sourceCaveats": {
    "favoriteCount": "The source marks this deprecated count as zero when supplied."
  }
}
```

### Expected Metrics

| Metric | Source meaning | Available representation | Unavailable representation |
| --- | --- | --- | --- |
| `viewCount` | Source-provided video views. | `state: "available"` with preserved decimal `value`. | `state: "unavailable"`, no `value`. |
| `likeCount` | Source-provided likes. | `state: "available"` with preserved decimal `value`. | `state: "unavailable"`, no `value`. |
| `commentCount` | Source-provided comments. | `state: "available"` with preserved decimal `value`. | `state: "unavailable"`, no `value`. |
| `favoriteCount` | Deprecated source count. | `state: "available"` with preserved decimal `value`, normally `"0"`; callers receive the caveat. | `state: "unavailable"`, no `value`. |

An available zero is a reported source value, not an unavailable value. The tool does not coerce counts through floating point, replace an unavailable value with zero, estimate a value, derive an analytic, or expose an undocumented raw field. In particular, it excludes `dislikeCount`.

Discovery metadata records the `dislikeCount` exclusion as an owner-sensitive source caveat; individual successful results do not create a metric or caveat entry for it.

## Error Contract

| Category | Trigger | Safe response rule |
| --- | --- | --- |
| `invalid_parameters` | Invalid `videoId` or unknown input field | Identify the invalid field and instruct the caller to correct it before retrying. |
| `unavailable_resource` | Empty source result or source not-found/removed outcome | Use a different accessible identifier; do not reveal whether the video is private, deleted, restricted, or nonexistent. |
| `authorization_sensitive_data` | Access is denied or requires authorization | Obtain appropriate authorization if applicable. |
| `quota_exhaustion` | Capacity or rate limit blocks lookup | Retry after capacity is available. |
| `upstream_failure` | Other source-service failure | Retry when the source service is available. |

All error results must omit API keys, authorization values, credentials, tokens, headers, stack traces, signed links, raw request and response bodies, and media data.

## Compatibility and Rollback

- This is an additive public tool; it does not change existing video tool inputs or results.
- Discovery metadata must not include a representative-only marker for this executable tool.
- Rolling back removes this tool's export and default registration only; the lower-level video lookup remains intact.
