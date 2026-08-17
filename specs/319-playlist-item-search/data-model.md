# Data Model: Search Playlist Items

## Playlist Search Request

| Field | Type | Required | Validation |
| --- | --- | --- | --- |
| `playlistId` | text | Yes | Must be text and non-blank after trimming. |
| `query` | text | Yes | Must be text and non-blank after trimming; repeated internal whitespace is collapsed. |
| `maxResults` | whole number | No | Must be 1 through 50; defaults to 25. |

Unknown request fields are rejected. The request accepts no pagination or continuation value.

## Source Playlist Item

An internally retrieved playlist entry. It is not returned unchanged.

| Field | Meaning | Handling |
| --- | --- | --- |
| Playlist position | Source sequence of the entry | Preserves source order. |
| Playlist-item identifier | Identity of the playlist entry | Returned when exposed. |
| Video identifier | Identity of the referenced video | Returned and searchable when exposed. |
| Title | Exposed item title | Returned and searchable when exposed. |
| Description | Exposed item description | Returned and searchable when exposed. |
| Channel identity | Exposed channel identifier and name | Identity is returned when exposed; name is searchable when exposed. |
| Publication time | Exposed item publication time | Returned when exposed. |
| Availability state | Whether useful public details are exposed | Never inferred; unavailable entries may match only exposed fields. |

## Search Match

A normalized source item that satisfies the literal query in one or more exposed fields.

| Field | Type | Rules |
| --- | --- | --- |
| `position` | whole number | Preserved source position when exposed. |
| `playlistItemId` | text or absent | Included only when exposed. |
| `videoId` | text or absent | Included only when exposed. |
| `title` | text or absent | Included only when exposed. |
| `description` | text or absent | Included only when exposed. |
| `channelId` | text or absent | Included only when exposed. |
| `channelTitle` | text or absent | Included only when exposed. |
| `publishedAt` | timestamp text or absent | Included only when exposed. |
| `availabilityState` | `available` or `unavailable` | Always included; unavailable values are not fabricated. |
| `matchingFields` | ordered text collection | Non-empty subset of `title`, `description`, `channelTitle`, `videoId`, in that order. |

## Search Coverage

| Field | Type | Meaning |
| --- | --- | --- |
| `inspectedEntryCount` | whole number, 0-500 | Number of playlist entries inspected in source order. |
| `isComplete` | boolean | `true` only when traversal reaches the end of accessible entries before the 500-entry cap. |
| `terminationReason` | `end_of_playlist` or `inspection_cap` | Explains whether coverage ended naturally or at the documented cap. |

## Playlist Search Result

| Field | Type | Meaning |
| --- | --- | --- |
| `playlistId` | text | Normalized requested playlist identifier. |
| `query` | text | Normalized literal phrase used for matching. |
| `items` | ordered collection of Search Match | Returned matches, capped by `appliedLimit`. |
| `returnedCount` | whole number, 0-50 | Number of returned matches. |
| `appliedLimit` | whole number, 1-50 | Effective result limit. |
| `searchCoverage` | Search Coverage | Scope inspected by this request. |
| `additionalMatchesOmitted` | `true`, `false`, or `null` | `true` when an additional matching item was observed after the returned limit; `false` when complete coverage proves none was omitted; `null` when incomplete coverage prevents a definitive answer. |
| `searchContext` | object | Documents literal matching, searchable fields, source ordering, no ranking, and excluded search types. |
| `fieldProvenance` | object | Distinguishes source-preserved values from normalized contract values. |

## State Transitions

```text
valid request
  -> playlist availability confirmed
  -> inspect page(s), 0-500 entries
  -> terminal page: complete coverage
     OR inspection cap: incomplete coverage
  -> filter and return normalized source-ordered matches

invalid request / unavailable playlist / safe lower-layer failure
  -> safe structured error (no successful search result)
```
