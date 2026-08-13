# MCP Contract: `transcripts_getTimestampedCaptions`

## Purpose

Retrieve accessible timestamped caption segments for one YouTube video so an MCP client can relate caption text to explicit video-timeline positions.

## Compatibility and Migration

This is an additive public MCP tool. It changes no existing tool name, schema, or result shape, so no client migration is required. Its executable discovery metadata must not include `representativeOnly`.

## Input Contract

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["videoId"],
  "properties": {
    "videoId": { "type": "string", "minLength": 1 },
    "language": { "type": "string", "minLength": 1 }
  }
}
```

The handler trims text inputs and validates a supplied `language` as a language tag. Unknown fields, empty text, and incorrectly typed values are `invalid_parameters` and do not invoke caption discovery.

## Track Selection and Composition Boundary

| Aspect | Contract |
|--------|----------|
| Explicit language | Match an accessible usable source track with the exact normalized language tag; do not substitute another language or translate. |
| No language | Select a usable source-designated default only when a documented source default indicator is supplied; otherwise select the first usable track in completed source order. |
| Usable track | A track that is returned by authorized listing, has an identifier and language, and is not in the source `failed` state. |
| Discovery dependency | One authorized `captions.list` request using `part: snippet` and the requested video. |
| Download dependency | At most one authorized `captions.download` request for the selected track using `tfmt: vtt`. |
| Segment representation | VTT is decoded into one normalized segment per valid source cue. Each segment carries source cue text and explicit start/end elapsed seconds. |
| Boundedness | One video, zero or one selected track, one discovery call, and at most one download call. |
| Authentication | Eligible OAuth authorization is required, including permission to download the selected caption track. |
| Quota caveat | A normal successful flow uses 50 caption-discovery plus 200 caption-download quota units before retries. |
| Fallback policy | No public, third-party, translated, or other-language fallback is used. |

## Successful Result Contract

```json
{
  "videoId": "abc123",
  "language": "en",
  "languageSelectionSource": "explicit_language",
  "captionTrackId": "caption-track-123",
  "availability": "available",
  "segments": [
    {
      "text": "First spoken sentence.",
      "startTimeSeconds": 0.0,
      "endTimeSeconds": 1.25
    },
    {
      "text": "Second spoken sentence.",
      "startTimeSeconds": 1.25,
      "endTimeSeconds": 3.5
    }
  ],
  "fieldProvenance": {
    "videoId": "normalized",
    "language": "raw_upstream",
    "languageSelectionSource": "normalized",
    "captionTrackId": "raw_upstream",
    "availability": "normalized",
    "segments.text": "normalized",
    "segments.startTimeSeconds": "normalized",
    "segments.endTimeSeconds": "normalized"
  }
}
```

`startTimeSeconds` and `endTimeSeconds` are non-negative elapsed seconds from the beginning of the video, and an end time is never earlier than its segment's start time. Segments retain the selected source track's cue order and boundaries; adjacent, overlapping, and blank-text cues remain distinct. Markup is removed and entities are decoded from cue text, but caption text is otherwise not merged, split, sorted, translated, or generated.

A completed authorized empty caption listing without an explicit language is successful:

```json
{
  "videoId": "abc123",
  "availability": "no_accessible_captions",
  "segments": [],
  "fieldProvenance": {
    "videoId": "normalized",
    "availability": "normalized",
    "segments": "normalized"
  }
}
```

## Error Contract

The tool returns safe MCP-compatible errors with stable category data and sanitized details. It never returns caption text, VTT/raw bytes, credentials, tokens, source response bodies, signed URLs, protected track metadata, or stack traces after a failed retrieval.

| Category | When returned | Caller guidance |
|----------|---------------|-----------------|
| `invalid_parameters` | Input is missing, malformed, wrongly typed, or contains an unsupported field | Correct the named input and retry. |
| `language_unavailable` | A supplied language has no usable accessible exact-language track | Select an available language or a different video. |
| `authorization_sensitive_data` | Authorization is absent, insufficient, or cannot access the caption track | Obtain eligible caption authorization. |
| `quota_exhaustion` | Caption discovery or download cannot proceed because quota is exhausted | Retry after capacity is available. |
| `source_unavailable` | The caption-list or caption-download source endpoint is unavailable | Retry when the caption source is available. |
| `upstream_failure` | Downloaded content is malformed or undecodable, or another unclassified source operation fails | Retry when the source is available. |

`no_accessible_captions` is not an error: it confirms that authorized listing completed with no usable accessible track and no explicit language was requested. A source resource failure is never reported as this successful absence.

## Discovery Metadata Requirements

The executable descriptor must expose the public schema; `transcripts` family; timestamped-caption retrieval composition kind; both lower-layer dependencies; one-video/one-list/at-most-one-download bounds; OAuth and quota caveats; language and default-selection behavior; segment timing units and source-granularity rules; source versus normalized field provenance; the no-fallback policy; safe categories; and recovery guidance. Public metadata must pass the repository's safety validation.
