# MCP Contract: `playlists_getPlaylistItems`

## Purpose

List the entries exposed by one known YouTube playlist through a stable, source-ordered MCP result. This is a higher-level composed tool that normalizes one playlist-item listing for research clients; it is not raw endpoint passthrough, playlist management, pagination traversal, search, ranking, transcript retrieval, or video enrichment.

## Compatibility and Migration

This is an additive public MCP tool. It does not alter an existing public tool name, schema, or result shape, so no client migration is required. Discovery metadata must not include `representativeOnly`.

## Input Contract

```json
{
  "type": "object",
  "required": ["playlistId"],
  "additionalProperties": false,
  "properties": {
    "playlistId": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 25 }
  }
}
```

The tool additionally enforces trimmed nonblank text and distinguishes whole-number limits from booleans. It accepts no continuation input: `maxResults` applies only to the one bounded listing performed for this call.

## Composition Boundary

| Aspect | Contract |
| --- | --- |
| Kind | `source_ordered_collection` |
| Dependency | Exactly one public `playlistItems.list` request. |
| Request | `snippet,contentDetails,status` detail groups, the validated playlist identifier, and the applied limit. |
| Boundedness | One playlist, one listing, and 1–50 returned entries; default 25. |
| Ordering | Preserve source playlist order observed at request time. No ranking, sorting, de-duplication, or filtering is applied. |
| Pagination | No caller continuation input and no traversal beyond the one source response. |
| Authentication | Uses configured public-read capability only; no owner-scoped data is requested. |
| Quota caveat | The one required lower-layer read consumes available public-read capacity and can fail when capacity is exhausted. |
| Empty-result policy | A source response that successfully contains no entries is a successful empty collection. |
| Unavailable-entry policy | Preserve every exposed entry in source order; mark entries without usable public video details or with an unavailable source indication as unavailable, without fabricating fields. |

## Processing Semantics

1. Validate and normalize `playlistId` and `maxResults`.
2. List the requested playlist once using the required detail groups and applied limit.
3. Translate a lower-layer failure to a safe whole-request outcome.
4. For each returned source item, retain its order and map available public position, playlist-item identity, video identity, title, channel identity, and publication time.
5. Label each item as available or unavailable from safely exposed source information; preserve unavailable entries rather than dropping them.
6. Return the normalized item collection, count, applied limit, source-signaled limited indicator, provenance, and collection context.

The response represents source content observed at request time. It does not promise historical snapshots, a complete playlist beyond the one response, chronological ordering, relevance ranking, or a provider-specific explanation for a successful empty response.

## Successful Result Contract

```json
{
  "playlistId": "PL123",
  "items": [
    {
      "position": 0,
      "playlistItemId": "playlist-item-123",
      "videoId": "video-123",
      "title": "Example video",
      "channelId": "UC123",
      "channelTitle": "Example channel",
      "publishedAt": "2026-03-01T12:00:00Z",
      "availabilityState": "available"
    },
    {
      "position": 1,
      "availabilityState": "unavailable"
    }
  ],
  "returnedCount": 2,
  "appliedLimit": 25,
  "isLimited": false,
  "collectionContext": {
    "source": "playlist_items",
    "ordering": "source_playlist_order_at_request_time",
    "rankingApplied": false,
    "paginationTraversed": false,
    "publicContentOnly": true,
    "requestTimeVariability": "playlist_can_change"
  },
  "fieldProvenance": {
    "items.position": "raw_upstream",
    "items.playlistItemId": "raw_upstream",
    "items.videoId": "raw_upstream",
    "items.title": "raw_upstream",
    "items.channelId": "raw_upstream",
    "items.channelTitle": "raw_upstream",
    "items.publishedAt": "raw_upstream",
    "items.availabilityState": "normalized",
    "playlistId": "normalized",
    "returnedCount": "normalized",
    "appliedLimit": "normalized",
    "isLimited": "normalized",
    "collectionContext": "normalized"
  }
}
```

Optional item fields appear only when publicly available. A successfully returned empty source collection contains `items: []`, `returnedCount: 0`, and `isLimited: false`. `isLimited` becomes true only when the source response provides a safe continuation signal; it is not inferred merely because `returnedCount` equals `appliedLimit`.

## Field Provenance and Availability Disclosure

| Field or group | Provenance | Caller guidance |
| --- | --- | --- |
| `items.position`, `items.playlistItemId`, `items.videoId`, `items.title`, `items.channelId`, `items.channelTitle`, `items.publishedAt` | `raw_upstream` | Available public values preserve their source meaning; absent optional values are not fabricated. |
| `items.availabilityState` | `normalized` | Identifies whether the exposed playlist entry has usable public video details. |
| `playlistId`, `returnedCount`, `appliedLimit`, `isLimited`, `collectionContext` | `normalized` | Stable context derived from validated input and one bounded source listing. |
| Item sequence | `normalized` ordering rule | Preserves exposed source playlist order at request time; it is not relevance-ranked, sorted, de-duplicated, or guaranteed immutable. |

Use a search-oriented tool for keyword matching or relevance-ranked discovery. Use a transcript-oriented tool to retrieve captions. This tool lists only the exposed entries in one playlist response.

## Error Contract

The tool returns safe MCP-compatible errors with a stable category and sanitized details. It never exposes credentials, keys, tokens, stack traces, raw request or response bodies, signed URLs, private owner context, or non-public video data.

| Category | When returned | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | Request shape, field type, blank identifier, unknown field, or result-limit validation fails. | Correct the identified field and retry. |
| `unavailable_resource` | The lower-layer source reports that the requested playlist cannot be returned. | Use a different accessible playlist identifier. |
| `authorization_sensitive_data` | Configured public access cannot retrieve the required listing. | Obtain appropriate public-read capability if applicable. |
| `quota_exhaustion` | The required listing cannot proceed because available capacity is exhausted. | Retry after capacity is available. |
| `upstream_failure` | The source service fails for another reason. | Retry when the source service is available. |

An empty successful collection is not an error and does not disclose or infer a provider-specific availability cause.

## Discovery Metadata Requirements

The executable descriptor must expose the public schema; default and bounds; `source_ordered_collection` composition boundary; `playlistItems.list` as its sole lower-layer dependency; public-read and capacity caveats; one-playlist/one-read boundedness; source-order and no-ranking semantics; source-versus-normalized field provenance; empty, unavailable-entry, and limited-result policies; safe error categories; and recovery guidance. It must not expose representative-only markers or unsafe metadata keys.
