# Tool Specifications (v1)
## Project: YouTube MCP Server on Cloud Run

## 1. Purpose
This document defines the public Layer 3 MCP tool contract for the YouTube MCP
Server.

It is intentionally focused on the user-facing tool layer:

- Layer 1: internal integrations and wrappers
- Layer 2: optional future lower-level/raw-resource MCP tools
- Layer 3: higher-level public MCP tools

This file specifies Layer 3 only.

## 2. Design Principles
- Tool names are grouped by domain:
  - `videos_*`
  - `transcripts_*`
  - `channels_*`
  - `playlists_*`
- Tool names do not include a redundant `youtube_` prefix.
- MCP transport, JSON-RPC framing, and top-level result/error envelopes are
  governed by the foundation contracts.
- This file defines the logical request schema and logical payload returned in
  MCP tool results.
- Public tool contracts use MCP-facing parameter names, not raw YouTube API
  parameter names.
- Tools may combine multiple upstream YouTube endpoints and local enrichment
  logic before producing a final result.
- Public contracts must distinguish:
  - raw upstream fields
  - normalized fields
  - heuristic or inferred fields

## 3. Common Conventions

### 3.1 Identifiers
- `videoId`: YouTube video ID
- `channelId`: YouTube channel ID
- `playlistId`: YouTube playlist ID
- `channelIds`: array of YouTube channel IDs

### 3.2 Time and Date Formats
- Date/time values use ISO 8601 timestamps.
- Duration values use ISO 8601 duration strings.
- Filter inputs such as `publishedAfter`, `publishedBefore`,
  `lastUploadAfter`, and `lastUploadBefore` MUST accept ISO 8601 timestamps.

### 3.3 Pagination and Limits
- The public Layer 3 catalog prefers `maxResults` over `pageSize`.
- Unless a tool defines otherwise:
  - default `maxResults` = `10`
  - maximum `maxResults` = `50`
- Batch input arrays SHOULD be validated explicitly.
- If implementation needs a lower bound than the contract default for safety or
  quota reasons, that lower bound must be documented before rollout.

### 3.4 Search and Ordering Semantics
- `query` is the canonical public search field.
- `order` maps to upstream ordering where supported.
- `sortBy` is a Layer 3 ranking field and may be implemented partly or fully in
  server-side logic after upstream retrieval.

Supported Layer 3 `sortBy` values where applicable:
- `relevance`
- `subscribers_asc`
- `subscribers_desc`
- `indie_priority`
- `recent_activity`

Semantics:
- `relevance`: preserve the base upstream or composite relevance order
- `subscribers_asc`: smallest qualifying channels first
- `subscribers_desc`: largest qualifying channels first
- `indie_priority`: prefer smaller creator-like channels over large brands when
  enough metadata exists to support that distinction
- `recent_activity`: prefer channels whose latest upload activity is more recent

### 3.5 Transcript Language Semantics
- `language` uses BCP-47-style strings such as `en`, `en-US`, or `es`.
- For transcript tools, language resolution order is:
  1. explicit `language` parameter
  2. `YOUTUBE_TRANSCRIPT_LANG`
  3. `en`

### 3.6 `parts` Semantics
`parts` is a public field that controls optional response expansion for tools
that can expose additional upstream resource parts.

The contract permits `parts` only on:
- `videos_getVideo`
- `channels_getChannels`

If `parts` is omitted:
- the tool returns its default normalized response shape
- the server MAY still fetch extra upstream data needed to populate normalized
  fields

If `parts` is present:
- only supported public part names may be requested
- unsupported part names MUST fail validation

## 4. Common Output Rules

### 4.1 Logical Payload Model
Each tool returns a logical payload object that will be embedded inside the
MCP-native tool result content.

This file does not redefine the transport envelope. It defines the
`structuredContent` payload shape that agents should expect for each tool.

### 4.2 List Result Shape
Tools returning multiple items SHOULD follow this shape when applicable:

```json
{
  "items": [],
  "nextPageToken": "token-or-null",
  "maxResults": 10,
  "totalResults": 123
}
```

Rules:
- `nextPageToken` is present when continuation is meaningful and available.
- `totalResults` is present when the server can provide it reliably.
- For composite tools, `totalResults` MAY be omitted if it would be misleading
  or disproportionately expensive to compute.

