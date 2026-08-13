# MCP Contract: `transcripts_listLanguages`

## Purpose

Discover the accessible transcript or caption language tracks for one video before a client requests transcript content.

## Compatibility and Migration

This is an additive public MCP tool. It changes no existing tool name, schema, or result shape, so no client migration is required. Its executable discovery metadata must not include `representativeOnly`.

## Input Contract

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["videoId"],
  "properties": {
    "videoId": { "type": "string", "minLength": 1 }
  }
}
```

The handler trims `videoId`. Unknown fields, empty text, and non-text values are invalid parameters and do not invoke caption discovery.

## Composition Boundary

| Aspect | Contract |
|--------|----------|
| Composition kind | `transcript_language_discovery` |
| Lower-layer dependency | One authorized `captions.list` request using `part: snippet` and the requested video |
| Boundedness | One video, exactly one caption-list request, zero caption downloads |
| Authentication | Eligible OAuth authorization is required; the caller sees only tracks accessible through the configured authorized context |
| Quota caveat | A normal discovery lookup uses 50 documented caption quota units before retries |
| Selection policy | The tool exposes returned options; it does not select, rank, deduplicate, translate, or fall back between languages |
| Out of scope | Caption text, raw download data, timestamped segments, and transcript retrieval |

## Successful Result Contract

```json
{
  "videoId": "abc123",
  "languageOptions": [
    {
      "language": "en",
      "availability": "available",
      "captionTrackId": "Aeqx6m",
      "trackMetadata": {
        "name": "English",
        "status": "serving",
        "trackKind": "standard",
        "isDraft": false,
        "isAutoSynced": false
      }
    },
    {
      "language": "en",
      "availability": "available",
      "captionTrackId": "Bfdp2c",
      "trackMetadata": {
        "trackKind": "ASR"
      }
    }
  ],
  "availability": "available",
  "fieldProvenance": {
    "videoId": "normalized",
    "languageOptions.language": "raw_upstream",
    "languageOptions.captionTrackId": "raw_upstream",
    "languageOptions.trackMetadata": "raw_upstream",
    "languageOptions.availability": "normalized",
    "availability": "normalized"
  }
}
```

The result preserves every returned track as a separate option and preserves source order. `captionTrackId` is null or omitted only when the source does not provide an identifier. `trackMetadata` contains only source-provided, approved caller-relevant fields and may be empty or omitted when none are available.

A completed authorized listing with no returned tracks is successful:

```json
{
  "videoId": "abc123",
  "languageOptions": [],
  "availability": "no_accessible_languages",
  "fieldProvenance": {
    "videoId": "normalized",
    "languageOptions.language": "raw_upstream",
    "languageOptions.captionTrackId": "raw_upstream",
    "languageOptions.trackMetadata": "raw_upstream",
    "languageOptions.availability": "normalized",
    "availability": "normalized"
  }
}
```

## Error Contract

The tool returns safe MCP-compatible errors with stable category data and sanitized details. It never returns caption text, inaccessible track metadata, credentials, tokens, raw source bodies, signed URLs, or stack traces after a failed listing.

| Category | When returned | Caller guidance |
|----------|---------------|-----------------|
| `invalid_parameters` | `videoId` is missing, malformed, wrongly typed, or an unsupported field is supplied | Correct the named input and retry. |
| `authorization_sensitive_data` | Authorization is absent, insufficient, or cannot list caption tracks for the video | Obtain eligible caption authorization. |
| `quota_exhaustion` | Caption discovery cannot proceed because quota is exhausted | Retry after capacity is available. |
| `source_unavailable` | The caption-listing source endpoint is unavailable | Retry when caption discovery is available. |
| `upstream_failure` | A source resource cannot be listed or another unclassified source operation fails | Retry when the source is available or use a different video. |

`no_accessible_languages` is not an error: it confirms that a listing completed successfully without accessible options.

## Discovery Metadata Requirements

The executable descriptor must expose the public schema; `transcripts` family; language-discovery composition kind; `captions.list` dependency; one-call and no-download bounds; OAuth and quota caveats; successful and empty result shapes; source versus normalized field provenance; no selection/retrieval scope; safe categories; and recovery guidance. Public metadata must pass the repository's safety validation.
