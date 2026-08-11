# Data Model: YT-306 Batch Channel Details

## Batch Channel Request

Represents one request for normalized public details for multiple channels.

| Field | Type | Default | Rules |
| --- | --- | --- | --- |
| `channelIds` | list of text | none | Required. Contains 1–50 nonblank IDs after trimming. IDs must be distinct after trimming. |
| `parts` | list of text | `["snippet"]` | Optional. Must be a nonempty, duplicate-free selection from `snippet` and `contentDetails`. |
| `includeLatestUpload` | Boolean | `true` | Optional. Controls whether latest-upload enrichment is attempted. |

**Relationships**:

- Produces exactly one Batch Channel Result or one request-wide invalid/operational error.
- Every valid requested ID produces exactly one ordered Batch Item after a successful core lookup.

## Batch Channel Result

Represents the caller-ready result of a successful bulk core lookup.

| Field | Meaning |
| --- | --- |
| `requestedChannelIds` | The validated, trimmed IDs in caller order. |
| `results` | One Batch Item per requested ID in the same order. |
| `summary` | Counts that partition the request: `requested`, `successful`, `unavailable`, and `partiallyEnriched`. |

**Summary rules**:

- `requested` equals the number of `requestedChannelIds` and `results`.
- `successful` counts items with a usable core profile and enrichment `complete`, `unavailable`, or `not_requested`.
- `unavailable` counts items with outcome category `unavailable_resource`.
- `partiallyEnriched` counts items with a usable core profile and enrichment status `partial`; these items are not also counted as `successful`.
- `requested = successful + unavailable + partiallyEnriched`.

## Batch Item

Represents the independent result for one requested channel ID.

**Common fields**:

- `channelId`: the validated requested ID; raw source provenance only when confirmed by a successful source item.
- `outcome`: an item-level status that is `success`, `partial`, or `unavailable`.
- `fieldProvenance`: a mapping for every returned successful-item field path; batch container fields are not represented as channel source fields.

**Successful-item fields**:

- `title`, `description`, `thumbnails`: available raw public profile values when `snippet` is selected.
- `normalizedMetadata`: the selected-data-permitting normalized public metadata group.
- `heuristics`: public-data-derived contact and creator-type context when `snippet` is selected.
- `contentDetails.uploadsPlaylistId`: public uploads-playlist identifier only when `contentDetails` is selected and available.
- `latestVideoPublishedAt`: normalized enrichment timestamp only when enrichment is complete.
- `enrichment`: one Latest-upload Enrichment state.

**Rules**:

- A successful source item retains only supported selected source-detail groups plus identity, outcome, enrichment, and provenance.
- A missing source item has an `unavailable_resource` outcome and no synthesized profile, normalized metadata, heuristic, or enrichment data.
- A partial item keeps its usable core fields and carries a safe partial enrichment state.

## Normalized Metadata

Represents stable mappings from selected public profile material.

| Field | Provenance | Rule |
| --- | --- | --- |
| `country` | `normalized` | Available public channel country; otherwise unavailable. |
| `defaultLanguage` | `normalized` | Available public default language; otherwise unavailable. |
| `joinedAt` | `normalized` | Available public channel joining timestamp; otherwise unavailable. |
| `customUrl` | `normalized` | Available public custom URL or handle; otherwise unavailable. |
| `emailsFound` | `heuristic_inferred` | Valid, de-duplicated public email values from returned public material only. |
| `contactLinks` | `heuristic_inferred` | Valid, de-duplicated public HTTP(S) links from returned public material only. |

## Channel Heuristic

Represents non-canonical research context derived from selected public profile material.

- `creatorClassification`: `creator`, `brand`, or `unknown`.
- `creatorSignals`: deterministic safe identifiers for the applicable public signals.

**Rules**:

- Positive, non-conflicting public signals are required for `creator` or `brand`.
- Missing or conflicting signals yield `unknown` with no unsupported assertion.
- Contact values and heuristics do not verify ownership, affiliation, identity, or permission to contact.

## Latest-upload Enrichment

Represents the state of the optional bounded enrichment for a successful core item.

| Status | Timestamp | Additional fields | Meaning |
| --- | --- | --- | --- |
| `complete` | Present | none | A valid latest publicly visible upload timestamp was determined. |
| `unavailable` | Omitted | none | No usable uploads playlist, item, or valid timestamp is available. |
| `partial` | Omitted | `category: partial_enrichment_failure`, safe `causeCategory` | Post-core enrichment failed safely. |
| `not_requested` | Omitted | none | Caller set `includeLatestUpload` to `false`; no enrichment lookup occurs. |

Safe `causeCategory` values for `partial` are `authorization_sensitive_data`, `quota_exhaustion`, and `upstream_failure`.

## Item and Request Outcomes

| Boundary | Category | Meaning | Caller guidance |
| --- | --- | --- | --- |
| Request | `invalid_parameters` | The batch shape, ID list, selection, or unknown field is invalid. | Correct the identified input before retrying. |
| Request | `authorization_sensitive_data` | The bulk core lookup requires unavailable authorization. | Obtain appropriate authorization if applicable. |
| Request | `quota_exhaustion` | Capacity prevents the bulk core lookup. | Retry after capacity is available. |
| Request | `upstream_failure` | Another source failure prevents the bulk core lookup. | Retry when the source service is available. |
| Item | `unavailable_resource` | A requested ID is absent from an otherwise successful core response. | Use a different accessible identifier. |
| Item | `partial_enrichment_failure` | Optional enrichment failed after core success. | Use the returned core profile; retry later if the safe cause category is actionable. |

All outcomes omit credentials, authorization values, headers, tokens, private owner context, stack traces, raw source bodies, signed links, and non-public contact information.

## State Transitions

```text
received
  -> invalid_parameters
  -> bulk_core_lookup
       -> authorization_sensitive_data | quota_exhaustion | upstream_failure
       -> core_items_indexed
            -> requested ID absent -> unavailable item
            -> source item normalized
                 -> enrichment disabled -> successful item (not_requested)
                 -> enrichment complete -> successful item
                 -> enrichment unavailable -> successful item
                 -> enrichment safe failure -> partial item
  -> ordered batch result and summary
```