### 4.3 Raw vs Normalized vs Heuristic Fields
- Raw fields:
  - values taken directly from upstream resources with no semantic expansion
- Normalized fields:
  - values renamed or reshaped for consistency across tools
- Heuristic fields:
  - values inferred by server-side rules rather than guaranteed by YouTube

Heuristic fields MUST be documented clearly and must not masquerade as raw
YouTube guarantees.

## 5. Common Error Categories
The exact transport error envelope is governed by the MCP foundation, but Layer
3 tools should map failures into stable logical categories such as:

- `invalid_argument`
- `resource_not_found`
- `quota_exceeded`
- `upstream_unavailable`
- `transcript_unavailable`
- `language_not_available`
- `transcript_access_not_permitted`
- `partial_data_unavailable`
- `internal_execution_failure`

## 6. Upstream Endpoint Dependencies
Initial Layer 3 tools may depend on these upstream YouTube Data API endpoints:

- `videos.list`
- `search.list`
- `channels.list`
- `playlists.list`
- `playlistItems.list`
- `captions.list`
- `captions.download`

Composite tools must document where they depend on more than one endpoint.

## 7. Tool Catalog

### 7.1 Video Tools

#### 7.1.1 `videos_getVideo`
Purpose:
- Return detailed information about a single YouTube video in a normalized
  shape.

Primary upstream dependency:
- `videos.list`

Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "additionalProperties": false,
  "properties": {
    "videoId": { "type": "string", "minLength": 1 },
    "parts": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["snippet", "contentDetails", "statistics", "status", "topicDetails"]
      },
      "uniqueItems": true
    }
  }
}
```

Behavior notes:
- The tool MUST always return the default normalized video shape.
- `parts` expands the response contract to include supported optional groups.
- Unsupported parts MUST fail validation.

Logical payload:
```json
{
  "videoId": "abc123",
  "title": "Video title",
  "description": "...",
  "publishedAt": "2025-12-01T10:00:00Z",
  "channelId": "UC123",
  "channelTitle": "Channel title",
  "duration": "PT12M33S",
  "categoryId": "27",
  "tags": ["tag1", "tag2"],
  "thumbnails": {
    "default": "https://...",
    "medium": "https://...",
    "high": "https://..."
  },
  "statistics": {
    "viewCount": "1000",
    "likeCount": "45",
    "commentCount": "8"
  },
  "status": {
    "privacyStatus": "public",
    "madeForKids": false
  }
}
```

#### 7.1.2 `videos_searchVideos`
Purpose:
- Search for videos and optionally refine results using channel- and
  creator-aware filters.

Primary upstream dependencies:
- `search.list`
- optional enrichment via `channels.list`

Input schema:
```json
{
  "type": "object",
  "required": ["query"],
  "additionalProperties": false,
  "properties": {
    "query": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 },
    "order": { "type": "string", "enum": ["date", "rating", "relevance", "title", "viewCount"] },
    "publishedAfter": { "type": "string", "format": "date-time" },
    "publishedBefore": { "type": "string", "format": "date-time" },
    "channelId": { "type": "string", "minLength": 1 },
    "uniqueChannels": { "type": "boolean", "default": false },
    "channelMinSubscribers": { "type": "integer", "minimum": 0 },
    "channelMaxSubscribers": { "type": "integer", "minimum": 0 },
    "channelLastUploadAfter": { "type": "string", "format": "date-time" },
    "channelLastUploadBefore": { "type": "string", "format": "date-time" },
    "creatorOnly": { "type": "boolean", "default": false },
    "sortBy": {
      "type": "string",
      "enum": ["relevance", "subscribers_asc", "subscribers_desc", "indie_priority", "recent_activity"],
      "default": "relevance"
    }
  }
}
```

Behavior notes:
- Base retrieval comes from video search.
- Channel-level filters may require enrichment of matched videos through
  channel lookups.
- `uniqueChannels=true` means at most one returned result per distinct channel.
- `creatorOnly` applies heuristic creator-vs-brand classification where enough
  metadata exists.
- `sortBy` may reorder the candidate set after enrichment.

Logical payload:
```json
{
  "items": [
    {
      "videoId": "abc123",
      "title": "Video title",
      "description": "...",
      "publishedAt": "2025-12-01T10:00:00Z",
      "channelId": "UC123",
      "channelTitle": "Channel title",
      "thumbnails": { "medium": "https://..." },
      "channel": {
        "subscriberCount": "5000",
        "latestVideoPublishedAt": "2026-03-01T12:00:00Z",
        "creatorClassification": "creator"
      }
    }
  ],
  "maxResults": 10,
  "nextPageToken": "token-or-null"
}
```

#### 7.1.3 `videos_getStatistics`
Purpose:
- Return statistics for a single video.

Primary upstream dependency:
- `videos.list`

Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "additionalProperties": false,
  "properties": {
    "videoId": { "type": "string", "minLength": 1 }
  }
}
```

