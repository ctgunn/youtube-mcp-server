# Data Model: YT-316 Channel Playlist Listing

## Channel Playlist Request

**Fields**: `channelId` is required trimmed nonblank text; `maxResults` is an optional whole number from 1 through 50, default 25.

**Validation**: Unknown fields, booleans, fractions, strings, zero, negatives, and values above 50 are rejected as `invalid_parameters` before any listing.

## Normalized Playlist Record

**Fields**: Required `playlistId` and `title`; available `description`, `channelId`, `channelTitle`, `publishedAt`, `thumbnails`, `itemCount`, and `privacyStatus`.

**Rules**: Records retain source order. Optional absent values are omitted. A malformed source record without usable identity or title is omitted rather than fabricated.

## Channel Playlist Listing

**Fields**: Normalized requested `channelId`, ordered `items`, `returnedCount`, `appliedLimit`, `appliedInputs`, `collectionContext`, and `fieldProvenance`.

**Rules**: Contains zero through the applied limit. An accessible empty collection for a verified channel is a successful listing with zero items. Context declares source order at request time, no ranking, public-content-only scope, and request-time variability.

## Listing Outcome

| Category | Meaning | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | Input is missing, blank, malformed, out of range, or unknown. | Correct the identified field and retry. |
| `unavailable_resource` | The requested listing cannot be retrieved. | Use an accessible channel identifier. |
| `authorization_sensitive_data` | Access cannot retrieve the required public listing. | Obtain applicable access if available. |
| `quota_exhaustion` | Capacity prevents listing. | Retry after capacity is available. |
| `upstream_failure` | Another source failure prevents listing. | Retry when the source is available. |

## State Transitions

```text
received -> invalid_parameters
received -> validate -> channel_verification
channel_verification -> unavailable_resource | authorization_sensitive_data | quota_exhaustion | upstream_failure
channel_verification -> one_playlist_listing
one_playlist_listing -> successful_empty_listing
one_playlist_listing -> normalize_source_order -> successful_listing
one_playlist_listing -> authorization_sensitive_data | quota_exhaustion | upstream_failure
```
