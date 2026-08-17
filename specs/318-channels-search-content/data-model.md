# Data Model: YT-318 Channel Content Search

## Channel Content Search Request

Represents one public `channels_searchContent` invocation.

**Fields**:

- `channelId`: required nonblank text identifier for exactly one channel.
- `query`: required nonblank text search expression.
- `maxResults`: optional final result cap; whole number from 1 through 50, default 10.
- `order`: optional direct-search ordering; one of `relevance`, `date`, or `viewCount`, default `relevance`.
- `language`: optional BCP 47 language tag used only as a relevance preference.

**Validation Rules**:

- No unknown fields are accepted.
- `channelId`, `query`, and a supplied `language` are trimmed and must remain nonblank.
- `maxResults` must be an integer rather than a boolean, fraction, string, zero, negative number, or value above 50.
- `order` must be one of the documented values.
- `language` must be a valid BCP 47 language tag. It refines relevance only and does not guarantee language-only results.
- Invalid input produces `invalid_parameters` before the lower-layer search begins.

**Relationships**:

- Produces one Channel-Constrained Search Request and one Search Result Collection or Safe Search Outcome.

## Channel-Constrained Search Request

Represents the single internal public-read search created from one valid public request.

**Fields**:

- `channelId`: normalized requested channel identifier.
- `query`: normalized requested query.
- `contentType`: fixed `video` scope.
- `maxResults`, `order`, `language`: effective public request options.

**Rules**:

- Uses exactly one lower-layer search request with public video scope and the requested channel constraint.
- The language preference maps only to the source relevance preference when supplied.
- No continuation token, owner selector, private-content selector, enrichment request, or local ranking input is accepted.

## Channel Content Item

Represents one distinct usable public video returned by the channel-constrained source search.

**Fields**:

- `videoId`: nonblank public video identity.
- `contentType`: normalized `video` value.
- `title`, `description`, `publishedAt`, `channelId`, `channelTitle`, `thumbnails`: available public source values.

**Validation Rules**:

- A source item must have a usable video identity and an available source channel identity equal to the requested `channelId`.
- Duplicate video identities retain their first usable source occurrence.
- Optional source values remain absent when unavailable; the tool does not fabricate them.
- Item fields preserve public source meaning and are labeled `raw_upstream` in field provenance except `contentType`, which is normalized from the fixed public search scope.

**Relationships**:

- Belongs to one Search Result Collection.
- Is sourced by exactly one Channel-Constrained Search Request.

## Search Result Collection

Represents a successful bounded channel-content search response.

**Fields**:

- `channelId`, `query`: normalized required request values.
- `items`: zero through `maxResults` distinct Channel Content Items in direct-search source order.
- `returnedCount`: number of returned items.
- `maxResults`: effective result cap.
- `appliedInputs`: all normalized values used for this invocation, including a supplied language preference.
- `searchContext`: normalized declaration of direct channel-constrained matching, selected upstream ordering, public-only content, no local enrichment/filtering/re-ranking, and language-hint limitations.
- `fieldProvenance`: field-path-to-category mapping for returned fields.
- `partialAvailability`: optional safe aggregate disclosure for omitted malformed, duplicate, or out-of-scope source records.

**Rules**:

- Matching and ordering are direct-source behavior; the tool does not add a second ranking or filtering rule.
- A successful no-match source response has `items: []` and `returnedCount: 0` with complete request and search context.
- A collection may contain only items associated with the requested channel.
- A failed required search cannot produce a collection or partial collection.

## Partial Availability

Represents safe aggregate disclosure after a source search succeeds but one or more returned records cannot be represented safely.

**Fields**:

- `status`: `partial`.
- `omittedItemCount`: safely determinable number of omitted records.
- `reasons`: safe aggregate categories, including `unusable_or_out_of_scope_source_item`.

**Rules**:

- Contains no item identity, raw source payload, private channel context, credential, token, signed URL, or stack trace.
- Does not imply a failed source search or identify whether an omitted record is unavailable, restricted, deleted, malformed, or mismatched.

## Safe Search Outcome

Represents a safe whole-request outcome when no Search Result Collection can be returned.

| Category | Meaning | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | Input is missing, blank, malformed, out of range, unsupported, or contains an invalid language tag. | Correct the identified field and retry. |
| `unavailable_resource` | The requested public search scope cannot be accessed. | Use another accessible channel identifier or retry later. |
| `authorization_sensitive_data` | Configured public access cannot retrieve required data. | Obtain applicable public-read capability if available. |
| `quota_exhaustion` | Capacity prevents the required search. | Retry after capacity is available. |
| `upstream_failure` | Another source failure prevents search completion. | Retry when the source service is available. |

**Safety Rules**:

- Whole-request outcomes exclude credentials, headers, tokens, stack traces, raw request/response bodies, signed links, owner context, and non-public content.

## Request State Transitions

```text
received
  -> invalid_parameters
  -> direct_channel_constrained_search
       -> unavailable_resource
       -> authorization_sensitive_data
       -> quota_exhaustion
       -> upstream_failure
       -> normalize_associate_deduplicate_cap
            -> successful_empty_collection
            -> successful_collection
            -> successful_partial_availability_collection
```