Logical payload:
```json
{
  "videoId": "abc123",
  "statistics": {
    "viewCount": "1000",
    "likeCount": "45",
    "commentCount": "8",
    "favoriteCount": "0"
  }
}
```

Behavior notes:
- Hidden or unavailable counts SHOULD be omitted or returned as null-like
  values consistently; the final implementation must not invent counts.

### 7.2 Transcript Tools

#### 7.2.1 `transcripts_getTranscript`
Purpose:
- Retrieve the transcript of a video using the supported transcript strategy.

Primary upstream dependencies:
- `captions.list`
- `captions.download`

Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "additionalProperties": false,
  "properties": {
    "videoId": { "type": "string", "minLength": 1 },
    "language": { "type": "string", "minLength": 2 }
  }
}
```

Behavior notes:
- Language resolution order is explicit `language`, then
  `YOUTUBE_TRANSCRIPT_LANG`, then `en`.
- If official caption access is required and not permitted, the tool MUST fail
  with a transcript-access-specific error rather than pretending the transcript
  does not exist.

Logical payload:
```json
{
  "videoId": "abc123",
  "language": "en",
  "segments": [
    {
      "start": 0.0,
      "duration": 4.2,
      "text": "Welcome to the video"
    }
  ],
  "fullText": "Welcome to the video ..."
}
```

#### 7.2.2 `transcripts_listLanguages`
Purpose:
- List available transcript or caption languages for a video.

Primary upstream dependency:
- `captions.list`

Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "additionalProperties": false,
  "properties": {
    "videoId": { "type": "string", "minLength": 1 }
  }
}
```

Logical payload:
```json
{
  "videoId": "abc123",
  "languages": [
    {
      "language": "en",
      "captionTrackId": "Aeqx6m",
      "trackKind": "standard",
      "isAutoSynced": false
    },
    {
      "language": "es",
      "captionTrackId": "Bfdp2c",
      "trackKind": "ASR",
      "isAutoSynced": true
    }
  ]
}
```

#### 7.2.3 `transcripts_getTimestampedCaptions`
Purpose:
- Return transcript or caption data with explicit segment timing.

