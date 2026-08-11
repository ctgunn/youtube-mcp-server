# MCP Contract: `transcripts_getTranscript`

## Purpose

Retrieve complete plain transcript text for one YouTube video in one predictable, authorized official-caption language.

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

The handler trims text inputs and validates that `language`, when supplied, is a valid language tag. Unknown fields, empty text, and incorrectly typed values are invalid parameters.

## Language Selection and Composition Boundary

| Aspect | Contract |
|--------|----------|
| Language order | Explicit `language`, then configured `YOUTUBE_TRANSCRIPT_LANG`, then `en` |
| Matching | Exact normalized BCP-47 tag only; no base-language substitution or translation |
| Track selection | Exclude failed tracks; prefer serving, standard, non-draft tracks; use caption identifier as final tie-breaker |
| Discovery dependency | One authorized `captions.list` request for the video |
| Download dependency | At most one authorized `captions.download` request for the selected track |
| Download representation | VTT is normalized to complete plain text; timestamps and raw caption bytes are not returned |
| Boundedness | One video, zero or one selected track, one discovery call, and at most one download call |
| Authentication | Eligible OAuth authorization is required, including permission to download the target caption track |
| Quota caveat | A normal successful flow uses 50 caption-discovery plus 200 caption-download quota units before retries |
| Fallback policy | No public, third-party, other-language, or translated fallback is used |

## Successful Result Contract

```json
{
  "videoId": "abc123",
  "language": "en",
  "languageSource": "explicit",
  "availability": "available",
  "captionTrackId": "caption-track-123",
  "text": "First spoken sentence. Second spoken sentence.",
  "fieldProvenance": {
    "videoId": "normalized",
    "language": "normalized",
    "languageSource": "normalized",
    "availability": "normalized",
    "captionTrackId": "raw_upstream",
    "text": "normalized"
  }
}
```

`captionTrackId` is omitted only when the source does not provide it. A successfully downloaded track with no textual cues returns the same shape with `availability: "empty"` and `text: ""`. Timestamped segment output is outside this contract.

## Error Contract

The tool returns safe MCP-compatible errors with stable category data and sanitized details. It never returns transcript text, downloaded bytes, credentials, tokens, raw source bodies, signed URLs, or stack traces after a failed retrieval.

| Category | When returned | Caller guidance |
|----------|---------------|-----------------|
| `invalid_parameters` | Input or configured default is missing, malformed, wrongly typed, or unsupported | Correct the named input or configuration and retry. |
| `transcript_unavailable` | No accessible exact-language track exists, or the selected track is no longer available | Request an available language or a different video. |
| `authorization_sensitive_data` | Authorization is absent, insufficient, or cannot access the associated caption track | Obtain eligible caption authorization. |
| `quota_exhaustion` | Caption discovery or download cannot proceed because quota is exhausted | Retry after capacity is available. |
| `upstream_failure` | The source service, content decoding, or another non-classified operation fails | Retry when the source is available. |

For `transcript_unavailable`, safe detail may identify the resolved language. It must not claim another-language content was used.

## Discovery Metadata Requirements

The executable descriptor must expose the public schema; transcript-retrieval composition kind; both dependencies; official OAuth and quota caveats; one-video/one-download boundedness; exact language policy; selection rule; response field provenance; empty-text behavior; no-fallback policy; safe error categories; and recovery guidance. Metadata must pass the repository's public-safety validation.
