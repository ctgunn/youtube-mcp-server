# Data Model: YT-317 Channel Statistics

## Channel Statistics Request

Represents one client request for source-provided statistics about exactly one channel.

**Fields**:

- `channelId`: required nonblank text identifier for exactly one channel.

**Validation Rules**:

- Only `channelId` is accepted.
- `channelId` must be nonblank text after trimming.
- Missing, blank, non-text, non-object, or unknown inputs produce `invalid_parameters` before a source lookup.

**Relationships**:

- Produces one Channel Statistics Result or one Lookup Outcome.
- Causes exactly one lower-level `channels.list` lookup using the source `statistics` group.

## Channel Statistics Result

Represents the normalized successful result for one retrievable channel.

**Fields**:

- `channelId`: the requested trimmed channel identifier.
- `statistics`: a stable mapping of all expected Statistic Metrics.
- `fieldProvenance`: caller-visible declaration that values are source-provided and metric states are normalized.
- `sourceCaveats`: caller-visible notes that subscriber counts are rounded, video counts cover public videos, and view counts include Shorts starts and replays under the source's current definition.

**Rules**:

- The result represents exactly one channel and never a collection, pagination, enrichment, ranking, or derived analytics.
- It contains all three expected metrics regardless of whether each source value is available.
- It contains no raw `hiddenSubscriberCount` or undocumented raw source fields.

**Relationships**:

- Contains exactly three Statistic Metrics.
- Is derived from the first item in one lower-level `channels.list` response.

## Statistic Metric

Represents one expected public count: `subscriberCount`, `videoCount`, or `viewCount`.

**Fields**:

- `state`: `available`, `hidden`, or `unavailable`.
- `value`: present only when `state` is `available`; a non-negative decimal source count, including `"0"`.
- `provenance`: `source_provided` for an available count and `normalized` for hidden or unavailable states.

**Validation Rules**:

- A source-present non-negative count is `available`, including zero, unless the subscriber hiddenness rule applies.
- `subscriberCount` is `hidden` and has no `value` when source `hiddenSubscriberCount` is `true`.
- An expected count absent from source data, or an invalid count representation, is `unavailable` and has no `value`.
- The tool never substitutes zero, an estimate, a derived number, or a count from another channel.

**Relationships**:

- Belongs to exactly one Channel Statistics Result.

## Lookup Outcome

Represents the safe outcome for a request that cannot produce a statistics result.

| Category | Meaning | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | The request did not meet input rules. | Correct `channelId` and retry. |
| `unavailable_resource` | The requested channel cannot be returned. | Use a different accessible identifier; do not infer the cause. |
| `authorization_sensitive_data` | Access to source data is not permitted. | Obtain appropriate authorization if applicable. |
| `quota_exhaustion` | Source capacity prevents the lookup. | Retry after capacity is available. |
| `upstream_failure` | The source could not complete the lookup for another reason. | Retry when appropriate. |

**Safety Rules**:

- Unavailable outcomes do not distinguish deleted, suspended, restricted, and not-found channels.
- Error details exclude credentials, headers, tokens, stack traces, signed links, raw source bodies, and media content.

## Request State Transitions

```text
received
  -> invalid_parameters
  -> validated
       -> unavailable_resource
       -> authorization_sensitive_data
       -> quota_exhaustion
       -> upstream_failure
       -> channel_statistics_result
```
