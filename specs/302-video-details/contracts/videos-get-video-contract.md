# Contract: `videos_getVideo`

## Purpose

Return normalized, caller-ready details for exactly one YouTube video. This contract is additive to the existing public tool catalog and does not alter the existing `videos_list` contract.

## Discovery Metadata

| Property | Contract |
| --- | --- |
| Public name | `videos_getVideo` |
| Family | `videos` |
| Retrieval boundary | Normalized retrieval of one video through `videos.list` |
| Lower-level dependency | `videos.list` |
| Result bound | Exactly one normalized video on success; no fan-out, ranking, or enrichment |
| Access and quota | Surface safe access and capacity caveats in metadata and errors; do not expose secrets or internal diagnostics |

## Input Contract

```json
{
  "type": "object",
  "required": ["videoId"],
  "additionalProperties": false,
  "properties": {
    "videoId": {
      "type": "string",
      "minLength": 1,
      "description": "One YouTube video identifier."
    },
    "parts": {
      "type": "array",
      "uniqueItems": true,
      "items": {
        "type": "string",
        "enum": ["snippet", "contentDetails", "statistics", "status", "topicDetails"]
      },
      "description": "Optional additive detail groups. An empty array is equivalent to omitting this field."
    }
  }
}
```

The tool rejects missing, blank, non-text, duplicate, unsupported, and unknown inputs as `invalid_parameters` before initiating the lookup.

## Result Contract

### Default normalized fields

Every successful result includes every available field from this default set:

| Field | Provenance | Source meaning |
| --- | --- | --- |
| `videoId` | raw-source | Video identifier. |
| `title`, `description`, `publishedAt` | normalized | Descriptive video metadata. |
| `channelId`, `channelTitle` | normalized | Publisher metadata. |
| `duration`, `categoryId` | normalized | Content metadata. |
| `tags`, `thumbnails` | normalized | Available descriptive collections. |

### Optional part mappings

| Requested part | Additional fields |
| --- | --- |
| `snippet` | `liveBroadcastContent`, `defaultLanguage`, `defaultAudioLanguage` |
| `contentDetails` | `dimension`, `definition`, `caption`, `licensedContent`, `regionRestriction`, `projection` |
| `statistics` | `viewCount`, `likeCount`, `favoriteCount`, `commentCount` |
| `status` | `uploadStatus`, `privacyStatus`, `license`, `embeddable`, `publicStatsViewable`, `madeForKids`, `selfDeclaredMadeForKids` |
| `topicDetails` | `topicCategories` |

The tool always obtains the source groups needed for default fields and unions any requested supported groups. It returns an optional group as an object keyed by its requested part name, containing only available mapped fields. It does not create synthetic values or expose unrequested optional groups.

### Successful example

```json
{
  "videoId": "abc123",
  "title": "Example video",
  "description": "A short description",
  "publishedAt": "2026-01-15T12:00:00Z",
  "channelId": "UC123",
  "channelTitle": "Example Channel",
  "duration": "PT12M33S",
  "categoryId": "27",
  "tags": ["example"],
  "thumbnails": {"default": "https://example.invalid/thumbnail.jpg"},
  "statistics": {"viewCount": "1000", "likeCount": "45", "favoriteCount": "0", "commentCount": "8"}
}
```

The `statistics` object appears in this example only because the client requested `statistics`.

## Error Contract

| Category | Trigger | Safe response rule |
| --- | --- | --- |
| `invalid_parameters` | Invalid `videoId`, `parts`, or unknown input field | Identify the invalid field and instruct the caller to correct it before retrying. |
| `unavailable_resource` | Empty lookup result or source not-found/removed outcome | Use a different accessible identifier; do not reveal whether the video is private, deleted, restricted, or nonexistent. |
| `authorization_sensitive_data` | Access is denied or requires authorization | Obtain appropriate authorization if applicable. |
| `quota_exhaustion` | Capacity or rate limit blocks lookup | Retry after capacity is available. |
| `upstream_failure` | Other source-service failure | Retry when the source service is available. |

All error results must omit API keys, authorization values, credentials, tokens, headers, stack traces, signed links, raw request and response bodies, and media data.

## Compatibility and Rollback

- This is an additive public tool; it does not change `videos_list` inputs or results.
- Discovery metadata must not include a representative-only marker for this executable tool.
- Rolling back removes this tool's export and default registration only; the lower-level video lookup remains intact.
