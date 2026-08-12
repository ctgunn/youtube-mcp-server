# Data Model: YT-309 Channel Video Listing

## Channel Video Listing Request

Represents one public `channels_listVideos` invocation.

**Fields**:

- `channelId`: required nonblank text identifier for exactly one channel.
- `maxResults`: optional final result cap; whole number from 1 through 50, default 10.

**Validation Rules**:

- No unknown fields are accepted.
- `channelId` is trimmed and must remain nonblank.
- `maxResults` must be an integer rather than a boolean, fraction, string, zero, negative number, or a value above 50.
- Invalid input produces `invalid_parameters` before either lower-layer lookup begins.

**Relationships**:

- Produces one Listing Result or one whole-request Listing Outcome.

## Channel Uploads Collection

Represents the publicly listable collection associated with one available channel at request time.

**Fields**:

- `channelId`: requested public channel identifier.
- `collectionReference`: internal public collection reference derived from the available channel record; never required as caller input.
- `sourceOrder`: the order returned by the public collection for this request.

**Rules**:

- The reference is resolved by one channel lookup.
- A missing usable reference produces a successful empty Listing Result, not an unavailable channel.
- The tool does not claim that source order is relevance-ranked, globally chronological, or immutable between requests.
- The collection is read at most once with the validated final cap.

## Channel Video Item

Represents one distinct publicly available video in the collection.

**Fields**:

- `videoId`: nonblank public video identifier.
- `title`, `description`, `thumbnails`: available public source values.
- `publishedAt`: available public publication time from the collection item.

**Validation Rules**:

- A source item without a usable video identifier is omitted.
- Duplicate video identifiers resolve to the first usable source occurrence.
- Optional source values remain unavailable when absent; the tool does not fabricate them.
- Returned item fields are source-preserved values and are labeled `raw_upstream` in field provenance.

## Listing Result

Represents a successful bounded collection response.

**Fields**:

- `channelId`: normalized requested identifier.
- `items`: zero through `maxResults` distinct Channel Video Items in observed source order.
- `returnedCount`: number of returned items.
- `maxResults`: validated applied cap.
- `appliedInputs`: normalized request values applied to the listing.
- `collectionContext`: normalized declaration of uploads-collection source, source ordering, no-ranking behavior, and request-time variability.
- `fieldProvenance`: field-path-to-category mapping for returned fields.
- `partialAvailability`: optional safe aggregate disclosure of known item-level omissions.

**Relationships**:

- Is produced from one Channel Video Listing Request.
- Reads one Channel Uploads Collection at most once.
- Contains zero through `maxResults` distinct Channel Video Items.

**Rules**:

- `channelId`, `returnedCount`, `maxResults`, `appliedInputs`, `collectionContext`, and partial-availability context are normalized contract values.
- Source-order preservation, de-duplication, and cap occur in that order: preserve usable source sequence, retain first distinct identities, then cap.
- A successful empty collection has `items: []` and `returnedCount: 0`.

## Partial Availability

Represents a safe aggregate disclosure when a successful collection result establishes known item-level omissions.

**Fields**:

- `status`: `partial`.
- `omittedItemCount`: number of known omitted items when safely determinable.
- `reasons`: safe aggregate availability categories.

**Rules**:

- Contains no item identity, private channel context, credential, token, raw source payload, or stack trace.
- Exists only after a collection response otherwise succeeds.
- A failed required collection lookup is a whole-request safe error, not Partial Availability.

## Listing Outcome

Represents a safe whole-request outcome when no Listing Result can be returned.

| Category | Meaning | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | Input is missing, blank, wrong type, out of range, or includes an unknown field. | Correct the identified field and retry. |
| `unavailable_resource` | The requested channel cannot be publicly listed. | Use a different accessible channel identifier. |
| `authorization_sensitive_data` | Required public listing data is inaccessible with current authorization. | Obtain the applicable public-read capability if available. |
| `quota_exhaustion` | Capacity prevents a required lookup. | Retry after capacity is available. |
| `upstream_failure` | Another source failure prevents listing. | Retry when the source service is available. |

**Safety Rules**:

- Unavailable outcomes do not distinguish deleted, hidden, restricted, and not-found channels.
- Whole-request errors exclude credentials, headers, tokens, owner context, stack traces, raw source payloads, signed links, and non-public video data.

## Request State Transitions

```text
received
  -> invalid_parameters
  -> channel_lookup
       -> unavailable_resource
       -> authorization_sensitive_data
       -> quota_exhaustion
       -> upstream_failure
       -> uploads_reference_missing -> successful_empty_listing
       -> uploads_collection_lookup
            -> authorization_sensitive_data
            -> quota_exhaustion
            -> upstream_failure
            -> normalize_deduplicate_cap
                 -> successful_empty_listing
                 -> successful_listing
                 -> successful_partial_availability_listing
```
