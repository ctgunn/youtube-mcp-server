# Data Model: YT-307 Channel Search

## Channel Search Request

Represents one public `channels_searchChannels` invocation.

**Fields**:

- `query`: required non-blank text search expression.
- `maxResults`: final result cap; whole number from 1 through 50, default 10.
- `order`: optional base-search order: `date`, `relevance`, `title`, or `videoCount`.
- `channelType`: optional base channel type: `any` or `show`; omitted means no type restriction.
- `minSubscribers` / `maxSubscribers`: optional inclusive, non-negative subscriber bounds.
- `lastUploadAfter` / `lastUploadBefore`: optional inclusive ISO 8601 public latest-upload boundaries with an explicit timezone.
- `creatorOnly`: optional boolean, default `false`.
- `sortBy`: optional final ranking: `relevance`, `subscribers_asc`, `subscribers_desc`, `indie_priority`, or `recent_activity`; default `relevance`.

**Validation Rules**:

- No unknown fields are accepted.
- The query is trimmed and must remain non-blank.
- `maxResults` is a whole number, not a boolean, in the inclusive 1–50 range.
- Dates use ISO 8601 with `Z` or an explicit numeric offset; a paired `After` boundary cannot be later than its paired `Before` boundary.
- Subscriber bounds are whole numbers greater than or equal to zero; a supplied minimum cannot exceed a supplied maximum.
- Boolean fields must be booleans; `order`, `channelType`, and `sortBy` must use their documented enumerations.

## Channel Candidate

Represents one distinct publicly discoverable channel found by the base search.

**Fields**:

- `channelId`: public stable channel identifier from the base result.
- `title`, `description`, `thumbnails`: available public profile fields.
- `normalizedMetadata`: available stable normalized public profile values, including `customUrl` and `joinedAt` when available.
- `statistics.subscriberCount`: available public subscriber count; otherwise unknown.
- `latestVideoPublishedAt`: available derived public latest-upload timestamp; otherwise unknown.
- `heuristics.creatorClassification`: `creator`, `brand`, or `unknown`, based only on public signals.
- `heuristics.creatorSignals`: public signals supporting a non-unknown classification.
- `baseSearchPosition`: internal zero-based position used only to resolve duplicates and ranking ties; never returned.
- `fieldProvenance`: public declaration of source-preserved, normalized, and heuristic-inferred fields.

**Relationships**:

- A candidate belongs to exactly one Channel Search Request.
- A candidate references zero or one Channel Enrichment by `channelId`.

**Validation Rules**:

- A base item without a non-empty `channelId` cannot become a candidate.
- Duplicate identifiers resolve to the candidate at the earliest base-search position.
- Unavailable profile, statistics, activity, or heuristic information is not fabricated.

## Channel Enrichment

Represents public information conditionally used to evaluate an active refinement or ranking rule.

**Fields**:

- `subscriberCount`: available public count, otherwise unknown.
- `uploadsPlaylistId`: internal public playlist reference used only when latest activity is required; never returned as an enrichment claim.
- `latestVideoPublishedAt`: normalized activity timestamp from the available public uploads playlist, otherwise unknown.
- `creatorClassification` and `creatorSignals`: conservative public-signal heuristic result.
- `availability`: `available`, `unavailable`, or `not_requested` for each enrichment datum.

**Validation Rules**:

- Hidden or missing subscriber counts are not converted to zero.
- Latest activity is available only after the bounded public activity lookup succeeds.
- Creator classification is heuristic-inferred, carries a basis and limitation, and never verifies identity or ownership.
- A candidate lacking a datum required by an active filter or non-relevance rank is excluded rather than treated as matching.

## Partial Enrichment Summary

Represents a safe aggregate disclosure after a successful base search where some candidates could not be evaluated for an active rule.

**Fields**:

- `status`: `complete` or `partial`.
- `excludedCandidateCount`: count of candidates excluded because required enrichment was unavailable.
- `reasons`: safe aggregate categories, such as unavailable channel metadata or unavailable latest activity.
- `requiredFor`: active filter or ranking rules that required unavailable information.

**Validation Rules**:

- Contains counts and safe categories only; it contains no credentials, tokens, private owner data, raw source payloads, or stack traces.
- Is included only when an active rule requires enrichment and one or more candidates were excluded for its unavailability.
- If every candidate requiring enrichment cannot be evaluated, the result transitions to the safe `partial_enrichment_failure` state rather than returning an unverified collection.

## Search Result Collection

Represents the final MCP-facing result.

**Fields**:

- `items`: ordered collection of final Channel Candidates with public returned fields only.
- `appliedInputs`: normalized request values that were applied.
- `returnedCount`: number of returned channels.
- `maxResults`: applied final cap.
- `nextPageToken`: optional base-search continuation context; it is not a continuation promise for the final ranked collection.
- `fieldProvenance`: declarations distinguishing `raw_upstream`, `normalized`, and `heuristic_inferred` output fields.
- `partialEnrichment`: optional Partial Enrichment Summary.

**Relationships**:

- Is produced from exactly one Channel Search Request.
- Contains zero to `maxResults` distinct Channel Candidates.
- May contain one Partial Enrichment Summary.

**State Transitions**:

```text
valid request -> base search -> normalize/deduplicate -> no enrichment needed -> completed or empty collection
valid request -> base search -> conditional enrichment -> filter -> rank -> completed, partial, or empty collection
valid request -> base search -> required enrichment unavailable for all candidates -> partial_enrichment_failure
valid request -> safe structured error (authorization, quota, upstream, unavailable)
invalid request -> safe structured invalid-parameter error
```
