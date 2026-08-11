# Data Model: YT-305 Channel Details

## Channel Detail Request

Represents one client request for normalized details about one channel.

**Fields**:

- `channelId`: required, nonblank text identifier for exactly one channel.

**Validation Rules**:

- Only `channelId` is accepted.
- `channelId` must be text and remain nonblank after trimming.
- Invalid input produces `invalid_parameters` before any lookup.

**Relationships**:

- Produces one Channel Detail or one whole-request Lookup Outcome.

## Channel Detail

Represents the successful bounded result for one available channel.

**Core fields**:

- `channelId`: source-provided canonical channel identifier.
- `title`, `description`, `thumbnails`: available public channel profile values.
- `normalizedMetadata`: stable normalized public metadata.
- `latestVideoPublishedAt`: normalized latest-video enrichment when available.
- `enrichment`: status of latest-video enrichment.
- `heuristics`: non-canonical public-contact and channel-type context.
- `fieldProvenance`: field-path-to-category mapping for every returned field.

**Rules**:

- The result contains one channel only and never exposes a lower-layer collection envelope, ranking, pagination, or additional channel lookup.
- Core profile values preserve their source meaning; unavailable values are not synthesized.
- `channelId`, `title`, `description`, and `thumbnails` are `raw_upstream` values.
- Normalized source mappings are `normalized`; derived contacts and channel-type conclusions are `heuristic_inferred`.

**Relationships**:

- Has one Normalized Metadata group, one Latest-video Enrichment state, and one Channel Heuristic group.
- Is derived from one core channel lookup and at most one uploads-playlist item lookup.

## Normalized Metadata

Represents stable public channel metadata.

| Field | Meaning | Provenance rule |
| --- | --- | --- |
| `country` | Available public channel country. | `normalized` |
| `defaultLanguage` | Available public default language. | `normalized` |
| `joinedAt` | Available public channel joining timestamp. | `normalized` |
| `customUrl` | Available public custom channel URL or handle. | `normalized` |
| `emailsFound` | Valid, de-duplicated public email values found in returned public channel material. | `heuristic_inferred` |
| `contactLinks` | Valid, de-duplicated HTTP(S) links found in returned public channel material. | `heuristic_inferred` |

**Rules**:

- Absent source values remain unavailable.
- Contact values are not identity verification, owner information, or canonical source truth.
- Contact extraction does not fetch or crawl external pages and omits malformed, duplicate, unsupported, private, or non-public values.

## Latest-video Enrichment

Represents the availability-aware result of the one optional public uploads-playlist read.

**Fields**:

- `latestVideoPublishedAt`: available publication timestamp for the most recent publicly visible video, or unavailable.
- `status`: one of `complete`, `unavailable`, or `partial`.
- `category`: `partial_enrichment_failure` only when `status` is `partial`.
- `causeCategory`: safe underlying category only when `status` is `partial`.

**State Rules**:

- `complete`: the single playlist-item lookup yields a valid publication timestamp.
- `unavailable`: no usable uploads-playlist identifier, no item, or no valid timestamp is available; the core channel profile remains successful.
- `partial`: a safe access, quota, or source failure occurs after core profile success; no timestamp is returned.
- At most one playlist-item lookup is made, with one result requested.

## Channel Heuristic

Represents explicitly non-canonical research context derived from public channel material.

**Fields**:

- `creatorClassification`: `creator`, `brand`, or `unknown`.
- `creatorSignals`: deterministic public signal identifiers that support the classification.

**Rules**:

- A `creator` or `brand` result requires positive, non-conflicting public signals.
- Missing or conflicting signals produce `unknown` and do not assert a classification.
- Signal identifiers describe the evidence category, not raw copied profile text.
- The group is `heuristic_inferred`; it is not verified identity, ownership, or canonical source data.

## Lookup Outcome

Represents a safe whole-request outcome when no Channel Detail can be returned.

| Category | Meaning | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | Input is missing, blank, wrong type, or includes an unknown field. | Correct the identified input and retry. |
| `unavailable_resource` | The requested channel cannot be returned. | Use a different accessible channel identifier. |
| `authorization_sensitive_data` | Required source data is not accessible with current authorization. | Obtain appropriate authorization if applicable. |
| `quota_exhaustion` | Capacity prevents the core lookup. | Retry after capacity is available. |
| `upstream_failure` | Another source failure prevents the core lookup. | Retry when the source service is available. |

**Safety Rules**:

- Unavailable outcomes do not distinguish deleted, hidden, restricted, and not-found channels.
- Whole-request errors and partial enrichment detail exclude credentials, headers, tokens, owner context, stack traces, raw source payloads, signed links, and non-public contact information.

## Request State Transitions

```text
received
  -> invalid_parameters
  -> core_channel_lookup
       -> unavailable_resource
       -> authorization_sensitive_data
       -> quota_exhaustion
       -> upstream_failure
       -> core_profile_normalized
            -> enrichment_complete -> channel_detail
            -> enrichment_unavailable -> channel_detail
            -> enrichment_partial -> channel_detail
```
