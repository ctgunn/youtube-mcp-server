# MCP Contract: `playlists_getVideoTranscripts`

## Purpose

Retrieve timestamped transcript outcomes for a bounded, source-ordered set of videos in one YouTube playlist. This is a higher-level composite tool, not a direct endpoint passthrough, transcript generator, translator, playlist-management operation, or unbounded playlist scan.

## Compatibility and Migration

This is an additive public MCP tool. It does not alter an existing public tool name, schema, or result shape, so no client migration is required. Its executable discovery metadata must not include `representativeOnly`.

## Input Contract

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["playlistId"],
  "properties": {
    "playlistId": { "type": "string", "minLength": 1 },
    "language": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
  }
}
```

The tool trims text inputs, validates supplied language tags, rejects unknown fields, and distinguishes whole-number limits from booleans. It accepts no continuation input. `maxResults` limits both the playlist items considered in the one source response and the number of transcript retrieval attempts.

## Language and Composition Boundary

| Aspect | Contract |
| --- | --- |
| Composition kind | `bounded_playlist_transcript_fan_out` |
| Playlist dependency | Exactly one `playlistItems.list` request with `snippet,contentDetails,status`, validated `playlistId`, and applied limit. |
| Transcript dependency | At most one timestamped caption retrieval for each eligible item; no attempt is made for an unavailable playlist item. |
| Language order | Explicit `language`, then configured `YOUTUBE_TRANSCRIPT_LANG`, then `en`. |
| Language matching | Exact normalized language only; no source-default, source-order, other-language, translated, public, or third-party fallback. |
| Boundedness | One playlist response; 1–50 items considered; default 10; zero through the applied-limit number of transcript attempts. |
| Ordering | Preserve source playlist order observed at request time. No ranking, sorting, de-duplication, or filtering. |
| Pagination | No caller continuation input and no traversal beyond the one source response. |
| Authentication | Playlist enumeration uses existing configured public-read capability; caption retrieval uses existing eligible authorized caption access. |
| Cost and latency | Playlist and caption retrieval capacity multiply across the bounded fan-out; callers must use `maxResults` to control work. |
| Partial-result policy | A caption failure for one considered video becomes a safe per-video outcome and does not discard successful results for other videos. |

The tool resolves the language at its own boundary and explicitly supplies it to the timestamped-caption dependency. This avoids changing the dependency's separately established no-language selection behavior.

## Processing Semantics

1. Validate and normalize `playlistId`, optional `language`, and `maxResults`.
2. Resolve one request language using explicit input, configured default, then English.
3. List the playlist once using the applied limit.
4. Preserve the resulting source order. For each item, retain safe public item identity and return `video_unavailable` without attempting captions if no usable video is available.
5. For each eligible video, retrieve timestamped captions once using the resolved exact language.
6. Return `available` or `empty` for successful retrievals; map captionless or requested-language-missing outcomes to `transcript_unavailable`; retain authorization, capacity, source-unavailable, and upstream conditions as safe per-video statuses.
7. Return the item outcomes and fan-out summary. `additionalPlaylistItemsNotAttempted` is true only when the source provides a continuation signal.

The response represents source content observed at request time. It does not promise a historical snapshot, complete playlist coverage beyond the bounded source response, a provider-specific explanation for a successful empty playlist, or the existence of inaccessible captions.

## Successful Result Contract

```json
{
  "playlistId": "PL123",
  "language": "en",
  "languageSource": "configured_default",
  "items": [
    {
      "position": 0,
      "playlistItemId": "playlist-item-123",
      "videoId": "video-123",
      "transcriptStatus": "available",
      "language": "en",
      "languageSource": "configured_default",
      "captionTrackId": "caption-track-123",
      "segments": [
        {
          "text": "Welcome",
          "startTimeSeconds": 0.0,
          "endTimeSeconds": 4.2
        }
      ]
    },
    {
      "position": 1,
      "playlistItemId": "playlist-item-124",
      "videoId": "video-124",
      "transcriptStatus": "transcript_unavailable",
      "safeReason": "No accessible transcript is available in the requested language."
    }
  ],
  "fanOutSummary": {
    "appliedLimit": 10,
    "consideredItemCount": 2,
    "transcriptAttemptCount": 2,
    "outcomeCounts": {
      "available": 1,
      "transcript_unavailable": 1
    },
    "additionalPlaylistItemsNotAttempted": false
  },
  "fieldProvenance": {
    "items.position": "raw_upstream",
    "items.playlistItemId": "raw_upstream",
    "items.videoId": "raw_upstream",
    "items.transcriptStatus": "normalized",
    "items.language": "raw_upstream",
    "items.languageSource": "normalized",
    "items.captionTrackId": "raw_upstream",
    "items.segments.text": "normalized",
    "items.segments.startTimeSeconds": "normalized",
    "items.segments.endTimeSeconds": "normalized",
    "playlistId": "normalized",
    "language": "normalized",
    "languageSource": "normalized",
    "fanOutSummary": "normalized"
  }
}
```

The `items` collection may be empty after a successful empty playlist listing. Optional source fields appear only when available. Successful `empty` outcomes include `segments: []`; failed outcomes omit `segments`, caption-track identity, and transcript text. `language` is the source-declared language on a successful item and the resolved request language at the result level.

## Per-video Outcome Contract

| `transcriptStatus` | Meaning | Caller guidance |
| --- | --- | --- |
| `available` | An exact-language caption track was retrieved with one or more segments. | Consume the returned segments. |
| `empty` | An exact-language caption track was retrieved but contains no textual cues. | Treat as a successful empty transcript. |
| `video_unavailable` | The playlist item has no usable public video identity or is unavailable. | Use a different accessible playlist or video. |
| `transcript_unavailable` | No accessible caption exists, or no exact-language caption exists. | Request an accessible exact language or another video. |
| `authorization_sensitive_data` | Caption access is absent or insufficient for this video. | Obtain eligible caption authorization. |
| `quota_exhaustion` | Caption retrieval cannot proceed because capacity is exhausted. | Retry after capacity is available. |
| `source_unavailable` | Caption source availability prevents retrieval. | Retry when the source is available. |
| `upstream_failure` | Another safe source or parsing failure prevents retrieval. | Retry when the source is available. |

## Whole-request Error Contract

Invalid request and playlist-listing failures produce a safe MCP-compatible error with stable category data and sanitized details.

| Category | When returned | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | Request or configured language is invalid, unsupported, or out of range. | Correct the named input or configuration field and retry. |
| `unavailable_resource` | The requested playlist cannot be listed. | Use a different accessible playlist identifier. |
| `authorization_sensitive_data` | Required access cannot list the playlist. | Obtain appropriate access if applicable. |
| `quota_exhaustion` | Capacity prevents listing the playlist. | Retry after capacity is available. |
| `upstream_failure` | Another source failure prevents playlist listing. | Retry when the source is available. |

Neither whole-request errors nor unsuccessful per-video outcomes may include transcript text, caption bytes, credentials, tokens, protected metadata, raw source bodies, signed URLs, or stack traces.

## Discovery Metadata Requirements

The executable descriptor must expose the public schema; playlist-transcript fan-out composition kind; `playlistItems.list`, `captions.list`, and `captions.download` dependencies; default/minimum/maximum limit and no-continuation policy; one-page and at-most-one-attempt-per-eligible-item bounds; source-order policy; explicit/configured/English language order and exact-match rule; mixed credential and capacity caveats; response field provenance; per-video partial-result and empty-result policies; fan-out summary semantics; safe error categories; recovery guidance; and no unsafe or representative-only metadata keys.
