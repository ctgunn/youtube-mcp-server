# MCP Contract: `videos_searchVideos`

## Purpose

Search publicly discoverable YouTube videos and, when requested, refine and rank the result set using public channel metadata and derived public latest-activity information.

## Compatibility and Migration

This is an additive public MCP tool. It does not alter any existing tool name, schema, or result shape; no client migration is required. Discovery metadata must not include `representativeOnly`.

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
    "publishedAfter": { "type": "string", "format": "date-time" },
    "publishedBefore": { "type": "string", "format": "date-time" },
    "channelId": { "type": "string", "minLength": 1 },
    "uniqueChannels": { "type": "boolean", "default": false },
    "channelMinSubscribers": { "type": "integer", "minimum": 0 },
    "channelMaxSubscribers": { "type": "integer", "minimum": 0 },
    "channelLastUploadAfter": { "type": "string", "format": "date-time" },
    "channelLastUploadBefore": { "type": "string", "format": "date-time" },
    "creatorOnly": { "type": "boolean", "default": false },
    "sortBy": {
      "type": "string",
      "enum": ["relevance", "subscribers_asc", "subscribers_desc", "indie_priority", "recent_activity"],
      "default": "relevance"
    }
  }
}
```

The handler additionally enforces trimmed non-blank text, explicit-timezone ISO 8601 timestamps, paired date-window ordering, subscriber-bound ordering, and strict boolean/integer distinctions.

## Composition Boundary

| Aspect | Contract |
|--------|----------|
| Kind | `ranked_enrichment` |
| Base dependency | `search.list`, restricted to `type=video` |
| Channel dependency | Conditional `channels.list` for public channel metadata |
| Latest-activity dependency | Conditional `playlistItems.list` read of each enriched channel's public uploads playlist, bounded by base candidates |
| Boundedness | 1–50 final items; at most 50 distinct candidate channels are enriched; one additional uploads-playlist lookup per distinct channel only when latest-upload filtering or recent-activity ranking is requested |
| Authentication | Public configured API-key capability for supported public search/channel lookups; no owner-scoped data is requested |
| Quota caveat | Base search has documented search quota; channel and conditional latest-activity enrichment add lower-layer calls and may exhaust available quota |
| Partial-result policy | Keep candidates with unavailable enrichment only when no active rule requires it; otherwise exclude and disclose partial enrichment |

## Processing Semantics

1. Validate and normalize the request.
2. Retrieve base video candidates.
3. Conditionally enrich distinct channel IDs only when required by selected filters or ranking.
4. Exclude candidates whose missing enrichment prevents evaluation of an active channel rule.
5. Apply all selected filters.
6. Apply the selected final ranking; every tie preserves base-search order.
7. If `uniqueChannels=true`, keep the first ranked candidate for each distinct channel.
8. Apply the final `maxResults` cap.

### Filter Semantics

- Publication and latest-upload date boundaries are inclusive.
- Subscriber limits are inclusive.
- `creatorOnly=true` accepts only the positive `creator` result of the disclosed conservative public-metadata heuristic.
- Unknown/hidden data never satisfies a data-dependent filter.

### Ranking Semantics

| `sortBy` | Behavior |
|----------|----------|
| `relevance` | Preserve base-search order after filtering. |
| `subscribers_asc` | Smallest available qualifying subscriber count first. |
| `subscribers_desc` | Largest available qualifying subscriber count first. |
| `indie_priority` | Positive creator classifications with smaller available subscriber counts first; classification is heuristic. |
| `recent_activity` | More recent available derived public latest-upload activity first. |

Any candidate lacking the value needed for a non-relevance ranking is excluded and included only in safe partial-enrichment aggregate information.

## Successful Result Contract

```json
{
  "items": [
    {
      "videoId": "abc123",
      "title": "Video title",
      "description": "Video description",
      "publishedAt": "2026-01-15T12:00:00Z",
      "channelId": "UC123",
      "channelTitle": "Channel title",
      "thumbnails": { "medium": "https://example.invalid/thumbnail" },
      "channel": {
        "subscriberCount": "5000",
        "latestVideoPublishedAt": "2026-03-01T12:00:00Z",
        "creatorClassification": "creator"
      }
    }
  ],
  "appliedInputs": { "query": "example", "maxResults": 10, "sortBy": "relevance" },
  "returnedCount": 1,
  "maxResults": 10,
  "nextPageToken": "optional-continuation-token",
  "fieldProvenance": {
    "videoId": "raw_upstream",
    "title": "normalized",
    "channel.subscriberCount": "raw_upstream",
    "channel.latestVideoPublishedAt": "normalized",
    "channel.creatorClassification": "heuristic_inferred"
  },
  "partialEnrichment": {
    "status": "partial",
    "excludedCandidateCount": 1,
    "reasons": ["channel_metadata_unavailable"],
    "requiredFor": ["channelMinSubscribers"]
  }
}
```

`description`, thumbnails, channel enrichment, continuation, and `partialEnrichment` are included only when available or applicable. A valid request with no matching or qualifying candidates returns a successful result with `items: []` and `returnedCount: 0`.

## Field Provenance and Heuristic Disclosure

| Field or group | Provenance | Caller guidance |
|----------------|------------|-----------------|
| `videoId` | `raw_upstream` | Identifier supplied by the base video search result. |
| Core video fields | `normalized` | Stable names derived from public base-search result metadata. |
| `channel.subscriberCount` | `raw_upstream` | Present only when public channel statistics expose it. |
| `channel.latestVideoPublishedAt` | `normalized` | Derived from a conditional public uploads-playlist read; unavailable activity is never fabricated. |
| `channel.creatorClassification` | `heuristic_inferred` | A conservative positive-only classification based on documented public channel signals; it can be incomplete or incorrect and must not be treated as an official channel type. |
| Final ranking | `heuristic_inferred` when it uses creator or latest-activity data | It is a documented ordering aid, not a statement of source authority or quality. |

## Error Contract

The tool must return safe MCP-compatible errors with a stable category and sanitized details. It must never expose credentials, API keys, tokens, stack traces, raw request/response bodies, or signed URLs.

| Category | When returned | Caller guidance |
|----------|---------------|-----------------|
| `invalid_parameters` | Request shape, field type, enum, bounds, or paired-window validation fails | Correct the named field and retry. |
| `unsupported_filter_or_sort` | A requested public filter/sort cannot be applied | Use a documented supported value or combination. |
| `unavailable_resource` | Required public video/channel data is unavailable or hidden | Use a different accessible query or channel constraint. |
| `authorization_sensitive_data` | Configured public access cannot retrieve required data | Use permitted public data or obtain the necessary capability. |
| `quota_exhaustion` | A lower-layer request cannot proceed because available quota is exhausted | Retry after capacity is available. |
| `upstream_failure` | A lower-layer service fails for another reason | Retry when the source service is available. |
| `partial_enrichment_failure` | Base search succeeds but no candidate can be evaluated for a required channel-aware rule | Relax the enrichment-dependent rule or retry when public metadata is available. |

## Discovery Metadata Requirements

The executable descriptor must expose the public input schema and metadata for the composition boundary, lower-layer dependencies, auth/quota caveats, boundedness, field provenance, all ranking/filtering rules, creator-heuristic limitations, partial-result policy, safe error categories, and error guidance. It must not expose representative-only markers or unsafe metadata keys.
