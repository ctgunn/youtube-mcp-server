# Data Model: YT-303 Video Search with Channel Refinement

## Video Search Request

Represents one caller's public `videos_searchVideos` invocation.

**Fields**:

- `query`: required non-blank text search expression.
- `maxResults`: final result cap; integer from 1 through 50, default 10.
- `order`: optional base-search order: `date`, `rating`, `relevance`, `title`, or `viewCount`.
- `publishedAfter` / `publishedBefore`: optional inclusive ISO 8601 video-publication boundaries with explicit timezone.
- `channelId`: optional public channel scope for the base video search.
- `uniqueChannels`: optional boolean, default `false`.
- `channelMinSubscribers` / `channelMaxSubscribers`: optional inclusive non-negative subscriber limits.
- `channelLastUploadAfter` / `channelLastUploadBefore`: optional inclusive ISO 8601 public latest-upload boundaries with explicit timezone.
- `creatorOnly`: optional boolean, default `false`.
- `sortBy`: optional final ranking: `relevance`, `subscribers_asc`, `subscribers_desc`, `indie_priority`, or `recent_activity`; default `relevance`.

**Validation Rules**:

- No unknown fields are accepted.
- Text identifiers and query values are trimmed; `query` and a supplied `channelId` must remain non-blank.
- `maxResults` is an integer, not a boolean, in the inclusive 1–50 range.
- Dates use ISO 8601 with `Z` or an explicit numeric offset.
- A paired `After` boundary cannot be later than its paired `Before` boundary.
- Subscriber bounds are integers greater than or equal to zero, and a supplied minimum cannot exceed a supplied maximum.
- Boolean fields must be booleans; `order` and `sortBy` must use their respective enumerations.

## Video Candidate

Represents one normalized video discovered by the base search.

**Fields**:

- `videoId`: raw video identifier from the base result.
- `title`, `description`, `publishedAt`, `channelId`, `channelTitle`, `thumbnails`: normalized core video fields when available.
- `baseSearchPosition`: internal zero-based position used only for deterministic ties.
- `channelEnrichment`: optional related Channel Enrichment.

**Relationships**:

- A candidate belongs to one Video Search Request.
- A candidate references zero or one Channel Enrichment by `channelId`.
- Multiple candidates can reference the same channel enrichment.

**State Transitions**:

```text
base result -> normalized candidate -> conditionally enriched -> filtered -> ranked -> de-duplicated -> returned or excluded
```

## Channel Enrichment

Represents public channel information used to evaluate an eligible video candidate.

**Fields**:

- `channelId`: public channel identifier matching the candidate.
- `subscriberCount`: raw public subscriber count when available; otherwise unknown.
- `latestVideoPublishedAt`: normalized date-ordered public activity timestamp when requested and available.
- `creatorClassification`: `creator` or `unknown`; a heuristic-inferred field.
- `creatorSignals`: safe public explanation of positive signals when a creator classification is present.
- `availability`: `available`, `unavailable`, or `not_requested` for each required enrichment datum.

**Validation Rules**:

- Hidden or missing subscriber count is not converted to zero.
- Latest activity is available only when conditional date-ordered enrichment succeeds.
- Creator classification is never presented as raw source data and must include a basis and limitation in the public contract.
- A candidate lacking metadata required by an active filter or non-relevance rank is excluded rather than treated as matching.

## Partial Enrichment Summary

Represents safe aggregate disclosure when base search succeeds but not every candidate can be evaluated for requested channel-aware behavior.

**Fields**:

- `status`: `complete` or `partial`.
- `excludedCandidateCount`: number of candidates excluded because required enrichment was unavailable.
- `reasons`: safe aggregate reason categories, such as unavailable channel metadata or unavailable latest activity.
- `requiredFor`: active filter or ranking rules that required the unavailable data.

**Validation Rules**:

- Contains counts and safe categories only; no upstream bodies, credentials, tokens, or stack traces.
- Is included only when enrichment was requested or needed by an active rule.
- If every candidate requiring enrichment cannot be evaluated, the invocation transitions to the safe `partial_enrichment_failure` error state instead of returning an unverified collection.

## Search Result Collection

Represents the final MCP-facing output.

**Fields**:

- `items`: ordered collection of final Video Candidates, with only public returned fields.
- `appliedInputs`: normalized request values actually applied.
- `returnedCount`: number of returned items.
- `maxResults`: applied final cap.
- `nextPageToken`: optional continuation token from the base search when present.
- `fieldProvenance`: declarations distinguishing `raw_upstream`, `normalized`, and `heuristic_inferred` output fields.
- `partialEnrichment`: optional Partial Enrichment Summary.

**Relationships**:

- Is produced from exactly one Video Search Request.
- Contains zero to `maxResults` Video Candidates.
- May contain one Partial Enrichment Summary.

**State Transitions**:

```text
valid request -> base-search success -> completed collection | partial collection | empty successful collection
valid request -> safe structured error (authorization, quota, upstream, unavailable, partial enrichment)
invalid request -> safe structured invalid-parameter error
```
