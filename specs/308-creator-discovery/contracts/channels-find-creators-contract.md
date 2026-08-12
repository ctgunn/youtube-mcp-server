# MCP Contract: `channels_findCreators`

## Purpose

Discover publicly visible creator-channel candidates from videos matching a topic, then optionally enrich, filter, rank, and provide bounded topic-matching video samples for each returned channel.

## Compatibility and Migration

This is an additive public MCP tool. It does not alter any existing public tool name, schema, or result shape, so no client migration is required. Discovery metadata must not include `representativeOnly`.

## Input Contract

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["query"],
  "properties": {
    "query": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 },
    "order": { "type": "string", "enum": ["date", "rating", "relevance", "title", "viewCount"] },
    "videoPublishedAfter": { "type": "string", "format": "date-time" },
    "videoPublishedBefore": { "type": "string", "format": "date-time" },
    "channelMinSubscribers": { "type": "integer", "minimum": 0 },
    "channelMaxSubscribers": { "type": "integer", "minimum": 0 },
    "channelLastUploadAfter": { "type": "string", "format": "date-time" },
    "channelLastUploadBefore": { "type": "string", "format": "date-time" },
    "creatorOnly": { "type": "boolean", "default": false },
    "sortBy": {
      "type": "string",
      "enum": ["relevance", "subscribers_asc", "subscribers_desc", "indie_priority", "recent_activity"],
      "default": "relevance"
    },
    "sampleVideosPerChannel": { "type": "integer", "minimum": 0, "maximum": 10, "default": 0 }
  }
}
```

The handler additionally enforces trimmed non-blank text, explicit-timezone ISO 8601 timestamps, paired date-window ordering, subscriber-bound ordering, and strict boolean/whole-number distinctions.

## Composition Boundary

| Aspect | Contract |
|--------|----------|
| Kind | `ranked_enrichment` |
| Base dependency | `search.list`, restricted to `type=video` |
| Candidate derivation | Group topic-matching public videos by public owning-channel identifier; preserve the earliest base-video position per channel |
| Channel dependency | Conditional `channels.list` request for public profile, statistics, and uploads-playlist metadata |
| Latest-activity dependency | Conditional public uploads-playlist read for each enriched candidate, bounded by distinct candidates |
| Boundedness | At most 50 base video candidates and 50 distinct channel candidates; 1–50 final channels; at most one uploads-playlist item per enriched channel for an activity rule; 0–10 samples per final channel |
| Authentication | Configured public read capability; no owner-scoped data is requested |
| Quota caveat | Video search is quota-intensive; conditional channel and activity enrichment add bounded lower-layer calls and can exhaust available quota |
| Partial-result policy | Retain a candidate with unavailable enrichment only when no active rule needs that datum; otherwise exclude it and disclose partial enrichment |

## Processing Semantics

1. Validate and normalize the request.
2. Retrieve a bounded collection of up to 50 base video candidates using the selected base constraints.
3. Normalize usable matched videos and group them by channel identifier, preserving each candidate's earliest base-video position and ordered matching-video collection.
4. Conditionally enrich candidates only when an active filter or ranking requires public channel metadata or latest activity.
5. Exclude candidates whose unavailable enrichment prevents evaluation of an active rule.
6. Apply all selected filters.
7. Apply the selected final ranking; every tie preserves earliest base-video position.
8. Apply the final `maxResults` channel cap.
9. For each final candidate, include up to `sampleVideosPerChannel` matching videos in that candidate's base-video order.

### Filter Semantics

- Video-publication, subscriber, and latest-upload date boundaries are inclusive.
- `creatorOnly=true` accepts only the positive `creator` result of the disclosed public-signal heuristic.
- Unknown, hidden, or unavailable data never satisfies a data-dependent filter.
- A matched video's publication time is not a substitute for latest public channel activity.

### Ranking Semantics

| `sortBy` | Behavior |
|----------|----------|
| `relevance` | Preserve earliest base-video order after filtering. |
| `subscribers_asc` | Smallest available qualifying subscriber count first. |
| `subscribers_desc` | Largest available qualifying subscriber count first. |
| `indie_priority` | Positive creator classifications with smaller available subscriber counts first; classification is heuristic. |
| `recent_activity` | More recent available derived public latest-upload activity first. |

Any candidate lacking the value needed for a non-relevance ranking is excluded and represented only in safe partial-enrichment aggregate information.

## Successful Result Contract

```json
{
  "items": [
    {
      "channelId": "UC123",
      "title": "Channel name",
      "description": "Public channel description",
      "thumbnails": { "medium": "https://example.invalid/channel-thumbnail" },
      "matchedVideoBasis": { "count": 3, "firstVideoId": "abc123" },
      "normalizedMetadata": { "customUrl": "@channel", "joinedAt": "2020-01-01T00:00:00Z" },
      "statistics": { "subscriberCount": "5000" },
      "latestVideoPublishedAt": "2026-03-01T12:00:00Z",
      "heuristics": { "creatorClassification": "creator", "creatorSignals": ["public_creator_term"] },
      "sampleVideos": [
        { "videoId": "abc123", "channelId": "UC123", "title": "Topic video", "publishedAt": "2026-02-01T12:00:00Z" }
      ]
    }
  ],
  "appliedInputs": { "query": "example", "maxResults": 10, "creatorOnly": false, "sortBy": "relevance", "sampleVideosPerChannel": 0 },
  "returnedCount": 1,
  "maxResults": 10,
  "nextPageToken": "optional-base-video-search-continuation-token",
  "fieldProvenance": {
    "channelId": "raw_upstream",
    "matchedVideoBasis": "normalized",
    "statistics.subscriberCount": "raw_upstream",
    "latestVideoPublishedAt": "normalized",
    "heuristics.creatorClassification": "heuristic_inferred",
    "sampleVideos": "normalized"
  },
  "partialEnrichment": {
    "status": "partial",
    "excludedCandidateCount": 1,
    "reasons": ["channel_metadata_unavailable"],
    "requiredFor": ["channelMinSubscribers"]
  }
}
```

Optional public fields, samples, continuation context, enrichment values, and `partialEnrichment` are included only when available or applicable. A valid request with no matching or qualifying candidates returns `items: []` and `returnedCount: 0`. `nextPageToken`, when present, continues only the base video search and does not paginate the final filtered/ranked collection.

## Field Provenance and Heuristic Disclosure

| Field or group | Provenance | Caller guidance |
|----------------|------------|-----------------|
| `channelId` and matched-video identifiers | `raw_upstream` | Public identities supplied by matching video search results. |
| `matchedVideoBasis` and `sampleVideos` grouping | `normalized` | Stable grouping and bounded sample selection from matching videos in base order. |
| Core channel fields | `raw_upstream` | Available public channel fields preserved from base video search or public channel enrichment. |
| `normalizedMetadata` | `normalized` | Stable public fields normalized from available channel profile data. |
| `statistics.subscriberCount` | `raw_upstream` | Present only when public channel statistics expose a count. |
| `latestVideoPublishedAt` | `normalized` | Derived from one conditional public uploads-playlist read; unavailable activity is never fabricated. |
| `heuristics.creatorClassification` and `creatorSignals` | `heuristic_inferred` | Conservative public-signal inference; can be incomplete or incorrect and never verifies identity, ownership, or independence. |
| `indie_priority` ordering | `heuristic_inferred` | A documented research ordering aid, not a statement of source authority, quality, or channel independence. |

## Error Contract

The tool returns safe MCP-compatible errors with a stable category and sanitized details. It never exposes credentials, API keys, tokens, stack traces, raw request/response bodies, signed URLs, or private owner context.

| Category | When returned | Caller guidance |
|----------|---------------|-----------------|
| `invalid_parameters` | Request shape, field type, enum, bounds, or paired-window validation fails | Correct the identified field and retry. |
| `unsupported_filter_or_sort` | A requested public refinement cannot be applied | Use a documented supported value or combination. |
| `unavailable_resource` | Required public video or channel data is unavailable or hidden | Use a different accessible query or relax the affected refinement. |
| `authorization_sensitive_data` | Configured public access cannot retrieve required data | Use permitted public data or obtain the necessary capability. |
| `quota_exhaustion` | A lower-layer request cannot proceed because available quota is exhausted | Retry after capacity is available. |
| `upstream_failure` | A lower-layer service fails for another reason | Retry when the source service is available. |
| `partial_enrichment_failure` | Base search succeeds but no candidate can be evaluated for a required enrichment-dependent rule | Relax the rule or retry when public metadata is available. |

## Discovery Metadata Requirements

The executable descriptor must expose the public input schema and metadata for its composition boundary, video-derived candidate grouping, sample bounds/order, lower-layer dependencies, public-access and quota caveats, boundedness, field provenance, filtering/ranking rules, creator-heuristic limitations, continuation caveat, partial-result policy, safe error categories, and error guidance. It must not expose representative-only markers or unsafe metadata keys.
