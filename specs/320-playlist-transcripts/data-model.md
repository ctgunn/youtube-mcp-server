# Data Model: YT-320 Playlist Video Transcript Aggregation

## Playlist Video Transcript Request

Represents one public `playlists_getVideoTranscripts` invocation.

**Fields**:

- `playlistId`: required, trimmed, non-empty identifier for exactly one playlist.
- `language`: optional, trimmed language tag supplied by the caller.
- `maxResults`: optional whole-number cap from 1 through 50; defaults to 10.

**Validation Rules**:

- No unknown fields are accepted.
- `playlistId` must be text and remain non-empty after trimming.
- A supplied `language` must be a valid language tag after harmless case normalization.
- `maxResults` must be an integer, not a boolean, fraction, string, zero, negative number, or value above 50.
- Invalid input creates a safe `invalid_parameters` outcome before playlist listing begins.

## Resolved Playlist Language

Represents the one language forwarded to every eligible video transcript attempt.

**Fields**:

- `language`: normalized language tag.
- `languageSource`: one of `explicit`, `configured_default`, or `english_fallback`.

**State Transitions**:

```text
explicit request -> explicit
no explicit request + valid configured default -> configured_default
no explicit request + no configured default -> english_fallback (en)
invalid explicit input or configured default -> safe invalid_parameters outcome
```

## Playlist Video Transcript Outcome

Represents the source-ordered result for one playlist item considered by the request.

**Common Fields**:

- `playlistItemId`: source playlist-item identifier when publicly available.
- `videoId`: source video identifier when publicly available.
- `position`: source playlist position when available.
- `transcriptStatus`: one of `available`, `empty`, `video_unavailable`, `transcript_unavailable`, `authorization_sensitive_data`, `quota_exhaustion`, `source_unavailable`, or `upstream_failure`.
- `language`: actual source language for successful transcript results.
- `languageSource`: request-level language selection source for successful transcript results.
- `captionTrackId`: source caption-track identifier for successful transcript results.
- `segments`: ordered timestamped Transcript Segments for successful transcript results.
- `safeReason`: caller-safe limitation guidance for non-successful outcomes.

**Rules**:

- Outcomes preserve the source order returned by the one bounded playlist listing; no ranking, sorting, de-duplication, or filtering is applied.
- A playlist item without a usable public video identifier or identified as unavailable is returned as `video_unavailable` and has no transcript attempt.
- A captionless video or absence of the exact resolved language is `transcript_unavailable`.
- A successful caption with no cues is `empty`; a successful caption with cues is `available`.
- No unsuccessful outcome includes caption text, segments, credentials, protected metadata, raw source payloads, or internal details.

## Transcript Segment

Represents one ordered cue from a successfully retrieved caption track.

**Fields**:

- `text`: normalized transcript text for the cue.
- `startTimeSeconds`: non-negative cue start time.
- `endTimeSeconds`: cue end time, equal to or greater than `startTimeSeconds`.

**Relationships**:

- A successful Playlist Video Transcript Outcome contains zero or more Transcript Segments.
- Segments preserve caption-cue order.

## Fan-out Summary

Represents the bounded processing accounting for the request.

**Fields**:

- `appliedLimit`: validated item and attempt cap.
- `consideredItemCount`: number of playlist items returned by the one bounded listing.
- `transcriptAttemptCount`: number of eligible items for which caption retrieval was attempted; never greater than `consideredItemCount` or `appliedLimit`.
- `outcomeCounts`: count of outcomes by `transcriptStatus`.
- `additionalPlaylistItemsNotAttempted`: true only when the source safely indicates another page after the bounded listing.

**Relationships**:

- One Playlist Video Transcript Request produces zero or one Fan-out Summary.
- A completed summary accounts for every Playlist Video Transcript Outcome in the result.

## Whole-request Failure Outcome

Represents a safe failure before the playlist can produce per-video outcomes.

| Category | Meaning | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | Input or configured language is malformed, wrongly typed, unsupported, or out of range. | Correct the named request or configuration field and retry. |
| `unavailable_resource` | The requested playlist cannot be returned. | Use a different accessible playlist identifier. |
| `authorization_sensitive_data` | Required access cannot retrieve the playlist listing. | Obtain appropriate access if applicable. |
| `quota_exhaustion` | Capacity prevents the playlist listing. | Retry after capacity is available. |
| `upstream_failure` | Another source failure prevents playlist listing. | Retry when the source service is available. |

**Safety Rules**:

- Whole-request and per-video failures never contain credentials, authorization values, caption text, raw source responses, signed links, private owner context, or stack traces.

## Request State Transitions

```text
received
  -> invalid_parameters
  -> language_resolved
       -> playlist_listing
            -> unavailable_resource
            -> authorization_sensitive_data
            -> quota_exhaustion
            -> upstream_failure
            -> empty_success
            -> bounded_fan_out
                 -> per_item_video_unavailable | per_item_transcript_attempt
                 -> completed_partial_or_full_success
```
