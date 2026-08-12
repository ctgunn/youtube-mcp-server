# MCP Contract: `channels_listVideos`

## Purpose

List publicly available videos for one known YouTube channel through a stable, source-ordered MCP result. This is a higher-level composed tool: it resolves the channel's public uploads collection and lists that collection. It is not keyword search and does not rank results by relevance.

## Compatibility and Migration

This is an additive public MCP tool. It does not alter an existing public tool name, schema, or result shape, so no client migration is required. Discovery metadata must not include `representativeOnly`.

## Input Contract

```json
{
  "type": "object",
  "required": ["channelId"],
  "additionalProperties": false,
  "properties": {
    "channelId": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
  }
}
```

The tool additionally enforces trimmed nonblank text and distinguishes whole-number values from booleans. It accepts no continuation input: `maxResults` applies only to the current bounded listing.

## Composition Boundary

| Aspect | Contract |
| --- | --- |
| Kind | `source_ordered_collection` |
| Channel dependency | One public channel lookup to resolve the available uploads collection reference. |
| Collection dependency | At most one public uploads-collection item listing using the validated result limit. |
| Boundedness | One channel lookup and at most one collection listing; 1–50 returned distinct items, default 10. |
| Ordering | Preserve usable uploads-collection order observed at request time, retain the first occurrence of a duplicate video identity, then apply the final cap. |
| Ranking | No query matching, relevance ranking, or other reordering is applied. |
| Authentication | Uses configured public-read capability only; no owner-scoped data is requested. |
| Quota caveat | Both bounded lower-layer reads consume available public-read capacity and can fail when capacity is exhausted. |
| Partial-result policy | A missing uploads reference or successful empty source collection is a successful empty result. A failed required collection read is a whole-request error. Known item-level omissions after a successful collection response are disclosed only as safe aggregate partial availability. |

## Processing Semantics

1. Validate and normalize `channelId` and `maxResults`.
2. Resolve the requested channel's public uploads collection reference.
3. If no usable reference is available, return a successful empty collection.
4. List the uploads collection once using the applied `maxResults`.
5. Iterate returned items without sorting; omit items lacking a usable video identifier; retain the first usable occurrence of every video identifier.
6. Apply the final `maxResults` cap after de-duplication.
7. Return the ordered public items, normalized request and collection context, counts, field provenance, and safe partial-availability context when applicable.

The response represents public content available at request time. A later request can legitimately differ because a channel's public uploads collection can change. The tool does not promise chronological newest-first ordering, historical snapshots, or final-result pagination.

## Successful Result Contract

```json
{
  "channelId": "UC123",
  "items": [
    {
      "videoId": "video-123",
      "title": "Example video",
      "description": "Available public description",
      "publishedAt": "2026-03-01T12:00:00Z",
      "thumbnails": { "medium": "https://example.invalid/thumbnail" }
    }
  ],
  "returnedCount": 1,
  "maxResults": 10,
  "appliedInputs": { "channelId": "UC123", "maxResults": 10 },
  "collectionContext": {
    "source": "channel_uploads_collection",
    "ordering": "source_order_at_request_time",
    "rankingApplied": false,
    "publicContentOnly": true,
    "requestTimeVariability": "collection_can_change"
  },
  "fieldProvenance": {
    "items.videoId": "raw_upstream",
    "items.title": "raw_upstream",
    "items.description": "raw_upstream",
    "items.publishedAt": "raw_upstream",
    "items.thumbnails": "raw_upstream",
    "channelId": "normalized",
    "returnedCount": "normalized",
    "maxResults": "normalized",
    "appliedInputs": "normalized",
    "collectionContext": "normalized"
  }
}
```

Optional item fields appear only when publicly available. A channel with no publicly available uploads returns `items: []` and `returnedCount: 0`; it is not an unavailable-resource error. `partialAvailability`, when applicable, contains safe aggregate status and never identifies inaccessible individual content.

`partialAvailability` has `status: "partial"` and includes only safely determinable aggregate omission count and reason values. A failed required collection lookup remains a whole-request error rather than a partial result.

## Field Provenance and Ordering Disclosure

| Field or group | Provenance | Caller guidance |
| --- | --- | --- |
| `items.videoId`, `items.title`, `items.description`, `items.publishedAt`, `items.thumbnails` | `raw_upstream` | Available public values preserve their source meaning; absent optional values are not fabricated. |
| `channelId`, `returnedCount`, `maxResults`, `appliedInputs`, `collectionContext` | `normalized` | Stable contract context derived from validated input and the bounded collection result. |
| Item sequence | `normalized` ordering rule | Preserves usable uploads-collection order at request time after first-occurrence de-duplication and final cap; it is not relevance-ranked or guaranteed chronological. |
| `partialAvailability` | `normalized` | Safe aggregate completeness context only; it never exposes inaccessible item identity or sensitive source detail. |

Use a search-oriented tool when keyword matching or relevance-ranked discovery is required; this tool lists only publicly available videos in the uploads collection observed for the request.

## Error Contract

The tool returns safe MCP-compatible errors with a stable category and sanitized details. It never exposes credentials, keys, tokens, stack traces, raw request or response bodies, signed URLs, private owner context, or non-public video data.

| Category | When returned | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | Request shape, field type, blank identifier, or result-limit validation fails. | Correct the identified field and retry. |
| `unavailable_resource` | The requested channel cannot be publicly listed. | Use a different accessible channel identifier. |
| `authorization_sensitive_data` | Configured public access cannot retrieve a required lookup. | Obtain appropriate public-read capability if applicable. |
| `quota_exhaustion` | A required lower-layer lookup cannot proceed because available capacity is exhausted. | Retry after capacity is available. |
| `upstream_failure` | A required lower-layer service fails for another reason. | Retry when the source service is available. |

## Discovery Metadata Requirements

The executable descriptor must expose the public input schema; default and bounds; `source_ordered_collection` composition boundary; `channels.list` and `playlistItems.list` dependencies; public-read and capacity caveats; one-channel/two-read boundedness; no-ranking and request-time ordering semantics; source-versus-normalized field provenance; empty and partial-availability policies; safe error categories; and recovery guidance. It must not expose representative-only markers or unsafe metadata keys.
