# Data Model: YT-311 Playlist Items

## Playlist Item Listing Request

Represents one public `playlists_getPlaylistItems` invocation.

**Fields**:

- `playlistId`: required nonblank text identifier for exactly one playlist.
- `maxResults`: optional final result cap; whole number from 1 through 50, default 25.

**Validation Rules**:

- No unknown fields are accepted.
- `playlistId` is trimmed and must remain nonblank.
- `maxResults` must be an integer rather than a boolean, fraction, string, zero, negative number, or value above 50.
- Invalid input produces `invalid_parameters` before the lower-layer listing begins.

**Relationships**:

- Produces one Playlist Item Collection or one whole-request Listing Outcome.

## Playlist Item

Represents one entry exposed by the source playlist in observed playlist order.

**Available Fields**:

- `position`: available numeric playlist position.
- `playlistItemId`: available source playlist-item identifier.
- `videoId`: available public video identifier.
- `title`: available public video title.
- `channelId`, `channelTitle`: available public channel identity.
- `publishedAt`: available public publication time.
- `availabilityState`: normalized `available` or `unavailable` state.

**Rules**:

- Items retain the source sequence exactly as returned for the request; no ranking, sorting, de-duplication, or filtering is applied.
- An item with usable public video identity and no unavailable source indication is `available`.
- An exposed item without usable public video details, or with an unavailable source indication, is retained as `unavailable` and does not receive fabricated details.
- Optional source values are omitted when absent.

## Playlist Item Collection

Represents a successful bounded response.

**Fields**:

- `playlistId`: normalized requested playlist identifier.
- `items`: zero through `maxResults` Playlist Items in observed source order.
- `returnedCount`: number of returned entries.
- `appliedLimit`: validated final result cap.
- `isLimited`: whether the source response signals additional entries beyond the applied limit.
- `collectionContext`: normalized declaration of playlist source, source order, no-ranking behavior, one-page boundary, public-content boundary, and request-time variability.
- `fieldProvenance`: field-path-to-category mapping for returned values.

**Rules**:

- A successfully returned empty collection has `items: []`, `returnedCount: 0`, and `isLimited: false`.
- `isLimited` is true only when the source response safely signals additional entries; it is not guessed from the requested limit alone.
- `playlistId`, counts, limits, collection context, and provenance are normalized contract values.
- Item values preserve available source meaning and are labeled as raw upstream or normalized availability context in field provenance.

**Relationships**:

- Is produced by exactly one Playlist Item Listing Request and exactly one lower-layer playlist-item listing.
- Contains zero through `maxResults` Playlist Items.

## Listing Outcome

Represents a safe whole-request outcome when no collection can be returned.

| Category | Meaning | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | Input is missing, blank, wrong type, out of range, or includes an unknown field. | Correct the identified field and retry. |
| `unavailable_resource` | The source reports that the requested playlist cannot be returned. | Use a different accessible playlist identifier. |
| `authorization_sensitive_data` | Configured public access cannot retrieve the required source data. | Obtain appropriate access if applicable. |
| `quota_exhaustion` | Capacity prevents the required listing. | Retry after capacity is available. |
| `upstream_failure` | Another source failure prevents listing. | Retry when the source service is available. |

**Safety Rules**:

- Error details exclude credentials, headers, tokens, private owner context, stack traces, raw source payloads, signed links, and non-public video data.
- A successful empty collection is not converted into an unavailable outcome and does not claim a provider-specific cause.

## Request State Transitions

```text
received
  -> invalid_parameters
  -> validated
       -> playlist_item_listing
            -> unavailable_resource
            -> authorization_sensitive_data
            -> quota_exhaustion
            -> upstream_failure
            -> normalize_source_order
                 -> successful_empty_collection
                 -> successful_collection
                 -> successful_limited_collection
```
