# Data Model: YT-314 Timestamped Caption Retrieval

## Timestamped Caption Request

Represents one public `transcripts_getTimestampedCaptions` invocation.

**Fields**:

- `videoId`: required, trimmed, non-empty video identifier.
- `language`: optional, trimmed language tag requested explicitly by the caller.

**Validation Rules**:

- No unknown fields are accepted.
- `videoId` and a supplied `language` must be text and remain non-empty after trimming.
- A supplied language must be a valid normalized language tag.
- Invalid input ends before a caption-list request is attempted.

## Caption Track Selection

Represents the one accessible source caption track chosen for a request.

**Fields**:

- `captionTrackId`: source-provided identifier for the selected track.
- `language`: source-provided language tag of the selected track.
- `selectionSource`: `explicit_language`, `source_default`, or `source_order_fallback`.
- `status`: source track state used to exclude failed tracks.

**Validation and Selection Rules**:

- A supplied language must exactly match a usable track's normalized source language; no translated, base-language, or other-language substitution is permitted.
- A source-designated default may be chosen only when a documented source default indicator is present and the track is usable.
- Without an explicit language or source-designated default, select the first usable track in completed source order.
- A failed track is not usable. Other source attributes are not inferred or exposed unless the public contract explicitly allows them.
- One request selects zero or one Caption Track Selection.

## Timestamped Caption Segment

Represents one VTT source cue supplied by the selected caption track.

**Fields**:

- `text`: source cue text after safe markup removal and entity decoding; it may be empty.
- `startTimeSeconds`: non-negative elapsed seconds from the beginning of the video.
- `endTimeSeconds`: non-negative elapsed seconds from the beginning of the video and not earlier than `startTimeSeconds`.

**Validation and Presentation Rules**:

- One valid source cue creates exactly one Timestamped Caption Segment.
- Cue order and timing boundaries are preserved. Adjacent or overlapping cues are not merged, split, or reordered.
- Timing accepts the VTT forms `MM:SS.mmm` and `HH:MM:SS.mmm` and is normalized to numeric elapsed seconds.
- An undecodable or malformed download, including missing or malformed cue timing, produces an `upstream_failure` without partial segments.

## Timestamped Caption Result

Represents a completed successful retrieval.

**Fields**:

- `videoId`: normalized requested video identifier.
- `language`: selected source track's language.
- `languageSelectionSource`: normalized description of how the track was selected.
- `captionTrackId`: selected source track identifier.
- `availability`: `available` when a selected track is successfully parsed, or `no_accessible_captions` only after a completed empty listing without an explicit language.
- `segments`: ordered collection of zero or more Timestamped Caption Segments.
- `fieldProvenance`: field-category mapping that distinguishes source-provided and normalized result fields.

**Relationships**:

- One Timestamped Caption Request causes exactly one caption-listing operation.
- One Caption Track Selection causes at most one caption-download operation.
- One successful parsed download yields one Timestamped Caption Result containing zero or more Timestamped Caption Segments.

**State Transitions**:

```text
valid request + explicit language -> exact usable track -> VTT download -> available
valid request + no language -> source default usable track -> VTT download -> available
valid request + no language + no source default -> first usable source-order track -> VTT download -> available
valid request + no language + completed empty listing -> no_accessible_captions
valid request + explicit language + no usable exact track -> language_unavailable
valid request -> authorization unavailable -> authorization_sensitive_data
valid request -> quota exhausted -> quota_exhaustion
valid request -> source endpoint unavailable -> source_unavailable
valid request -> malformed/undecodable VTT or unexpected source failure -> upstream_failure
invalid request -> invalid_parameters
```

## Safe Failure Outcome

Represents a non-success result without caption segments or caption content.

**Fields**:

- `category`: stable public error category.
- `message`: safe recovery-oriented explanation.
- `details`: optional sanitized diagnostics; a requested language is permitted only when needed to explain `language_unavailable`.

**Validation Rules**:

- Never includes caption text, VTT/raw bytes, credentials, authorization values, source response bodies, signed URLs, protected track metadata, or internal traces.
- `no_accessible_captions` is a successful Timestamped Caption Result, never a failure category.
