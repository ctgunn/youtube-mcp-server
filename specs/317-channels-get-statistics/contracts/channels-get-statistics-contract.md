# Contract: `channels_getStatistics`

## Purpose

Return normalized public statistics for exactly one YouTube channel. This is an additive Layer 3 public tool; it does not change the existing `channels_list`, `channels_getChannel`, or `channels_getChannels` contracts.

## Discovery Metadata

| Property | Contract |
| --- | --- |
| Public name | `channels_getStatistics` |
| Family | `channels` |
| Retrieval boundary | Normalized retrieval of one channel through `channels.list` |
| Lower-level dependency | `channels.list` using only `statistics` |
| Result bound | Exactly one normalized statistics result on success; no pagination, fan-out, ranking, enrichment, or derived analytics |
| Access and quota | Public channel lookup uses the existing API-key-compatible path and one source read; surface safe authorization and capacity caveats without exposing credentials |

## Input Contract

```json
{
  "type": "object",
  "required": ["channelId"],
  "additionalProperties": false,
  "properties": {
    "channelId": {
      "type": "string",
      "minLength": 1,
      "description": "One YouTube channel identifier."
    }
  }
}
```

The tool rejects missing, blank, non-text, non-object, and unknown inputs as `invalid_parameters` before requesting source data.

## Result Contract

Each successful result represents exactly one retrievable channel and has this shape:

```json
{
  "channelId": "UC123",
  "statistics": {
    "subscriberCount": {"state": "hidden", "provenance": "normalized"},
    "videoCount": {"state": "available", "value": "42", "provenance": "source_provided"},
    "viewCount": {"state": "available", "value": "1000", "provenance": "source_provided"}
  },
  "fieldProvenance": {
    "statistics.*.value": "source_provided",
    "statistics.*.state": "normalized"
  },
  "sourceCaveats": {
    "subscriberCount": "The source rounds public subscriber counts down to three significant figures.",
    "videoCount": "The source reports public videos only.",
    "viewCount": "The source's current definition includes Shorts starts and replays."
  }
}
```

### Expected Metrics

| Metric | Source meaning | Available representation | Hidden or unavailable representation |
| --- | --- | --- | --- |
| `subscriberCount` | Public subscriber count, rounded down to three significant figures by the source. | `state: "available"` with preserved decimal `value` when not source-flagged hidden. | `state: "hidden"`, no `value`, when `hiddenSubscriberCount` is true; otherwise `state: "unavailable"`, no `value`, when no valid source count is available. |
| `videoCount` | Count of public videos uploaded to the channel. | `state: "available"` with preserved decimal `value`. | `state: "unavailable"`, no `value`. |
| `viewCount` | Aggregate channel views under the source's current view definition. | `state: "available"` with preserved decimal `value`. | `state: "unavailable"`, no `value`. |

An available zero is a reported source value, not a hidden or unavailable value. The tool does not coerce counts through floating point, replace a hidden or unavailable value with zero, estimate a value, derive an analytic, or expose undocumented raw fields. `hiddenSubscriberCount` controls subscriber-state shaping only and is not itself a public result field.

## Error Contract

| Category | Trigger | Safe response rule |
| --- | --- | --- |
| `invalid_parameters` | Invalid `channelId` or unknown input field | Identify the invalid field and instruct the caller to correct it before retrying. |
| `unavailable_resource` | Empty source result or source not-found/removed outcome | Use a different accessible identifier; do not reveal whether the channel is deleted, suspended, restricted, or nonexistent. |
| `authorization_sensitive_data` | Access is denied or requires authorization | Obtain appropriate authorization if applicable. |
| `quota_exhaustion` | Capacity or rate limit blocks lookup | Retry after capacity is available. |
| `upstream_failure` | Other source-service failure | Retry when the source service is available. |

All error results must omit API keys, authorization values, credentials, tokens, headers, stack traces, signed links, raw request and response bodies, and media data.

## Compatibility and Rollback

- This is an additive public tool; it does not change existing channel-tool inputs or results.
- Discovery metadata must not include a representative-only marker for this executable tool.
- Rolling back removes this tool's export and default registration only; the lower-level channel lookup remains intact.
