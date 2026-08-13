# Data Model: YT-312 Video Statistics

## Video Statistics Request

Represents one client request for source-provided statistics about exactly one video.

**Fields**:

- `videoId`: required nonblank text identifier for exactly one video.

**Validation Rules**:

- Only `videoId` is accepted.
- `videoId` must be nonblank text after trimming.
- Missing, blank, non-text, non-object, or unknown inputs produce `invalid_parameters` before a source lookup.

**Relationships**:

- Produces one Video Statistics Result or one Lookup Outcome.
- Causes exactly one lower-level `videos.list` lookup using the source `statistics` group.

## Video Statistics Result

Represents the normalized successful result for one retrievable video.

**Fields**:

- `videoId`: requested video identifier, preserved from the returned source item when available.
- `statistics`: a stable mapping of all expected Statistic Metrics.
- `fieldProvenance`: caller-visible declaration that counts are source-provided and availability states are normalized.
- `sourceCaveats`: caller-visible notes for source semantics that materially affect interpretation, including favorite-count deprecation. Discovery metadata separately documents dislike-count exclusion.

**Rules**:

- The result represents exactly one video and never a collection, pagination, enrichment, ranking, or derived analytics.
- It contains all four expected metrics regardless of whether each source value is available.
- It contains no `dislikeCount` or undocumented raw source fields.

**Relationships**:

- Contains exactly four Statistic Metrics.
- Is derived from the first item in one lower-level `videos.list` response.

## Statistic Metric

Represents one expected public count: `viewCount`, `likeCount`, `commentCount`, or `favoriteCount`.

**Fields**:

- `state`: `available` or `unavailable`.
- `value`: present only when `state` is `available`; a non-negative decimal source count, including `"0"`.
- `provenance`: `source_provided` for an available count and `normalized` for an unavailable state.

**Validation Rules**:

- A source-present non-negative count is `available`, including zero.
- An expected count absent from source data is `unavailable` and has no `value`.
- The tool never substitutes zero, an estimate, a derived number, or a count from another video.
- `favoriteCount`, when available, retains its source value while sourceCaveats disclose that the source deprecates it and reports it as zero.

**Relationships**:

- Belongs to exactly one Video Statistics Result.

## Lookup Outcome

Represents the safe outcome for a request that cannot produce a statistics result.

| Category | Meaning | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | The request did not meet input rules. | Correct `videoId` and retry. |
| `unavailable_resource` | The requested video cannot be returned. | Use a different accessible identifier; do not infer the cause. |
| `authorization_sensitive_data` | Access to source data is not permitted. | Obtain appropriate authorization if applicable. |
| `quota_exhaustion` | Source capacity prevents the lookup. | Retry after capacity is available. |
| `upstream_failure` | The source could not complete the lookup for another reason. | Retry when appropriate. |

**Safety Rules**:

- Unavailable outcomes do not distinguish private, deleted, restricted, and not-found videos.
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
       -> video_statistics_result
```
