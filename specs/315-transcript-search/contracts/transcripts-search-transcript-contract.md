# MCP Contract: `transcripts_searchTranscript`

## Purpose

Search accessible timestamped transcript segments for one YouTube video and return chronological matching snippets with the corresponding video-timeline positions.

## Compatibility and Migration

This is an additive public MCP tool. It changes no existing tool name, schema, or result shape, so no client migration is required. Its executable discovery metadata must not include `representativeOnly`.

## Input Contract

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["videoId", "query"],
  "properties": {
    "videoId": { "type": "string", "minLength": 1 },
    "query": { "type": "string", "minLength": 1 },
    "language": { "type": "string", "minLength": 1 },
    "maxMatches": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
  }
}
```

The handler trims textual inputs. Unknown fields, wrong types, blank text, malformed language, and an out-of-range `maxMatches` are `invalid_parameters` and do not retrieve captions.

## Composition, Match, and Snippet Rules

| Aspect | Contract |
|---|---|
| Timed retrieval dependency | One injected `transcripts_getTimestampedCaptions` handler call for the requested video and optional language. |
| Underlying boundedness | The timed dependency performs one authorized caption discovery and at most one authorized caption download. |
| Language | A supplied language uses the timed dependency's exact matching policy. Without one, its source-default then source-order policy applies. No translation or other-language fallback occurs. |
| Match rule | Unicode case-insensitive literal matching within one normalized source segment only. A segment returns once even if it has several occurrences. |
| Cross-segment rule | A phrase spanning segment boundaries is not a match; no synthetic timing or context is created. |
| Ranking | Matches sort by ascending segment start time; equal start times retain source segment order. The limit applies after sorting. |
| Snippet | The first source-text match anchors a same-segment context window of up to 160 characters. Ellipses identify omitted text; no ellipsis appears at a segment boundary with no omitted text. |
| Authentication and quota | Official caption access requires eligible OAuth authorization. The underlying normal retrieval uses caption discovery and caption-download quota. |

## Successful Result Contract

When a selected transcript has matching segments:

```json
{
  "videoId": "abc123",
  "language": "en",
  "languageSelectionSource": "explicit_language",
  "captionTrackId": "caption-track-123",
  "availability": "available",
  "matches": [
    {
      "matchedText": "launch plan",
      "snippet": "...the launch plan begins with the research phase...",
      "startTimeSeconds": 42.5,
      "endTimeSeconds": 48.0
    }
  ],
  "fieldProvenance": {
    "videoId": "normalized",
    "language": "raw_upstream",
    "languageSelectionSource": "normalized",
    "captionTrackId": "raw_upstream",
    "availability": "normalized",
    "matches.matchedText": "normalized_source_segment",
    "matches.snippet": "normalized_source_segment",
    "matches.startTimeSeconds": "normalized_source_segment",
    "matches.endTimeSeconds": "normalized_source_segment"
  }
}
```

`startTimeSeconds` and `endTimeSeconds` are the matching segment's non-negative elapsed seconds from the beginning of the video. `matchedText` preserves source casing. Snippets and timestamps reflect only the selected source segment and may inherit source-caption timing or text limitations.

When timed retrieval succeeds for a selected language but no segment matches, the response is successful:

```json
{
  "videoId": "abc123",
  "language": "en",
  "languageSelectionSource": "source_default",
  "captionTrackId": "caption-track-123",
  "availability": "no_matches",
  "matches": [],
  "fieldProvenance": {
    "videoId": "normalized",
    "language": "raw_upstream",
    "languageSelectionSource": "normalized",
    "captionTrackId": "raw_upstream",
    "availability": "normalized",
    "matches": "normalized"
  }
}
```

## Error Contract

The tool returns safe MCP-compatible errors with stable category data and sanitized details. It never returns caption text, snippets, VTT bytes, credentials, tokens, source response bodies, signed URLs, protected track data, or stack traces after failure.

| Category | When returned | Caller guidance |
|---|---|---|
| `invalid_parameters` | Input is absent, malformed, wrongly typed, or has an unsupported field | Correct the named input and retry. |
| `transcript_unavailable` | No accessible caption track exists for an omitted-language request | Use a different video or obtain eligible caption access. |
| `language_unavailable` | A supplied language has no usable accessible exact-language track | Select an available language or a different video. |
| `authorization_sensitive_data` | Authorization is absent, insufficient, or cannot access the caption track | Obtain eligible caption authorization. |
| `quota_exhaustion` | Caption retrieval cannot proceed because quota is exhausted | Retry after capacity is available. |
| `source_unavailable` | Caption retrieval source is temporarily unavailable | Retry when the source is available. |
| `upstream_failure` | Caption content or another source operation cannot complete safely | Retry when the source is available. |

An absent literal match is not an error and never uses `no_matching_results`.

## Discovery Metadata Requirements

The executable descriptor must expose the public schema; transcript-text-search composition kind; timestamped-retrieval and local-search dependencies; one-video boundedness; literal-match, snippet, ordering, and no-cross-segment rules; field provenance; underlying caption authorization/quota caveats; `no_matches` empty-result policy; safe categories and recovery guidance. Metadata must pass the repository's public-safety validation.
