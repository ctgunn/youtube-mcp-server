# MCP Contract: `channels_searchChannels`

## Purpose

Search publicly discoverable channels by handle, channel name, or general query and, when requested, refine and rank the result collection using available public channel metadata and derived public latest activity.

## Compatibility and Migration

This is an additive public MCP tool. It does not alter an existing public tool name, schema, or result shape, and no client migration is required. The supporting lower-level `channelType` field is an additive optional field. Discovery metadata must not include `representativeOnly`.

## Input Contract

```json
{
  "type": "object",
  "required": ["query"],
  "additionalProperties": false,
  "properties": {
    "query": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 },
    "order": { "type": "string", "enum": ["date", "relevance", "title", "videoCount"] },
    "channelType": { "type": "string", "enum": ["any", "show"] },
    "minSubscribers": { "type": "integer", "minimum": 0 },
    "maxSubscribers": { "type": "integer", "minimum": 0 },
    "lastUploadAfter": { "type": "string", "format": "date-time" },
    "lastUploadBefore": { "type": "string", "format": "date-time" },
    "creatorOnly": { "type": "boolean", "default": false },
    "sortBy": {
      "type": "string",
      "enum": ["relevance", "subscribers_asc", "subscribers_desc", "indie_priority", "recent_activity"],
      "default": "relevance"
    }
  }
}
```

The tool additionally enforces trimmed non-blank text, explicit-timezone ISO 8601 timestamps, paired date-window ordering, subscriber-bound ordering, and strict boolean/whole-number distinctions.

## Composition Boundary

| Aspect | Contract |
|--------|----------|
| Kind | `ranked_enrichment` |
| Base dependency | `search.list`, restricted to `type=channel` |
| Channel dependency | Conditional `channels.list` request for public profile, statistics, and uploads-playlist metadata |
| Latest-activity dependency | Conditional public uploads-playlist read for each enriched candidate, bounded by base candidates |
| Boundedness | 1–50 final items; no more than 50 distinct base candidates or enrichments; at most one uploads-playlist item per distinct candidate, and only when latest-upload filtering or recent-activity ranking is requested |
| Authentication | Configured public read capability; no owner-scoped data is requested |
| Quota caveat | Base search is quota-intensive; conditional channel and activity enrichment add bounded lower-layer calls and can exhaust available quota |
| Partial-result policy | Retain a candidate with unavailable enrichment only when no active rule needs that datum; otherwise exclude it and disclose partial enrichment |

## Processing Semantics

1. Validate and normalize the request.
2. Retrieve base channel candidates with the selected base constraints.
3. Normalize valid channel identifiers and de-duplicate them, preserving earliest base-search position.
4. Conditionally enrich candidates only when an active filter or ranking requires public channel metadata or latest activity.
5. Exclude candidates whose unavailable enrichment prevents evaluation of an active rule.
6. Apply all selected filters.
7. Apply the selected final ranking; every tie preserves base-search order.
8. Apply the final `maxResults` cap.

### Filter Semantics

- Subscriber and latest-upload boundaries are inclusive.
- `creatorOnly=true` accepts only the positive `creator` result of the disclosed public-signal heuristic.
- Unknown, hidden, or unavailable data never satisfies a data-dependent filter.

### Ranking Semantics

| `sortBy` | Behavior |
|----------|----------|
| `relevance` | Preserve base-search order after filtering. |
| `subscribers_asc` | Smallest available qualifying subscriber count first. |
| `subscribers_desc` | Largest available qualifying subscriber count first. |
| `indie_priority` | Creator-like channels first, then smaller available subscriber counts; classification is heuristic. |
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
      "normalizedMetadata": {
        "customUrl": "@channel",
        "joinedAt": "2020-01-01T00:00:00Z"
      },
      "statistics": { "subscriberCount": "5000" },
      "latestVideoPublishedAt": "2026-03-01T12:00:00Z",
      "heuristics": { "creatorClassification": "creator", "creatorSignals": ["public_creator_term"] }
    }
  ],
  "appliedInputs": { "query": "example", "maxResults": 10, "creatorOnly": false, "sortBy": "relevance" },
  "returnedCount": 1,
  "maxResults": 10,
  "nextPageToken": "optional-base-search-continuation-token",
  "fieldProvenance": {
    "channelId": "raw_upstream",
    "title": "raw_upstream",
    "normalizedMetadata.customUrl": "normalized",
    "statistics.subscriberCount": "raw_upstream",
    "latestVideoPublishedAt": "normalized",
    "heuristics.creatorClassification": "heuristic_inferred"
  },
  "partialEnrichment": {
    "status": "partial",
    "excludedCandidateCount": 1,
    "reasons": ["channel_metadata_unavailable"],
    "requiredFor": ["minSubscribers"]
  }
}
```

Optional public fields, continuation context, enrichment values, and `partialEnrichment` are included only when available or applicable. A valid request with no matching or qualifying candidates returns `items: []` and `returnedCount: 0`. `nextPageToken`, when present, continues the base search and does not claim pagination over the final filtered/ranked collection.

## Field Provenance and Heuristic Disclosure

| Field or group | Provenance | Caller guidance |
|----------------|------------|-----------------|
| `channelId`, `title`, `description`, `thumbnails` | `raw_upstream` | Available public fields preserved from the base search result. |
| `normalizedMetadata` | `normalized` | Stable public fields normalized from available channel profile data. |
| `statistics.subscriberCount` | `raw_upstream` | Present only when public channel statistics expose a count. |
| `latestVideoPublishedAt` | `normalized` | Derived from one conditional public uploads-playlist read; unavailable activity is never fabricated. |
| `heuristics.creatorClassification` and `creatorSignals` | `heuristic_inferred` | Conservative public-signal inference; can be incomplete or incorrect and never verifies identity or ownership. |
| `indie_priority` ordering | `heuristic_inferred` | A documented research ordering aid, not a statement of source authority, quality, or channel independence. |

## Error Contract

The tool returns safe MCP-compatible errors with a stable category and sanitized details. It never exposes credentials, keys, tokens, stack traces, raw request/response bodies, signed URLs, or private owner context.

| Category | When returned | Caller guidance |
|----------|---------------|-----------------|
| `invalid_parameters` | Request shape, field type, enum, bounds, or paired-window validation fails | Correct the identified field and retry. |
| `unsupported_filter_or_sort` | A requested public refinement cannot be applied | Use a documented supported value or combination. |
| `unavailable_resource` | Required public channel data is unavailable or hidden | Use a different accessible query or relax the affected refinement. |
| `authorization_sensitive_data` | Configured public access cannot retrieve required data | Use permitted public data or obtain the necessary capability. |
| `quota_exhaustion` | A lower-layer request cannot proceed because available quota is exhausted | Retry after capacity is available. |
| `upstream_failure` | A lower-layer service fails for another reason | Retry when the source service is available. |
| `partial_enrichment_failure` | Base search succeeds but no candidate can be evaluated for a required enrichment-dependent rule | Relax the rule or retry when public metadata is available. |

## Discovery Metadata Requirements

The executable descriptor must expose the public input schema and metadata for its composition boundary, lower-layer dependencies, public-access and quota caveats, boundedness, field provenance, all filtering/ranking rules, heuristic limitations, continuation caveat, partial-result policy, safe error categories, and error guidance. It must not expose representative-only markers or unsafe metadata keys.
