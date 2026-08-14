# MCP Contract: `channels_listPlaylists`

## Purpose and Compatibility

List publicly accessible playlists for one channel through a stable, source-ordered result. This additive tool changes no existing public schema; no migration is required. Discovery must not mark it `representativeOnly`.

## Input Contract

```json
{
  "type": "object",
  "required": ["channelId"],
  "additionalProperties": false,
  "properties": {
    "channelId": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 25 }
  }
}
```

Input text is trimmed and must remain nonblank. Whole-number validation rejects booleans and non-integers. There is no continuation input; the limit applies only to this bounded listing.

## Composition Boundary

| Aspect | Contract |
| --- | --- |
| Kind | `source_ordered_collection` |
| Dependencies | One public `channels.list` verification followed by one public `playlists.list` request scoped to `channelId`. |
| Request | `snippet,contentDetails,status` with the validated limit. |
| Boundedness | One verification and one listing only; 1–50 records, default 25. |
| Ordering | Preserve usable source order at request time. |
| Ranking | No query matching, ranking, filtering, or generated records. |
| Empty policy | A successful empty source collection for a verified channel returns successful `items: []`; an unavailable channel is a safe error. |

## Successful Result

```json
{
  "channelId": "UC123",
  "items": [{"playlistId": "PL123", "title": "Example playlist", "itemCount": 12}],
  "returnedCount": 1,
  "appliedLimit": 25,
  "appliedInputs": {"channelId": "UC123", "maxResults": 25},
  "collectionContext": {"source": "channel_playlist_collection", "ordering": "source_order_at_request_time", "rankingApplied": false, "publicContentOnly": true, "stateObservedAtRequest": true},
  "fieldProvenance": {"items.playlistId": "raw_upstream", "items.title": "normalized", "channelId": "normalized", "returnedCount": "normalized", "appliedLimit": "normalized", "appliedInputs": "normalized", "collectionContext": "normalized"}
}
```

`description`, `channelId`, `channelTitle`, `publishedAt`, `thumbnails`, `itemCount`, and `privacyStatus` appear in a record only when available. Stable contract fields and field extraction are labeled normalized; source-derived values are labeled `raw_upstream`. Results can change between requests as public channel playlists change.

## Error Contract

Errors use only `invalid_parameters`, `unavailable_resource`, `authorization_sensitive_data`, `quota_exhaustion`, and `upstream_failure`. They provide safe recovery guidance and never disclose credentials, keys, tokens, headers, owner context, stack traces, raw source payloads, signed URLs, or non-public playlist information.

## Discovery Requirements

Metadata must expose the input schema, defaults/bounds, fixed two-read composition, dependencies, public-read/capacity caveats, source ordering, no-ranking rule, field provenance, empty-success semantics, error categories, and caller recovery guidance.