Primary upstream dependencies:
- `captions.list`
- `captions.download`

Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "additionalProperties": false,
  "properties": {
    "videoId": { "type": "string", "minLength": 1 },
    "language": { "type": "string", "minLength": 2 }
  }
}
```

Logical payload:
```json
{
  "videoId": "abc123",
  "language": "en",
  "captions": [
    {
      "start": 0.0,
      "end": 4.2,
      "text": "Welcome to the video"
    }
  ]
}
```

#### 7.2.4 `transcripts_searchTranscript`
Purpose:
- Search transcript text and return matching snippets with timing.

Primary dependencies:
- transcript retrieval flow
- in-server text search

Input schema:
```json
{
  "type": "object",
  "required": ["videoId", "query"],
  "additionalProperties": false,
  "properties": {
    "videoId": { "type": "string", "minLength": 1 },
    "query": { "type": "string", "minLength": 1 },
    "language": { "type": "string", "minLength": 2 },
    "maxMatches": { "type": "integer", "minimum": 1, "maximum": 100, "default": 20 }
  }
}
```

Behavior notes:
- This is a composite tool, not a direct YouTube endpoint.
- Match order SHOULD be deterministic.
- Returned snippets SHOULD include enough surrounding text to be interpretable.

Logical payload:
```json
{
  "videoId": "abc123",
  "query": "api key",
  "matches": [
    {
      "start": 125.1,
      "duration": 3.8,
      "text": "Set your API key in Secret Manager"
    }
  ]
}
```

### 7.3 Channel Tools

#### 7.3.1 `channels_getChannel`
Purpose:
- Return information about a single channel in a normalized and enriched shape.

Primary upstream dependencies:
- `channels.list`
- optional latest-upload enrichment via `search.list` or uploads-playlist path

Input schema:
```json
{
  "type": "object",
  "required": ["channelId"],
  "additionalProperties": false,
  "properties": {
    "channelId": { "type": "string", "minLength": 1 }
  }
}
```

Logical payload:
```json
{
  "channelId": "UC123",
  "title": "Channel name",
  "description": "...",
  "latestVideoPublishedAt": "2026-03-01T12:00:00Z",
  "normalizedMetadata": {
    "country": "US",
    "defaultLanguage": "en",
    "joinedAt": "2020-01-01T00:00:00Z",
    "customUrl": "@channel",
    "emailsFound": ["contact@example.com"],
    "contactLinks": ["https://example.com"]
  },
  "heuristics": {
    "creatorClassification": "creator",
    "creatorSignals": ["has-face-forward-branding", "recent-upload-activity"]
  },
  "thumbnails": {
    "default": "https://...",
    "high": "https://..."
  }
}
```

Behavior notes:
- `normalizedMetadata` contains public normalized fields.
- `heuristics` contains inferred fields and must not be treated as canonical
  upstream truth.

#### 7.3.2 `channels_getChannels`
Purpose:
- Return information about multiple channels in one request.

Primary upstream dependency:
- `channels.list`

Input schema:
```json
{
  "type": "object",
  "required": ["channelIds"],
  "additionalProperties": false,
  "properties": {
    "channelIds": {
      "type": "array",
      "minItems": 1,
      "maxItems": 50,
      "uniqueItems": true,
      "items": { "type": "string", "minLength": 1 }
    },
    "parts": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["snippet", "statistics", "brandingSettings", "contentDetails", "status", "topicDetails"]
      },
      "uniqueItems": true
    },
    "includeLatestUpload": { "type": "boolean", "default": true }
  }
}
```

Logical payload:
```json
{
  "items": [
    {
      "channelId": "UC123",
      "title": "Channel name",
      "latestVideoPublishedAt": "2026-03-01T12:00:00Z",
      "normalizedMetadata": {
        "country": "US",
        "defaultLanguage": "en",
        "joinedAt": "2020-01-01T00:00:00Z",
        "customUrl": "@channel"
      }
    }
  ]
}
```

#### 7.3.3 `channels_searchChannels`
Purpose:
- Search for channels by handle, name, or general query.

Primary upstream dependencies:
- `search.list`
- optional enrichment via `channels.list`

Input schema:
```json
{
  "type": "object",
  "required": ["query"],
  "additionalProperties": false,
  "properties": {
    "query": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 },
    "order": { "type": "string", "enum": ["date", "relevance", "title", "videoCount"] },
    "channelType": { "type": "string", "enum": ["any", "show"] },
    "minSubscribers": { "type": "integer", "minimum": 0 },
    "maxSubscribers": { "type": "integer", "minimum": 0 },
    "lastUploadAfter": { "type": "string", "format": "date-time" },
    "lastUploadBefore": { "type": "string", "format": "date-time" },
    "creatorOnly": { "type": "boolean", "default": false },
    "sortBy": {
      "type": "string",
      "enum": ["relevance", "subscribers_asc", "subscribers_desc", "indie_priority", "recent_activity"],
      "default": "relevance"
    }
  }
}
```

Logical payload:
```json
{
  "items": [
    {
      "channelId": "UC123",
      "title": "Channel name",
      "normalizedMetadata": {
        "customUrl": "@channel",
        "joinedAt": "2020-01-01T00:00:00Z"
      },
      "statistics": {
        "subscriberCount": "5000"
      },
      "heuristics": {
        "creatorClassification": "creator"
      }
    }
  ],
  "maxResults": 10,
  "nextPageToken": "token-or-null"
}
```

#### 7.3.4 `channels_findCreators`
Purpose:
- Discover creator channels from matched or mentioning videos and then filter
  and rank them.

Primary upstream dependencies:
- `search.list`
- `channels.list`
- optional latest-activity or sample-video enrichment

Input schema:
```json
{
  "type": "object",
  "required": ["query"],
  "additionalProperties": false,
  "properties": {
    "query": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 },
    "order": { "type": "string", "enum": ["date", "relevance", "title", "viewCount"] },
    "videoPublishedAfter": { "type": "string", "format": "date-time" },
    "videoPublishedBefore": { "type": "string", "format": "date-time" },
    "channelMinSubscribers": { "type": "integer", "minimum": 0 },
    "channelMaxSubscribers": { "type": "integer", "minimum": 0 },
    "channelLastUploadAfter": { "type": "string", "format": "date-time" },
    "channelLastUploadBefore": { "type": "string", "format": "date-time" },
    "creatorOnly": { "type": "boolean", "default": true },
    "sortBy": {
      "type": "string",
      "enum": ["relevance", "subscribers_asc", "subscribers_desc", "indie_priority", "recent_activity"],
      "default": "relevance"
    },
    "sampleVideosPerChannel": { "type": "integer", "minimum": 1, "maximum": 10, "default": 3 }
  }
}
```

Behavior notes:
- This is explicitly a composite higher-level tool.
- Candidate channels may be discovered from matched videos before final
  channel-level filtering.
- Returned sample videos are illustrative support data, not exhaustive channel
  inventories.

Logical payload:
```json
{
  "items": [
    {
      "channelId": "UC123",
      "title": "Creator channel",
      "statistics": { "subscriberCount": "12000" },
      "latestVideoPublishedAt": "2026-03-01T12:00:00Z",
      "heuristics": { "creatorClassification": "creator" },
      "sampleVideos": [
        {
          "videoId": "abc123",
          "title": "Mentioned video",
          "publishedAt": "2026-02-01T12:00:00Z"
        }
      ]
    }
  ]
}
```

#### 7.3.5 `channels_listVideos`
Purpose:
- List videos for a specific channel.

Primary upstream dependencies:
- `search.list` or uploads-playlist path

Input schema:
```json
{
  "type": "object",
  "required": ["channelId"],
  "additionalProperties": false,
  "properties": {
    "channelId": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
  }
}
```

Behavior notes:
- Final implementation must document whether it uses:
  - ranked search behavior
  - uploads-playlist behavior
  - or a documented combination of both

Logical payload:
```json
{
  "channelId": "UC123",
  "items": [
    {
      "videoId": "abc123",
      "title": "Channel video",
      "publishedAt": "2025-12-01T10:00:00Z",
      "description": "...",
      "thumbnails": { "medium": "https://..." }
    }
  ],
  "maxResults": 10,
  "nextPageToken": "token-or-null"
}
```

#### 7.3.6 `channels_listPlaylists`
Purpose:
- List playlists associated with a channel.

Primary upstream dependency:
- `playlists.list`

Input schema:
```json
{
  "type": "object",
  "required": ["channelId"],
  "additionalProperties": false,
  "properties": {
    "channelId": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
  }
}
```

Logical payload:
```json
{
  "channelId": "UC123",
  "items": [
    {
      "playlistId": "PL123",
      "title": "Playlist title",
      "description": "...",
      "publishedAt": "2025-01-01T00:00:00Z",
      "itemCount": 12
    }
  ],
  "maxResults": 10,
  "nextPageToken": "token-or-null"
}
```

#### 7.3.7 `channels_getStatistics`
Purpose:
- Return statistics for a single channel.

Primary upstream dependency:
- `channels.list`

Input schema:
```json
{
  "type": "object",
  "required": ["channelId"],
  "additionalProperties": false,
  "properties": {
    "channelId": { "type": "string", "minLength": 1 }
  }
}
```

Logical payload:
```json
{
  "channelId": "UC123",
  "statistics": {
    "viewCount": "100000",
    "subscriberCount": "5000",
    "videoCount": "124"
  }
}
```

#### 7.3.8 `channels_searchContent`
Purpose:
- Search within the content of a specific channel.

Primary upstream dependency:
- `search.list`

Input schema:
```json
{
  "type": "object",
  "required": ["channelId", "query"],
  "additionalProperties": false,
  "properties": {
    "channelId": { "type": "string", "minLength": 1 },
    "query": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 },
    "order": { "type": "string", "enum": ["date", "rating", "relevance", "title", "viewCount"] }
  }
}
```

Logical payload:
```json
{
  "channelId": "UC123",
  "query": "deployment",
  "items": [
    {
      "videoId": "abc123",
      "title": "Cloud Run deployment guide",
      "publishedAt": "2025-12-01T10:00:00Z",
      "description": "..."
    }
  ],
  "maxResults": 10,
  "nextPageToken": "token-or-null"
}
```

### 7.4 Playlist Tools

#### 7.4.1 `playlists_getPlaylist`
Purpose:
- Return information about a playlist.

Primary upstream dependency:
- `playlists.list`

Input schema:
```json
{
  "type": "object",
  "required": ["playlistId"],
  "additionalProperties": false,
  "properties": {
    "playlistId": { "type": "string", "minLength": 1 }
  }
}
```

Logical payload:
```json
{
  "playlistId": "PL123",
  "title": "Playlist title",
  "description": "...",
  "channelId": "UC123",
  "channelTitle": "Channel title",
  "publishedAt": "2025-01-01T00:00:00Z",
  "itemCount": 42
}
```

#### 7.4.2 `playlists_getPlaylistItems`
Purpose:
- Return the videos contained in a playlist.

Primary upstream dependency:
- `playlistItems.list`

Input schema:
```json
{
  "type": "object",
  "required": ["playlistId"],
  "additionalProperties": false,
  "properties": {
    "playlistId": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
  }
}
```

Logical payload:
```json
{
  "playlistId": "PL123",
  "items": [
    {
      "playlistItemId": "UEx123",
      "videoId": "abc123",
      "title": "Video title",
      "position": 0,
      "publishedAt": "2025-12-01T10:00:00Z"
    }
  ],
  "maxResults": 10,
  "nextPageToken": "token-or-null"
}
```

#### 7.4.3 `playlists_searchItems`
Purpose:
- Search within a playlist for matching items.

Primary dependencies:
- `playlistItems.list`
- in-server filtering and ranking

Input schema:
```json
{
  "type": "object",
  "required": ["playlistId", "query"],
  "additionalProperties": false,
  "properties": {
    "playlistId": { "type": "string", "minLength": 1 },
    "query": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
  }
}
```

Behavior notes:
- This is a composite higher-level tool.
- Matching may inspect title and description fields from playlist items.

Logical payload:
```json
{
  "playlistId": "PL123",
  "query": "deployment",
  "items": [
    {
      "videoId": "abc123",
      "title": "Cloud Run deployment guide",
      "position": 3,
      "snippet": "..."
    }
  ]
}
```

#### 7.4.4 `playlists_getVideoTranscripts`
Purpose:
- Retrieve transcript data for videos in a playlist.

Primary dependencies:
- `playlistItems.list`
- transcript retrieval flow

Input schema:
```json
{
  "type": "object",
  "required": ["playlistId"],
  "additionalProperties": false,
  "properties": {
    "playlistId": { "type": "string", "minLength": 1 },
    "language": { "type": "string", "minLength": 2 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
  }
}
```

Behavior notes:
- This is a bounded fan-out composite tool.
- The implementation MUST document whether `maxResults` limits:
  - playlist items fetched
  - transcripts attempted
  - or both

Logical payload:
```json
{
  "playlistId": "PL123",
  "items": [
    {
      "videoId": "abc123",
      "language": "en",
      "segments": [
        {
          "start": 0.0,
          "duration": 4.2,
          "text": "Welcome"
        }
      ],
      "transcriptAvailable": true
    }
  ]
}
```

## 8. Implementation Notes for Future Agents
- Do not expose raw YouTube API response shapes directly unless the public
  contract explicitly calls for them.
- Prefer one normalized shape per tool and keep optional expansions controlled.
- When adding heuristic fields, document:
  - what the field means
  - whether it is inferred
  - what upstream data influenced it
- When a tool is composite:
  - document the upstream call flow
  - document the ranking/filtering stage
  - document any bounded fan-out rules
- When a tool exposes `maxResults`, ensure the implementation does not silently
  exceed upstream quota expectations without documentation.

## 9. Acceptance Checks
- Every public Layer 3 tool has JSON-schema-validatable input.
- Every tool has a documented logical payload for MCP `structuredContent`.
- Composite tools are explicitly labeled as composite.
- Transcript tools document language fallback and auth-sensitive behavior.
- Channel enrichment tools document normalized and heuristic fields.
- Search tools document ranking and filtering semantics where implemented
  partly in-server.
