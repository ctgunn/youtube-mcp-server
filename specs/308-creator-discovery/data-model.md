# Data Model: YT-308 Creator Discovery

## Creator Discovery Request

Represents one public `channels_findCreators` invocation.

**Fields**:

- `query`: required non-blank topic search expression.
- `maxResults`: final channel-result cap; whole number from 1 through 50, default 10.
- `order`: optional base video-search order: `date`, `rating`, `relevance`, `title`, or `viewCount`.
- `videoPublishedAfter` / `videoPublishedBefore`: optional inclusive ISO 8601 video-publication boundaries with an explicit timezone.
- `channelMinSubscribers` / `channelMaxSubscribers`: optional inclusive, non-negative subscriber bounds.
- `channelLastUploadAfter` / `channelLastUploadBefore`: optional inclusive ISO 8601 latest-upload boundaries with an explicit timezone.
- `creatorOnly`: optional boolean, default `false`.
- `sortBy`: optional final ranking: `relevance`, `subscribers_asc`, `subscribers_desc`, `indie_priority`, or `recent_activity`; default `relevance`.
- `sampleVideosPerChannel`: whole number from 0 through 10, default 0.

**Validation Rules**:

- No unknown fields are accepted; text is trimmed and `query` must remain non-blank.
- `maxResults` and `sampleVideosPerChannel` are whole numbers, not booleans, within their inclusive bounds.
- Date values use ISO 8601 with `Z` or an explicit numeric offset; an `After` boundary cannot be later than its paired `Before` boundary.
- Subscriber bounds are whole numbers greater than or equal to zero; a supplied minimum cannot exceed its paired maximum.
- `creatorOnly` must be boolean; `order` and `sortBy` must use documented enumerations.

## Matched Video

Represents a public topic-matching source video used to derive or sample a creator candidate.

**Fields**:

- `videoId`: stable public video identifier.
- `channelId`: stable public owning-channel identifier.
- `title`: available public video title.
- `publishedAt`: available public video publication timestamp.
- `channelTitle`, `thumbnails`: available public video search metadata.
- `baseSearchPosition`: internal zero-based source position, never returned directly.

**Validation Rules**:

- A base result without a non-blank video identifier and channel identifier cannot contribute a sample or candidate.
- Publication constraints are applied before candidate derivation.
- Source order is retained for candidate tie-breaking and samples.

## Creator Candidate

Represents one distinct publicly discoverable channel derived from one or more Matched Videos.

**Fields**:

- `channelId`: stable public channel identifier.
- `matchedVideoBasis`: normalized evidence that the candidate was derived from at least one matched video.
- `baseSearchPosition`: internal earliest matched-video position used for deterministic order and ties.
- `matchingVideos`: internal ordered Matched Video collection from which returned samples are selected.
- `title`, `description`, `thumbnails`: available public channel fields.
- `normalizedMetadata`: available stable normalized public profile values.
- `statistics.subscriberCount`: available public subscriber count, otherwise unknown.
- `latestVideoPublishedAt`: available derived public latest-upload timestamp, otherwise unknown.
- `heuristics.creatorClassification`: `creator`, `brand`, or `unknown`, inferred only from public signals.
- `heuristics.creatorSignals`: public signals supporting a non-unknown classification.
- `sampleVideos`: bounded public sample collection, included only when requested.
- `fieldProvenance`: public declaration of source-preserved, normalized, and heuristic-inferred fields.

**Relationships**:

- A candidate belongs to exactly one Creator Discovery Request.
- A candidate derives from one or more Matched Videos sharing its `channelId`.
- A candidate references zero or one Channel Enrichment by `channelId`.
- A returned candidate contains zero through `sampleVideosPerChannel` Video Samples.

**Validation Rules**:

- Duplicate `channelId` values resolve to the earliest Matched Video position.
- Missing profile, statistics, activity, and classification data are never fabricated.
- A candidate missing data required by an active filter or non-relevance rank is excluded, rather than treated as qualifying.

## Channel Enrichment

Represents public information conditionally used to evaluate active refinements or ranking.

**Fields**:

- `subscriberCount`: available public count, otherwise unknown.
- `uploadsPlaylistId`: internal public playlist reference used only for latest-activity lookup; never returned as a public enrichment claim.
- `latestVideoPublishedAt`: normalized public activity timestamp, otherwise unknown.
- `creatorClassification` and `creatorSignals`: conservative public-signal heuristic result.
- `availability`: `available`, `unavailable`, or `not_requested` for each enrichment datum.

**Validation Rules**:

- Hidden or missing subscriber counts are not converted to zero.
- Matched-video publication is never substituted for unavailable latest channel activity.
- Creator classification is heuristic-inferred, includes a basis and limitation, and never verifies identity or ownership.

## Video Sample

Represents bounded topic evidence for a returned Creator Candidate.

**Fields**:

- `videoId`, `channelId`, `title`: stable identity and available public title.
- `publishedAt`: included when available.
- `baseSearchPosition`: internal ordering value, never returned directly.

**Validation Rules**:

- Samples belong to a returned candidate only.
- Samples are taken in base video-search order after final candidates are filtered, ranked, and capped.
- The sample count never exceeds the requested `sampleVideosPerChannel` value.

## Partial Enrichment Summary

Represents safe aggregate disclosure after a successful base search where some candidates could not be evaluated for an active rule.

**Fields**:

- `status`: `partial`.
- `excludedCandidateCount`: count of candidates excluded because required enrichment was unavailable.
- `reasons`: safe categories such as unavailable channel metadata, subscriber count, or latest activity.
- `requiredFor`: active filters or ranking rules requiring unavailable information.

**Validation Rules**:

- Contains only counts and safe categories; it contains no credentials, tokens, private owner data, raw source payloads, or stack traces.
- Is included only when an active rule excludes one or more candidates for unavailable required enrichment.
- If every candidate requiring enrichment is unevaluable, the result transitions to `partial_enrichment_failure` rather than an unverified collection.

## Creator Discovery Result Collection

Represents the final MCP-facing result.

**Fields**:

- `items`: ordered collection of final Creator Candidates with public fields only.
- `appliedInputs`: normalized request values applied to the invocation.
- `returnedCount`: number of returned candidates.
- `maxResults`: final channel cap.
- `nextPageToken`: optional base-video-search continuation context; it is not a continuation promise for the final filtered/ranked collection.
- `fieldProvenance`: declarations distinguishing `raw_upstream`, `normalized`, and `heuristic_inferred` output fields.
- `partialEnrichment`: optional Partial Enrichment Summary.

**State Transitions**:

```text
valid request -> bounded base video search -> group by channel -> no enrichment needed -> completed or empty collection
valid request -> bounded base video search -> group by channel -> conditional enrichment -> filter -> rank -> sample -> completed, partial, or empty collection
valid request -> bounded base video search -> required enrichment unavailable for all candidates -> partial_enrichment_failure
valid request -> safe structured error (authorization, quota, upstream, unavailable)
invalid request -> safe structured invalid-parameter error
```
